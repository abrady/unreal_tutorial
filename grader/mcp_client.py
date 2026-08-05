"""Minimal MCP client for driving a running Unreal editor.

Speaks the same HTTP JSON-RPC that an AI client uses, with no AI involved.
Standard library only, so the grader has no install step beyond pytest.

Verified against UE 5.8's built-in ModelContextProtocol plugin:

  endpoint        http://localhost:8000/mcp
  session header  Mcp-Session-Id
  version header  Mcp-Protocol-Version
  initialize      plain application/json response
  tools/call      streaming SSE on the POST connection - no Content-Length,
                  no chunked encoding, result arrives as an `event: message`
                  frame. This is why the transport is raw sockets rather
                  than urllib, which cannot read that shape.
  tool results    the return value is wrapped as {"returnValue": ...}
  tool names      fully qualified as <Plugin>.<Toolset>.<Tool>
  optional args   TOptional<> parameters must still be sent explicitly as
                  null; omitting the key is rejected despite the tool's
                  inputSchema listing no required fields.
"""

from __future__ import annotations

import json
import socket
from typing import Any
from urllib.parse import urlparse

PROTOCOL_VERSION = "2025-11-25"
DEFAULT_URL = "http://localhost:8000/mcp"


class McpError(RuntimeError):
    """A JSON-RPC error, a tool-reported failure, or an unreachable editor."""


class CheckFailed(Exception):
    """A check didn't pass.

    Lives here rather than in the runner so that `from check import
    CheckFailed` can't resolve to a second copy of the class when check.py is
    executed as __main__ - which silently breaks every except clause.
    """


class EditorNotRunning(McpError):
    """Nothing is listening on the MCP endpoint."""


class UnrealMcp:
    def __init__(self, url: str = DEFAULT_URL, timeout: float = 180.0) -> None:
        parsed = urlparse(url)
        self.url = url
        self.host = parsed.hostname or "localhost"
        self.port = parsed.port or 80
        self.path = parsed.path or "/mcp"
        self.timeout = timeout
        self.session_id: str | None = None
        self._next_id = 0
        self._tools: list[str] = []
        self._tool_search = False

    # -- lifecycle ---------------------------------------------------------

    def connect(self) -> UnrealMcp:
        self._request(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "unreal-tutorial-grader", "version": "1.0"},
            },
        )
        self._notify("notifications/initialized")
        self._tools = [tool["name"] for tool in self.list_tools()]
        self._tool_search = "call_tool" in self._tools
        return self

    def __enter__(self) -> UnrealMcp:
        return self.connect()

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        if not self.session_id:
            return
        try:
            self._exchange("DELETE", None, expect_id=None)
        except McpError:
            pass  # editor may already be gone; nothing to clean up
        self.session_id = None

    # -- tools -------------------------------------------------------------

    def list_tools(self) -> list[dict[str, Any]]:
        return self._request("tools/list", {}).get("tools", [])

    def tools(self) -> list[str]:
        """Every registered tool name, fully qualified."""
        return list(self._tools)

    def has_tool(self, tool_name: str, toolset: str | None = None) -> bool:
        return self._resolve(tool_name, toolset) is not None

    def _resolve(self, tool_name: str, toolset: str | None = None) -> str | None:
        """Map a short tool name onto its fully-qualified registration.

        The engine registers tools as `<Plugin>.<Toolset>.<Tool>`, so a check
        asking for `StartPIE` must match `EditorToolset.EditorAppToolset.StartPIE`.
        """
        if tool_name in self._tools:
            return tool_name

        matches = [t for t in self._tools if t.rsplit(".", 1)[-1] == tool_name]
        if toolset:
            matches = [t for t in matches if toolset in t.split(".")]

        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise McpError(
                f"{tool_name!r} is ambiguous: {matches}. Pass toolset= to disambiguate."
            )
        return None

    def call(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        toolset: str | None = None,
    ) -> Any:
        """Invoke a tool by short or fully-qualified name.

        Works whether or not bEnableToolSearch is enabled, so a learner's
        editor settings can't silently break the grader.
        """
        arguments = arguments or {}
        resolved = self._resolve(tool_name, toolset)

        if resolved:
            payload = {"name": resolved, "arguments": arguments}
        elif self._tool_search:
            inner: dict[str, Any] = {"tool_name": tool_name, "arguments": arguments}
            if toolset:
                inner["toolset_name"] = toolset
            payload = {"name": "call_tool", "arguments": inner}
        else:
            near = [t for t in self._tools if tool_name.lower() in t.lower()][:5]
            hint = f" Did you mean: {near}?" if near else ""
            raise McpError(
                f"No tool named {tool_name!r} among {len(self._tools)} registered "
                f"tools, and tool-search is off.{hint}"
            )

        return self._unwrap(self._request("tools/call", payload))

    # -- PIE convenience ---------------------------------------------------

    def start_pie(self, warmup_seconds: float = 0.0, simulate: bool = False) -> Any:
        """Start Play-In-Editor.

        StartPIE's schema requires bSimulate, playMode and warmupSeconds, so
        they're always sent rather than left to defaults.
        """
        return self.call(
            "StartPIE",
            {
                "options": {
                    "bSimulate": simulate,
                    "playMode": "PlayMode_InViewPort",
                    "warmupSeconds": warmup_seconds,
                }
            },
        )

    def stop_pie(self) -> Any:
        return self.call("StopPIE")

    def is_pie_running(self) -> bool:
        return bool(self.call("IsPIERunning"))

    # -- json-rpc ----------------------------------------------------------

    def _request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self._next_id += 1
        request_id = self._next_id
        response = self._exchange(
            "POST",
            {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params},
            expect_id=request_id,
        )

        if response is None:
            raise McpError(f"{method}: empty response")
        if "error" in response:
            err = response["error"]
            raise McpError(f"{method}: [{err.get('code')}] {err.get('message')}")
        return response.get("result", {})

    def _notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        self._exchange(
            "POST",
            {"jsonrpc": "2.0", "method": method, "params": params or {}},
            expect_id=None,
        )

    # -- transport ---------------------------------------------------------

    def _exchange(
        self, verb: str, body: dict[str, Any] | None, expect_id: int | None
    ) -> dict[str, Any] | None:
        """One request/response over a fresh connection.

        Handles both reply shapes the server uses: a plain JSON body with a
        Content-Length, and a keep-alive SSE stream whose frames arrive with
        no length header at all.
        """
        payload = json.dumps(body).encode() if body is not None else b""
        lines = [
            f"{verb} {self.path} HTTP/1.1",
            f"Host: {self.host}:{self.port}",
            "Content-Type: application/json",
            "Accept: application/json, text/event-stream",
            f"Mcp-Protocol-Version: {PROTOCOL_VERSION}",
            f"Content-Length: {len(payload)}",
        ]
        if self.session_id:
            lines.append(f"Mcp-Session-Id: {self.session_id}")
        raw = ("\r\n".join(lines) + "\r\n\r\n").encode() + payload

        try:
            conn = socket.create_connection((self.host, self.port), timeout=self.timeout)
        except OSError as exc:
            raise EditorNotRunning(
                f"Could not reach the MCP server at {self.url} ({exc}).\n"
                "Is the Unreal editor open with the ModelContextProtocol plugin "
                "enabled? Launch it with -ModelContextProtocolStartServer, or set "
                "bAutoStartServer=True. See SETUP.md."
            ) from exc

        try:
            conn.settimeout(self.timeout)
            conn.sendall(raw)
            head, rest = self._read_headers(conn)
            status, headers = self._parse_head(head)

            session = headers.get("mcp-session-id")
            if session:
                self.session_id = session

            if status >= 400:
                raise McpError(f"HTTP {status} from {self.url}: {rest[:500]!r}")

            if "text/event-stream" in headers.get("content-type", ""):
                return self._read_sse(conn, rest, expect_id)

            length = int(headers.get("content-length", 0))
            while len(rest) < length:
                chunk = conn.recv(65536)
                if not chunk:
                    break
                rest += chunk
            text = rest.decode(errors="replace").strip()
            return json.loads(text) if text else None
        finally:
            conn.close()

    @staticmethod
    def _read_headers(conn: socket.socket) -> tuple[bytes, bytes]:
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = conn.recv(65536)
            if not chunk:
                raise McpError("connection closed before headers were complete")
            buf += chunk
        head, _, rest = buf.partition(b"\r\n\r\n")
        return head, rest

    @staticmethod
    def _parse_head(head: bytes) -> tuple[int, dict[str, str]]:
        lines = head.decode(errors="replace").split("\r\n")
        status = int(lines[0].split()[1])
        headers = {}
        for line in lines[1:]:
            key, _, value = line.partition(":")
            if key:
                headers[key.strip().lower()] = value.strip()
        return status, headers

    def _read_sse(
        self, conn: socket.socket, buffered: bytes, expect_id: int | None
    ) -> dict[str, Any] | None:
        """Read SSE frames until the reply we're waiting for shows up.

        Progress notifications share the stream, so frames that aren't our
        response get skipped rather than mistaken for the result.
        """
        if expect_id is None:
            return None

        buf = buffered
        while True:
            while b"\r\n\r\n" in buf:
                frame, _, buf = buf.partition(b"\r\n\r\n")
                data = "".join(
                    line.partition("data:")[2].strip()
                    for line in frame.decode(errors="replace").splitlines()
                    if line.startswith("data:")
                )
                if not data:
                    continue
                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    continue
                if message.get("id") == expect_id:
                    return message

            chunk = conn.recv(65536)
            if not chunk:
                raise McpError(
                    f"stream closed before a reply to request {expect_id} arrived"
                )
            buf += chunk

    # -- results -----------------------------------------------------------

    @staticmethod
    def _unwrap(result: dict[str, Any]) -> Any:
        """Reduce an MCP tool result to the useful part.

        Engine tools wrap their return as {"returnValue": ...}; that gets
        peeled off. Some tools then put a JSON *string* inside it, so a
        second parse is attempted before giving up.
        """
        if result.get("isError"):
            raise McpError(UnrealMcp._text_of(result) or "tool reported an error")

        value: Any
        if "structuredContent" in result:
            value = result["structuredContent"]
        else:
            text = UnrealMcp._text_of(result)
            if text is None:
                return result
            try:
                value = json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return text

        if isinstance(value, dict) and set(value) == {"returnValue"}:
            value = value["returnValue"]

        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith(("{", "[")):
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError:
                    return value
        return value

    @staticmethod
    def _text_of(result: dict[str, Any]) -> str | None:
        chunks = [
            block.get("text", "")
            for block in result.get("content", [])
            if block.get("type") == "text"
        ]
        return "\n".join(chunks) if chunks else None

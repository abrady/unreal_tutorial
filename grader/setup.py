#!/usr/bin/env python3
"""Get this machine ready for the lab.

    python3 grader/setup.py

Finds your Unreal install, builds the project, starts the editor with its MCP
server, and verifies the whole chain end to end. Standard library only.

Written to be run by an AI agent on the learner's behalf, so every failure
says what to do next rather than just what went wrong. Safe to re-run.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
UPROJECT = REPO / "Lab01_FirstRoom" / "Lab01.uproject"
MIN_MINOR = 8
PORT = 8000

_TTY = sys.stdout.isatty()
GREEN, RED, YELLOW, DIM, BOLD, OFF = (
    ("\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m")
    if _TTY else ("",) * 6
)


def say(msg: str = "") -> None:
    print(msg, flush=True)


def ok(msg: str) -> None:
    say(f"  {GREEN}✓{OFF} {msg}")


def warn(msg: str) -> None:
    say(f"  {YELLOW}!{OFF} {msg}")


class SetupFailed(Exception):
    """Something the learner (or their agent) has to act on."""


# -- finding the engine ---------------------------------------------------


def candidate_engines() -> list[Path]:
    home = Path.home()
    found: list[Path] = []

    # Whatever the Epic Launcher registered.
    manifests = [
        home / "Library/Application Support/Epic/UnrealEngineLauncher/LauncherInstalled.dat",
        Path(os.environ.get("PROGRAMDATA", "C:/ProgramData"))
        / "Epic/UnrealEngineLauncher/LauncherInstalled.dat",
    ]
    for manifest in manifests:
        try:
            for entry in json.loads(manifest.read_text()).get("InstallationList", []):
                location = entry.get("InstallLocation")
                if location:
                    found.append(Path(location))
        except (OSError, json.JSONDecodeError):
            pass

    # Common install roots, plus source builds.
    for guess in (
        home / "UE_5.8",
        Path("/Users/Shared/Epic Games/UE_5.8"),
        Path("C:/Program Files/Epic Games/UE_5.8"),
    ):
        found.append(guess)
    found.extend(sorted(home.glob("ue5*")))
    found.extend(sorted(home.glob("UnrealEngine*")))

    seen, unique = set(), []
    for path in found:
        if path not in seen:
            seen.add(path)
            unique.append(path)
    return unique


def engine_version(root: Path) -> tuple[int, int, int] | None:
    try:
        data = json.loads((root / "Engine/Build/Build.version").read_text())
        return data["MajorVersion"], data["MinorVersion"], data.get("PatchVersion", 0)
    except (OSError, json.JSONDecodeError, KeyError):
        return None


def find_engine() -> tuple[Path, tuple[int, int, int]]:
    override = os.environ.get("UNREAL_ENGINE_ROOT")
    roots = [Path(override)] if override else candidate_engines()

    rejected = []
    for root in roots:
        version = engine_version(root)
        if not version:
            continue
        if (version[0], version[1]) < (5, MIN_MINOR):
            rejected.append(f"{root}  (found {version[0]}.{version[1]}, need 5.{MIN_MINOR}+)")
            continue
        if not (root / "Engine/Plugins/Experimental/ModelContextProtocol").is_dir():
            rejected.append(f"{root}  (no ModelContextProtocol plugin)")
            continue
        return root, version

    detail = "\n".join(f"      {r}" for r in rejected)
    raise SetupFailed(
        f"Couldn't find Unreal 5.{MIN_MINOR} or newer with the MCP plugin.\n\n"
        + (f"    Engines I looked at but couldn't use:\n{detail}\n\n" if rejected else "")
        + "    Install Unreal 5.8+ from the Epic Games Launcher, or point me at\n"
        "    an existing install:\n\n"
        "        UNREAL_ENGINE_ROOT=/path/to/UE_5.8 python3 grader/setup.py"
    )


# -- building -------------------------------------------------------------


def build_script(engine: Path) -> Path:
    name = {"Darwin": "Mac/Build.sh", "Windows": "Build.bat"}.get(
        platform.system(), "Linux/Build.sh"
    )
    path = engine / "Engine/Build/BatchFiles" / name
    if not path.exists():
        raise SetupFailed(f"No build script at {path}. Is this a complete engine install?")
    return path


def editor_is_running() -> bool:
    try:
        out = subprocess.run(
            ["pgrep", "-f", "Lab01.uproject"], capture_output=True, text=True, timeout=10
        )
        return bool(out.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        return False


def stop_editor() -> None:
    subprocess.run(["pkill", "-f", "Lab01.uproject"], capture_output=True)
    time.sleep(5)


def build_project(engine: Path) -> None:
    target = "Lab01Editor"
    host = {"Darwin": "Mac", "Windows": "Win64"}.get(platform.system(), "Linux")
    cmd = [
        str(build_script(engine)), target, host, "Development",
        f"-Project={UPROJECT}", "-WaitMutex",
    ]
    say(f"  {DIM}building {target}… (first run can take a few minutes){OFF}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)

    if result.returncode != 0:
        errors = [
            line for line in (result.stdout + result.stderr).splitlines()
            if "error:" in line.lower()
        ][:12]
        raise SetupFailed(
            "The project didn't build.\n\n"
            + ("\n".join(f"      {e}" for e in errors) if errors else
               "      (no compiler errors found — see the full log above)")
            + "\n\n    If this mentions hot reload or hyphens, the editor is still\n"
            "    open. Close it and re-run."
        )


# -- launching ------------------------------------------------------------


def port_open(port: int = PORT) -> bool:
    with socket.socket() as probe:
        probe.settimeout(0.5)
        return probe.connect_ex(("127.0.0.1", port)) == 0


def launch_editor(engine: Path) -> None:
    binary = {
        "Darwin": engine / "Engine/Binaries/Mac/UnrealEditor",
        "Windows": engine / "Engine/Binaries/Win64/UnrealEditor.exe",
    }.get(platform.system(), engine / "Engine/Binaries/Linux/UnrealEditor")

    if not binary.exists():
        raise SetupFailed(f"No editor binary at {binary}.")

    log = Path("/tmp/lab01_editor.log")
    with log.open("w") as handle:
        subprocess.Popen(
            [str(binary), str(UPROJECT), "-ModelContextProtocolStartServer"],
            stdout=handle, stderr=subprocess.STDOUT, start_new_session=True,
        )

    say(f"  {DIM}starting the editor… (up to 3 minutes on a cold open){OFF}")
    for _ in range(180):
        if port_open():
            return
        time.sleep(1)

    raise SetupFailed(
        f"The editor started but its MCP server never came up on port {PORT}.\n\n"
        "    Two things to check:\n"
        "      • A modal dialog may be blocking startup. Look for\n"
        "        \"Missing Lab01 Modules\" behind your other windows and click Yes.\n"
        f"      • Something else may hold port {PORT}: lsof -nP -iTCP:{PORT}\n\n"
        f"    Editor log: {log}"
    )


# -- client wiring --------------------------------------------------------

MCP_ENTRY = {"type": "http", "url": f"http://localhost:{PORT}/mcp"}


def wire_client() -> str:
    """Add the server to ~/.claude.json if it isn't there. Returns a status."""
    config = Path.home() / ".claude.json"
    try:
        data = json.loads(config.read_text()) if config.exists() else {}
    except (OSError, json.JSONDecodeError):
        return "unreadable"

    servers = data.setdefault("mcpServers", {})
    if servers.get("unreal") == MCP_ENTRY:
        return "already"

    servers["unreal"] = MCP_ENTRY
    try:
        if config.exists():
            shutil.copy(config, config.with_suffix(".json.lab-backup"))
        config.write_text(json.dumps(data, indent=2))
    except OSError:
        return "unwritable"
    return "added"


# -- main -----------------------------------------------------------------


def main() -> int:
    say(f"\n{BOLD}Setting up the Unreal lab{OFF}\n")

    try:
        engine, version = find_engine()
        ok(f"Unreal {version[0]}.{version[1]}.{version[2]} at {engine}")

        if editor_is_running():
            warn("An editor is already open — closing it so the build can run.")
            stop_editor()

        build_project(engine)
        ok("Project builds")

        launch_editor(engine)
        ok(f"Editor running, MCP server up on port {PORT}")

    except SetupFailed as exc:
        say(f"\n  {RED}✗{OFF} {exc}\n")
        return 1

    checks = subprocess.run(
        [sys.executable, str(REPO / "grader/check.py"), "ch00"],
        capture_output=True, text=True,
    )
    say(checks.stdout.rstrip())
    if checks.returncode != 0:
        say(f"  {RED}Setup checks didn't pass.{OFF} See above.\n")
        return 1

    state = wire_client()
    say()
    if state == "added":
        ok("Added the Unreal MCP server to ~/.claude.json")
        say(f"\n{YELLOW}One thing left, and only you can do it:{OFF}")
        say(f"  {BOLD}restart your AI client{OFF} so it picks up the new tools.")
        say(f"  {DIM}Then say: \"start lesson one\"{OFF}\n")
    elif state == "already":
        ok("Your client is already pointed at the editor")
        say(f"\n{GREEN}You're ready.{OFF} Say {BOLD}\"start lesson one\"{OFF}.\n")
    else:
        warn(f"Couldn't update ~/.claude.json ({state}). Add this yourself:")
        say(f"\n      {json.dumps({'mcpServers': {'unreal': MCP_ENTRY}}, indent=6)}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

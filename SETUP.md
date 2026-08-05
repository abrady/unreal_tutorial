# Setup — Chapter 0

**Do this before the session.** The engine build is long, and showing up
without it means showing up unable to participate.

You need a PC or Mac that can run Unreal. **You do not need a VR headset.**

---

## 1. Get Unreal 5.8 or newer

The lab depends on the engine's built-in MCP server, which landed in **5.8**.

> **Strongly prefer a binary install from the Epic Launcher.**
>
> A source-built engine works, but building it is a multi-thousand-action
> compile that can take an hour or more even on a fast machine — and a
> partially-built engine fails in confusing ways (missing
> `ShaderCompileWorker`, missing `UnrealEditor-Engine.dylib`) rather than
> telling you it's incomplete. That is not how you want to spend the
> morning. Binary installs also ship the helper programs already built.

Either engine works:

- **Vanilla Epic** Unreal 5.8+
- **The Meta fork** — what most of DRE already runs

The MCP plugin is Epic's, shipped in `Engine/Plugins/Experimental/`, so it's
present in both. Nothing in the half day requires the MetaXR plugin, the
Android toolchain, or a headset.

## 2. Clone and open

```bash
git clone <this repo>
cd unreal_tutorial
```

Open `Lab01_FirstRoom/Lab01.uproject`. First open will build the game module —
this is the slow part. Let it finish.

## 3. Enable the MCP plugins

Already set in `Lab01.uproject`, so this should just work:

| Plugin | Why |
|---|---|
| `ModelContextProtocol` | The MCP server itself |
| `ToolsetRegistry` | Tool registration layer |
| `EditorToolset` | PIE control and viewport inspection |

If the editor prompts to restart after enabling plugins, do it.

## 4. Configure the server

Already set in `Config/DefaultEditorPerProjectUserSettings.ini`:

```ini
[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]
bAutoStartServer=True
bEnableToolSearch=False
ServerPortNumber=8000
ServerUrlPath=/mcp
```

Both non-default values matter. The engine defaults are
`bAutoStartServer=False` (server never starts) and `bEnableToolSearch=True`
(only `list_toolsets` / `describe_toolset` / `call_tool` get registered).
The grader copes with either tool-search setting.

> **If the server doesn't come up**, the ini isn't always picked up. The
> reliable override is a command-line flag:
>
> ```bash
> UnrealEditor <Project>.uproject -ModelContextProtocolStartServer
> ```
>
> Confirm it's live with `lsof -nP -iTCP:8000 -sTCP:LISTEN`, or check
> **Edit → Project Settings → Model Context Protocol**.

## 5. Point your AI client at the editor

Claude Code, user scope (`~/.claude.json`):

```json
{ "mcpServers": { "unreal": { "type": "http", "url": "http://localhost:8000/mcp" } } }
```

Restart the client after the editor is running so it picks up the tool list.

> Tools only exist while the editor is open. If your agent says it has no
> Unreal tools, the editor is closed or the server didn't start.

## 6. Set up the grader

```bash
cd grader
python3 -m venv .venv
.venv/bin/pip install pytest
```

## 7. Confirm you're ready

With the editor open:

```bash
cd grader
.venv/bin/python -m pytest checks/ch00_setup.py
```

Five passing checks is your ticket in. They verify the handshake, the tool
list, the toolsets the lab needs, that PIE starts and stops on command, and
that live viewport inspection reports actors.

If they **skip** rather than fail, the grader couldn't reach the editor — go
back to step 4.

---

## Troubleshooting

**`Could not reach the MCP server at http://localhost:8000/mcp`**
Editor closed, or `bAutoStartServer` is still `False`. Check
Edit → Project Settings → Model Context Protocol.

**Port 8000 already in use**
Change `ServerPortNumber`, then point the grader at it:
```bash
UNREAL_MCP_URL=http://localhost:8123/mcp .venv/bin/python -m pytest
```

**`Tool 'X' is not registered and tool-search is off`**
A toolset plugin isn't enabled. Check step 3 and restart the editor.

**`Unable to launch ShaderCompileWorker`, or the editor dies during startup**
A partially-built source engine. Check `Engine/Binaries/Mac/` (or `Win64/`)
for `ShaderCompileWorker`, `InterchangeWorker`, and
`UnrealEditor-Engine.dylib`. If any are missing the engine build never
finished — build the editor target and let it complete:
```bash
Engine/Build/BatchFiles/Mac/Build.sh UnrealEditor Mac Development
```
Binary installs from the Epic Launcher already have all of this.

> `UnrealLightmass` does **not** build on Apple Silicon. It's only needed for
> baked lighting, which this lab doesn't use. Skip it.

**`Hot-reloadable files are expected to contain a hyphen`**
Unreal Build Tool tried a hot-reload build because the editor is running.
Close the editor and build again.

**Agent sees no Unreal tools**
MCP clients read the tool list once at handshake. Start the editor first,
then restart your client.

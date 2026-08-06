# Setup — Chapter 0

**Do this before the session.** The engine build is long, and showing up
without it means showing up unable to participate.

You need a PC or Mac that can run Unreal. **You do not need a VR headset.**

---

## 1. Get Unreal 5.8 or newer

The lab depends on the engine's built-in MCP server, which landed in **5.8**.

> **Strongly prefer a binary install from the Epic Launcher.**
>
> A source-built engine works, but the first build of the project's editor
> target pulls in most of the engine's editor modules — ~2,700 compile
> actions, measured at 24 minutes on a 16-core machine. Binary installs skip
> all of that and ship the helper programs already built. That is not how you
> want to spend the morning.

Either engine works:

- **Vanilla Epic** Unreal 5.8+
- **The Meta fork** — what most of DRE already runs

The MCP plugin is Epic's, shipped in `Engine/Plugins/Experimental/`, so it's
present in both. Nothing in the lab requires the MetaXR plugin, the
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
Your assistant copes with either tool-search setting.

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

## 6. Confirm you're ready

With the editor open, ask your assistant:

> **check my setup**

It'll verify the handshake, the tool list, that PIE starts and stops on
command, and that it can inspect the running world. Those five things are
what everything else depends on — see
[`chapters/00-setup/CHECKS.md`](chapters/00-setup/CHECKS.md) for exactly what
it's looking at.

If your assistant says it has no Unreal tools, the editor is closed or the
client wasn't restarted after step 5.

---

## Troubleshooting

**Your assistant has no Unreal tools**
Editor closed, `bAutoStartServer` still `False`, or the client wasn't
restarted. Check Edit → Project Settings → Model Context Protocol, then
restart the client.

**Port 8000 already in use**
Change `ServerPortNumber`, and use the same port in your client config.

**`Tool 'X' is not registered and tool-search is off`**
A toolset plugin isn't enabled. Check step 3 and restart the editor.

**`Unable to launch ShaderCompileWorker`**
Source-built engines don't always build the helper programs. Check
`Engine/Binaries/Mac/` (or `Win64/`) for `ShaderCompileWorker` and
`InterchangeWorker`, and build any that are missing:
```bash
Engine/Build/BatchFiles/Mac/Build.sh ShaderCompileWorker Mac Development
```
Binary installs from the Epic Launcher already have these.

> Note when checking by hand on macOS: engine module binaries carry a `lib`
> prefix (`libUnrealEditor-Engine.dylib`). The helper *programs* don't.

> `UnrealLightmass` does **not** build on Apple Silicon. It's only needed for
> baked lighting, which this lab doesn't use. Skip it.

**The first project build takes ~25 minutes**
On a source engine, building the project's editor target can pull in most of
the engine's editor modules — roughly 2,700 compile actions, about 24 minutes
on 16 cores. This is a one-time cost, but it's exactly why the Epic Launcher
binary is the recommended path for the lab.

**Editor seems to launch but the MCP server never comes up**
Check for a modal dialog behind your other windows. The most common one is
**"Missing Lab01 Modules — built with a different engine version. Would you
like to rebuild them now?"** It blocks startup, so from the outside this
looks identical to a broken MCP server.

Click **Yes**. It means your engine and your project module drifted apart —
usually because the engine was rebuilt after the project module was. Nothing
is wrong with your code.

**`Hot-reloadable files are expected to contain a hyphen`**
Unreal Build Tool tried a hot-reload build because the editor is running.
Close the editor and build again.

**Agent sees no Unreal tools**
MCP clients read the tool list once at handshake. Start the editor first,
then restart your client.

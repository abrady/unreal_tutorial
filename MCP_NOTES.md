# Driving Unreal over MCP

**Notes for the AI assistant.** Everything here was found by hitting it
against a live UE 5.8.1 editor, not by reading docs. Several of these will
waste your time if you rediscover them the hard way.

*Last re-verified 2026-09-11 against UE 5.8.1, driving the editor from Claude
Code. A few entries turn on how your client serialises arguments — where that
matters it's called out, because a different client may behave differently.*

---

## Tool names

Tools are registered fully qualified, dot-separated:

```
EditorToolset.EditorAppToolset.StartPIE
editor_toolset.toolsets.actor.ActorTools.get_actor_transform
editor_toolset.toolsets.scene.SceneTools.find_actors
```

There are ~250 of them. Your client probably renames them — Claude Code shows
the first as `mcp__unreal__EditorToolset_EditorAppToolset_StartPIE`, dots
turned to underscores behind a prefix. The dotted form above is still the real
name, and it's what `execute_tool_script` expects.

**There is no tool discovery.** `list_toolsets` and `describe_toolset` do not
exist in 5.8.1 — both come back `Invalid tool name`. Browse your client's tool
list instead.

## Class paths drop the A/U prefix

`ATargetDummy` in C++ is `TargetDummy` to the reflection system:

```
/Script/CombatGym.TargetDummy      ✓
/Script/CombatGym.ATargetDummy     ✗  "is not valid Class"
```

Same for `UDamageHistory` → `/Script/CombatGym.DamageHistory`.

## You cannot spawn actors while PIE is running

> `Cannot create actors while PIE is active.`

The editor world is the template PIE duplicates from. So the order is always:

1. spawn into the **editor** world
2. `StartPIE`
3. `find_actors` to get the **PIE copy** — a different object
4. assert on that copy
5. `StopPIE`

Anything you spawn for a check should be removed afterwards
(`remove_from_scene`), or you'll silently pollute the learner's level.

## `find_actors`: send the empty ones, omit the null ones

`name`, `tag` and `collision_channels` have no default, so you must send them
even when empty. `root`, `bounds` and `actor_type` default to null — **omit
those keys entirely.** Sending them explicitly is what breaks; see the null
section below.

```json
{"name": "", "tag": "", "collision_channels": [],
 "actor_type": {"refPath": "/Script/CombatGym.TargetDummy"}}
```

Searching on a **C++** class also matches Blueprint subclasses of it. That's
usually what you want, and it's how you check whether a learner actually
replaced their raw `TargetDummy` with a `BP_TargetDummy_C`.

During PIE it returns PIE-world actors, which is what you want.
(`GetVisibleActors` still returns *editor*-world actors during play — it hands
back `Lvl_FirstRoom.Lvl_FirstRoom:PersistentLevel...` paths while PIE is up,
not `UEDPIE_0_...`. A trap.)

## A component's path is its name, not its type

```
.../TargetDummy_0.Body     ← "Body" is the component's NAME
```

To find out what it actually *is*, call `get_class`:

```
get_class({"instance": component}) → {"refPath": "/Script/Engine.StaticMeshComponent"}
```

Filtering components by their path will silently match nothing.

## `set_properties` wants a JSON **string**

```json
{"instance": actor, "values": "{\"MaxHealth\": 250}"}    ✓
{"instance": actor, "values": {"MaxHealth": 250}}        ✗ returns false, silently
```

It returns `false` rather than erroring, so this fails quietly.

## `get_properties` needs you to name the properties

There's no "give me everything" mode:

```json
{"instance": actor, "properties": ["Health", "MaxHealth"]}
```

`list_properties` will tell you what exists. Note it reports camelCase
(`maxHealth`) while the C++ declares PascalCase — reads tolerate either.

It returns each property's name, type and the doc comment sitting above the
member — but **not** the UPROPERTY specifiers. You cannot tell
`EditDefaultsOnly` from `EditAnywhere` through the MCP. When a check depends on
which one they chose, read the header.

## `StartPIE` needs its options object

```json
{"options": {"bSimulate": false, "playMode": "PlayMode_InViewPort",
             "warmupSeconds": 1.0}}
```

All three fields are required despite looking optional.

## You probably cannot send a JSON null at all

Claude Code serialises a bare `null` argument as the **string** `"null"`, and
the server rejects it:

```
{"root":"null","bounds":"null"}
→ could not convert incoming function input params Json to a UStruct
```

So "just pass null explicitly" is not advice you can act on from a tool call.
What works depends on whether the parameter declares a default:

| Parameter | What to do |
|---|---|
| Has `"default": null` — `find_actors` `root`/`bounds`, `get_components` `component_type`, `add_to_scene_from_class` `parent` | **Omit the key.** |
| No default — `CaptureViewport` `captureTransform` and `annotations` | **Send a real value.** The server answers `input param X needs a default value` and will not let you skip it. |

For `CaptureViewport` that means reading a pose with `GetCameraTransform` and
passing it back, plus an annotations block switched off by zeroing it:

```json
{"gridSpacing": 0, "gridExtent": 0, "gridHeight": 0, "maxLabelDistance": 0,
 "maxLabels": 0, "classFilter": {"refPath": "/Script/Engine.Actor"}}
```

If you genuinely need a null, go through `execute_tool_script` below — you
build the JSON yourself there, so Python's `None` arrives as a real null.

## Checking whether a class exists

`get_default_object` is **Blueprint-only** and rejects C++ classes. Use:

```json
search_subclasses({"base_class": {"refPath": "/Script/Engine.Actor"},
                   "class_name": "TargetDummy"})
```

Empty list means the class isn't compiled in.

## `execute_tool_script` batches everything (and fixes nulls)

`editor_toolset.toolsets.programmatic.ProgrammaticToolset.execute_tool_script`
runs Python inside the editor. It is the highest-leverage tool in the set and
the easiest to overlook.

- `execute_tool(dotted_name, json_string)` calls any registered tool.
- You build the payload with `json.dumps`, so `None` really is null.
- One round trip instead of ten. A whole chapter's checks fit in a single call.
- Imports are limited to `json`, `math`, `datetime`, `copy`, `re`, `time`.
- The script must define `run()` returning a dict.

```python
import json

def call(name, payload):
    return execute_tool(name, json.dumps(payload))["returnValue"]

def run():
    placed = call("editor_toolset.toolsets.scene.SceneTools.find_actors",
                  {"root": None, "name": "", "tag": "", "bounds": None,
                   "collision_channels": [],
                   "actor_type": {"refPath": "/Script/CombatGym.TargetDummy"}})
    return {"placed": placed}
```

Call `get_execution_environment` once before your first script — its
`instructions` field is the real documentation.

This does **not** buy you arbitrary UFUNCTION calls. `execute_tool` only
reaches tools that are already registered.

## `CaptureViewport` returns megabytes

One capture came back as ~4 MB of base64 — about four million characters. That
blows past the context limit and your client will spill it to a file instead of
showing you the image. Plan to decode it:

```python
import base64, re
s = open(dumped_path).read()
png = base64.b64decode(re.search(r"[A-Za-z0-9+/=]{5000,}", s).group(0))
open("shot.png", "wb").write(png)
```

Then downscale before reading it back (`sips -Z 900` on macOS) or you'll spend
the context you just saved.

---

## Things the MCP cannot do

Worth knowing before you promise a learner something.

| | |
|---|---|
| **Create or save a level** | No `new_level` tool. `save_assets` can't see an unsaved map, `load_level` needs an existing asset. The lab ships `Lvl_FirstRoom.umap` for this reason. |
| **Simulate input** | No way to press a key or trigger an InputAction. You cannot test "press fire → projectile appears." Verify the wiring and the projectile separately. |
| **Call arbitrary UFUNCTIONs at runtime** | The Blueprint tools author graphs; they don't invoke functions. |

Things it *can* do that you might assume it can't:

- **Create Enhanced Input assets** — `DataAssetTools.create` with
  `/Script/EnhancedInput.InputAction` or `.InputMappingContext`. Both derive
  from `UDataAsset`.
- **Attach components at runtime** — `add_component` with a class refPath.
- **Edit properties on actors in a saved level** — but *not* in an unsaved
  temp map, where `set_properties` returns false.

---

## Building and restarting

The learner must close the editor for any structural C++ change — a new
`UCLASS`, a new `UPROPERTY`, anything that alters class layout. Live Coding
only handles `.cpp` bodies.

```bash
# macOS
<engine>/Engine/Build/BatchFiles/Mac/Build.sh CombatGymEditor Mac Development \
  -Project=<repo>/CombatGym/CombatGym.uproject -WaitMutex

# Windows
<engine>\Engine\Build\BatchFiles\Build.bat CombatGymEditor Win64 Development ^
  -Project=<repo>\CombatGym\CombatGym.uproject -WaitMutex
```

If the build complains about hot reload or hyphens, the editor is still open.

Relaunch with the MCP server:

```bash
<engine>/Engine/Binaries/Mac/UnrealEditor <repo>/CombatGym/CombatGym.uproject \
  -ModelContextProtocolStartServer
```

Give it up to 3 minutes on a cold open. If it never comes up, look for a modal
dialog behind other windows — **"Missing CombatGym Modules"** blocks startup and
looks exactly like a hung editor.

Your tools only exist while that editor is open — but the two failure modes
behave differently, and the difference will cost you a session if you don't
know it:

| When | What happens |
|---|---|
| Editor **not running when your client starts** | The server is marked failed for the whole session. Starting the editor afterwards does **not** revive it — you must reconnect (`/mcp` in Claude Code) or restart the client. |
| Editor restarted or crashes **mid-session** | The client reconnects by itself. The next tool call just works. |

So: **start the editor first, then your client.** Getting that order wrong
looks exactly like a broken install — and the editor log will cheerfully say
`Starting MCP server on port 8000` and `Created new HttpListener` the entire
time you're staring at a client that has no Unreal tools.

Don't bother hand-rolling HTTP against port 8000 to work around it. The
listener accepts the TCP connection and then answers nothing on any transport
shape worth trying; reconnecting the client is the fix.

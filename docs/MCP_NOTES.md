# Driving Unreal over MCP

**Notes for the AI assistant.** Everything here was found by hitting it
against a live UE 5.8.1 editor, not by reading docs. Several of these will
waste your time if you rediscover them the hard way.

---

## Tool names

Tools are registered fully qualified:

```
EditorToolset.EditorAppToolset.StartPIE
editor_toolset.toolsets.actor.ActorTools.get_actor_transform
editor_toolset.toolsets.scene.SceneTools.find_actors
```

There are ~255 of them. `list_toolsets` and `describe_toolset` help when you
need something not listed below.

## Class paths drop the A/U prefix

`ATargetDummy` in C++ is `TargetDummy` to the reflection system:

```
/Script/Lab01.TargetDummy      ✓
/Script/Lab01.ATargetDummy     ✗  "is not valid Class"
```

Same for `UDamageHistory` → `/Script/Lab01.DamageHistory`.

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

## `find_actors` wants every parameter

Even the empty ones:

```json
{"root": null, "name": "", "actor_type": {"refPath": "/Script/Lab01.TargetDummy"},
 "tag": "", "bounds": null, "collision_channels": []}
```

Omitting any of them is an error. During PIE it returns PIE-world actors,
which is what you want. (`GetVisibleActors` returns *editor*-world actors even
during play — a trap.)

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

## `StartPIE` needs its options object

```json
{"options": {"bSimulate": false, "playMode": "PlayMode_InViewPort",
             "warmupSeconds": 1.0}}
```

All three fields are required despite looking optional.

## `TOptional` arguments must be sent explicitly as null

`CaptureViewport` and friends list no required fields but still reject a
missing key:

```json
{"captureTransform": null, "annotations": null, "bShowUI": false}
```

## Checking whether a class exists

`get_default_object` is **Blueprint-only** and rejects C++ classes. Use:

```json
search_subclasses({"base_class": {"refPath": "/Script/Engine.Actor"},
                   "class_name": "TargetDummy"})
```

Empty list means the class isn't compiled in.

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
<engine>/Engine/Build/BatchFiles/Mac/Build.sh Lab01Editor Mac Development \
  -Project=<repo>/Lab01_FirstRoom/Lab01.uproject -WaitMutex

# Windows
<engine>\Engine\Build\BatchFiles\Build.bat Lab01Editor Win64 Development ^
  -Project=<repo>\Lab01_FirstRoom\Lab01.uproject -WaitMutex
```

If the build complains about hot reload or hyphens, the editor is still open.

Relaunch with the MCP server:

```bash
<engine>/Engine/Binaries/Mac/UnrealEditor <repo>/Lab01_FirstRoom/Lab01.uproject \
  -ModelContextProtocolStartServer
```

Give it up to 3 minutes on a cold open. If it never comes up, look for a modal
dialog behind other windows — **"Missing Lab01 Modules"** blocks startup and
looks exactly like a hung editor.

Your tools only exist while that editor is open. If they vanish mid-session,
the editor closed or crashed.

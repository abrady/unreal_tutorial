# Checks — Chapter 1b: the C++/Blueprint boundary

*For the assistant. Five checks. Number 4 is the one that matters, and it is
**expected to fail** on a first attempt — that failure is the chapter.*

Unlike Chapter 1, **none of this needs PIE.** `OnConstruction` runs when an
actor is placed and again when the map loads, so the editor world already
knows the answer. Spawn nothing you don't remove afterwards.

Reminder from [`MCP_NOTES.md`](../../MCP_NOTES.md): reflection drops the
`A`/`U` prefix, so the C++ class is `/Script/CombatGym.TargetDummy` and the
Blueprint's generated class is `/Game/CombatGym/BP_TargetDummy.BP_TargetDummy_C`.
An unset object property reads back as the string `"None"`; a set one reads
back as `{"refPath": "..."}`.

---

**1. The C++ no longer knows which mesh.**

Spawn a *raw* `ATargetDummy` — the C++ class, not their Blueprint — and read
its body component:

```
add_to_scene_from_class  {"actor_type": {"refPath": "/Script/CombatGym.TargetDummy"},
                          "name": "RawProbe", "xform": {"location": {...}}}
get_properties           {"instance": <...TargetDummy_0.Body>, "properties": ["StaticMesh"]}
```

Must come back `"None"`.

If it comes back with a mesh, an `FObjectFinder` is still sitting in the
constructor and they've added the new properties *alongside* it rather than
*instead of* it. The chapter is about deleting the hardcoded path, not
supplementing it — a base class that still hardcodes a cylinder hasn't moved
the decision anywhere.

`remove_from_scene` the probe when you're done.

**2. A Blueprint subclass exists.**

```
search_subclasses({"base_class": {"refPath": "/Script/Engine.Actor"},
                   "class_name": "TargetDummy"})
```

Should return **two** entries now — the C++ class and
`/Game/CombatGym/BP_TargetDummy.BP_TargetDummy_C`. Confirm the parentage
rather than trusting the name:

```
get_parent({"blueprint": {"refPath": "/Game/CombatGym/BP_TargetDummy.BP_TargetDummy"}})
    → {"refPath": "/Script/CombatGym.TargetDummy"}
```

A Blueprint deriving from plain `Actor` looks identical in the Content Browser
and is the most common way to get this wrong.

**3. The Blueprint fills the slots.**

```
get_properties({"instance": {"refPath": "/Game/CombatGym/BP_TargetDummy.BP_TargetDummy"},
                "properties": ["BodyMesh", "HeadMesh"]})
```

Both must be real assets, not `"None"`.

> Pass the **Blueprint asset** path here, not the `_C` class path.
> `ObjectTools` resolves the CDO for you.

**4. The meshes actually reach the components.**

This is the check. Find their placed dummy, get its components, and read the
`StaticMesh` off each:

```
get_properties({"instance": <...BP_TargetDummy_C_0.Body>, "properties": ["StaticMesh"]})
get_properties({"instance": <...BP_TargetDummy_C_0.Head>, "properties": ["StaticMesh"]})
```

Both must match what check 3 reported.

**Expect this to fail the first time, with check 3 passing.** The Blueprint
holds the right meshes and the components hold nothing. That combination has
exactly one common cause: they applied the meshes in the **constructor**.

```cpp
ATargetDummy::ATargetDummy()
{
    if (BodyMesh) { Body->SetStaticMesh(BodyMesh); }   // always false
}
```

A Blueprint subclass deserialises its defaults *after* the C++ constructor
runs. In the constructor `BodyMesh` is still the C++ default — null — so the
branch never fires and `SetStaticMesh` is never called. No error, no warning,
no mesh. If they dropped the `if`, they get a visible "set to None" instead,
which is at least honest.

The fix is to do it somewhere that runs after property initialisation.
`OnConstruction(const FTransform&)` is the idiomatic one: it fires on
placement, on map load, on spawn, and again on every edit in the Details
panel. It is the C++ half of a Construction Script.

**Don't hand them that.** Show them the two readings — Blueprint says
Cylinder, component says None — and ask when they think the Blueprint's value
arrives relative to their constructor. Most people get there from that alone.
Chapter 2 check 2 is the same bug wearing a different hat (`Health = MaxHealth`
in the constructor missing a per-instance `MaxHealth` override), so the
mental model they build here pays off almost immediately.

If they land on `BeginPlay` instead, that works in PIE and leaves the editor
viewport empty. Worth pointing out rather than failing them for.

**5. The level contains the Blueprint, not the raw C++ actor.**

```
find_actors({"name": "", "actor_type": {"refPath": "/Script/CombatGym.TargetDummy"},
             "tag": "", "collision_channels": []})
```

Every result should be a `BP_TargetDummy_C_*`. A bare `TargetDummy_*` means
they built the Blueprint but left the old hand-placed actor behind — it will
render untextured next to a working one, which is a confusing thing to leave
in a level they'll keep using for six more chapters.

> Searching on the **C++** class deliberately matches Blueprint subclasses
> too. That's what makes this check able to see both.

---

## What you can't check from here

**Whether the properties are `EditDefaultsOnly` or `EditAnywhere`.**
`list_properties` reports names, types and the doc comment, but not the
UPROPERTY specifiers. You have to read the header.

Both choices pass every check above, and that's fine — the README asks them to
make the call, not to make a specific call. Worth one question if they chose
`EditAnywhere`: *should a level designer be able to give one dummy in this room
a different head?* Either answer is defensible. Not having thought about it
isn't.

---

## Then encourage the delegation

Once it's green, they've done the C++/Blueprint boundary once by hand. The
second and third are typing:

- Offer to make `BP_TargetDummy_Heavy` / `_Fast` variants — same parent,
  different meshes and `DegreesPerSecond`.
- Offer to place a firing line of them.

Note whether it works, and tell them plainly if it doesn't. Finding the edges
of the tooling is part of the point.

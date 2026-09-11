# Checks — Chapter 1b: the Blueprint boundary

*For the assistant. All three must hold. Starts from green Chapter 1a.*

Adding a `UPROPERTY` changes class layout, so if the class doesn't exist or
the new properties are missing, they likely edited the header without a full
rebuild (editor closed) — same rule as 1a.

---

**1. No hardcoded asset paths left.**

The constructor must not call `FObjectFinder` for the meshes anymore. The
class declares the choice instead:

- `BodyMesh` / `HeadMesh` exist as `UPROPERTY(EditDefaultsOnly)` — check with
  `list_properties` on the class or a spawned instance
- If `FObjectFinder` is still in the constructor, they added the properties
  without removing the old loading — the meshes they set in the Blueprint are
  being overwritten (or ignored)

**2. A Blueprint subclass exists, with meshes set.**

A Blueprint deriving from `ATargetDummy` exists (conventionally
`BP_TargetDummy` in `Content/CombatGym/`), with the body and head meshes set
in its defaults.

You can create the Blueprint for them — `BlueprintTools.create` takes a parent
class — since that's asset plumbing. **Don't choose which properties to
expose for them.** That's the design judgement the chapter is teaching:
every `EditDefaultsOnly` is a promise that someone else can change it without
a programmer.

**3. The level holds the Blueprint, not the raw C++ actor.**

`find_actors` for the `TargetDummy` family in the level should return the
Blueprint instances. If only raw C++ actors are placed, they did the work but
never switched the level over — the thing a player sees is still the
hardcoded one.

Verify the placed Blueprint actually renders: `get_components` on the PIE
copy → two mesh components, same as 1a check 2. A Blueprint with empty mesh
slots spawns a turning invisible dummy.

---

Once green, the data lives with designers. Chapter 2 gives the dummy
something to lose.

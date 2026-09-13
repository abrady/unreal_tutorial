# Checks — Chapter 1b: the Blueprint boundary

*For the assistant. All three must hold. Starts from green Chapter 1a.*

This chapter changes component defaults in a Blueprint rather than adding new
C++ properties. If the Blueprint still inherits hardcoded meshes, they likely
did not rebuild after removing the constructor-time loading.

---

**1. No hardcoded asset paths left.**

The constructor must not call `FObjectFinder` or `SetStaticMesh` for the
meshes anymore. It creates and attaches the `Body` / `Head` components but
does not choose their assets.

If either remains, C++ still owns the asset choice and the Blueprint boundary
has not actually moved.

**2. A Blueprint subclass exists, with meshes set.**

A Blueprint deriving from `ATargetDummy` exists (conventionally
`BP_TargetDummy` in `Content/CombatGym/`). Use `get_default_object`, then
`get_components` on its CDO. Read `StaticMesh` from the inherited `Body` and
`Head` component templates; they must be Cylinder and Sphere respectively.

You can create the Blueprint for them — `BlueprintTools.create` takes a parent
class — since that's asset plumbing. Let them decide that mesh choice belongs
in Blueprint; then configuring the two component defaults is mechanical.

**3. The level holds the Blueprint, not the raw C++ actor.**

`find_actors` for the `TargetDummy` family in the editor world should return
Blueprint instances and no raw `/Script/CombatGym.TargetDummy` instances. If
a raw C++ actor remains, they added the Blueprint without replacing the old
level actor.

Verify the placed Blueprint actually renders: `get_components` on the PIE
slots spawns a turning invisible dummy.

Finally, verify the Blueprint and level packages are saved (`is_dirty` is
false). Compiling a Blueprint updates the in-memory class; saving persists its
defaults and the level replacement across an editor restart.

---

Once green, the data lives with designers. Chapter 2 gives the dummy
something to lose.

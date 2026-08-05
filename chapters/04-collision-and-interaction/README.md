# Chapter 4 — Collision, overlap, and the interaction interface

**Goal:** step on a plate, a door opens. Walk into a thing, you pick it up.

This is the chapter where the room becomes a game, and it's also where the
lab makes its actual argument about writing VR-ready code — without a
headset anywhere in sight.

**Time:** ~45 minutes.

---

## What green looks like

```console
$ cd grader && .venv/bin/python -m pytest checks/ch04_interaction.py
```

The checks teleport your pawn onto the plate and assert the door moved,
then overlap the pickup and assert it's gone.

---

## Part A — collision is a matrix, not a boolean

Every primitive component carries:

- an **object type** (what it *is*: WorldStatic, Pawn, PhysicsBody…)
- a **response** to each channel: `Ignore`, `Overlap`, or `Block`

The rule that catches everyone:

> **Both parties must agree.** A blocks B only if A blocks B **and** B
> blocks A. For an overlap *event* to fire, at least one side must be set
> to Overlap, and **Generate Overlap Events** must be true on both.

So "my trigger doesn't fire" is nearly always one half of a matrix you only
checked one side of.

**Profiles** are named presets over that matrix — `Trigger`, `Pawn`,
`BlockAll`, `OverlapAllDynamic`. Use them. Hand-setting individual channel
responses is how you end up with an actor that works everywhere except one
specific interaction.

For a pressure plate you want a trigger volume that overlaps pawns and
blocks nothing.

---

## Part B — the interface

Here's the design question, and it's the point of the chapter.

The naive version: the pawn checks *what it hit*.

```cpp
// Don't do this.
if (ADoor* Door = Cast<ADoor>(Other))        { Door->Open(); }
else if (APickup* P = Cast<APickup>(Other))  { P->Collect(); }
// ...and one more branch every time you add anything
```

Every new interactable edits the pawn. The pawn accumulates knowledge of
every object in your game.

The version you'll write: the pawn asks *whether the thing is interactable*.

```cpp
UINTERFACE(MinimalAPI, Blueprintable)
class UInteractable : public UInterface { GENERATED_BODY() };

class IInteractable
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintNativeEvent, Category = "Interaction")
    void Interact(AActor* Instigator);
};
```

Now the pawn does one thing:

```cpp
if (Other->Implements<UInteractable>())
{
    IInteractable::Execute_Interact(Other, this);
}
```

It never learns what a door is.

### The two-class thing

`UInterface` + `IInterface` is Unreal's reflection tax. The `U` class exists
so the reflection system has a `UObject` to point at; the `I` class holds
your actual functions and is what you inherit from. Declare both, implement
the `I`.

### `BlueprintNativeEvent`

Means: C++ provides a default, Blueprint may override. You implement
`Interact_Implementation` in C++, and call it via
`IInteractable::Execute_Interact(Obj, Args)` — never call `Interact()`
directly, or you'll bypass any Blueprint override.

That `Execute_` prefix is unintuitive and it's the single most common
mistake in this chapter.

---

## Your task

1. A **pressure plate** with a trigger volume that fires on pawn overlap.
2. A **door** that implements `IInteractable` and rotates 90° when
   interacted with.
3. A **pickup** that implements the *same* interface and destroys itself.
4. Wire the plate to the door.

The plate should not know it's connected to a door. Expose a
`TObjectPtr<AActor>` you set in the editor, check `Implements<UInteractable>`,
and call through the interface.

---

## Stuck?

<details>
<summary>My overlap event never fires</summary>

Check both sides of the matrix, and check Generate Overlap Events on both
components. Then confirm the pawn's collision actually reaches the volume —
ask your agent to inspect the plate's component setup during PIE.
</details>

<details>
<summary>Implements&lt;UInteractable&gt;() is false but I implemented it</summary>

You inherited from the wrong one. Inherit `IInteractable` (the I), and list
it in the class declaration:
`class ADoor : public AActor, public IInteractable`.
</details>

<details>
<summary>The C++ runs but a Blueprint override is ignored</summary>

You called `Interact()` directly instead of
`IInteractable::Execute_Interact(Obj, Args)`. Direct calls skip the
Blueprint dispatch entirely.
</details>

<details>
<summary>The door teleports instead of swinging</summary>

Fine for the checks — they only assert final yaw. If you want it to
animate, interpolate in Tick toward a target rotation, or use a Timeline.
</details>

---

## Run the checks

```bash
cd grader && .venv/bin/python -m pytest checks/ch04_interaction.py -v
```

---

## You built a thing

A room you can walk around, with objects that respond to you. In C++, in
about four hours, having started from an empty project.

More usefully: you can now open an unfamiliar Unreal project and have a
reasonable guess about where things live and why.

---

## The VR part

There wasn't one. No headset, no MetaXR plugin, no Android toolchain.

But look at what you built. Your door and your pickup don't know what
touched them — only that something asked them to `Interact`. Your pawn
doesn't know what it touched — only that it implements an interface.

**Swap the desktop pawn for a VR pawn and every interaction still works.**
Different pawn, different mapping context, same `IA_Move`, same
`IInteractable`. Nothing in the interaction layer changes.

That's the whole lesson about writing VR-ready systems, and you just
learned it on a laptop. The optional take-home capstone does the swap if
you have a headset — it's mostly configuration, which is the point.

---

## Where to go next

Take-home chapters, self-serve: delegates and game state · UMG HUD from
C++ · AI patrol with NavMesh, Behavior Trees and Blackboards (the best
showcase of live MCP inspection) · audio · packaging a standalone build ·
the VR pawn swap.

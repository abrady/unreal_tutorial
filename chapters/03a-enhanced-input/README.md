# Chapter 3a — You, and input

**Goal:** stand in the gym, move, look around, and jump.

The character, camera, and movement component are already written for you.
You are connecting physical controls to that character. The point is not to
memorize Unreal's subsystem lookup; it is to understand where input lives and
how an input asset eventually calls C++.

**Time:** ~30 minutes.

---

## Part A — the six classes

Almost every "why is my data gone?" bug in Unreal is state living in the wrong
one of these.

| Class | How many | Lives where | Owns |
|---|---|---|---|
| `GameMode` | one | **server only** | rules, spawning, win conditions |
| `GameState` | one | replicated to all | shared match state |
| `PlayerController` | one per player | that client + server | input, camera, UI |
| `PlayerState` | one per player | replicated to all | that player's data (score) |
| `Pawn` / `Character` | one per body | in the world | the physical thing |
| `HUD` | one per player | local only | legacy 2D drawing |

**Possession** joins them: a `PlayerController` possesses a `Pawn`. The
controller is *you*; the pawn is your current body.

Put the player's score on the **Pawn** and it dies when the pawn dies. Put it
on **PlayerState** and it survives respawning — which is precisely why
`PlayerState` exists.

Put game rules on the **PlayerController** and in multiplayer every client
runs its own copy. Put them on **GameMode**, which exists only on the server,
and there is one authority.

Single-player hides these distinctions. Possession is the first place you can
see them: the controller receives local input, and its current pawn supplies
the input component and gameplay behavior.

---

## Part B — how Enhanced Input works

Before touching an API, follow one key press through the engine:

```text
Space Bar
    ↓ mapped by the active Input Mapping Context
IA_Jump
    ↓ matched by the possessed pawn's input binding
ACharacter::Jump()
```

There are two different kinds of setup:

- **Assets describe the controls.** An `InputAction` names an intent and its
  value type. An `InputMappingContext` maps physical controls to actions.
- **C++ makes those controls live.** It activates a mapping context for the
  local player, then binds actions to functions on the possessed pawn.

`DefaultMappingContext` is not a special engine object or magic name. It is a
property on `ALabCharacter` that points at an Input Mapping Context asset — in
this project, `IMC_Default`. Keeping that choice in a property lets the same
character use mouse and keyboard today and VR controllers later without
recompiling.

The asset and the binding must reference the **same** `IA_Jump` object. The
context can emit `IA_Jump`, but nothing happens without a binding. The pawn
can bind a `JumpAction`, but that binding never fires if no active context maps
a key to it. Most silent input failures are one of those two halves missing.

---

## Part C — do one yourself

The project supplies `IA_Move`, `IA_Look`, `IA_Fire`, and an empty
`IMC_Default`. Create the first action and mapping yourself:

1. Create `IA_Jump` in `Content/CombatGym/Input`.
2. Set its value type to **Digital (bool)**.
3. Add `IA_Jump → Space Bar` to `IMC_Default`.
4. Add a reflected `JumpAction` property beside the existing action properties
   on `ALabCharacter`.
5. In `BeginPlay`, add `DefaultMappingContext` to the local player's
   `UEnhancedInputLocalPlayerSubsystem`.
6. In `SetupPlayerInputComponent`, cast to `UEnhancedInputComponent` and bind
   `JumpAction` on `Started` to `ACharacter::Jump` and on `Completed` to
   `ACharacter::StopJumping`.

`Jump` and `StopJumping` already exist on `ACharacter`. With a nonzero
`JumpMaxHoldTime`, releasing the action early produces a shorter jump.

Every link in the controller → local player → subsystem chain can be null.
Guard it. You do not need to memorize that lookup; knowing what the subsystem
owns is the useful part.

---

## Part D — delegate the repetition

You have now created and mapped one action. Doing it six more times is typing,
not learning. Ask your assistant to add the supplied actions to `IMC_Default`:

- W/S → forward/back on `IA_Move`
- A/D → left/right on `IA_Move`
- Mouse XY → `IA_Look`
- Left Mouse Button → `IA_Fire`

W and S need the axis-swizzle modifier; S and A also need negation. Ask the
assistant to verify the saved mapping array rather than trusting a successful
tool response.

After you bind Jump once, delegate the repetitive Move, Look, and Fire binding
calls too. Move and Look use `Triggered`; Fire uses `Started`. Leave the Fire
handler empty for Chapter 3b.

The editor tools may succeed, fail, or expose the asset without a convenient
mapping API. Report that honestly. Finding the boundary of the tooling is part
of the exercise.

---

## Part E — movement and Blueprint defaults

`IA_Move` and `IA_Look` both carry a two-dimensional value. Implement their
handlers:

- Move Y drives the actor's forward vector; Move X drives its right vector.
- Look X drives controller yaw; Look Y drives controller pitch.

The C++ properties are still null until something assigns assets to them.
Reapply the Blueprint boundary from Chapter 1b:

1. After compiling the new reflected property, create `BP_LabCharacter` from
   `ALabCharacter`.
2. Assign `IMC_Default`, `IA_Move`, `IA_Look`, `IA_Jump`, and `IA_Fire` in its
   Class Defaults.
3. Create `BP_LabGameMode` from `ALabGameMode` and set its Default Pawn Class
   to `BP_LabCharacter`.
4. Select `BP_LabGameMode` as the level's GameMode Override, or as the
   project's default GameMode under Maps & Modes.

The mapping context contains `Space → IA_Jump`. `JumpAction` separately tells
C++ which action to listen for. Assigning only one of them gives you a silent
no-op.

---

## Stuck?

<details>
<summary>PIE starts but I am not controlling BP_LabCharacter</summary>

Check the active GameMode and its Default Pawn Class. Also make sure the level
contains a Player Start. Ask your assistant which pawn the player controller
actually possesses; live inspection beats guessing.
</details>

<details>
<summary>All of the keys do nothing</summary>

The mapping context probably was not added. Assets sitting in the Content
Browser are inert. Confirm `DefaultMappingContext` is assigned and that the
local-player subsystem receives it during `BeginPlay`.
</details>

<details>
<summary>Space is mapped but Jump never runs</summary>

Check `BP_LabCharacter.JumpAction`. The mapping row and C++ binding must both
point to `IA_Jump`; Unreal does not connect them by variable name.
</details>

<details>
<summary>WASD moves along the wrong axes</summary>

Digital keys begin as a one-dimensional X value. W/S need Swizzle Axis Values
to feed Y; S and A need Negate for their negative directions.
</details>

---

## Run the checks

Ask your assistant:

> **check my work**

Then [Chapter 3b](../03b-projectiles/), where the input starts shooting.

---

## What just happened

You connected hardware-neutral intent to a possessed body. The indirection is
what lets Space, a gamepad button, and a VR-controller input all trigger the
same `Jump` code without changing the character.

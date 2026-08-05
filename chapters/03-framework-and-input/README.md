# Chapter 3 — The gameplay framework, and Enhanced Input

**Goal:** a first-person character you can walk around with.

Most of this chapter is already written for you. That's deliberate — the
lesson here isn't "can you type a Character class," it's **which of Unreal's
six framework classes owns what**, and why putting a thing in the wrong one
causes bugs that look inexplicable later.

**Time:** ~45 minutes.

---

## What green looks like

```console
$ cd grader && .venv/bin/python -m pytest checks/ch03_input.py
```

The checks start PIE, confirm a pawn got possessed, inject movement input,
and assert the pawn actually moved.

---

## The six classes

Before you write anything, get this table into your head. Nearly every
"why is my data gone?" bug in Unreal traces back to putting state in the
wrong one.

| Class | How many | Lives where | Owns |
|---|---|---|---|
| `GameMode` | one | **server only** | rules, win conditions, spawning |
| `GameState` | one | replicated to everyone | shared match state |
| `PlayerController` | one per player | that player's machine + server | input, camera, UI |
| `PlayerState` | one per player | replicated to everyone | that player's data (score, name) |
| `Pawn` / `Character` | one per possessed body | in the world | the physical thing |
| `HUD` | one per player | local only | legacy 2D drawing |

**Possession** is the join between them: a `PlayerController` possesses a
`Pawn`. The controller is *you*; the pawn is your current body.

### The trap this table prevents

Put the player's score on the **Pawn** and it dies when the pawn dies. Put
it on **PlayerState** and it survives respawning, which is why
`PlayerState` exists.

Put game rules on the **PlayerController** and in multiplayer every client
runs their own copy of the rules. Put them on **GameMode**, which only
exists on the server, and they can't.

Single-player hides all of this. It surfaces the first time something gets
networked — which for partners is usually late and expensive.

---

## Enhanced Input

The old system bound a function directly to a key. Enhanced Input adds two
layers of indirection, and both earn their keep.

```
InputAction        IA_Move          "the intent to move"     (an asset)
     ↑
MappingContext     IMC_Default      "W/A/S/D and left stick" (an asset)
     ↑
Binding            C++ or Blueprint  "call this on Move"
```

**Why bother?** Because the intent and the keys are now separate things.
You get remapping for free. You can push a menu context that shadows the
gameplay one and pop it later. And the same `IA_Move` handler works for
keyboard, gamepad, and — this is the one that matters for us — **VR
controllers**, without touching gameplay code.

That last point is why the lab uses it. The optional VR capstone swaps the
pawn and pushes a different mapping context. `IA_Move` never changes.

### The three steps

1. **Create the assets** — `IA_Move` (Value Type: Axis2D) and an
   `IMC_Default` mapping context that binds W/A/S/D to it with the
   appropriate modifiers (Negate, Swizzle) to produce a 2D vector.
2. **Add the mapping context** in `BeginPlay`, via the local player's
   `UEnhancedInputLocalPlayerSubsystem`.
3. **Bind the action** in `SetupPlayerInputComponent`, casting the
   component to `UEnhancedInputComponent`.

Step 1 is editor work. Steps 2 and 3 are the C++ you're writing.

---

## Your task

You're given `ALabCharacter` with the camera and movement already set up.
**You wire the input.**

1. In `BeginPlay`, get the `UEnhancedInputLocalPlayerSubsystem` from the
   owning `APlayerController`'s local player, and add your mapping context.
2. In `SetupPlayerInputComponent`, cast to `UEnhancedInputComponent` and
   bind `IA_Move` (Triggered) to a handler.
3. In the handler, read the `FInputActionValue` as a `FVector2D` and feed
   it to `AddMovementInput`.

Then set your `GameMode`'s Default Pawn Class so the character is what
gets possessed at play.

**Ask your agent** to explain any of the types involved, or to inspect the
live pawn during PIE. **Don't ask it to write the binding** — it's about
fifteen lines, and they're the fifteen that make the framework click.

---

## Stuck?

<details>
<summary>PIE starts but I'm not controlling anything</summary>

Either the GameMode's Default Pawn Class isn't your character, or the
Player Start is missing from the level. Ask your agent what pawn the
controller actually possessed — that's a live-inspection question it can
answer directly.
</details>

<details>
<summary>The pawn exists but input does nothing</summary>

Almost always the mapping context wasn't added. It's easy to write that
code and have it silently no-op if the subsystem lookup returned null.
Log it and check. Order matters: the local player must exist, which it does
by `BeginPlay` for a possessed pawn but *not* in the constructor.
</details>

<details>
<summary>I move in only one axis, or the directions are wrong</summary>

That's the modifiers on the mapping context, not your C++. W/S and A/D need
Negate and Swizzle to combine into a sensible Axis2D. This is fiddly and
entirely editor-side.
</details>

<details>
<summary>Where do I get the subsystem from?</summary>

`ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>()`, and you
reach the local player through the controller. Everything in that chain can
be null — check as you go rather than at the end.
</details>

---

## Run the checks

```bash
cd grader && .venv/bin/python -m pytest checks/ch03_input.py -v
```

Then [Chapter 4](../04-collision-and-interaction/).

---

## What just happened

You met the framework Unreal expects you to build inside. The class carousel
looks like ceremony until you see what each one is for — and then it looks
like the accumulated scar tissue of a lot of shipped multiplayer games,
which is what it is.

You also used an input system that deliberately refuses to let you bind a
key to a behavior. That indirection is what makes the VR swap in the
capstone a configuration change instead of a rewrite.

Next chapter you make the world react to you.

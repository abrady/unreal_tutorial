# Chapter 3 — You, and you can shoot

**Goal:** stand in the gym, click, and watch something fly at the dummy.

The character, camera, and movement are already written for you. You wire the
input and make the projectile. That's a deliberate scope cut — character
boilerplate teaches almost nothing and eats the clock.

**Time:** ~60 minutes.

---

## What green looks like

```console
$ cd grader && .venv/bin/python -m pytest checks/ch03_shooting.py
```

The checks start PIE, confirm a pawn got possessed, inject a fire input, and
assert a projectile actually exists in the world.

---

## Part A — the six classes

Get this into your head before you write anything. Almost every "why is my
data gone?" bug in Unreal is state living in the wrong one of these.

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

### The trap

Put the player's score on the **Pawn** and it dies when the pawn dies. Put it
on **PlayerState** and it survives respawning — which is precisely why
`PlayerState` exists.

Put game rules on the **PlayerController** and in multiplayer every client
runs its own copy of the rules. Put them on **GameMode**, which only exists on
the server, and they can't.

Single-player hides all of this. It surfaces when something gets networked,
which for partners is usually late and expensive.

---

## Part B — Enhanced Input

The old system bound a function straight to a key. Enhanced Input adds two
layers, and both earn their keep.

```
InputAction        IA_Fire       "the intent to fire"     (an asset)
     ↑
MappingContext     IMC_Default   "left mouse / R trigger" (an asset)
     ↑
Binding            C++            "call this on Fire"
```

**Why bother?** Intent and keys are now separate. You get remapping free. You
can push a menu context that shadows gameplay and pop it later. And the same
`IA_Fire` works for mouse, gamepad, and — the one that matters here — **VR
controllers**, with no gameplay change.

That's not a hypothetical. It's the reason the optional VR capstone is a
configuration swap instead of a rewrite.

### The three steps

1. **Create the assets** — `IA_Fire` (Value Type: Digital/bool) and an
   `IMC_Default` binding left mouse to it. Editor work.
2. **Add the mapping context** in `BeginPlay`, via the local player's
   `UEnhancedInputLocalPlayerSubsystem`.
3. **Bind the action** in `SetupPlayerInputComponent`, casting to
   `UEnhancedInputComponent`.

Steps 2 and 3 are your C++.

---

## Part C — the projectile

Make an `AProjectile` actor:

- A **sphere mesh** as root, scaled small.
- A `UProjectileMovementComponent` — another component, doing the physics for
  you. Set `InitialSpeed` and `MaxSpeed`.
- A lifespan so stray shots clean themselves up: `InitialLifeSpan = 3.f`.

Then, in your fire handler, `SpawnActor<AProjectile>` at the muzzle, oriented
down the camera's forward vector.

Two things that bite:

**`FActorSpawnParameters`.** Set `Owner` and `Instigator` to the firing pawn.
Chapter 4 needs them to know who dealt the damage, and forgetting is a bug you
won't see until then.

**Spawn collision handling.** The default can refuse to spawn a projectile
that starts overlapping the player. Spawn slightly in front, or set
`SpawnCollisionHandlingOverride`.

---

## Your task

1. Wire `IA_Fire` — mapping context in `BeginPlay`, binding in
   `SetupPlayerInputComponent`.
2. Build `AProjectile` with mesh, movement component, and lifespan.
3. Spawn it on fire, from the camera, with `Owner` and `Instigator` set.
4. Point the GameMode's Default Pawn Class at `ALabCharacter`.

Nothing damages anything yet. Projectiles fly through the dummy. That's
Chapter 4.

---

## Stuck?

<details>
<summary>PIE starts but I'm not controlling anything</summary>

Either the GameMode's Default Pawn Class isn't `ALabCharacter`, or there's no
Player Start in the level. Ask your agent which pawn the controller actually
possessed — live inspection answers that directly.
</details>

<details>
<summary>The pawn works but firing does nothing</summary>

Almost always the mapping context wasn't added. That code silently no-ops if
the subsystem lookup returned null. Log it. Order matters: the local player
exists by `BeginPlay` for a possessed pawn, but **not** in the constructor.
</details>

<details>
<summary>The binding fires but no projectile appears</summary>

Either the spawn was refused by collision handling, or it spawned inside you
and died instantly, or `InitialSpeed` is zero so it's sitting on your face.
Ask your agent to list actors of your projectile class during PIE — if
they're there, it's a movement problem, not a spawn problem.
</details>

<details>
<summary>Projectiles fly in the wrong direction</summary>

You're using the pawn's rotation rather than the camera's. In first person
they diverge as soon as you look up or down.
</details>

<details>
<summary>Where do I get the input subsystem from?</summary>

`ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>()`, reached
through the controller. Every link in that chain can be null — check as you
go, not at the end.
</details>

---

## Run the checks

```bash
cd grader && .venv/bin/python -m pytest checks/ch03_shooting.py -v
```

Then [Chapter 4](../04-damage/), where the dummy starts to notice.

---

## What just happened

You met the framework Unreal expects you to build inside. The class carousel
looks like ceremony until you see what each one is for, and then it looks like
the accumulated scar tissue of a lot of shipped multiplayer games — which is
what it is.

You also used an input system that refuses to let you bind a key to a
behaviour. That indirection is exactly what makes the same firing code work
from a mouse, a gamepad, or a VR trigger.

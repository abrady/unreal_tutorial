---
marp: true
theme: default
paginate: true
header: 'Unreal, the hard way'
style: |
  section { font-size: 26px; }
  h1 { color: #1a1a2e; }
  code { background: #f4f4f8; }
  .small { font-size: 20px; }
  .big { font-size: 40px; font-weight: 600; }
---

<!-- _paginate: false -->
<!-- _header: '' -->

# Unreal, the hard way

### A half-day lab for people who already know C++

Aaron Brady · DRE

<span class="small">You do not need a VR headset.</span>

---

## Why we're doing this

There is no internal Unreal course.

The Eng Bootcamp Immersive 3D path lists **one** hands-on engine course.
It's Unity.

This has been proposed **three times** since 2022 — 2022, and twice in 2023,
once by our own team. None shipped. All three were framed as a *curriculum*.

Both Unity attempts shipped. Both were **a single lab**.

<span class="small">So: one lab. Four hours. Complete on its own.</span>

---

## How today works

<span class="big">The lab is a test suite.</span>

Every chapter ships **failing checks**. You're done when they're green.

```console
$ pytest grader/checks/ch04_interaction.py
FAILED  test_plate_opens_door    - BP_Door yaw was 0.0, expected ~90.0
FAILED  test_pickup_is_consumed  - Pickup still present after overlap
```

The grader doesn't read your source. It boots your project, starts PIE,
walks the player onto the plate, and asks the **live editor** what happened.

---

## The AI rules, and why they exist

Bastani et al. 2024 — ~1000 students, three arms:

| | Practice | Unassisted exam |
|---|---|---|
| No AI | — | — |
| **Unrestricted GPT-4** | **+48%** | **−17%** |
| Guardrailed tutor | positive | no harm |

Unrestricted AI made people dramatically better — until you took it away,
at which point they were **worse than never having had it**.

---

## So, during a chapter

**The agent may** — explain, inspect live state, diagnose compile errors,
point at docs, ask you questions.

**The agent may not** — write your solution, edit `Source/` for the current
chapter, or peek at `chNN-solution`.

**Once your checks are green** — no restrictions. Diff against the
reference. Ask it to tear your version apart.

<span class="small">Enforcement is a config file and an honour system. We're
showing you the study instead of pretending the guardrail is airtight.</span>

---

## But delegate the repetition

<span class="big">Do it once by hand. Then hand off the grind.</span>

You wire `IA_Fire`. The agent adds `IA_Reload` and `IA_Dash`.
You place one dummy. The agent places four more.

Doing it a second time isn't learning — it's typing.

<span class="small">And when it *can't* do something, note that. It cannot
create a level, for instance. Partners will ask you where the edges are.</span>

---

## Your agent is *inside* the editor

Unreal 5.8 ships Epic's `ModelContextProtocol` plugin.
HTTP + JSON-RPC on `localhost:8000/mcp`.

It can start PIE, capture a viewport annotated with every actor's world
position, and read real compiler errors.

**Same interface the grader uses.** So "why is check 3 failing?" is a
question it can actually go and answer.

---

## And you can extend it

```cpp
UFUNCTION(meta = (AICallable))
static float GetDoorAngle(AActor* Door);
```

Restart your client. That's now a tool the agent can call.

<span class="small">The agent isn't something being done to you.
It's something you build on. Partners will ask you about this.</span>

---

<!-- _class: lead -->

# Chapter 1
## The iteration loop, and your first Actor

---

## Unreal's C++ isn't quite C++

`UCLASS()` `UPROPERTY()` `UFUNCTION()` feed a **code generator** that runs
before the compiler.

It emits reflection data: type info, serialization, Blueprint exposure,
garbage-collection tracking.

That's why `#include "MyActor.generated.h"` must be the **last** include.
Everything above it gets scanned.

<span class="small">Get the order wrong and the error message will not tell
you that's the problem.</span>

---

## Two ways to compile

| | Speed | Handles |
|---|---|---|
| **Live Coding** | seconds | `.cpp` bodies |
| **Full rebuild** | minutes | headers, new files, `Build.cs` |

Live Coding patches the running editor. It cannot add a `UPROPERTY`,
change a class layout, or introduce a new file.

<span class="small">When Live Coding "works" but nothing changes, you
needed a full rebuild.</span>

---

<!-- _class: lead -->

# Chapter 2
## Lifecycle, GC, and the CDO

<span class="small">The chapter that matters.</span>

---

## Your constructor can't see per-instance edits

At editor startup, Unreal builds **one** of every UCLASS: the
**Class Default Object**. Your constructor runs there first.

It runs again per instance — but overrides land **after** it:

```
1. construct from the CDO template   <- MaxHealth still 100
2. apply per-instance overrides      <- MaxHealth becomes 250
3. BeginPlay                         <- first point you can trust it
```

<span class="small">A constructor that reads `MaxHealth` reads the default,
never the value set in the level.</span>

---

## And `GetWorld()` is a trap

You'll read that the constructor has no world.

True **for the CDO**. Often false for a spawned instance.

<span class="big">The rule isn't "no world." It's "can't rely on it."</span>

<span class="small">Same code path, two contexts, one of them null. Code that
works when you spawn at runtime can crash at editor startup.</span>

---

## Where does my code go?

| Hook | When | Use it for |
|---|---|---|
| Constructor | CDO creation, editor startup | defaults, creating components |
| `OnConstruction` | every property edit | editor-time generated content |
| `PostInitializeComponents` | after components exist | component wiring |
| `BeginPlay` | gameplay starts | **anything touching the world** |
| `Tick` | every frame | continuous behavior |

<span class="small">Default answer: `BeginPlay`.</span>

---

## The GC trap

Unreal has a garbage collector. It only knows about pointers it can see.

```cpp
UPROPERTY()
TObjectPtr<UMyThing> Tracked;   // ✓ GC keeps it alive

UMyThing* Untracked;            // ✗ collected out from under you
```

No compiler error. No warning. Works fine — until a collection runs,
and then you're reading freed memory.

<span class="big">You'll break this on purpose today.</span>

---

<!-- _class: lead -->

# Chapter 3
## The gameplay framework

---

## Six classes, and which owns what

| Class | Lives | Owns |
|---|---|---|
| `GameMode` | server only | rules, spawning |
| `GameState` | replicated to all | shared match state |
| `PlayerController` | one per player | input, camera, UI |
| `PlayerState` | replicated | per-player data (score) |
| `Pawn` / `Character` | in the world | the physical body |

**Possession** is the join: a Controller possesses a Pawn.

<span class="small">Put player data on the Pawn and it dies with the body.</span>

---

## Enhanced Input

Old way: bind directly to a key.
New way: three layers.

**Input Action** — *what* (`IA_Jump`), an asset
**Mapping Context** — *which keys*, pushed/popped at runtime
**Binding** — your C++ handler

Costs more setup. Buys remapping, layered contexts (on foot vs. in menu),
and the same code path for keyboard, gamepad, and VR controllers.

<span class="small">That last one is why we're using it.</span>

---

<!-- _class: lead -->

# Chapter 4
## Collision and interaction

---

## Collision is a matrix, not a boolean

Every component has an **object type** and, for each **channel**, a response:

`Ignore` · `Overlap` · `Block`

Both parties must agree. A blocks B only if **A blocks B *and* B blocks A**.

For overlap events you also need **Generate Overlap Events** on both.

<span class="small">"My trigger doesn't fire" is almost always one half of
this matrix.</span>

---

## Interfaces, and the C++/Blueprint boundary

```cpp
UINTERFACE(MinimalAPI, Blueprintable)
class UInteractable : public UInterface { GENERATED_BODY() };

class IInteractable
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintNativeEvent)
    void Interact(AActor* Instigator);
};
```

`BlueprintNativeEvent` = C++ default, overridable in Blueprint.

The pawn talks to `IInteractable`. It never knows about doors or pickups.

---

## Why that interface is the point

The pawn doesn't implement interaction. It **asks** for it.

Swap the desktop pawn for a VR pawn and every door, plate, and pickup
keeps working, untouched.

<span class="big">That's the VR lesson.</span>

<span class="small">And you just learned it without a headset.</span>

---

## Where to go next

Take-home, self-serve, optional:

- Delegates and game state
- UMG HUD from C++
- **AI patrol** — NavMesh, Behavior Trees, Blackboards
  <span class="small">(best showcase of live MCP inspection)</span>
- Audio
- Packaging a standalone build
- **The VR pawn swap** — headset required

---

<!-- _class: lead -->
<!-- _paginate: false -->

# Go build a room

<span class="small">`pytest grader/checks/ch01_actor.py`</span>

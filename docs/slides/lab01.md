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

### Build a combat gym. In C++. In about five hours.

Aaron Brady · DRE

<span class="small">You do not need a VR headset.</span>

---

## What we're building

A room with a target dummy.

You shoot it. Damage numbers pop off.

Then you attach a component and **it shoots back**.

<span class="small">Five chapters. Nothing you build gets thrown away.</span>

---

## Why we're doing this

There is no internal Unreal course.

The Eng Bootcamp Immersive 3D path lists **one** hands-on engine course.
It's Unity.

Proposed **three times** since 2022 — including once by our own team.
None shipped. All three were framed as a *curriculum*.

Both Unity attempts shipped. Both were **a single lab**.

---

## How today works

<span class="big">The lab is a test suite.</span>

Every chapter ships **failing checks**. You're done when they're green.

```console
$ pytest grader/checks/ch04_damage.py
FAILED  test_dummy_takes_damage   - Health still 100.0 after 3 hits
FAILED  test_history_records_hit  - DamageHistory is empty
```

The grader doesn't read your source. It boots your project, starts PIE,
fires a projectile, and asks the **live editor** what happened.

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

**Once your checks are green** — no restrictions.

<span class="small">Enforcement is a config file and an honour system. We're
showing you the study instead of pretending the guardrail is airtight.</span>

---

## But delegate the repetition

<span class="big">Do it once by hand. Then hand off the grind.</span>

You wire `IA_Fire`. The agent adds `IA_Reload` and `IA_Dash`.
You place one dummy. The agent places four more.

Doing it a second time isn't learning — it's typing.

<span class="small">And when it *can't* do something, note that. The 255 tools
have edges, and partners will ask you where they are.</span>

---

## Your agent is *inside* the editor

Unreal 5.8 ships Epic's `ModelContextProtocol` plugin.
HTTP + JSON-RPC on `localhost:8000/mcp`. **255 tools.**

Start PIE, inspect live actors, read real compiler errors.

**Same interface the grader uses.** So *"why is check 3 failing?"* is a
question it can actually go and answer.

---

## And you can extend it

```cpp
UFUNCTION(meta = (AICallable))
static float GetDummySpinRate(AActor* Dummy);
```

Restart your client. That's now a tool the agent can call.

<span class="small">The agent isn't something being done to you.
It's something you build on. Partners will ask about this.</span>

---

<!-- _class: lead -->

# Chapter 1
## The iteration loop, and the dummy

---

## Unreal's C++ isn't quite C++

`UCLASS()` `UPROPERTY()` `UFUNCTION()` feed a **code generator** that runs
before the compiler.

It emits reflection data: type info, serialization, Blueprint exposure,
garbage-collection tracking.

That's why `#include "TargetDummy.generated.h"` must be the **last**
include. Everything above it gets scanned.

<span class="small">Get the order wrong and the error will not mention
includes.</span>

---

## Actors are assembled, not inherited

An `AActor` is mostly an empty container. Everything comes from
**components**.

| Class | Adds |
|---|---|
| `UActorComponent` | behaviour, no position |
| `USceneComponent` | a transform, can be attached |
| `UPrimitiveComponent` | geometry and collision |

**The root component defines the actor's transform.**
Attach the head to the body, and the head comes along.

---

## Two ways to compile

| | Speed | Handles |
|---|---|---|
| **Live Coding** | seconds | `.cpp` bodies |
| **Full rebuild** | minutes | headers, new files, `Build.cs` |

Live Coding cannot add a `UPROPERTY`, change class layout, or add a file.

<span class="small">When Live Coding "works" but nothing changed, you
needed a full rebuild. Close the editor first.</span>

---

<!-- _class: lead -->

# Chapter 2
## Health, the CDO, and the collector

<span class="small">The chapter that matters.</span>

---

## Where do you set `Health = MaxHealth`?

Put three dummies in the level. Set one to `MaxHealth = 250`.

**In the constructor?** All three start at 100.
**In `BeginPlay`?** The edited one starts at 250.

---

## Your constructor runs on an object that isn't yours

At editor startup, Unreal instantiates **one** of every UCLASS: the
**Class Default Object**.

Your constructor runs there, once, before any level loads.
Every instance is then **copied from the CDO**.

```cpp
ATargetDummy::ATargetDummy()
{
    MaxHealth = 100.f;                    // ✓ a default
    Body = CreateDefaultSubobject<...>(); // ✓ structure
    Health = MaxHealth;                   // ✗ too early
    GetWorld()->SpawnActor<AThing>();     // ✗ no world
}
```

---

## Where does my code go?

| Hook | When | Use it for |
|---|---|---|
| Constructor | CDO creation | defaults, components |
| `OnConstruction` | every property edit | editor-time content |
| `PostInitializeComponents` | components exist | component wiring |
| `BeginPlay` | gameplay starts | **anything world-dependent** |
| `Tick` | every frame | continuous behaviour |

<span class="small">Default answer: `BeginPlay`.</span>

---

## The GC trap

Unreal has a garbage collector. It walks the **reflection graph**.

```cpp
UPROPERTY()
TObjectPtr<UDamageHistory> History;   // ✓ GC sees it

UDamageHistory* History;              // ✗ collected
```

No compiler error. No warning. Works fine — until a collection runs,
and then you're reading freed memory.

<span class="big">You'll break this on purpose today.</span>

---

<!-- _class: lead -->

# Chapter 3
## You, and you can shoot

---

## Six classes, and which owns what

| Class | Lives | Owns |
|---|---|---|
| `GameMode` | server only | rules, spawning |
| `GameState` | replicated | shared match state |
| `PlayerController` | one per player | input, camera, UI |
| `PlayerState` | replicated | per-player data (score) |
| `Pawn` / `Character` | in the world | the physical body |

**Possession** is the join: a Controller possesses a Pawn.

<span class="small">Score on the Pawn dies with the body. That's what
PlayerState is for.</span>

---

## Enhanced Input

**Input Action** — *what* (`IA_Fire`), an asset
**Mapping Context** — *which keys*, pushed and popped at runtime
**Binding** — your C++ handler

Costs more setup. Buys remapping, layered contexts, and the same code path
for mouse, gamepad, and **VR controllers**.

<span class="small">That last one is why we're using it.</span>

---

<!-- _class: lead -->

# Chapter 4
## Hits, damage, floating numbers

---

## Collision is a matrix, not a boolean

Every component has an **object type** and, per **channel**, a response:

`Ignore` · `Overlap` · `Block`

Both parties must agree. A blocks B only if **A blocks B *and* B blocks A**.

| | Fires when | Use for |
|---|---|---|
| `OnComponentHit` | two **blocking** things collide | projectiles that stop |
| `OnComponentBeginOverlap` | entering an **overlap** volume | triggers, pickups |

---

## Route damage through the pipeline

```cpp
UGameplayStatics::ApplyDamage(HitActor, 25.f,
    InstigatorController, this, UDamageType::StaticClass());
```

Then override `AActor::TakeDamage`. **Call `Super`.**

Looks like ceremony at this scale. Stops looking like ceremony the first
time someone asks for a shield that halves incoming damage.

---

<!-- _class: lead -->

# Chapter 5
## Ability components

<span class="small">The most important architectural chapter.</span>

---

## The design question

You want a dummy that shoots. The obvious move:

```
ATargetDummy
 └── AShootingDummy
      └── AHomingShootingDummy
           └── AHomingExplodingShootingDummy   ← hell
```

Every combination needs a class.

---

## Composition instead

```
ATargetDummy
 ├── Body (StaticMesh)
 ├── Head (StaticMesh)
 └── CannonAbility (UAbilityComponent)   ← dummy knows nothing
```

Exploding homing dummy? **Attach two components.**

No new class. No inheritance diamond. And a designer can do it in the
editor without touching code.

<span class="small">This is why `AActor` is nearly empty.</span>

---

## Keep the component ignorant

```cpp
AActor* Owner = GetOwner();
```

That's the component's whole view of the world.

A component that casts its owner to `ATargetDummy` has thrown away its
reusability.

<span class="big">Keep it working against `AActor`.</span>

<span class="small">Then it drops onto the player, a turret, or a barrel
unchanged.</span>

---

## Where the VR lesson lands

Your ability doesn't know what triggered it.
Your damage pipeline doesn't know what dealt it.
Your firing code doesn't know what device sent `IA_Fire`.

**Swap the pawn for VR hands. The combat layer is untouched.**

<span class="small">You just learned it without a headset.</span>

---

## Take-home

**Ch 6** — three dummies, three powers: AOE, homing, spread.
Where composition starts paying real dividends.

**Ch 7** — attacks driven by animation timing, via montage notifies.
How real combat games actually do it.

<span class="small">Also: UMG health bars · Behavior Trees (best MCP
inspection showcase) · audio · packaging · the VR pawn swap.</span>

---

<!-- _class: lead -->
<!-- _paginate: false -->

# Go build a gym

<span class="small">`pytest grader/checks/ch01_dummy.py`</span>

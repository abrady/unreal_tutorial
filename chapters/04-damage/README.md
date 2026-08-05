# Chapter 4 — Hits, damage, and floating numbers

**Goal:** shoot the dummy and watch `-25` pop off it.

This is the payoff chapter. It's the first time the gym stops being a tech
demo and starts being a game.

**Time:** ~60 minutes.

---

## What green looks like

```console
$ cd grader && python3 check.py ch04
```

The checks fire a projectile at a dummy and assert its health dropped and the
damage history recorded the hit.

---

## Part A — collision is a matrix, not a boolean

Every primitive component carries:

- an **object type** — what it *is* (WorldStatic, Pawn, PhysicsBody…)
- a **response** to each channel — `Ignore`, `Overlap`, or `Block`

The rule that catches everyone:

> **Both parties must agree.** A blocks B only if A blocks B **and** B blocks
> A. For an overlap *event*, at least one side must be set to Overlap, and
> **Generate Overlap Events** must be true on both.

"My projectile passes straight through" is nearly always one half of a matrix
you only checked once.

**Profiles** are named presets over that matrix — `BlockAll`, `Pawn`,
`OverlapAllDynamic`, `Projectile`. Use them. Hand-setting individual channel
responses is how you end up with something that works everywhere except one
interaction.

### Hit vs. overlap

| | Fires when | Use for |
|---|---|---|
| `OnComponentHit` | two **blocking** things collide | projectiles that stop |
| `OnComponentBeginOverlap` | something enters an **overlap** volume | triggers, pickups |

A projectile that should stop dead on impact wants **Hit**. A projectile that
should pass through and damage everything it touches wants **Overlap**. Pick
deliberately — this choice shapes how the rest of your combat feels.

---

## Part B — the damage pipeline

Unreal ships a damage system. Use it rather than calling `Health -= 25`
directly, because it gives you a single choke point where armour, resistances,
invulnerability frames, and damage-type logic can live later.

```cpp
UGameplayStatics::ApplyDamage(
    HitActor,          // who's being hit
    DamageAmount,
    InstigatorController,
    this,              // the damage causer (the projectile)
    UDamageType::StaticClass());
```

On the receiving end, override `AActor::TakeDamage`:

```cpp
float ATargetDummy::TakeDamage(float Damage, FDamageEvent const& Event,
                               AController* Instigator, AActor* Causer)
{
    const float Applied = Super::TakeDamage(Damage, Event, Instigator, Causer);
    // reduce Health, record in History, react
    return Applied;
}
```

**Call `Super::TakeDamage` and respect its return value.** It applies damage
modifiers, and skipping it means your damage silently ignores anything the
engine or a future subsystem wants to say about it.

This is where Chapter 2's `UDamageHistory` earns its place — record each hit
as it lands.

---

## Part C — damage numbers

Debug visualisation is a real skill, not a toy. Being able to see what your
systems are doing is most of what makes combat tuning possible.

```cpp
DrawDebugString(GetWorld(), Location, FString::Printf(TEXT("-%.0f"), Damage),
                nullptr, FColor::Yellow, 1.5f /*duration*/);
```

You'll want `#include "DrawDebugHelpers.h"`.

Draw at the hit location, offset slightly up. Proper floating combat text
belongs in UMG and is a take-home chapter; this is the version that takes five
minutes and tells you everything you need during development.

---

## Your task

1. Give `AProjectile` a collision response that interacts with dummies, and
   bind a hit or overlap handler.
2. On hit, `ApplyDamage` to what you struck, then destroy the projectile.
3. Override `TakeDamage` on `ATargetDummy` — reduce health, append to the
   damage history, and handle reaching zero however you like.
4. Draw a damage number at the impact point.

---

## Stuck?

<details>
<summary>Nothing happens on impact</summary>

Work the matrix from both ends. Ask your agent to inspect the collision
settings on both the projectile and the dummy during PIE, then check that
your handler is actually bound — an unbound delegate is silent.
</details>

<details>
<summary>The projectile stops but TakeDamage never runs</summary>

Either `ApplyDamage` got a null actor, or the instigator chain is broken.
This is where Chapter 3's `Owner`/`Instigator` spawn parameters come due.
</details>

<details>
<summary>Damage applies twice per shot</summary>

Both a hit and an overlap fired, or the projectile bounced and struck again
before being destroyed. Destroy it in the same frame it lands, and pick one
event type.
</details>

<details>
<summary>The number appears but instantly vanishes</summary>

`DrawDebugString` duration is in seconds; a value of 0 means one frame. Also
check you're not drawing at the projectile's location *after* destroying it.
</details>

<details>
<summary>Health goes negative</summary>

Clamp it. Worth thinking about where that clamp belongs — in `TakeDamage`, or
in whatever reads `Health`? There's a real design argument either way.
</details>

---

## Run the checks

```bash
cd grader && python3 check.py ch04
```

Then [Chapter 5](../05-ability-components/), where the dummy shoots back.

---

## What just happened

You wired a full damage loop: input → projectile → collision → damage → state
change → visible feedback. That loop, in some form, is the spine of every
action game ever shipped.

You also routed damage through the engine's pipeline rather than mutating a
float. That looks like ceremony at this scale. It stops looking like ceremony
the first time someone asks for a shield that halves incoming damage.

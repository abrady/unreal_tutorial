# Chapter 6 — Three dummies, three powers

*Take-home. ~60–90 minutes.*

**Goal:** an AOE dummy, a homing-missile dummy, and a spread-shot dummy —
without adding a single new actor class.

This is where Chapter 5's design pays off. If the base was right, three new
behaviours cost three components and nothing else changes.

---

## What green looks like

```console
$ cd grader && python3 check.py ch06
```

---

## The three abilities

**`UAoeAbilityComponent`** — no projectile. On activation, sphere-overlap
around the owner and damage everything hostile inside.

Look at `UKismetSystemLibrary::SphereOverlapActors` or
`UWorld::OverlapMultiByChannel`. Draw it with `DrawDebugSphere` — an AOE you
can't see is an AOE you can't tune.

**`UHomingAbilityComponent`** — a projectile that steers.

`UProjectileMovementComponent` does this for you:

```cpp
Movement->bIsHomingProjectile = true;
Movement->HomingTargetComponent = Target->GetRootComponent();
Movement->HomingAccelerationMagnitude = 5000.f;
```

Tune the acceleration until it's threatening but dodgeable. That tuning *is*
the exercise — it's what combat design actually feels like.

**`USpreadAbilityComponent`** — N projectiles in an arc.

Rotate the base direction by `FRotator(0, Angle, 0)` per shot. Expose count
and total arc as `EditAnywhere` so you can tune it live in the editor.

---

## What this chapter is really teaching

**Virtual dispatch earns its keep.** Three subclasses, one `Activate()`
override each, and the dummy still knows nothing. If you find yourself needing
to change `UAbilityComponent` to add a subclass, the base abstraction is
wrong — that's a useful signal, not a failure.

**Data-driven beats code-driven.** Every tunable value should be
`UPROPERTY(EditAnywhere)`. The test: can you retune the whole gym without
recompiling? If yes, a designer could too, and you've built something a real
team can use.

```cpp
UPROPERTY(EditAnywhere, Category = "Ability",
          meta = (ClampMin = "0.1", UIMin = "0.1", UIMax = "10.0"))
float Cooldown = 2.f;
```

Those `meta` specifiers are worth learning. They're the difference between a
property a designer can use safely and one they'll accidentally set to -47.

**Composition composes.** Attach two ability components to one dummy. It uses
both. That's the moment the pattern clicks — you didn't design for that
combination and it works anyway.

---

## Stretch

- **A `UHealthComponent`.** Health currently lives on `ATargetDummy`, which
  means the player has its own separate copy. Pull it into a component and
  both use it. That's the same refactor you just did for abilities, applied to
  state — and it's how shipping projects actually organise this.
- **A data table** of ability configs, so powers are rows rather than classes.
- **Telegraphs.** Draw the AOE radius a second before it fires. Suddenly the
  gym has readable, dodgeable attacks, which is most of what makes combat feel
  fair.

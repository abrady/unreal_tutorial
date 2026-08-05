# Chapter 5 — Ability components: the dummy shoots back

**Goal:** attach a component to a dummy and it starts firing cannonballs at
you. Detach it and it's a punching bag again. Never edit `ATargetDummy` to do
either.

This is the most important architectural chapter in the lab. Composition is
how Unreal is built, and once you see it you'll see it everywhere in every
partner project you open.

**Time:** ~90 minutes.

---

## What green looks like

```console
$ cd grader && .venv/bin/python -m pytest checks/ch05_abilities.py
```

The checks start PIE, wait past the cooldown, and assert a dummy-spawned
projectile exists and the player took damage.

---

## The design question

You want a dummy that shoots. The obvious move is to subclass:

```
ATargetDummy
 └── AShootingDummy
      └── AHomingShootingDummy
           └── AHomingExplodingShootingDummy      ← you are now in hell
```

Every combination needs a class. A dummy that shoots *and* explodes needs a
class that inherits from both, which C++ will let you do and you will regret.

**Composition instead.** The dummy stays a dummy. Abilities are components you
attach:

```
ATargetDummy
 ├── Body (StaticMesh)
 ├── Head (StaticMesh)
 └── CannonAbility (UAbilityComponent)     ← the dummy knows nothing about this
```

Want an exploding homing dummy? Attach two components. No new actor class, no
inheritance diamond, and — the part that matters in a real project — a
designer can do it in the editor without touching code.

This is why `AActor` is nearly empty and `ACharacter` is mostly a bag of
components. You've been using the pattern since Chapter 1; now you're building
with it.

---

## What a component actually is

Chapter 1 covered the hierarchy. The distinction matters now:

| Class | Has a transform? | Use for |
|---|---|---|
| `UActorComponent` | **no** | pure behaviour — abilities, health, inventory |
| `USceneComponent` | yes | anything needing a position |
| `UPrimitiveComponent` | yes, plus geometry | meshes, collision volumes |

An ability doesn't have a location — the *actor* does. So `UAbilityComponent`
derives from `UActorComponent`. Reaching for `USceneComponent` by reflex is a
common early mistake; it drags a transform you don't want and quietly
complicates attachment.

### Components tick too

```cpp
UAbilityComponent::UAbilityComponent()
{
    PrimaryComponentTick.bCanEverTick = true;   // opt-in, same as actors
}

void UAbilityComponent::TickComponent(float DeltaTime, ELevelTick TickType,
                                      FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    // cooldown logic
}
```

### Getting at your owner

```cpp
AActor* Owner = GetOwner();
```

That's the component's whole view of the world, and it should stay that way.
A component that casts its owner to `ATargetDummy` has thrown away its
reusability — it can no longer be attached to anything else. Keep it working
against `AActor` and it drops onto the player, a turret, or a barrel
unchanged.

---

## Your task

**1. A base class.** `UAbilityComponent : public UActorComponent` with:

- `UPROPERTY(EditAnywhere)` cooldown and range
- cooldown tracking in `TickComponent`
- a `virtual void Activate()` that subclasses override
- a `CanActivate()` check — cooldown elapsed, target in range

**2. A concrete ability.** `UCannonAbilityComponent : public UAbilityComponent`
that overrides `Activate()` to spawn an `AProjectile` aimed at the player.

**3. Attach it.** Add it to your dummy — in C++ via
`CreateDefaultSubobject`, or in the editor via Add Component. Try the editor
route at least once; that's how a designer would do it, and it's the argument
for the whole pattern.

**4. Make it hurt.** The player needs health and a `TakeDamage` override.
`ALabCharacter` has the hooks; wire them up.

### Finding the player

`UGameplayStatics::GetPlayerPawn(this, 0)` works and is fine here. Worth
knowing it's a shortcut that assumes single-player — in a real project you'd
pass a target in rather than reach for the global.

---

## Stuck?

<details>
<summary>The component exists but never ticks</summary>

`PrimaryComponentTick.bCanEverTick = true` in the *component's* constructor.
The actor's tick setting doesn't cover its components.
</details>

<details>
<summary>Activate() runs but no projectile appears</summary>

Same three suspects as Chapter 3: spawn collision handling, zero speed, or
spawning inside the dummy's own collision and dying instantly. Spawn out at
the muzzle, not at the actor origin.
</details>

<details>
<summary>The dummy shoots itself</summary>

Set the projectile's `Owner`/`Instigator` to the dummy and ignore the owner in
your hit handler. Every shooter ships this bug once.
</details>

<details>
<summary>My override isn't called</summary>

`Activate()` must be `virtual` in the base and you must be calling it through
a base-class pointer. If you stored the component as
`UCannonAbilityComponent*` you've defeated the point of the exercise — store
it as `UAbilityComponent*`.
</details>

<details>
<summary>The component can't see the dummy's health</summary>

Good. It shouldn't. If an ability genuinely needs owner state, expose it
through an interface or a health component rather than casting to
`ATargetDummy` — otherwise you've rebuilt the inheritance coupling you were
avoiding.
</details>

---

## Run the checks

```bash
cd grader && .venv/bin/python -m pytest checks/ch05_abilities.py -v
```

---

## You built a combat gym

You walk in, you shoot a dummy, numbers pop off it, and it shoots back. In
C++, from an empty project, in about five hours.

More usefully: you can now open an unfamiliar Unreal project and have a
reasonable guess about what the classes are, why they're split that way, and
where to look when something doesn't fire.

---

## The VR part

There wasn't one. No headset, no MetaXR plugin, no Android toolchain.

But look at what you built:

- Your ability component doesn't know what triggered it.
- Your damage pipeline doesn't know what dealt the damage.
- Your firing code doesn't know what device sent `IA_Fire`.

**Swap the desktop pawn for a VR pawn and the combat layer is untouched.**
Different pawn, different mapping context, same `IA_Fire`, same abilities,
same damage. You'd change configuration, not systems.

That's the real lesson about writing VR-ready code, and you learned it on a
laptop. The optional capstone does the swap if you have a headset — it's
mostly configuration, which is exactly the point.

---

## Where to go next

**[Chapter 6](../06-powers/)** — three dummies, three powers: AOE, homing
missiles, spread shot. Where composition starts paying real dividends.

**[Chapter 7](../07-montage-notifies/)** — drive attacks off animation timing
instead of a cooldown, using montages and `AnimNotify`. How real combat games
actually do it.

Both are substantial — 60–90 minutes each. Also available: UMG health bars ·
AI with NavMesh and Behavior Trees (the best showcase of MCP live inspection)
· audio · packaging · the VR pawn swap.

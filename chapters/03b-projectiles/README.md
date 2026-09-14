# Chapter 3b — Something flies

**Goal:** click and watch a projectile fly from the camera toward the dummy.

Chapter 3a proved that input reaches your character. This chapter keeps that
known-good pipeline and adds one new system: constructing and spawning a
moving actor.

**Time:** ~30 minutes.

---

## The projectile

Make an `AProjectile` actor with:

- A sphere `UStaticMeshComponent` as its root, scaled small.
- A `UProjectileMovementComponent` that supplies velocity and collision-aware
  movement. Set `InitialSpeed` and `MaxSpeed` to nonzero values.
- `InitialLifeSpan = 3.f` so missed shots clean themselves up.

The component exists independently of its visual asset. As in Chapter 1b,
create `BP_Projectile` from the C++ class and assign the sphere mesh in
Blueprint defaults rather than hard-coding a content path.

`UProjectileMovementComponent` updates an actor every frame without requiring
you to enable `Tick`. It uses the actor's initial rotation to establish its
forward velocity.

---

## Spawning from Fire

`IA_Fire` is already mapped and bound to the empty `Fire` handler from Chapter
3a. Fill that handler in:

1. Start at the camera location plus its forward vector times `MuzzleOffset`.
2. Use the camera rotation, not the pawn rotation. They diverge as soon as the
   player looks up or down.
3. Spawn the configured `ProjectileClass` through the world.

Two details matter later:

**`FActorSpawnParameters`.** Set `Owner` and `Instigator` to the firing
character. Chapter 4 uses them to identify who dealt damage.

**Spawn collision handling.** The default may refuse to spawn an actor that
begins inside the player. Spawn in front of the camera and choose an explicit
`SpawnCollisionHandlingOverride` if needed.

Finally, assign `BP_Projectile` to `BP_LabCharacter.ProjectileClass`. The C++
property is only a slot; an empty slot gives `Fire` nothing to spawn.

Nothing damages anything yet. Projectiles can pass through the dummy. Collision
and damage belong to Chapter 4.

---

## Stuck?

<details>
<summary>Clicking does nothing</summary>

First confirm Chapter 3a still passes. Then check `ProjectileClass`. If the
mapping, binding, and class are present, log the Fire handler to separate an
input problem from a spawn problem.
</details>

<details>
<summary>Fire runs but no projectile appears</summary>

The spawn may be refused because it overlaps the player, or the projectile may
spawn inside the pawn and collide immediately. Move the spawn location farther
along the camera's forward vector or set the collision-handling override.
</details>

<details>
<summary>The projectile exists but does not move</summary>

Inspect its `UProjectileMovementComponent`. `InitialSpeed` and `MaxSpeed`
default to zero.
</details>

<details>
<summary>The projectile flies in the wrong direction</summary>

Use the camera's rotation and forward vector, not the pawn's. A first-person
camera can pitch independently of its body.
</details>

---

## Run the checks

Ask your assistant:

> **check my work**

Then [Chapter 4](../04-damage/), where the dummy starts to notice.

---

## What just happened

You separated input from the thing it creates. The character decides *when*
to fire; the projectile actor owns its own shape, movement, and lifetime. That
division lets Chapter 4 add collision and damage without making the player
class responsible for a projectile after it has been spawned.

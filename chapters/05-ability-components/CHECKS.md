# Checks — Chapter 5: ability components

*For the assistant. Three checks.*

**Do not attach the component for them.** Putting it on the dummy — and
seeing that `ATargetDummy` never changed to accommodate it — is the entire
lesson. If no dummy has one, say so and let them do it.

Setup: find a dummy with an ability component (any component whose
`get_class` contains "Ability"). `StartPIE`, wait ~6 seconds so a couple of
cooldowns elapse and shots have time to land, then read.

---

**1. The ability is a real, resolvable component.**

`get_class` on it returns something. It should derive from
`UActorComponent`, not `USceneComponent` — an ability has no position of its
own; the owning actor does. Reaching for `USceneComponent` drags in a
transform they don't want.

**2. It activated.**

`ActivationCount` > 0 on the component.

Zero after six seconds, two usual causes:

- `PrimaryComponentTick.bCanEverTick` wasn't set in the **component's**
  constructor. The actor's tick setting doesn't cover its components — this
  catches nearly everyone.
- `CanActivate` never returns true because the player is outside `Range`.

**3. The player took damage.**

`HitCount` > 0 on the `ALabCharacter` in the running world.

Activated but never landing means either the projectile isn't aimed at the
target, or it's colliding with the dummy that fired it. `Owner` and
`Instigator` on the spawn params, and ignore the owner in the hit handler —
every shooter ships that bug once.

---

## Worth looking at even when it passes

Does their component cast `GetOwner()` to `ATargetDummy`?

If so it works, and it's thrown away the reusability that was the whole point
— it can no longer be attached to a turret, a barrel, or the player. Worth
raising. The check can't catch it, but you can read for it.

## Then encourage the delegation

Offer to attach cannons to the other dummies with staggered cooldowns, then
inspect the result and report which dummies got what. Verifying an agent's
work through the same interface it used is a habit worth building.

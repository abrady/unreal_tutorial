# Checks — Chapter 4: hits, damage, floating numbers

*For the assistant. Three checks.*

Setup: place a projectile just in front of a dummy and let PIE do the rest.
Read the dummy's location, then spawn an `AProjectile` about 250 units back
along **-X** from it, at the same height. When play starts the projectile's
own movement component closes the gap.

**Don't take a "before" health reading.** The hit can land during PIE warmup,
so a baseline sampled after play starts may already be stale. Compare against
`MaxHealth` instead.

Give it ~2 seconds after `StartPIE`, then read the PIE dummy. Remove the
probe projectile afterwards.

---

**1. The dummy lost health.**

`Health` < `MaxHealth`.

Still at full means the hit never registered. Work the collision matrix from
**both** ends — the projectile and the dummy each need a response that
produces an event, and *Simulation Generates Hit Events* must be on. Both
sides have to agree; checking only one is the classic mistake.

If the projectile visibly stops but nothing happens, `ApplyDamage` probably
got a null actor, or `TakeDamage` isn't actually overridden.

**2. The hit was recorded.**

`HitCount` ≥ 1.

Health changed but nothing recorded means `TakeDamage` isn't appending to the
damage history — the `UDamageHistory` from Chapter 2, which is what the damage
numbers are drawn from.

**3. The totals agree.**

`DamageTaken` ≈ `MaxHealth` − `Health`, within 1.

A mismatch usually means damage applied twice: both a hit *and* an overlap
fired, or the projectile struck again before being destroyed.

---

## What you can't check

The floating damage number itself. `DrawDebugString` leaves nothing you can
query, so you'll have to take their word for it — or better, ask them to
describe what they saw. If they can't, they probably haven't run it.

# Checks — Chapter 3b: projectiles

*For the assistant. Five checks.*

**State the tooling boundary first:** MCP cannot press the learner's fire key.
Verify the projectile independently, then ask the learner to click for the
end-to-end check.

---

**1. The projectile classes exist.**

Find the native class:

```text
search_subclasses({"base_class":{"refPath":"/Script/Engine.Actor"},
                   "class_name":"Projectile"})
```

Confirm `BP_Projectile` derives from it.

**2. The projectile is assigned to the character.**

Read `ProjectileClass` from `BP_LabCharacter`. It must point to
`BP_Projectile_C`; otherwise `Fire` has nothing to spawn.

**3. The projectile has the required components and defaults.**

Inspect a probe projectile and confirm:

- Its root is a `UStaticMeshComponent`.
- It owns a `UProjectileMovementComponent`.
- `InitialSpeed` and `MaxSpeed` are nonzero.
- `InitialLifeSpan` is approximately three seconds.

**4. The projectile actually flies.**

While PIE is stopped, spawn one high and clear of geometry — around
`(-1200, 0, 900)` works in `Lvl_FirstRoom`. Capture the returned ref path.
Then start PIE with zero warmup, find the PIE copy, and sample its transform
twice roughly 0.25 seconds apart. It must move at least 100 units.

If it vanishes between samples, it flew away, hit something, or reached its
lifespan; that still proves it moved. Remove the editor-world probe afterward.

**5. Clicking exercises the integrated path.**

Start PIE and ask the learner to click once. Find the resulting projectile and
confirm its `Owner` and `Instigator` identify the possessed character. Be
explicit that the learner supplied the input; MCP did not synthesize it.

Stop PIE when finished.

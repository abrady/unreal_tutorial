# Checks — Chapter 3: you, and you can shoot

*For the assistant. Five checks.*

**A limitation to be upfront about:** the MCP cannot simulate input. There is
no way to press a key or trigger an InputAction, so you **cannot** test
"press fire → projectile appears." Verify the wiring and the projectile
separately, and tell the learner that's what you're doing. Finding the
tooling's edges is part of the lab.

---

**1. The player is possessed.**

`StartPIE`, then `find_actors` for `/Script/CombatGym.LabCharacter`. At least one.

None means the GameMode's Default Pawn Class isn't pointing at it, or the
level has no PlayerStart.

**2. The input assets are assigned.**

Read `DefaultMappingContext`, `MoveAction`, `FireAction` off the pawn. All
three non-null.

Enhanced Input fails *silently*: with no mapping context the bindings never
fire and nothing warns you. This check exists to make that loud.

**3. The projectile class exists.**

```
search_subclasses({"base_class": {"refPath": "/Script/Engine.Actor"},
                   "class_name": "Projectile"})
```

**4. The projectile is assigned to the character.**

`ProjectileClass` is set on the pawn. Otherwise `Fire` has nothing to spawn.

**5. The projectile actually flies.**

Spawn one high and clear of geometry — around `(-1200, 0, 900)` works in
`Lvl_FirstRoom` — so it isn't destroyed on impact before you can sample it
twice.

```
StartPIE (warmup 0)
get_actor_transform  → note location
wait ~0.25s
get_actor_transform  → must have moved ≥100 units
```

If it vanished between samples, it flew off or hit something — either way it
moved, so that passes.

If it's stationary, `InitialSpeed` and `MaxSpeed` on the
`UProjectileMovementComponent` both default to **0**. That's the usual cause.

Remove the probe projectile afterwards.

---

## Then encourage the delegation

They've wired one input action by hand. Offer to add `IA_Reload` and
`IA_Dash` the same way — assets, mappings, and bindings.

You **can** create these: `DataAssetTools.create` with
`/Script/EnhancedInput.InputAction`, since it derives from `UDataAsset`.

If some part of it doesn't work, say so plainly. A learner who has watched
you hit a wall can answer "can the MCP do X?" for a partner later. One who
assumes can't.

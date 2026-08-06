# Checks — Chapter 1: the dummy

*For the assistant. All four must hold. Verify each against the running
editor — don't read their code and form an opinion.*

Setup for checks 2–4: spawn an `ATargetDummy` into the **editor** world, then
`StartPIE`, then `find_actors` to get the PIE copy. Remove anything you
spawned when you're done.

---

**1. The class exists.**

```
search_subclasses({"base_class": {"refPath": "/Script/Engine.Actor"},
                   "class_name": "TargetDummy"})
```

Empty means it isn't compiled in. Either they haven't written it, or they
haven't rebuilt — adding a new `UCLASS` needs a full rebuild with the editor
closed, and Live Coding can't do it.

**2. It has a body and a head.**

`get_components` on the PIE instance → at least **two** whose `get_class`
contains `MeshComponent`.

> The component's refPath is its *name* (`...TargetDummy_0.Body`), not its
> type. You have to call `get_class` on each one.

If there's only one, they've made a single-component actor and missed the
attachment half of the chapter.

**3. The head is attached to the body.**

`get_parent_component` on the components → at least one returns another
component rather than null.

If everything is parentless, they created two components but never called
`SetupAttachment`. Worth showing them: move the actor and the head stays
behind.

**4. It rotates.**

```
get_actor_transform → note rotation.yaw
wait ~1 second
get_actor_transform → yaw must have changed by ≥5°
```

This is the check that separates "compiles" from "works". Two usual causes
when it fails:

- `PrimaryActorTick.bCanEverTick = true` was never set in the constructor
- `Tick` doesn't actually apply a rotation

A third, subtler one: they rotated the *mesh component* instead of the actor,
which spins the head on its neck and leaves the body still.

---

## Then encourage the delegation

Once it's green, offer to place four more dummies in a firing line. They've
built one by hand; repeating it teaches nothing. That's yours.

Note whether it works, and tell them if it doesn't — finding the tooling's
edges is part of the point.

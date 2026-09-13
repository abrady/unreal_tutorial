# Checks — Chapter 2: health, the CDO, and the collector

*For the assistant. Four checks across two lessons. The last one is
**expected to fail** on their first attempt — that's the exercise, not a bug.*

Setup: you need **two** dummies in the editor world — one at defaults, and
one with `MaxHealth` overridden. Create the second yourself:

```
add_to_scene_from_class  → a second ATargetDummy
set_properties           → {"instance": <it>, "values": "{\"MaxHealth\": 250}"}
```

> `values` must be a JSON **string**. Passing an object returns `false`
> silently. And this only works in a saved level, not an unsaved temp map.

Then `StartPIE` and read the PIE copies. Remove the probe dummy afterwards.

---

## Part A — the CDO

**1. Health starts at full.**

Every dummy: `Health` == its own `MaxHealth`.

If `Health` is 0, they declared it but never assigned it anywhere that runs
per instance.

**2. Health respects the per-instance override.**

The dummy whose `MaxHealth` is 250 must have started at `Health` 250.

**This is the whole lesson.** If it reads 100, they set `Health = MaxHealth`
in the constructor. Per-instance overrides are applied *after* the constructor
runs, so it read the class default and never saw this dummy's value.

Note that with every dummy left at defaults, both approaches look identical —
which is exactly why you create the overridden one.

## Part B — garbage collection

**3. The untracked history was collected.**

`bBadHistoryCollected` is true. The bad history is held only by a plain raw
pointer plus a weak observer. Once that observer becomes invalid, it proves a
collection actually ran and found no reflected strong reference.

`ForceGarbageCollection(true)` is a *request*, serviced at the next safe
point. Do not assume the first Tick is late enough. Poll the bad weak observer
until it becomes invalid, or hook
`FCoreUObjectDelegates::GetPostGarbageCollect()`.

**4. The tracked history survived the same collection.**

`bGoodHistorySurvived` is true, recorded only after
`bBadHistoryCollected` became true. The good history is held by a
`UPROPERTY()` `TObjectPtr`, and its weak observer must still be valid.

**Expected to fail first time.** Have them build the bad case before adding
the good comparison. The collector sees no reflected reference and frees the
bad object while its raw pointer happily keeps pointing at freed memory. No
compiler error, no warning.

Pause here and make the consequence explicit: collection does **not** null an
untracked raw pointer. A non-null check on `BadDamageHistory` can still pass,
but dereferencing it is unsafe. The weak observer is the only member they
should inspect after collection. Make sure the learner can explain that
distinction before moving on.

The comparison is `UPROPERTY()` on the good member. Let them find it if they
can; the contrast *is* the teaching. If they're stuck, point at the reflection
graph: the GC only traverses pointers it can see, and `UPROPERTY` is what
makes a strong pointer visible.

---

If a property comes back unreadable, that's its own signal — plain C++
members aren't visible to reflection, which is the same lesson arriving from
a different direction.

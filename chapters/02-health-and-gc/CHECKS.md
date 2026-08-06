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

**3. A collection actually ran.**

`bCollectionRan` is true. Without it the survival check below means nothing.

`ForceGarbageCollection(true)` is a *request*, serviced at the next safe
point — they need to read the result a tick later, or hook
`FCoreUObjectDelegates::GetPostGarbageCollect()`.

**4. The damage history survived it.**

`bHistorySurvived` is true.

**Expected to fail first time.** They'll have stored the history in a plain
pointer, the collector saw no references, and freed it — while their pointer
happily kept pointing at freed memory. No compiler error, no warning.

The fix is `UPROPERTY()` on the member. Let them find it if they can; the
failure *is* the teaching. If they're stuck, point at the reflection graph:
the GC only traverses pointers it can see, and `UPROPERTY` is what makes a
pointer visible.

---

If a property comes back unreadable, that's its own signal — plain C++
members aren't visible to reflection, which is the same lesson arriving from
a different direction.

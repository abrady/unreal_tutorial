# Chapter 2 — Health, the CDO, and the collector

**Goal:** give the dummy something to lose, and find out the hard way how
Unreal objects are actually born and destroyed.

This is the chapter that matters. Everything else in the lab is Unreal
knowledge you'd pick up eventually. This is the line between copying Unreal
tutorials and understanding Unreal, and every C++ engineer gets burned by it
exactly once.

Today you get burned on purpose, and your assistant will tell you — from
the running editor, not from reading your code — when you've actually fixed
it.

**Time:** ~45 minutes.

---

## What green looks like

Ask your assistant:

> **check my work**

Four checks. Two about *when* your code runs, two about *whether your objects
survive*.

---

## Part A — your constructor runs on an object that isn't your object

### Try it first

Give `ATargetDummy` health:

```cpp
UPROPERTY(EditAnywhere, Category = "Combat")
float MaxHealth = 100.f;

UPROPERTY(VisibleAnywhere, Category = "Combat")
float Health = 0.f;
```

Now: **where do you set `Health = MaxHealth`?**

Try the constructor. Put three dummies in the level. Change one dummy's
`MaxHealth` to 250 in the Details panel. Play.

Then try `BeginPlay` instead. Play again.

Write down what you expect before each run.

### What you'll find

Set in the **constructor**, `Health` is 100 on every dummy — including the
one you set to 250.

Set in **`BeginPlay`**, the edited dummy starts at 250.

### Why

At editor startup Unreal instantiates exactly one of every `UCLASS` — the
**Class Default Object**. Your constructor runs there first, before any level
loads.

The constructor then runs again for each instance. But here's the part that
bites: **per-instance overrides are applied *after* the constructor finishes.**
The order is:

```
1. construct from the CDO template     <- MaxHealth is still 100 here
2. apply per-instance overrides        <- MaxHealth becomes 250 now
3. PostInitializeComponents
4. BeginPlay                           <- first point you can trust it
```

So a constructor that reads `MaxHealth` reads the *default*, never the value
someone set in the level. Your 250-health dummy gets 100 health, and nothing
warns you.

### A warning about `GetWorld()`

You'll see advice that the constructor has no world. That's true **for the
CDO** — and misleading for instances, where `GetWorld()` often does return
something.

So the rule isn't "there's never a world." It's **"you can't rely on it."**
The same code path runs in both cases, and only one of them has a world.
Code that works when you spawn an actor at runtime can be null-dereferencing
at editor startup.

Try it if you like: record `GetWorld() != nullptr` in the constructor and see
what a spawned dummy reports. It may surprise you, and it's a good reminder
that "I tested it and it worked" is weaker evidence than it feels.

### What the constructor is for

```cpp
ATargetDummy::ATargetDummy()
{
    PrimaryActorTick.bCanEverTick = true;                      // ✓ config
    Body = CreateDefaultSubobject<UStaticMeshComponent>(...);  // ✓ structure
    MaxHealth = 100.f;                                         // ✓ a default

    Health = MaxHealth;                                        // ✗ reads the default
    GetWorld()->SpawnActor<AThing>();                          // ✗ may be null
}
```

**This is also why `CreateDefaultSubobject` only works in the constructor.**
It builds the CDO's component template, which instances are copied from.

### Where code goes

| Hook | When | Use it for |
|---|---|---|
| Constructor | CDO creation, editor startup | defaults, `CreateDefaultSubobject` |
| `OnConstruction` | every property edit in-editor | editor-time generated content |
| `PostInitializeComponents` | components exist, pre-BeginPlay | component wiring |
| `BeginPlay` | gameplay starts | **anything world- or instance-dependent** |
| `Tick` | every frame | continuous behaviour |

Default answer: `BeginPlay`.

To prove it to yourself, have the dummy record what `MaxHealth` looked like at
construction time versus at `BeginPlay`.

---

## Part B — the collector only sees what you tell it about

The dummy needs to remember what hit it. Chapter 4 will read that history to
draw damage numbers.

### Try it first

1. Make a `UDamageHistory : public UObject` that stores a `TArray<float>` of
   damage amounts.
2. In `BeginPlay`, create one with `NewObject<UDamageHistory>(this)` and store
   it in a **plain C++ pointer** — no `UPROPERTY()`.
3. Also keep a `TWeakObjectPtr<UDamageHistory>` to it. Weak pointers never
   keep anything alive; they just report honestly whether it's still there.
4. Force a collection: `GEngine->ForceGarbageCollection(true);`
5. Once the collection completes, set `bHistorySurvived` from
   `Observer.IsValid()`.

Run the checks. `test_damage_history_survives_gc` will **fail**. That's the
exercise.

### Then fix it

```cpp
UPROPERTY()
TObjectPtr<UDamageHistory> History;   // GC can see this — it survives

UDamageHistory* History;              // GC cannot — collected
```

Rebuild. Watch it pass.

### Why

Unreal's GC is mark-and-sweep over the **reflection graph**. `UPROPERTY()` is
what puts your pointer *into* that graph. Without it the collector sees no
references, concludes the object is garbage, and frees it.

Your raw pointer keeps its value. It now points at freed memory. No compiler
error, no warning, no assert — it works perfectly until a collection happens
to run, which in a shipped game means it works perfectly until it doesn't.

`TObjectPtr<T>` is the modern spelling of `T*` for tracked members. In
packaged builds it compiles down to a raw pointer; in the editor it adds
access tracking. Use it for `UPROPERTY` members and stop thinking about it.

**Not everything needs to be a `UPROPERTY`.** A local `UObject*` inside a
function is fine — you're not storing it. The rule is about *members that
outlive the current call*.

---

## Stuck?

<details>
<summary>Health is 0 when I play</summary>

You declared it but never assigned it anywhere that runs per-instance. That's
Part A's whole point — `BeginPlay`.
</details>

<details>
<summary>Both my constructor and BeginPlay values look the same</summary>

You probably haven't overridden `MaxHealth` on any instance. With every
dummy at the default, the two paths produce identical results and the
difference is invisible. Select one dummy in the level and change its
`MaxHealth` in the Details panel — that's what makes the CDO behaviour
observable.
</details>

<details>
<summary>The history survives even without UPROPERTY</summary>

Something else still references it, so the collector is right to keep it.
Check you passed `this` as the outer to `NewObject` and aren't also storing it
somewhere tracked. Also confirm the collection actually ran —
`ForceGarbageCollection(true)` is a *request*, serviced at the next safe
point. Read your flags a tick later, not immediately.
</details>

<details>
<summary>The editor crashes when I force GC</summary>

That's the lesson arriving loudly instead of quietly. Something dereferences
the collected object. Make sure nothing in `Tick` touches the untracked
pointer while you're in the broken state.
</details>

<details>
<summary>How do I run something after the collection?</summary>

`FCoreUObjectDelegates::GetPostGarbageCollect()` gives you a delegate that
fires when a collection finishes. Remember to unbind it in `EndPlay`.
</details>

---

## Run the checks

Ask your assistant:

> **check my work**

Then [Chapter 3](../03-shooting/), where you get to shoot at it.

---

## What just happened

Unreal `UObject`s aren't C++ objects with extra features. They're
participants in a reflected, garbage-collected object graph that happens to be
written in C++. Their construction is a template-copying step, not the start
of their life. Their lifetime is decided by reachability, not scope.

Nearly every baffling Unreal bug a strong C++ engineer hits in their first
month is one of these two things wearing a costume.

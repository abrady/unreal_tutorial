# Chapter 2 — Health, the CDO, and the collector

**Goal:** give the dummy something to lose, and find out the hard way how
Unreal objects are actually born and destroyed.

This is the chapter that matters. Everything else in the lab is Unreal
knowledge you'd pick up eventually. This is the line between copying Unreal
tutorials and understanding Unreal, and every C++ engineer gets burned by it
exactly once.

Today you get burned on purpose, with a grader telling you when you've
actually fixed it.

**Time:** ~45 minutes.

---

## What green looks like

```console
$ cd grader && .venv/bin/python -m pytest checks/ch02_health.py
```

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

Set in the **constructor**, `Health` is baked into the *Class Default Object*
and every dummy shares it. Your 250-health dummy still starts at 100, because
the constructor ran once, at editor startup, before your per-instance edit
existed.

Set in **`BeginPlay`**, each dummy reads its own `MaxHealth` and the edited
one starts at 250.

### Why

At editor startup Unreal instantiates exactly one of every `UCLASS` — the
**Class Default Object**. Your constructor runs *there*, once, long before any
level loads. Every instance you spawn is then **copied from the CDO** and
patched with whatever the level or Blueprint overrode.

So the constructor is for **defaults and structure**, never for anything that
depends on the world or on this particular instance:

```cpp
ATargetDummy::ATargetDummy()
{
    PrimaryActorTick.bCanEverTick = true;                      // ✓ config
    Body = CreateDefaultSubobject<UStaticMeshComponent>(...);  // ✓ structure
    MaxHealth = 100.f;                                         // ✓ a default

    Health = MaxHealth;                                        // ✗ too early
    GetWorld()->SpawnActor<AThing>();                          // ✗ no world
}
```

That last one won't reliably crash. It'll return null, do nothing, or corrupt
the CDO so every instance inherits the damage. Silent wrongness, which is
worse.

**This is also why `CreateDefaultSubobject` only works in the constructor.**
It builds the CDO's component template, which instances get copied from.

### Where code goes

| Hook | When | Use it for |
|---|---|---|
| Constructor | CDO creation, editor startup | defaults, `CreateDefaultSubobject` |
| `OnConstruction` | every property edit in-editor | editor-time generated content |
| `PostInitializeComponents` | components exist, pre-BeginPlay | component wiring |
| `BeginPlay` | gameplay starts | **anything world- or instance-dependent** |
| `Tick` | every frame | continuous behaviour |

Default answer: `BeginPlay`.

To prove it to yourself and the grader, record two flags —
`bHadWorldInConstructor` and `bHadWorldInBeginPlay`.

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
<summary>bHadWorldInConstructor comes back true</summary>

You're probably reading `GetWorld()` somewhere other than the constructor
body. Also note the CDO is built once per editor session — if you changed the
constructor and hot-patched with Live Coding, the existing CDO is stale.
Restart the editor.
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

```bash
cd grader && .venv/bin/python -m pytest checks/ch02_health.py -v
```

Then [Chapter 3](../03-shooting/), where you get to shoot at it.

---

## What just happened

Unreal `UObject`s aren't C++ objects with extra features. They're
participants in a reflected, garbage-collected object graph that happens to be
written in C++. Their construction is a template-copying step, not the start
of their life. Their lifetime is decided by reachability, not scope.

Nearly every baffling Unreal bug a strong C++ engineer hits in their first
month is one of these two things wearing a costume.

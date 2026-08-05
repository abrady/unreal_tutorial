# Chapter 2 — Lifecycle, GC, and the CDO

**Goal:** prove to yourself that Unreal's object model isn't the C++ object
model you already know.

This is the chapter that matters. Everything else in the lab is Unreal
trivia you'd pick up eventually. This one is the line between copying
Unreal tutorials and understanding Unreal, and every C++ engineer gets
burned by it exactly once.

Today you get burned on purpose, with a grader telling you when you've
actually fixed it.

**Time:** ~45 minutes.

---

## What green looks like

```console
$ cd grader && .venv/bin/python -m pytest checks/ch02_lifecycle.py
```

Four checks. Two about *when* your code runs, two about *whether your
objects survive*.

---

## Part A — your constructor runs on an object that isn't your object

### Try it first

Write an actor called `ALifecycleProbe` with four `bool` UPROPERTYs:

| Property | Set it to |
|---|---|
| `bHadWorldInConstructor` | whether `GetWorld()` was non-null **in the constructor** |
| `bHadWorldInBeginPlay` | whether `GetWorld()` was non-null **in BeginPlay** |

Before you run it, write down what you expect. Then run it.

### What you'll find

`bHadWorldInConstructor` is **false**. Every time.

At editor startup Unreal instantiates exactly one of every `UCLASS` — the
**Class Default Object**. Your constructor runs there, once, long before
any level exists. Every instance you ever spawn is then *copied from the
CDO* and patched up.

So in a constructor there is no world, no level, no other actors, and no
gameplay. This is legal:

```cpp
AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = true;              // config
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
}
```

This is not:

```cpp
AMyActor::AMyActor()
{
    GetWorld()->SpawnActor<AThing>();                  // no world yet
    UGameplayStatics::GetPlayerPawn(this, 0);          // no players yet
}
```

It won't reliably crash. It'll return null, do nothing, or corrupt the CDO
so that *every* instance inherits the damage. Silent wrongness is worse
than a crash, which is why this earns a whole chapter.

### Where code goes

| Hook | When | Use it for |
|---|---|---|
| Constructor | CDO creation, editor startup | defaults, `CreateDefaultSubobject` |
| `OnConstruction` | every property edit in-editor | editor-time generated content |
| `PostInitializeComponents` | components exist, before BeginPlay | component wiring |
| `BeginPlay` | gameplay starts | **anything touching the world** |
| `Tick` | every frame | continuous behavior |

Default answer: `BeginPlay`.

---

## Part B — the garbage collector only sees what you tell it about

### Try it first

Extend `ALifecycleProbe`:

1. In `BeginPlay`, create a `UObject` with `NewObject<UObject>(this)`.
2. Store it in a **plain C++ pointer** — no `UPROPERTY()`.
3. Also store a `TWeakObjectPtr<UObject>` to the same object. This is your
   observer; weak pointers don't keep anything alive, they just tell you
   truthfully whether it's still there.
4. Force a collection: `GEngine->ForceGarbageCollection(true);`
5. On the next tick, set `bTrackedObjectSurvived` from
   `WeakObserver.IsValid()`.

Run the checks. `test_tracked_object_survives_gc` will **fail**, and it's
supposed to.

### Then fix it

Add `UPROPERTY()` to the member. Rebuild. Watch it pass.

```cpp
UPROPERTY()
TObjectPtr<UObject> Tracked;      // GC can see this — object stays alive

UObject* Untracked;               // GC cannot — collected out from under you
```

### Why

Unreal's GC is a mark-and-sweep collector that walks the **reflection
graph**. `UPROPERTY()` is what puts your pointer *in* that graph. Without
it, the collector has no idea your pointer exists, sees no references to
the object, and frees it.

Your raw pointer keeps its value. It just points at freed memory now.
There's no compiler error, no warning, no assert — it works perfectly
until a collection happens to run, which in a real game means it works
perfectly until you ship.

`TObjectPtr<T>` is the modern spelling of `T*` for tracked members. In
packaged builds it compiles down to a raw pointer; in the editor it adds
access tracking. Use it for `UPROPERTY` members and don't think about it.

### Not everything needs to be a UPROPERTY

A local `UObject*` inside a function is fine — you're not storing it. The
rule is about **members that outlive the current call**.

---

## Stuck?

<details>
<summary>bHadWorldInConstructor is true, not false</summary>

You're probably setting it in the wrong place, or reading `GetWorld()`
somewhere other than the constructor body. Note the CDO is created once
per editor session — if you changed the constructor and used Live Coding,
the existing CDO may be stale. Restart the editor.
</details>

<details>
<summary>The object survives GC even without UPROPERTY</summary>

Something else is still referencing it, so the collector correctly keeps
it. Make sure you passed `this` as the outer to `NewObject` and aren't
also storing it somewhere tracked. Also make sure the collection actually
ran — `ForceGarbageCollection(true)` is a *request*; it happens at a safe
point, not on the spot. Read the flag a tick later, not immediately.
</details>

<details>
<summary>The editor crashes when I force GC</summary>

That's the lesson arriving loudly instead of quietly. Something is
dereferencing the collected object. Check that nothing in `Tick` touches
the untracked pointer while you're in the broken state.
</details>

<details>
<summary>How do I run something one tick later?</summary>

Simplest: a `bool` guard in `Tick`. There are timers and latent actions,
but don't reach for them here.
</details>

---

## Run the checks

```bash
cd grader && .venv/bin/python -m pytest checks/ch02_lifecycle.py -v
```

Then [Chapter 3](../03-framework-and-input/).

---

## What just happened

You learned that Unreal `UObject`s aren't C++ objects with extra features.
They're participants in a reflected, garbage-collected object graph that
happens to be written in C++. Their construction is a template-copying
step, not the start of their life, and their lifetime is decided by
reachability, not scope.

Nearly every confusing Unreal bug a strong C++ engineer hits in their
first month is one of these two things wearing a costume.

Next chapter is much easier.

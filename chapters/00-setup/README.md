# Before you start

Ten minute orientation covering some Unreal basics.

---

## What you're building

A combat gym. A target dummy you can shoot, damage numbers that pop off it,
and eventually a dummy that shoots back with an attack you can swap out like
a component — because that's what it will be.

You'll build it in C++, from a project that currently contains a floor, a
light, and a player who can't do anything yet.

## How this works

Each chapter follows the same shape:

1. You're given the task before the explanation. Try it first. You'll
   probably get partway and hit something confusing — that's the point, not a
   failure of the material. You remember things you had to fight for.
2. Then the concepts, aimed at whatever you just hit.
3. Then you check your work. Ask your assistant to check it; it verifies
   against the *running editor*, not by reading your code.
4. Hints are there when you want them, in collapsed sections, ordered
   from gentle to explicit.

You are not expected to finish in one sitting. Chapters stand alone. Two
chapters done properly beats five rushed, and coming back in three days is
normal — your assistant can tell you where you left off.

## AI and the MCP

Unreal 5.8 has an mcp built in and your llm of choice can talk to the running editor. It can start the game, inspect live actors mid-play, read real compiler errors, and tell you *why* something isn't working from actual state rather than guessing at your source.

During a chapter it explains, inspects, and diagnoses. Once your checks
pass, the restrictions lift entirely — compare against the reference, ask it
to tear your version apart.

Once you've done something enough, hand off the repetition.

---

## Unreal's C++:

### Unreal Header Tool (UHT)

Unreal builds in two stages:

```
your .h  →  UnrealHeaderTool  →  generated code  →  clang/MSVC  →  binary
                    ↑
            reads your macros
```

**UnrealHeaderTool (UHT)** scans your headers for macros like `UCLASS()` and
`UPROPERTY()`, and generates a pile of code you never see: type information,
serialisation, Blueprint bindings, and — importantly — the map the garbage
collector uses to find your pointers.

That's why:

- `#include "TargetDummy.generated.h"` must be the **last** include. UHT
  scans everything above it.
- A confusing error can come from stage one and never mention it.
- Changing a header means a full rebuild. Changing a `.cpp` body often
  doesn't.

**UnrealBuildTool (UBT)** is the thing that orchestrates all of this —
working out what needs rebuilding, running UHT, then invoking the real
compiler.

### What the macros actually mean

| | |
|---|---|
| `UCLASS()` | "Register this class with the reflection system." |
| `GENERATED_BODY()` | "Paste the generated code here." First line inside the class. |
| `UPROPERTY()` | "Track this member." Editor visibility, serialisation, **and GC.** |
| `UFUNCTION()` | "Expose this function." Blueprint, networking, delegates. |

The one that will bite you is `UPROPERTY()`. It's not decoration — it's how
the garbage collector learns your pointer exists. A member without it looks
fine, compiles fine, works fine, and then the object vanishes mid-session.
That's Chapter 2, and you'll do it on purpose.

### `A`, `U`, `F`, and other prefixes

Not style. The compiler doesn't care, but UHT does:

| Prefix | Means |
|---|---|
| `AActor` | An **A**ctor — something that can exist in a level |
| `UObject` | A managed object that isn't an actor (components, assets, data) |
| `FVector` | A plain struct. No reflection, no GC, cheap. |
| `IInteractable` | An interface |

Odd consequence worth knowing: the reflection system drops the prefix.
`ATargetDummy` in your code is `TargetDummy` in an asset path.

### There is one special instance of every class

This one has no equivalent in normal C++, and it's the thing most likely to
confuse you later, so it's worth knowing the name now.

At editor startup, Unreal creates **exactly one instance of every `UCLASS`**,
before any level loads. It's called the **Class Default Object** — the CDO.
It isn't in a level, nothing ticks it, and you'll never see it in the
viewport. It exists to be a *template*.

Every actor you place or spawn is **copied from the CDO** and then patched
with whatever that particular instance overrides.

```
     ATargetDummy CDO          created once, at startup
         │  copy
         ├─── dummy in the level      then: apply its overrides
         └─── dummy you spawned       then: apply its overrides
```

Two consequences you'll meet immediately:

- **Your constructor runs on the CDO**, at startup, before any world exists.
  It also runs per instance. Same code, two very different contexts.
- `CreateDefaultSubobject` only works in a constructor, because it's building
  the *template's* component layout for instances to copy.

That's as far as we'll go here. **Chapter 2 is where this stops being trivia**
— there's a specific way it will surprise you, and you'll find it by hitting
it rather than by being told.

### Garbage collection exists

`UObject`s are not `new`/`delete`. They're garbage collected, and the
collector finds your pointers by walking the reflection data UHT generated.

Which means a pointer without `UPROPERTY()` is **invisible to it**. The object
gets freed while your pointer still points at it. No error, no warning — it
works perfectly until a collection happens to run.

Also Chapter 2. Also on purpose.

## C++ and Blueprints

Unreal projects are written in **C++ and Blueprint**, and the split is a
convention worth learning on day one:

> **C++ owns behaviour. Blueprint owns data.**

The usual shape is a C++ base class with a Blueprint subclass on top:

```
AEnemyBase        (C++)        movement, health, attack logic
    └─ BP_Goblin  (Blueprint)   which mesh, which sounds, how much health
```

A programmer writes the class and exposes knobs with
`UPROPERTY(EditDefaultsOnly)`. A designer opens the Blueprint and turns them,
without a compile.

You'll do this at the end of Chapter 1. It matters for DRE specifically:
every partner project you open will look like this, and knowing where the
boundary sits tells you whether a bug lives in code or in data.

---

## A common iteration loop

| Change | What it needs | Cost |
|---|---|---|
| A `.cpp` body | **Live Coding** (`Ctrl+Alt+F11`) | seconds |
| A header, a new `UPROPERTY`, a new class | **Full rebuild, editor closed** | ~30–90s |

Note: Live Coding cannot add a property, change class layout, or add a file. When
it reports success and nothing changed, you needed a full rebuild.

Most of Chapters 1 and 2 are header changes, so expect the close-build-reopen
cycle. It's the single biggest time cost in the lab, and knowing which one you
need — before waiting on the wrong one — is most of what "being fast in
Unreal" means.

Your assistant can run the builds for you. Ask.

---

## What's already done

- The **project**, with a level, lighting, and a player character that has a
  camera and can take damage
- **`ATargetDummy` skeleton** — the class declaration exists, with `TODO`s
  where the interesting parts go. Setting up a `UCLASS` is ceremony; you don't
  need to practise it.
- **Input assets** for move, look, and fire
- A `CHECKS.md` beside each chapter, so the completion criteria are explicit
  rather than a matter of opinion

---

Next: Open [Chapter 1](../01-iteration-loop/README.md), or just tell your
assistant to start.

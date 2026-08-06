# Before you start

Ten minutes of orientation. You don't have to memorise any of it — it's here
so the first hour makes sense instead of feeling arbitrary.

---

## What you're building

A combat gym. A target dummy you can shoot, damage numbers that pop off it,
and eventually a dummy that shoots back with an attack you can swap out like
a component — because that's what it will be.

You'll build it in C++, from a project that currently contains a floor, a
light, and a player who can't do anything yet.

## How this works

Each chapter follows the same shape, and it's deliberate:

1. **You're given the task before the explanation.** Try it first. You'll
   probably get partway and hit something confusing — that's the point, not a
   failure of the material. You remember things you had to fight for.
2. **Then the concepts**, aimed at whatever you just hit.
3. **Then you check your work.** Ask your assistant to check it; it verifies
   against the *running editor*, not by reading your code.
4. **Hints are there when you want them**, in collapsed sections, ordered
   from gentle to explicit.

**You are not expected to finish in one sitting.** Chapters stand alone. Two
chapters done properly beats five rushed, and coming back in three days is
normal — your assistant can tell you where you left off.

## Your assistant, and the one rule

It's wired into the running editor. It can start the game, inspect live
actors mid-play, read real compiler errors, and tell you *why* something
isn't working from actual state rather than guessing at your source.

**It won't write your chapters.** Not because using AI is cheating — because
of a specific result. Bastani et al. (2024) gave ~1000 students unrestricted
GPT-4 or a guardrailed hint-giving tutor. The unrestricted group did **+48%**
on practice work and then **−17%** on an unassisted exam, ending up *worse
than students who never had AI at all*. The guardrailed group kept the gains.

So during a chapter it explains, inspects, and diagnoses. Once your checks
pass, the restrictions lift entirely — compare against the reference, ask it
to tear your version apart.

**The exception, and you should use it:** once you've done something *once*,
hand off the repetition. You wire one input action; it wires the next two.
You place one dummy; it places four more. That's the working pattern, not a
loophole.

---

## Unreal's C++ is not quite C++

This is the part that trips up experienced engineers, and it's worth
understanding before you write a line.

### There's a code generator in front of the compiler

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

---

## The iteration loop

You'll do this a lot, so know it now.

| Change | What it needs | Cost |
|---|---|---|
| A `.cpp` body | **Live Coding** (`Ctrl+Alt+F11`) | seconds |
| A header, a new `UPROPERTY`, a new class | **Full rebuild, editor closed** | ~30–90s |

Live Coding cannot add a property, change class layout, or add a file. When
it reports success and nothing changed, you needed a full rebuild.

Most of Chapters 1 and 2 are header changes, so expect the close-build-reopen
cycle. It's the single biggest time cost in the lab, and knowing which one you
need — before waiting on the wrong one — is most of what "being fast in
Unreal" means.

Your assistant can run the builds for you. Ask.

---

## What's already done for you

- The **project**, with a level, lighting, and a player character that has a
  camera and can take damage
- **`ATargetDummy` skeleton** — the class declaration exists, with `TODO`s
  where the interesting parts go. Setting up a `UCLASS` is ceremony; you don't
  need to practise it.
- **Input assets** for move, look, and fire
- A `CHECKS.md` beside each chapter, so the completion criteria are explicit
  rather than a matter of opinion

---

Ready. Open [Chapter 1](../01-iteration-loop/README.md), or just tell your
assistant to start.

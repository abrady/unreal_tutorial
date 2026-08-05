# Chapter 1 — The iteration loop, and your first Actor

**Goal:** an actor that spins.

That's deliberately trivial. This chapter is really about the compile loop —
the thing that wastes the most time for people new to Unreal, and the thing
you'll be fighting all morning if you don't get it straight now.

**Time:** ~45 minutes.

---

## What green looks like

```console
$ cd grader && .venv/bin/python -m pytest checks/ch01_actor.py
```

The checks spawn your actor into a running PIE session, sample its transform
twice, and assert it rotated. They also check it has a visible mesh.

---

## Try it first

Write a C++ actor class called `ARotatingPlate` that:

1. Has a **static mesh component** as its root, using any engine shape
   (`/Engine/BasicShapes/Cylinder` is a reasonable pick).
2. **Rotates continuously** around its Z axis while the game runs.

Don't read ahead. Try it. You know C++ and you know what a game loop is —
the only genuinely unfamiliar parts are Unreal's macros and where code is
allowed to go.

**You may ask your agent** to explain concepts, find the right API, or
decode a compiler error. **Don't ask it to write the class.** See
[`AGENTS.md`](../../AGENTS.md) for why that distinction matters.

---

## What you need to know

Four things that aren't guessable from C++ experience:

**Reflection macros.** `UCLASS()` above the class, `GENERATED_BODY()` as the
first thing inside it, `UPROPERTY()` above members you want Unreal to know
about. These feed a code generator that runs before the compiler.

**The generated header.** `#include "RotatingPlate.generated.h"` must be the
**last** include in your header. Everything above it gets scanned. Get the
order wrong and the error won't tell you that's the problem.

**Ticking is opt-in.** `PrimaryActorTick.bCanEverTick = true` in the
constructor, or `Tick` is never called.

**Components are created in the constructor**, with
`CreateDefaultSubobject<T>(TEXT("Name"))`. Not in `BeginPlay` — that's
Chapter 2's subject and you'll get there the hard way.

Useful APIs: `AActor::AddActorLocalRotation`, `FRotator`,
`UStaticMeshComponent::SetStaticMesh`, `SetRootComponent`,
`ConstructorHelpers::FObjectFinder`.

---

## Building

Your files go in `Lab01_FirstRoom/Source/Lab01/`.

**Adding a new file, or changing a header, means a full rebuild.** Close the
editor first — Unreal Build Tool tries a hot-reload build if the editor is
running, and fails with a confusing message about hyphens.

```bash
# from the engine root
Engine/Build/BatchFiles/Mac/Build.sh Lab01Editor Mac Development \
  -Project=<repo>/Lab01_FirstRoom/Lab01.uproject
```

Once the class exists and you're only editing `.cpp` bodies, **Live Coding**
(`Ctrl+Alt+F11`) patches the running editor in seconds. It cannot add a
`UPROPERTY`, change class layout, or add a file. When Live Coding says it
succeeded but nothing changed, you needed a full rebuild.

---

## Stuck?

<details>
<summary>My header won't compile and the error makes no sense</summary>

Check the include order. `.generated.h` last, always. Also confirm
`GENERATED_BODY()` is the first line inside the class body.
</details>

<details>
<summary>It compiles but Tick never fires</summary>

`PrimaryActorTick.bCanEverTick = true;` in the constructor. Ticking is off
by default.
</details>

<details>
<summary>It ticks but I can't see anything</summary>

Either no mesh was assigned, or the component isn't the root. Ask your agent
to inspect the spawned actor's components — that's exactly the kind of
question it should be answering for you.
</details>

<details>
<summary>How do I load a mesh asset from C++?</summary>

`ConstructorHelpers::FObjectFinder<UStaticMesh>` with the asset path, in the
constructor only. It asserts if used outside constructor scope — which is a
Chapter 2 lesson arriving early.
</details>

---

## Run the checks

```bash
cd grader && .venv/bin/python -m pytest checks/ch01_actor.py -v
```

All green means you're done. Go to
[Chapter 2](../02-lifecycle-and-gc/).

---

## Stretch: give your agent a new tool

Add this to a C++ class and rebuild:

```cpp
UFUNCTION(meta = (AICallable))
static float GetPlateSpin(AActor* Plate);
```

Restart your MCP client. That function is now a tool your agent can call —
it shows up alongside the 255 the engine already registers.

This is worth five minutes because it reframes what the agent is. It isn't a
fixed service you query; it's a surface you extend from inside your own code.
Partners will ask you about this.

---

## What just happened

You met Unreal's two-stage build: a code generator that reads your macros and
emits reflection data, then the actual C++ compiler. Most confusing early
Unreal errors come from stage one, and they rarely say so.

You also met the iteration loop you'll use all day — full rebuild for
structure, Live Coding for bodies. Knowing which one you need, before you
wait ninety seconds for the wrong one, is most of what "being fast in Unreal"
means.

Next chapter breaks something on purpose.

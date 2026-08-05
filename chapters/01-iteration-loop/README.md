# Chapter 1 — The iteration loop, and the dummy

**Goal:** a target dummy standing in an empty gym, turning slowly.

The dummy is deliberately simple. This chapter is really about two things:
the **compile loop**, which wastes more newcomer time than anything else, and
the **component model**, which is how every Unreal actor is assembled.

**Time:** ~45 minutes.

---

## What green looks like

```console
$ cd grader && .venv/bin/python -m pytest checks/ch01_dummy.py
```

The checks spawn your dummy into a running PIE session, verify it has a
two-part component tree with the head attached to the body, and sample its
rotation twice to confirm it's actually turning.

---

## Try it first

Write a C++ actor class called `ATargetDummy` that:

1. Has a **cylinder body** as its root — `/Engine/BasicShapes/Cylinder`.
2. Has a **sphere head** *attached to the body*, sitting on top of it.
3. **Rotates slowly** around Z while the game runs, so you can practise
   hitting a target that isn't standing still.

Don't read ahead. You know C++ and you know what a game loop is — the only
genuinely unfamiliar parts are Unreal's macros, where code is allowed to go,
and how components hang together.

**You may ask your agent** to explain concepts, find the right API, or decode
a compiler error. **Don't ask it to write the class.** See
[`AGENTS.md`](../../AGENTS.md) for why.

---

## What you need to know

### Reflection macros

`UCLASS()` above the class, `GENERATED_BODY()` as the first thing inside it,
`UPROPERTY()` above members Unreal should know about. These feed a code
generator — UnrealHeaderTool — that runs *before* the C++ compiler.

`#include "TargetDummy.generated.h"` must be the **last** include in your
header. Everything above it gets scanned. Get the order wrong and the error
won't mention includes.

### Components: how actors are actually built

This is the part worth slowing down for.

An `AActor` is mostly an empty container. Behaviour and geometry come from
**components** attached to it. Unreal's whole architecture is composition,
not deep inheritance hierarchies — a Character isn't a subclass of "thing
that moves," it's an actor that *has* a movement component.

Three levels matter:

| Class | Adds | Example |
|---|---|---|
| `UActorComponent` | behaviour, no position | your ability component in Ch 5 |
| `USceneComponent` | a transform, can be attached | scene roots, spring arms |
| `UPrimitiveComponent` | geometry and collision | `UStaticMeshComponent` |

**The root component defines the actor's transform.** Move the actor, the
root moves. Anything attached to the root follows it.

```cpp
Body = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Body"));
SetRootComponent(Body);

Head = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Head"));
Head->SetupAttachment(Body);              // in the constructor
Head->SetRelativeLocation(FVector(0, 0, 100));
```

Note `SetupAttachment` for constructor-time attachment, versus
`AttachToComponent` at runtime. Using the wrong one for the wrong phase is a
common early mistake.

Also note **`CreateDefaultSubobject` only works in the constructor.** That's
not arbitrary, and Chapter 2 explains exactly why.

### Ticking is opt-in

`PrimaryActorTick.bCanEverTick = true;` in the constructor, or `Tick` is never
called. No warning.

Useful APIs: `AActor::AddActorLocalRotation`, `FRotator`,
`UStaticMeshComponent::SetStaticMesh`, `ConstructorHelpers::FObjectFinder`.

---

## Building

Your files go in `Lab01_FirstRoom/Source/Lab01/`.

**Adding a new file, or changing a header, means a full rebuild with the
editor closed.** Unreal Build Tool attempts a hot-reload build if the editor
is running and fails with a confusing message about hyphens.

```bash
# from the engine root
Engine/Build/BatchFiles/Mac/Build.sh Lab01Editor Mac Development \
  -Project=<repo>/Lab01_FirstRoom/Lab01.uproject
```

Once the class exists and you're only editing `.cpp` bodies, **Live Coding**
(`Ctrl+Alt+F11`) patches the running editor in seconds. It cannot add a
`UPROPERTY`, change class layout, or add a file. When Live Coding reports
success but nothing changed, you needed a full rebuild.

---

## Stuck?

<details>
<summary>My header won't compile and the error makes no sense</summary>

Check the include order — `.generated.h` last, always. Then confirm
`GENERATED_BODY()` is the first line inside the class body.
</details>

<details>
<summary>The head is at the world origin, not on the dummy's shoulders</summary>

Either it was never attached, or you set world location instead of relative.
Attached components position themselves *relative to their parent*. Ask your
agent to inspect the spawned dummy's component tree — that's exactly the kind
of question live inspection answers well.
</details>

<details>
<summary>It compiles but never rotates</summary>

`PrimaryActorTick.bCanEverTick = true;` in the constructor. Ticking is off by
default.
</details>

<details>
<summary>The head rotates but the body doesn't, or vice versa</summary>

You're rotating a component instead of the actor. `AddActorLocalRotation`
moves the actor, which moves the root, which carries its children. Rotating
the head component alone spins the head on its neck.
</details>

<details>
<summary>How do I load a mesh asset from C++?</summary>

`ConstructorHelpers::FObjectFinder<UStaticMesh>` with the asset path, in the
constructor only. It asserts outside constructor scope — a Chapter 2 lesson
arriving early.
</details>

---

## Run the checks

```bash
cd grader && .venv/bin/python -m pytest checks/ch01_dummy.py -v
```

Green means you're done.

---

## Then delegate the rest

One dummy is a test case. A gym needs several.

You've built one by hand, so you know what it's made of. **Ask your agent to
place four more** in a firing line, spaced a few metres apart.

That's a level-editing operation, not a code one — exactly the kind of thing
the MCP should be good at and you shouldn't be doing by hand. Note whether it
works, and how it goes wrong if it doesn't.

This is the pattern for the whole lab: **do it once to understand it, then
hand off the repetition.**

On to [Chapter 2](../02-health-and-gc/).

---

## Stretch: give your agent a new tool

Add this to `ATargetDummy` and rebuild:

```cpp
UFUNCTION(meta = (AICallable))
static float GetDummySpinRate(AActor* Dummy);
```

Restart your MCP client. That function is now a tool your agent can call,
alongside the 255 the engine already registers.

Five minutes, and it reframes what the agent is: not a fixed service you
query, but a surface you extend from inside your own code. Partners will ask
you about this.

---

## What just happened

You met Unreal's two-stage build — a code generator that reads your macros and
emits reflection data, then the actual compiler. Most confusing early Unreal
errors come from stage one and rarely say so.

You also built your first component tree. Every actor you touch from here on
is a tree like this one, and "why isn't this thing where I put it" is almost
always a question about attachment.

Next chapter gives the dummy something to lose.

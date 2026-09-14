# Chapter 1a — The iteration loop, and the dummy

**Goal:** a target dummy standing in the gym, turning slowly.

The dummy is deliberately simple. This chapter is really about two things:
the **compile loop**, which wastes more newcomer time than anything else, and
the **component model**, which is how every Unreal actor is assembled.

The class shell is already written for you — you're filling in three `TODO`s.

**Time:** ~45 minutes.

> New to Unreal's C++? Read [Before you start](../00-setup/README.md) first.
> It covers UnrealBuildTool, what the macros do, and why the build works the
> way it does. Ten minutes, and the rest stops feeling arbitrary.

---

## Verifying your work

Ask your llm:

> check my work

The checks spawn your dummy into a running PIE session, verify it has a
two-part component tree with the head attached to the body, and sample its
rotation twice to confirm it's actually turning.

---

## Try it first

Open `CombatGym/Source/CombatGym/TargetDummy.h` and `.cpp`. The class shell
is already there — `UCLASS`, `GENERATED_BODY`, the `.generated.h` include.
That's ceremony, and you don't need to practise it.

What's left are three `TODO`s:

1. A **cylinder body** as the root — `/Engine/BasicShapes/Cylinder`
2. A **sphere head** *attached to the body*, sitting on top of it
3. **Slow rotation** around Z while the game runs, so you're shooting at
   something that isn't standing still

Don't read ahead. You know C++ and you know what a game loop is — the
unfamiliar parts are how components hang together and where Unreal lets you
put things.

**Ask your llm** to explain concepts, find the right API, or decode a
compiler error. **Don't ask it to write the class.** See
[`AGENTS.md`](../../AGENTS.md) for why.

---

## What you need to know

[Before you start](../00-setup/README.md) covered the macros and the build
loop. Two things specific to this chapter:

### Components: how actors are actually built

An `AActor` is mostly an empty container. Behaviour and geometry come from
**components** attached to it. Unreal's architecture is composition, not deep
inheritance — a Character isn't a subclass of "thing that moves," it's an
actor that *has* a movement component.

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
Head->SetupAttachment(Body);              // constructor-time attachment
Head->SetRelativeLocation(FVector(0, 0, 100));
```

Note `SetupAttachment` for constructor-time versus `AttachToComponent` at
runtime. Using the wrong one for the wrong phase is a common early mistake.

Also note **`CreateDefaultSubobject` only works in the constructor.** That's
not arbitrary, and Chapter 2 explains exactly why.

### Ticking is opt-in

`PrimaryActorTick.bCanEverTick = true;` in the constructor, or `Tick` is never
called. No warning.

Useful APIs: `AActor::AddActorLocalRotation`, `FRotator`,
`UStaticMeshComponent::SetStaticMesh`, `ConstructorHelpers::FObjectFinder`.

---

## Building

Your files go in `CombatGym/Source/CombatGym/`.

**Adding a new file, or changing a header, means a full rebuild with the
editor closed.** Unreal Build Tool attempts a hot-reload build if the editor
is running and fails with a confusing message about hyphens.

```bash
# from the engine root
Engine/Build/BatchFiles/Mac/Build.sh CombatGymEditor Mac Development \
  -Project=<repo>/CombatGym/CombatGym.uproject -WaitMutex
```

| Change | What it needs | Cost |
|---|---|---|
| Header, new `UPROPERTY`, new class/file | **Close editor → full build** (`Build.sh … -WaitMutex`) | ~30–90s |
| `.cpp` body only (e.g. `Tick`) | **Windows:** Live Coding (`Ctrl+Alt+F11`) patches in seconds. **Mac:** no Live Coding — use the Compile button (legacy Hot Reload, deprecated, *may* work for pure body changes like `Tick` but unreliable). Guaranteed path is **close → `Build.sh`** in ~3–7s (relink only). | seconds vs ~3–7s |

Live Coding (Windows, via Live++) and Hot Reload (Mac Compile button) cannot add a
`UPROPERTY`, change class layout, or add a file. When they report success but
nothing changed, you needed a full rebuild. On Mac, `Ctrl+Alt+F11` does nothing — use `Build.sh` or the Compile button.

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

Ask your llm:

> **check my work**

Green means you're done.

---

## Then delegate the rest

One dummy is a test case. A gym needs several.

You've built one by hand, so you know what it's made of. **Ask your llm
to place four more** in a firing line, spaced a few metres apart.

That's a level-editing operation, not a code one — exactly the kind of thing
the MCP should be good at and you shouldn't be doing by hand. Note whether it
works, and how it goes wrong if it doesn't.

This is the pattern for the whole lab: **do it once to understand it, then
hand off the repetition.**

---

Next: [Chapter 1b](../01b-blueprint-boundary/README.md) — what you just wrote
works, and no production project would ship it that way. Your mesh paths are
hardcoded into compiled code; next you'll move them into a Blueprint where a
designer can swap them without a programmer.

---

## What just happened

You met Unreal's two-stage build — a code generator that reads your macros and
emits reflection data, then the actual compiler. Most confusing early Unreal
errors come from stage one and rarely say so.

You also built your first component tree. Every actor you touch from here on
is a tree like this one, and "why isn't this thing where I put it" is almost
always a question about attachment.

Next: [Chapter 1b](../01b-blueprint-boundary/) hands your meshes to a
designer. Then Chapter 2 gives the dummy something to lose.

# Chapter 1b — C++ owns behaviour. Blueprint owns data.

**Goal:** get the hardcoded mesh paths out of your constructor and into a
Blueprint a designer can change without you.

Your dummy works. It also wouldn't ship: right now changing its mesh requires
a programmer and a rebuild, for something an artist should be able to swap in
ten seconds. This chapter moves the data out of your code. Short one.

**Time:** ~20 minutes.

**Starts from:** green Chapter 1a (a turning dummy with hardcoded meshes).

---

## What green looks like

Ask your llm:

> check my work

Three checks: no `FObjectFinder` left in the constructor, a `BP_TargetDummy`
Blueprint with meshes set, and the level holding the Blueprint instead of the
raw C++ actor.

---

## Try it first

Your constructor almost certainly contains something like this:

```cpp
static ConstructorHelpers::FObjectFinder<UStaticMesh> Cyl(
    TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
Body->SetStaticMesh(Cyl.Object);
```

That works, every Unreal tutorial does it, and **production code avoids it.**
You've hardcoded an asset path into compiled code.

### The pattern you'll see in every real project

**C++ owns behaviour. Blueprint owns data.**

The C++ class creates the component and says nothing about which asset it
renders:

```cpp
UPROPERTY(VisibleAnywhere, Category = "Components")
TObjectPtr<UStaticMeshComponent> Body;
```

Then a Blueprint *subclass* fills it in:

```
ATargetDummy          (C++)     tick, rotation, later: health and damage
    └─ BP_TargetDummy (Blueprint)  which meshes, what colour, spin rate
```

Nobody recompiles to retune a dummy. A designer opens `BP_TargetDummy`,
changes a value, hits play.

`VisibleAnywhere` makes the component reference visible but not replaceable.
The component's own editable settings — including **Static Mesh** — remain
configurable on the Blueprint class. C++ owns the component tree; Blueprint
owns the component defaults.

### Do it

1. Remove the `FObjectFinder` mesh loading and `SetStaticMesh` calls from the
   constructor, along with the now-unused `ConstructorHelpers` / `StaticMesh`
   includes. Keep the `Body` / `Head` components and their tree wiring.
2. Rebuild, then make a Blueprint class deriving from `ATargetDummy`, called
   `BP_TargetDummy`, in `Content/CombatGym/`.
3. In the Blueprint's Components panel, select inherited `Body` and set its
   **Static Mesh** to Cylinder. Select inherited `Head` and set its
   **Static Mesh** to Sphere.
4. **Compile and save** the Blueprint. Compile updates the in-memory class;
   Save is what makes those defaults survive an editor restart.
5. Put a `BP_TargetDummy` in the level, delete the old raw C++ actor, and save
   the level.

The component and mesh are different objects. The component is the place in
the world; its `StaticMesh` property references the shared geometry asset:

```text
Body (UStaticMeshComponent)
└─ Static Mesh → Cylinder (UStaticMesh asset)
```

The constructor now owns structure only:

```cpp
Body = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Body"));
SetRootComponent(Body);

Head = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Head"));
Head->SetupAttachment(Body);
Head->SetRelativeLocation(FVector(0, 0, 100));
```

This only changes a `.cpp` body, but the guaranteed path on every platform is
still a rebuild with the editor closed. On Windows, Live Coding can handle
this change; on Mac, the Compile button may work but remains unreliable.

---

## The one judgement that's yours

Your llm can create the Blueprint for you — that's asset plumbing, not
learning. But **you** decide where the C++ / Blueprint boundary belongs. C++
owns facts that define what the actor *is* — two attached components and its
turning behaviour. Blueprint owns choices a designer should make — which
meshes those components render.

You could add wrapper properties such as `BodyMesh`, but that duplicates a
setting the component already exposes and requires code to keep both values
in sync. Add a new property only when it creates a meaningful interface,
validation rule, or abstraction rather than another route to the same knob.

---

## Why this matters more than it looks

Open any partner's Unreal project and you'll find this everywhere —
`BP_Enemy` inheriting `AEnemyBase`, `BP_Rifle` inheriting `AWeaponBase`.
If you don't know where that boundary sits, you can't tell whether a bug
lives in code or in data, and that's the first question worth asking.

It also sets up Chapter 5. Part of the argument for ability components is
that a designer can attach one in a Blueprint without touching C++ at all.

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

You drew the line every real Unreal project is built on: behaviour in C++,
data in Blueprints. From here on, when something looks wrong, the first
question is which side of that line the bug lives on.

On to [Chapter 2](../02-health-and-gc/) — the dummy gets something to lose.

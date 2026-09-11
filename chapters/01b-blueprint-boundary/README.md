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

The C++ class declares a knob and says nothing about what goes in it:

```cpp
UPROPERTY(EditDefaultsOnly, Category = "Visuals")
TObjectPtr<UStaticMesh> BodyMesh;
```

Then a Blueprint *subclass* fills it in:

```
ATargetDummy          (C++)     tick, rotation, later: health and damage
    └─ BP_TargetDummy (Blueprint)  which meshes, what colour, spin rate
```

Nobody recompiles to retune a dummy. A designer opens `BP_TargetDummy`,
changes a value, hits play.

`EditDefaultsOnly` means "editable on the class, not per placed instance" —
which is what you want for something every dummy shares. `EditAnywhere`
would also let someone override it on one dummy in the level.

### Do it

1. Keep `Body`/`Head` components (`VisibleAnywhere`), **add** `BodyMesh`/`HeadMesh` asset slots (`EditDefaultsOnly`). Do not delete the components to add the meshes — they work together.
2. Make a Blueprint class deriving from `ATargetDummy`, called
   `BP_TargetDummy`, in `Content/CombatGym/`.
3. Set the body and head meshes on it.
4. Put a `BP_TargetDummy` in the level instead of the raw C++ actor.

Keep **both** pairs — they are different things. The components are the place
in the world; the meshes are the data to put there:

```cpp
// Places (created in the constructor)
UPROPERTY(VisibleAnywhere, Category="Components")
TObjectPtr<UStaticMeshComponent> Body;
UPROPERTY(VisibleAnywhere, Category="Components")
TObjectPtr<UStaticMeshComponent> Head;

// Asset slots (picked in the Blueprint defaults)
UPROPERTY(EditDefaultsOnly, Category="Visuals")
TObjectPtr<UStaticMesh> BodyMesh;
UPROPERTY(EditDefaultsOnly, Category="Visuals")
TObjectPtr<UStaticMesh> HeadMesh;
```

In the constructor, keep the tree wiring and make the assignment data-driven:

```cpp
Body = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Body"));
SetRootComponent(Body);
if (BodyMesh) Body->SetStaticMesh(BodyMesh);

Head = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Head"));
Head->SetupAttachment(Body);
Head->SetRelativeLocation(FVector(0, 0, 100));
if (HeadMesh) Head->SetStaticMesh(HeadMesh);
```

Adding a `UPROPERTY` changes class layout, so this needs a **full rebuild
with the editor closed** — same rule as Chapter 1a. Live Coding can't do it.

---

## The one judgement that's yours

Your llm can create the Blueprint for you — that's asset plumbing, not
learning. But **you** decide which properties to expose, because that's the
design judgement: every `EditDefaultsOnly` you add is a promise that someone
else can change it without you.

Don't ask it to pick the properties. That's the lesson.

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

// Every Unreal header starts this way. Read the comments once; you'll stop
// seeing them within a day.

// Standard include guard. Unreal uses #pragma once everywhere rather than
// #ifndef guards.
#pragma once

// A grab-bag of the core types you almost always need: FString, FVector,
// TArray, the logging macros, and several hundred other things. Unreal
// headers open with this by convention.
#include "CoreMinimal.h"

// The class we're deriving from. AActor is "a thing that can be placed in or
// spawned into a level."
#include "GameFramework/Actor.h"

// Needed for the BodyMesh/HeadMesh slots below: a UPROPERTY TObjectPtr
// member needs its element type's full declaration, not just a forward.
#include "Engine/StaticMesh.h"

// THIS MUST BE THE LAST INCLUDE. UnrealHeaderTool scans everything above it
// and generates the file being included here. Move it up and you'll get
// errors that don't mention includes and won't make sense.
//
// The name always matches the header: TargetDummy.h -> TargetDummy.generated.h
#include "TargetDummy.generated.h"

// Forward declaration. We only use UStaticMeshComponent* below, so the
// compiler needs to know the name exists but not its layout. This keeps
// header compile times down, which matters a lot in a codebase this size.
// The .cpp includes the real header.
class UStaticMeshComponent;

/**
 * A target dummy for the gym. You'll flesh this out in Chapter 1.
 *
 * The class boilerplate is done. What's left is the part worth doing: giving
 * it a body, hanging a head off that body, and making it turn.
 */

// UCLASS() registers this class with Unreal's reflection system. That
// registration is what buys you:
//   - the class showing up in the editor, and being placeable in a level
//   - serialisation (saving/loading), and property overrides per instance
//   - garbage collection knowing this type exists
//   - Blueprint being able to see or subclass it
//
// It takes optional specifiers, e.g. UCLASS(Abstract) or UCLASS(Blueprintable).
// Empty is the common case.
UCLASS()

// The 'A' prefix is not style - UnrealHeaderTool enforces it.
//   A...  an Actor (can exist in a level)
//   U...  a UObject that is not an Actor (components, assets, data)
//   F...  a plain struct - no reflection, no GC, cheap
//   I...  an interface
//
// Mildly confusing consequence: reflection drops the prefix. This class is
// "TargetDummy" in an asset path, never "ATargetDummy".
class ATargetDummy : public AActor
{
	// Pastes in the generated code for this class - constructors the engine
	// needs, the reflection registration, RTTI helpers.
	//
	// Must be the FIRST thing inside the class body. Note there's no
	// semicolon after it, because it expands to a block of declarations.
	//
	// It also resets access to 'private', which is why an explicit 'public:'
	// follows.
	GENERATED_BODY()

public:
	// Runs when the Class Default Object is built at editor startup, and
	// again for each instance. See Chapter 2 - the distinction matters more
	// than you'd expect.
	ATargetDummy();

	// Called every frame, but ONLY if you opt in. See the constructor.
	// 'override' is plain C++ and the engine builds with -Werror on missing
	// or mismatched overrides, so get the signature right.
	virtual void Tick(float DeltaSeconds) override;

	// Runs whenever the actor is (re)constructed: placed in a level, loaded
	// with the map, spawned at runtime, or nudged in the Details panel.
	//
	// Chapter 1b lives or dies on the timing here. The constructor runs BEFORE
	// a Blueprint subclass deserialises its defaults, so a constructor that
	// reads BodyMesh reads null and silently does nothing. OnConstruction runs
	// after, which makes it the first place the Blueprint's data is real.
	//
	// This is the C++ half of what a Construction Script does in Blueprint.
	virtual void OnConstruction(const FTransform& Transform) override;

	// UPROPERTY() tells the reflection system to track this member. It is not
	// decoration - it buys four separate things:
	//
	//   1. Editor visibility (per the specifiers below)
	//   2. Serialisation - the value survives save/load
	//   3. Blueprint access, if you ask for it
	//   4. GARBAGE COLLECTION. For pointer members, this is what stops the
	//      collector freeing the object out from under you. Chapter 2 is
	//      built around what happens when you forget.
	//
	// Common specifiers:
	//   EditAnywhere      editable on the class defaults AND on each instance
	//   EditDefaultsOnly  editable on the class only
	//   VisibleAnywhere   shown but read-only
	//   BlueprintReadWrite / BlueprintReadOnly   Blueprint access
	//   Category = "..."  which section of the Details panel it appears under
	UPROPERTY(EditAnywhere, Category = "Dummy")
	float DegreesPerSecond = 30.f;

protected:
	// Dry-run (Chapter 1 solution): the two-part component tree.
	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<UStaticMeshComponent> Body;

	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<UStaticMeshComponent> Head;

	// Chapter 1b: the asset slots. The components above are the places in
	// the world; these are the data to put there, picked in BP_TargetDummy
	// instead of hardcoded below. EditDefaultsOnly: shared by every dummy,
	// changeable without a programmer.
	UPROPERTY(EditDefaultsOnly, Category = "Visuals")
	TObjectPtr<UStaticMesh> BodyMesh;

	UPROPERTY(EditDefaultsOnly, Category = "Visuals")
	TObjectPtr<UStaticMesh> HeadMesh;
};

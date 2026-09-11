#pragma once

// A grab-bag of the core types you almost always need: FString, FVector,
// TArray, the logging macros, and several hundred other things. Unreal
// headers open with this by convention.
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"

// THIS MUST BE THE LAST INCLUDE. UnrealHeaderTool scans everything above it
// and generates the file being included here. Move it up and you'll get
// errors that don't mention includes and won't make sense.
//
// The name always matches the header: TargetDummy.h -> TargetDummy.generated.h
#include "TargetDummy.generated.h"

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
	GENERATED_BODY()

public:
	ATargetDummy();

	virtual void Tick(float DeltaSeconds) override;

	// UPROPERTY() tells the reflection system to track this member. 
	// it buys four separate things:
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
	// TODO (Chapter 1): declare two UStaticMeshComponent members here - a
	// Body and a Head - like this:
	//
	//     UPROPERTY(VisibleAnywhere, Category = "Components")
	//     TObjectPtr<UStaticMeshComponent> Body;
	//
	// TObjectPtr<T> is the modern spelling of T* for UPROPERTY members. In a
	// packaged build it compiles down to a raw pointer; in the editor it adds
	// access tracking. Use it for reflected members and don't think about it.
};

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
class UDamageHistory;

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

	// Chapter 2: per-instance setup happens here, not the constructor.
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	// Chapter 4: the damage entry point. ApplyDamage routes here.
	virtual float TakeDamage(
		float Damage,
		const FDamageEvent& DamageEvent,
		AController* EventInstigator,
		AActor* DamageCauser) override;

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

	// Chapter 2: per-instance editable. Overriding this in the level is the
	// CDO lesson - it lands AFTER the constructor, so Health is set in
	// BeginPlay rather than the constructor.
	UPROPERTY(EditAnywhere, Category = "Combat")
	float MaxHealth = 100.f;

	UPROPERTY(VisibleAnywhere, Category = "Combat")
	float Health = 0.f;

	// Chapter 4: how long damage numbers linger, and running totals mirrored
	// from History so they're readable via reflection.
	UPROPERTY(EditAnywhere, Category = "Combat")
	float DamageNumberDuration = 1.5f;

	UPROPERTY(VisibleAnywhere, Category = "Combat")
	float DamageTaken = 0.f;

	UPROPERTY(VisibleAnywhere, Category = "Combat")
	int32 HitCount = 0;

	// Chapter 2: did a collection actually happen? Without this, survival
	// means nothing.
	UPROPERTY(VisibleAnywhere, Category = "Lifecycle")
	bool bCollectionRan = false;

	// Chapter 2: did the damage history outlive the collection?
	UPROPERTY(VisibleAnywhere, Category = "Lifecycle")
	bool bHistorySurvived = false;

protected:
	// Chapter 2: runs after a garbage collection pass so we can observe what
	// survived it.
	void HandlePostGarbageCollect();
	// Dry-run (Chapter 1 solution): the two-part component tree.
	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<UStaticMeshComponent> Body;

	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<UStaticMeshComponent> Head;

	// Chapter 2: UPROPERTY puts this in the reflection graph, so the collector
	// can see it and won't free it out from under us.
	UPROPERTY()
	TObjectPtr<UDamageHistory> History;

private:
	// A weak pointer never keeps anything alive, so it reports honestly on
	// whether the History above actually survived.
	TWeakObjectPtr<UDamageHistory> Observer;

	FDelegateHandle PostGCHandle;
};

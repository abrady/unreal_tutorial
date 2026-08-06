#include "TargetDummy.h"

#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"

ATargetDummy::ATargetDummy()
{
	// TODO (Chapter 1): turn ticking on. It's opt-in — without this, Tick
	// below is never called and nothing warns you.

	// TODO (Chapter 1): create the Body with CreateDefaultSubobject and make
	// it the root, then create the Head and attach it to the Body with
	// SetupAttachment. Position the head above the body with
	// SetRelativeLocation — relative, because it's a child now.
	//
	// Both meshes come from engine primitives:
	//     /Engine/BasicShapes/Cylinder.Cylinder
	//     /Engine/BasicShapes/Sphere.Sphere
	//
	// Load them with ConstructorHelpers::FObjectFinder<UStaticMesh>, which
	// only works inside a constructor. Chapter 2 explains that too.
}

void ATargetDummy::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	// TODO (Chapter 1): rotate the dummy around Z by DegreesPerSecond.
	//
	// Rotate the *actor*, not a component — the actor carries its whole
	// component tree, so the head comes along. Rotating the head component
	// instead spins the head on its neck, which is a good thing to try once
	// so you can see the difference.
}

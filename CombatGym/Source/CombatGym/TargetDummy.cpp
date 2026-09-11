// The .cpp always includes its own header first. Unreal's build system
// enforces this (IWYU - "include what you use"), and it catches headers that
// don't stand on their own.
#include "TargetDummy.h"

#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"

// ConstructorHelpers::FObjectFinder - loads an asset by path. Constructor
// scope only; it asserts anywhere else.
#include "UObject/ConstructorHelpers.h"

ATargetDummy::ATargetDummy()
{
	// This constructor runs in two different situations. Once at editor
	// startup, on the Class Default Object - the single template instance
	// Unreal keeps for every UCLASS. And again for each actual dummy, which
	// is copied from that template.
	//
	// So this is the place for DEFAULTS and STRUCTURE. It is not the place
	// for anything depending on the world existing, or on this particular
	// instance's settings. Chapter 2 is where that distinction bites.

	// TODO (Chapter 1): turn ticking on.
	//
	//     PrimaryActorTick.bCanEverTick = true;
	//
	// Ticking is opt-in. Without this, Tick() below is simply never called -
	// no error, no warning, no log line. It just silently doesn't happen.

	// TODO (Chapter 1): build the component tree.
	//
	// An AActor is mostly an empty container. Geometry and behaviour come
	// from components attached to it.
	//
	// CreateDefaultSubobject<T>(TEXT("Name")) makes a component that's part
	// of this class's template. Constructor only - it's defining the CDO's
	// component layout, which instances get copied from.
	//
	// TEXT() wraps a literal as TCHAR. Unreal strings are wide, so a bare
	// "Body" is the wrong type.
	//
	// You want:
	//   - a Body (cylinder), made the root with SetRootComponent
	//   - a Head (sphere), attached to the Body with SetupAttachment,
	//     positioned above it with SetRelativeLocation
	//
	// "Relative" because once attached, the head's transform is expressed
	// relative to its parent, not to the world.
	//
	// SetupAttachment is the constructor-time version. AttachToComponent is
	// the runtime one. Using the wrong one for the phase you're in is a
	// classic early mistake.

	// TODO (Chapter 1): give the components their meshes.
	//
	//     static ConstructorHelpers::FObjectFinder<UStaticMesh> Mesh(
	//         TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	//     if (Mesh.Succeeded()) { Body->SetStaticMesh(Mesh.Object); }
	//
	// 'static' so the lookup happens once rather than on every construction.
	// Always check Succeeded() - a typo'd path fails at runtime, not compile
	// time.
	//
	// You'll also want /Engine/BasicShapes/Sphere.Sphere for the head.
	//
	// Fair warning: hardcoding asset paths in C++ is what tutorials do and
	// what shipping projects avoid. The end of Chapter 1 replaces this with
	// the pattern real projects use.
}

void ATargetDummy::Tick(float DeltaSeconds)
{
	// Call the parent implementation. Skipping Super:: on an engine override
	// is a reliable source of baffling behaviour.
	Super::Tick(DeltaSeconds);

	// DeltaSeconds is the time since the last frame. Multiply rates by it or
	// your dummy spins at a speed that depends on the frame rate.

	// TODO (Chapter 1): rotate the dummy around Z by DegreesPerSecond.
	//
	// AddActorLocalRotation takes an FRotator(Pitch, Yaw, Roll). Yaw is the
	// one that spins around the vertical axis.
	//
	// Rotate the *actor*, not a component. The actor carries its whole
	// component tree, so the head comes with it. Rotating the head component
	// instead spins the head on its neck - worth trying once, just to see
	// the difference.
}

// Dry-run Chapter 1 reference implementation (authored by Devmate to test the
// lab's check machinery on the CombatGym module).
#include "TargetDummy.h"

#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"

ATargetDummy::ATargetDummy()
{
	PrimaryActorTick.bCanEverTick = true;

	Body = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Body"));
	SetRootComponent(Body);

	Head = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Head"));
	Head->SetupAttachment(Body);
	Head->SetRelativeLocation(FVector(0.f, 0.f, 110.f));
	Head->SetRelativeScale3D(FVector(0.6f));

	// Chapter 1b: data-driven assignment. The tree wiring above stays; the
	// mesh choice moved to BP_TargetDummy. Nothing hardcoded to recompile.
	if (BodyMesh)
	{
		Body->SetStaticMesh(BodyMesh);
	}

	if (HeadMesh)
	{
		Head->SetStaticMesh(HeadMesh);
	}
}

void ATargetDummy::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	AddActorLocalRotation(FRotator(0.f, DegreesPerSecond * DeltaSeconds, 0.f));
}

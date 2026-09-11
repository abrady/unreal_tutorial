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

	// Note what is NOT here: any mention of which mesh. The constructor builds
	// the tree; BP_TargetDummy decides what goes in it. See OnConstruction.
}

void ATargetDummy::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);

	// Chapter 1b: data-driven assignment. By now the Blueprint's defaults have
	// been applied, so BodyMesh/HeadMesh hold whatever BP_TargetDummy set.
	//
	// Assigned unconditionally rather than behind an 'if (BodyMesh)' guard:
	// this re-runs every time someone edits the Blueprint, and clearing a slot
	// should clear the mesh rather than leave the old one stranded.
	Body->SetStaticMesh(BodyMesh);
	Head->SetStaticMesh(HeadMesh);
}

void ATargetDummy::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	AddActorLocalRotation(FRotator(0.f, DegreesPerSecond * DeltaSeconds, 0.f));
}

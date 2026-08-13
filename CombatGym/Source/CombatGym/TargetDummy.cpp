// Dry-run Chapter 1 reference implementation (authored by Devmate to test the
// lab's check machinery on the CombatGym module).
#include "TargetDummy.h"

#include "DamageHistory.h"
#include "Components/StaticMeshComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/Engine.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"
#include "UObject/UObjectGlobals.h"

ATargetDummy::ATargetDummy()
{
	PrimaryActorTick.bCanEverTick = true;

	Body = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Body"));
	SetRootComponent(Body);

	Head = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Head"));
	Head->SetupAttachment(Body);
	Head->SetRelativeLocation(FVector(0.f, 0.f, 110.f));
	Head->SetRelativeScale3D(FVector(0.6f));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(
		TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (CylinderMesh.Succeeded())
	{
		Body->SetStaticMesh(CylinderMesh.Object);
	}

	static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(
		TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	if (SphereMesh.Succeeded())
	{
		Head->SetStaticMesh(SphereMesh.Object);
	}
}

void ATargetDummy::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	AddActorLocalRotation(FRotator(0.f, DegreesPerSecond * DeltaSeconds, 0.f));
}

void ATargetDummy::BeginPlay()
{
	Super::BeginPlay();

	// Per instance, and late enough that the level's MaxHealth override has
	// been applied. Doing this in the constructor would read the CDO default.
	Health = MaxHealth;

	History = NewObject<UDamageHistory>(this);
	Observer = History;

	PostGCHandle = FCoreUObjectDelegates::GetPostGarbageCollect().AddUObject(
		this, &ATargetDummy::HandlePostGarbageCollect);

	if (GEngine)
	{
		// A request, not an immediate call - it runs at the next safe point.
		GEngine->ForceGarbageCollection(true);
	}
}

void ATargetDummy::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (PostGCHandle.IsValid())
	{
		FCoreUObjectDelegates::GetPostGarbageCollect().Remove(PostGCHandle);
		PostGCHandle.Reset();
	}

	Super::EndPlay(EndPlayReason);
}

void ATargetDummy::HandlePostGarbageCollect()
{
	bCollectionRan = true;
	bHistorySurvived = Observer.IsValid();
}

float ATargetDummy::TakeDamage(
	float Damage,
	const FDamageEvent& DamageEvent,
	AController* EventInstigator,
	AActor* DamageCauser)
{
	// Super applies engine-side modifiers. Skipping it means your damage
	// silently ignores anything the engine wants to say about it.
	const float Applied =
		Super::TakeDamage(Damage, DamageEvent, EventInstigator, DamageCauser);

	Health = FMath::Max(0.f, Health - Applied);

	if (History)
	{
		History->RecordHit(Applied);
		DamageTaken = History->TotalDamage();
		HitCount = History->HitCount();
	}

	// Debug visualisation isn't a toy - seeing what a combat system is doing
	// is most of what makes it tunable.
	DrawDebugString(
		GetWorld(),
		GetActorLocation() + FVector(0.f, 0.f, 160.f),
		FString::Printf(TEXT("-%.0f"), Applied),
		nullptr,
		Health > 0.f ? FColor::Yellow : FColor::Red,
		DamageNumberDuration);

	return Applied;
}

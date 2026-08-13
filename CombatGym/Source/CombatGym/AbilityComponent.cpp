#include "AbilityComponent.h"

#include "GameFramework/Actor.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"

UAbilityComponent::UAbilityComponent()
{
	// Opt-in, same as actors. The owner's tick setting doesn't cover this.
	PrimaryComponentTick.bCanEverTick = true;
}

void UAbilityComponent::BeginPlay()
{
	Super::BeginPlay();

	// Stagger the first shot so a row of dummies doesn't fire in lockstep.
	TimeSinceActivation = FMath::FRandRange(0.f, Cooldown);
}

void UAbilityComponent::TickComponent(
	float DeltaTime,
	ELevelTick TickType,
	FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	TimeSinceActivation += DeltaTime;

	if (CanActivate())
	{
		ActivateAbility();
		TimeSinceActivation = 0.f;
		++ActivationCount;
	}
}

bool UAbilityComponent::CanActivate() const
{
	if (!bEnabled || TimeSinceActivation < Cooldown)
	{
		return false;
	}

	const AActor* Target = GetTarget();
	const AActor* Owner = GetOwner();
	if (!Target || !Owner)
	{
		return false;
	}

	return FVector::Dist(Owner->GetActorLocation(), Target->GetActorLocation()) <= Range;
}

void UAbilityComponent::ActivateAbility()
{
	// Subclasses override. Nothing to do at the base.
}

AActor* UAbilityComponent::GetTarget() const
{
	// A shortcut that assumes single-player. In a real project you'd pass a
	// target in rather than reaching for the global.
	return UGameplayStatics::GetPlayerPawn(this, 0);
}

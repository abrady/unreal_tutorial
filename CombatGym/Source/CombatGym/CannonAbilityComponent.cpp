#include "CannonAbilityComponent.h"

#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "GameFramework/Pawn.h"
#include "Projectile.h"

UCannonAbilityComponent::UCannonAbilityComponent()
{
	Cooldown = 2.5f;

	// A sensible default so the cannon works the moment it's attached. Still
	// overridable in the editor.
	ProjectileClass = AProjectile::StaticClass();
}

void UCannonAbilityComponent::ActivateAbility()
{
	AActor* Owner = GetOwner();
	AActor* Target = GetTarget();
	if (!ProjectileClass || !Owner || !Target || !GetWorld())
	{
		return;
	}

	const FVector Origin = Owner->GetActorLocation() + FVector(0.f, 0.f, MuzzleHeight);
	const FVector ToTarget = (Target->GetActorLocation() - Origin).GetSafeNormal();
	const FVector Muzzle = Origin + ToTarget * MuzzleOffset;

	FActorSpawnParameters Params;
	Params.Owner = Owner;
	// So the projectile ignores the dummy that fired it.
	Params.Instigator = Cast<APawn>(Owner);
	Params.SpawnCollisionHandlingOverride =
		ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	GetWorld()->SpawnActor<AActor>(
		ProjectileClass, Muzzle, ToTarget.Rotation(), Params);
}

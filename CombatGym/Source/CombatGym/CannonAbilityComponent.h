#pragma once

#include "CoreMinimal.h"
#include "AbilityComponent.h"

#include "CannonAbilityComponent.generated.h"

/**
 * Chapter 5 reference solution: fires a projectile at the target.
 *
 * Attach this to a dummy and the dummy becomes dangerous. Detach it and it's
 * a punching bag again. ATargetDummy is never edited either way - that's the
 * whole argument for composition.
 */
UCLASS(Blueprintable, meta = (BlueprintSpawnableComponent))
class UCannonAbilityComponent : public UAbilityComponent
{
	GENERATED_BODY()

public:
	UCannonAbilityComponent();

	virtual void ActivateAbility() override;

	/** What to fire. Defaults to AProjectile; override in the editor. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cannon")
	TSubclassOf<AActor> ProjectileClass;

	/** How far in front of the owner the projectile appears. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cannon")
	float MuzzleOffset = 120.f;

	/** Vertical offset, so shots leave at roughly chest height. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cannon")
	float MuzzleHeight = 60.f;
};

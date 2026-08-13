#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"

#include "AbilityComponent.generated.h"

/**
 * Chapter 5 reference solution: the base every ability derives from.
 *
 * UActorComponent, not USceneComponent - an ability has no position of its
 * own. The owning actor does.
 *
 * Note what this class does NOT know: it never casts GetOwner() to
 * ATargetDummy. Keeping it working against a plain AActor is what lets the
 * same component drop onto a turret, a barrel, or the player unchanged.
 */
UCLASS(Abstract, Blueprintable, meta = (BlueprintSpawnableComponent))
class UAbilityComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UAbilityComponent();

	virtual void BeginPlay() override;
	virtual void TickComponent(
		float DeltaTime,
		ELevelTick TickType,
		FActorComponentTickFunction* ThisTickFunction) override;

	/** Seconds between activations. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ability",
		meta = (ClampMin = "0.1", UIMin = "0.1", UIMax = "10.0"))
	float Cooldown = 2.f;

	/** Beyond this distance from the target, the ability holds fire. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ability",
		meta = (ClampMin = "0.0"))
	float Range = 4000.f;

	/** Turn the ability off without detaching it. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ability")
	bool bEnabled = true;

	/** How many times this has fired. Handy for checks and for tuning. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Ability")
	int32 ActivationCount = 0;

	/** Subclasses put their actual behaviour here. */
	virtual void ActivateAbility();

	/** Off cooldown, enabled, and a target in range. */
	virtual bool CanActivate() const;

protected:
	/** Whoever this ability should act on. Single-player shortcut. */
	AActor* GetTarget() const;

	float TimeSinceActivation = 0.f;
};

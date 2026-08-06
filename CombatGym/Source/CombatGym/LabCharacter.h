#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"

#include "LabCharacter.generated.h"

class UCameraComponent;
class UInputAction;
class UInputMappingContext;
struct FInputActionValue;

/**
 * The player. Camera, movement, and health are done for you.
 *
 * Chapter 3 asks you to wire the input: add the mapping context in
 * BeginPlay, bind the actions in SetupPlayerInputComponent, and make Fire
 * spawn a projectile. Look for the TODO markers in the .cpp.
 */
UCLASS()
class ALabCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	ALabCharacter();

	virtual void BeginPlay() override;
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

	virtual float TakeDamage(
		float Damage,
		const FDamageEvent& DamageEvent,
		AController* EventInstigator,
		AActor* DamageCauser) override;

	// -- Input assets. Assign these on the Blueprint or in the level. -----

	/** Pushed in BeginPlay so the actions below can fire. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	TObjectPtr<UInputMappingContext> DefaultMappingContext;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	TObjectPtr<UInputAction> MoveAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	TObjectPtr<UInputAction> LookAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	TObjectPtr<UInputAction> FireAction;

	// -- Combat -----------------------------------------------------------

	/** What gets spawned when you fire. Chapter 3 asks you to write it. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Combat")
	TSubclassOf<AActor> ProjectileClass;

	/** How far in front of the camera projectiles appear. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Combat")
	float MuzzleOffset = 120.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Combat")
	float MaxHealth = 100.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat")
	float Health = 0.f;

	/** Total damage taken. Chapter 5 uses this to prove the dummies fought back. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat")
	float DamageTaken = 0.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat")
	int32 HitCount = 0;

protected:
	void Move(const FInputActionValue& Value);
	void Look(const FInputActionValue& Value);
	void Fire(const FInputActionValue& Value);

	/** Where projectiles come from. */
	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<UCameraComponent> Camera;
};

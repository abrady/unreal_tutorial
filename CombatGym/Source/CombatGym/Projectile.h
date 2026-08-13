#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"

#include "Projectile.generated.h"

class USphereComponent;
class UStaticMeshComponent;
class UProjectileMovementComponent;

/**
 * Chapter 3 reference solution: something to shoot.
 *
 * A sphere collider is the root and drives movement; the mesh is cosmetic.
 * Chapter 4 adds the damage on impact.
 */
UCLASS()
class AProjectile : public AActor
{
	GENERATED_BODY()

public:
	AProjectile();

	/** How much damage this deals on impact. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Combat")
	float Damage = 25.f;

protected:
	// Chapter 4: the hit event handler.
	UFUNCTION()
	void OnHit(
		UPrimitiveComponent* HitComponent,
		AActor* OtherActor,
		UPrimitiveComponent* OtherComponent,
		FVector NormalImpulse,
		const FHitResult& Hit);

	/** Root, and the thing that actually collides. */
	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<USphereComponent> Collision;

	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<UStaticMeshComponent> Mesh;

	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<UProjectileMovementComponent> Movement;
};

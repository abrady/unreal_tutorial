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

protected:
	/** Root, and the thing that actually collides. */
	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<USphereComponent> Collision;

	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<UStaticMeshComponent> Mesh;

	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<UProjectileMovementComponent> Movement;
};

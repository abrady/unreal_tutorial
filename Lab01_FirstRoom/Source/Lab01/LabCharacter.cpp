#include "LabCharacter.h"

#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"

ALabCharacter::ALabCharacter()
{
	PrimaryActorTick.bCanEverTick = false;

	Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
	Camera->SetupAttachment(GetCapsuleComponent());
	Camera->SetRelativeLocation(FVector(0.f, 0.f, 64.f));
	Camera->bUsePawnControlRotation = true;

	// First person: the body turns with the camera.
	bUseControllerRotationYaw = true;
	GetCharacterMovement()->bOrientRotationToMovement = false;
}

void ALabCharacter::BeginPlay()
{
	Super::BeginPlay();

	Health = MaxHealth;

	// TODO (Chapter 3): push DefaultMappingContext onto the local player's
	// UEnhancedInputLocalPlayerSubsystem. Without this, none of the actions
	// below will ever fire — and nothing will warn you.
}

void ALabCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	// TODO (Chapter 3): cast PlayerInputComponent to UEnhancedInputComponent
	// and bind MoveAction, LookAction and FireAction to the handlers below.
}

void ALabCharacter::Move(const FInputActionValue& Value)
{
	// TODO (Chapter 3): read Value as FVector2D and feed AddMovementInput.
}

void ALabCharacter::Look(const FInputActionValue& Value)
{
	// TODO (Chapter 3): read Value as FVector2D and drive
	// AddControllerYawInput / AddControllerPitchInput.
}

void ALabCharacter::Fire(const FInputActionValue& Value)
{
	// TODO (Chapter 3): spawn ProjectileClass at the camera, pointed down the
	// camera's forward vector. Set Owner and Instigator on the spawn params —
	// Chapter 4 needs them to work out who dealt the damage.
}

float ALabCharacter::TakeDamage(
	float Damage,
	const FDamageEvent& DamageEvent,
	AController* EventInstigator,
	AActor* DamageCauser)
{
	const float Applied =
		Super::TakeDamage(Damage, DamageEvent, EventInstigator, DamageCauser);

	Health = FMath::Max(0.f, Health - Applied);
	DamageTaken += Applied;
	++HitCount;

	return Applied;
}

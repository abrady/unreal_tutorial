#include "LabCharacter.h"

#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputAction.h"
#include "InputActionValue.h"
#include "InputMappingContext.h"
#include "Projectile.h"
#include "UObject/ConstructorHelpers.h"

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

	// Wire up the provided input assets and the projectile. In a shipping
	// project you'd more often do this on a Blueprint subclass than hard-code
	// the paths, but this keeps the reference self-contained.
	static ConstructorHelpers::FObjectFinder<UInputMappingContext> IMC(
		TEXT("/Game/CombatGym/Input/IMC_Default.IMC_Default"));
	if (IMC.Succeeded()) { DefaultMappingContext = IMC.Object; }

	static ConstructorHelpers::FObjectFinder<UInputAction> IaMove(
		TEXT("/Game/CombatGym/Input/IA_Move.IA_Move"));
	if (IaMove.Succeeded()) { MoveAction = IaMove.Object; }

	static ConstructorHelpers::FObjectFinder<UInputAction> IaLook(
		TEXT("/Game/CombatGym/Input/IA_Look.IA_Look"));
	if (IaLook.Succeeded()) { LookAction = IaLook.Object; }

	static ConstructorHelpers::FObjectFinder<UInputAction> IaFire(
		TEXT("/Game/CombatGym/Input/IA_Fire.IA_Fire"));
	if (IaFire.Succeeded()) { FireAction = IaFire.Object; }

	ProjectileClass = AProjectile::StaticClass();
}

void ALabCharacter::BeginPlay()
{
	Super::BeginPlay();

	Health = MaxHealth;

	// Without this, none of the actions below will ever fire - and nothing
	// warns you. Every link in this chain can be null.
	if (const APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (ULocalPlayer* LP = PC->GetLocalPlayer())
		{
			if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
					LP->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
			{
				if (DefaultMappingContext)
				{
					Subsystem->AddMappingContext(DefaultMappingContext, 0);
				}
			}
		}
	}
}

void ALabCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	UEnhancedInputComponent* Input = Cast<UEnhancedInputComponent>(PlayerInputComponent);
	if (!Input)
	{
		return;
	}

	if (MoveAction)
	{
		Input->BindAction(MoveAction, ETriggerEvent::Triggered, this, &ALabCharacter::Move);
	}
	if (LookAction)
	{
		Input->BindAction(LookAction, ETriggerEvent::Triggered, this, &ALabCharacter::Look);
	}
	if (FireAction)
	{
		Input->BindAction(FireAction, ETriggerEvent::Started, this, &ALabCharacter::Fire);
	}
}

void ALabCharacter::Move(const FInputActionValue& Value)
{
	const FVector2D Axis = Value.Get<FVector2D>();
	if (!Controller)
	{
		return;
	}

	const FRotator YawOnly(0.f, Controller->GetControlRotation().Yaw, 0.f);
	AddMovementInput(FRotationMatrix(YawOnly).GetUnitAxis(EAxis::X), Axis.Y);
	AddMovementInput(FRotationMatrix(YawOnly).GetUnitAxis(EAxis::Y), Axis.X);
}

void ALabCharacter::Look(const FInputActionValue& Value)
{
	const FVector2D Axis = Value.Get<FVector2D>();
	AddControllerYawInput(Axis.X);
	AddControllerPitchInput(Axis.Y);
}

void ALabCharacter::Fire(const FInputActionValue& Value)
{
	if (!ProjectileClass || !Camera)
	{
		return;
	}

	const FRotator Direction = Camera->GetComponentRotation();
	const FVector Muzzle =
		Camera->GetComponentLocation() + Direction.Vector() * MuzzleOffset;

	FActorSpawnParameters Params;
	// Chapter 4 needs these to work out who dealt the damage.
	Params.Owner = this;
	Params.Instigator = this;
	Params.SpawnCollisionHandlingOverride =
		ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	GetWorld()->SpawnActor<AActor>(ProjectileClass, Muzzle, Direction, Params);
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

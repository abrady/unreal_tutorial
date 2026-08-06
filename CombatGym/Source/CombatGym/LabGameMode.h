#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"

#include "LabGameMode.generated.h"

/**
 * Plumbing, given to you.
 *
 * Its whole job is to say which pawn the player controller possesses. That
 * is genuinely most of what a GameMode does in a small project - the rest
 * (rules, scoring, win conditions) is what you'd add as the game grows.
 *
 * Worth knowing: this class only exists on the server. Anything you put here
 * will not run on clients, which is exactly why game rules belong here and
 * not on the PlayerController.
 */
UCLASS()
class ALabGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	ALabGameMode();
};

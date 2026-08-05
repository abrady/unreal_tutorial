#include "LabGameMode.h"

#include "LabCharacter.h"

ALabGameMode::ALabGameMode()
{
	// The one line that matters: this is the pawn the player possesses.
	DefaultPawnClass = ALabCharacter::StaticClass();
}

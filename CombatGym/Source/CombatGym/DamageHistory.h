#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"

#include "DamageHistory.generated.h"

/**
 * Chapter 2 reference solution: a record of hits taken.
 *
 * Deliberately a bare UObject rather than a struct - the point of the
 * exercise is that UObjects are garbage collected, and only reachable
 * through the reflection graph.
 */
UCLASS()
class UDamageHistory : public UObject
{
	GENERATED_BODY()

public:
	void RecordHit(float Amount) { Hits.Add(Amount); }

	float TotalDamage() const
	{
		float Total = 0.f;
		for (const float Hit : Hits)
		{
			Total += Hit;
		}
		return Total;
	}

	int32 HitCount() const { return Hits.Num(); }

private:
	UPROPERTY()
	TArray<float> Hits;
};

"""Health, the CDO, and the collector.

Part A: the check places a dummy whose MaxHealth is overridden. That override
is applied *after* the constructor runs, so a constructor that sets
`Health = MaxHealth` reads the class default and gets it wrong.

Part B: the collector only sees pointers marked UPROPERTY. The damage-history
check is expected to fail on your first run — that's the exercise.
"""

from __future__ import annotations

from contextlib import contextmanager

import lab
from mcp_client import CheckFailed, UnrealMcp

ACTOR_CLASS = "ATargetDummy"

OVERRIDDEN_MAX_HEALTH = 250.0
SETTLE_SECONDS = 2.0


@contextmanager
def _dummies_in_pie(unreal: UnrealMcp):
    """One dummy at defaults, one with MaxHealth overridden, running in PIE.

    The override is created here rather than shipped in the level, because
    ATargetDummy doesn't exist until you write it in Chapter 1.
    """
    if not lab.class_exists(unreal, ACTOR_CLASS):
        raise CheckFailed(f"{ACTOR_CLASS} doesn't exist yet — finish Chapter 1 first.")

    lab.ensure_in_level(unreal, ACTOR_CLASS)

    probe = lab.spawn(unreal, ACTOR_CLASS, name="OverrideProbe", at=(600.0, 400.0, 100.0))
    if not probe:
        raise CheckFailed(f"Could not place a second {ACTOR_CLASS}.")
    if not lab.set_properties(unreal, probe, {"MaxHealth": OVERRIDDEN_MAX_HEALTH}):
        raise CheckFailed(
            "Could not set MaxHealth on the probe dummy.\n"
            "Is MaxHealth a UPROPERTY(EditAnywhere)?"
        )

    try:
        with lab.pie_session(unreal, warmup_seconds=SETTLE_SECONDS):
            found = lab.find_actors(unreal, ACTOR_CLASS)
            if not found:
                raise CheckFailed(f"No {ACTOR_CLASS} reached the running level.")
            yield found
    finally:
        lab.despawn(unreal, probe)


def _flag(unreal: UnrealMcp, actor, name: str) -> bool:
    value = lab.property_of(unreal, actor, name)
    if value is None:
        raise CheckFailed(
            f"{ACTOR_CLASS} has no readable property {name!r}.\n\n"
            "It needs to be a UPROPERTY() — plain C++ members aren't visible "
            "to reflection, which is the whole subject of Part B."
        )
    return bool(value)


def check_health_starts_at_full(unreal: UnrealMcp) -> None:
    with _dummies_in_pie(unreal) as dummies:
        for dummy in dummies:
            health = lab.property_of(unreal, dummy, "Health")
            max_health = lab.property_of(unreal, dummy, "MaxHealth")
            if health is None or max_health is None:
                raise CheckFailed("Add Health and MaxHealth as UPROPERTYs on the dummy.")
            if abs(float(health) - float(max_health)) > 0.01:
                raise CheckFailed(
                    f"A dummy has Health {health} but MaxHealth {max_health}.\n"
                    "If Health is 0, you never assigned it anywhere."
                )


def check_health_respects_per_instance_override(unreal: UnrealMcp) -> None:
    """The CDO lesson. This is the check that separates constructor from BeginPlay."""
    with _dummies_in_pie(unreal) as dummies:
        overridden = [
            d
            for d in dummies
            if abs(float(lab.property_of(unreal, d, "MaxHealth") or 0)
                   - OVERRIDDEN_MAX_HEALTH) < 0.01
        ]
        if not overridden:
            raise CheckFailed(
                f"No dummy with MaxHealth == {OVERRIDDEN_MAX_HEALTH} reached "
                "the running level.\n"
                "The check places one itself, so if it's missing, MaxHealth "
                "may not be an editable UPROPERTY."
            )

        for dummy in overridden:
            health = float(lab.property_of(unreal, dummy, "Health") or 0)
            if abs(health - OVERRIDDEN_MAX_HEALTH) > 0.01:
                raise CheckFailed(
                    f"This dummy's MaxHealth is {OVERRIDDEN_MAX_HEALTH:.0f} but "
                    f"its Health started at {health:.0f}.\n\n"
                    "You set Health in the constructor. Per-instance overrides "
                    "are applied *after* the constructor runs, so it read the "
                    "class default instead of this dummy's value.\n\n"
                    "Move the assignment to BeginPlay."
                )


def check_gc_actually_ran(unreal: UnrealMcp) -> None:
    with _dummies_in_pie(unreal) as dummies:
        if not _flag(unreal, dummies[0], "bCollectionRan"):
            raise CheckFailed(
                "No collection was observed, so the survival check below "
                "would be meaningless.\n\n"
                "ForceGarbageCollection(true) is a request, not an immediate "
                "call — it runs at the next safe point. Read your flags a tick "
                "later, or hook FCoreUObjectDelegates::GetPostGarbageCollect()."
            )


def check_damage_history_survives_gc(unreal: UnrealMcp) -> None:
    """Expected to fail until you add UPROPERTY(). That failure is the lesson."""
    with _dummies_in_pie(unreal) as dummies:
        if not _flag(unreal, dummies[0], "bHistorySurvived"):
            raise CheckFailed(
                "Your damage history was collected.\n\n"
                "The GC walks the reflection graph. An unmarked pointer isn't "
                "in that graph, so the collector saw no references and freed "
                "the object — while your pointer happily kept pointing at the "
                "freed memory.\n\n"
                "Add UPROPERTY() to the member and rebuild:\n"
                "    UPROPERTY()\n"
                "    TObjectPtr<UDamageHistory> History;"
            )

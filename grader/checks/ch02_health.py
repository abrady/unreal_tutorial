"""Chapter 2 — health, the CDO, and the collector.

Two lessons, four checks:

  Part A  your constructor runs on the Class Default Object, where there
          is no world and no per-instance data
  Part B  the collector only sees pointers marked UPROPERTY

test_damage_history_survives_gc is expected to FAIL on your first run.
That's the exercise, not a bug in the lab.
"""

from __future__ import annotations

import time

import pytest

import lab
from mcp_client import UnrealMcp

ACTOR_CLASS = "ATargetDummy"

# BeginPlay runs, then a collection is requested, then the result is read a
# tick later. Give all of that room to happen.
SETTLE_SECONDS = 2.0


@pytest.fixture
def dummy(pie: UnrealMcp):
    """A spawned dummy that has had time to run its lifecycle."""
    if not lab.class_exists(pie, ACTOR_CLASS):
        pytest.fail(
            f"{ACTOR_CLASS} doesn't exist yet — finish Chapter 1 first."
        )

    actor = lab.spawn(pie, ACTOR_CLASS)
    if not actor:
        pytest.fail(f"{ACTOR_CLASS} could not be spawned")

    time.sleep(SETTLE_SECONDS)
    return pie, actor


def _flag(unreal: UnrealMcp, actor, name: str) -> bool:
    value = lab.property_of(unreal, actor, name)
    if value is None:
        pytest.fail(
            f"{ACTOR_CLASS} has no readable property {name!r}.\n"
            "It needs to be a UPROPERTY() — plain C++ members aren't visible "
            "to reflection, which is the whole subject of Part B."
        )
    return bool(value)


# -- Part A: the CDO ------------------------------------------------------


def test_health_is_initialised_per_instance(dummy) -> None:
    """Health is set from MaxHealth, and set somewhere that runs per instance."""
    unreal, actor = dummy
    health = lab.property_of(unreal, actor, "Health")
    max_health = lab.property_of(unreal, actor, "MaxHealth")

    assert health is not None and max_health is not None, (
        "Add Health and MaxHealth as UPROPERTYs on the dummy."
    )
    assert float(health) == pytest.approx(float(max_health)), (
        f"Health is {health}, expected it to start at MaxHealth ({max_health}).\n"
        "If Health is 0, you declared it but never assigned it anywhere that "
        "runs per instance. If you set it in the constructor, that ran on the "
        "Class Default Object before this dummy existed — use BeginPlay."
    )


def test_constructor_had_no_world(dummy) -> None:
    """The constructor runs on the CDO, before any world exists."""
    unreal, actor = dummy
    assert not _flag(unreal, actor, "bHadWorldInConstructor"), (
        "GetWorld() returned something in your constructor.\n"
        "That shouldn't happen — the constructor runs on the Class Default "
        "Object at editor startup. Check you're recording it in the "
        "constructor body, and restart the editor so a stale CDO isn't reused."
    )


def test_begin_play_had_a_world(dummy) -> None:
    """BeginPlay runs in a live world — this is where gameplay code goes."""
    unreal, actor = dummy
    assert _flag(unreal, actor, "bHadWorldInBeginPlay"), (
        "GetWorld() was null in BeginPlay, which shouldn't be possible for a "
        "spawned actor. Make sure BeginPlay calls Super::BeginPlay()."
    )


# -- Part B: garbage collection -------------------------------------------


def test_damage_history_survives_gc(dummy) -> None:
    """A UPROPERTY reference keeps its object alive. A raw pointer doesn't.

    Expected to fail until you add UPROPERTY() to the member. That failure
    is the lesson.
    """
    unreal, actor = dummy

    assert _flag(unreal, actor, "bCollectionRan"), (
        "No collection was observed, so the survival check below would be "
        "meaningless.\n"
        "ForceGarbageCollection(true) is a request, not an immediate call — "
        "it runs at the next safe point. Read your flags a tick later, or "
        "hook FCoreUObjectDelegates::GetPostGarbageCollect()."
    )

    assert _flag(unreal, actor, "bHistorySurvived"), (
        "Your damage history was collected.\n\n"
        "The GC walks the reflection graph. An unmarked pointer isn't in that "
        "graph, so the collector saw no references and freed the object — "
        "while your pointer happily kept pointing at the freed memory.\n\n"
        "Add UPROPERTY() to the member and rebuild:\n"
        "    UPROPERTY()\n"
        "    TObjectPtr<UDamageHistory> History;"
    )

"""Chapter 2 — health, the CDO, and the collector.

Part A: the level ships a dummy whose MaxHealth is overridden per-instance.
That override is applied *after* the constructor runs, so a constructor that
sets `Health = MaxHealth` reads the class default and gets it wrong. Only a
BeginPlay assignment sees the real value.

Part B: the collector only sees pointers marked UPROPERTY.
test_damage_history_survives_gc is expected to FAIL on your first run —
that's the exercise, not a bug in the lab.
"""

from __future__ import annotations

import pytest

import lab
from mcp_client import UnrealMcp

ACTOR_CLASS = "ATargetDummy"

# Lvl_FirstRoom ships Dummy_2 with MaxHealth overridden to this. If the level
# changes, change this with it.
OVERRIDDEN_MAX_HEALTH = 250.0
SETTLE_SECONDS = 2.0


@pytest.fixture
def dummies(unreal: UnrealMcp):
    """Every dummy in a running PIE session, after BeginPlay has settled."""
    if not lab.class_exists(unreal, ACTOR_CLASS):
        pytest.fail(f"{ACTOR_CLASS} doesn't exist yet — finish Chapter 1 first.")

    lab.ensure_in_level(unreal, ACTOR_CLASS)

    with lab.pie_session(unreal, warmup_seconds=SETTLE_SECONDS):
        found = lab.find_actors(unreal, ACTOR_CLASS)
        if not found:
            pytest.fail(f"No {ACTOR_CLASS} reached the running level")
        yield unreal, found


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


def test_health_starts_at_full(dummies) -> None:
    """Every dummy begins at its own MaxHealth."""
    unreal, actors = dummies
    for actor in actors:
        health = lab.property_of(unreal, actor, "Health")
        max_health = lab.property_of(unreal, actor, "MaxHealth")
        assert health is not None and max_health is not None, (
            "Add Health and MaxHealth as UPROPERTYs on the dummy."
        )
        assert float(health) == pytest.approx(float(max_health)), (
            f"A dummy has Health {health} but MaxHealth {max_health}.\n"
            "If Health is 0 you never assigned it. See the next check for the "
            "more interesting failure."
        )


def test_health_respects_per_instance_override(dummies) -> None:
    """The dummy with an overridden MaxHealth starts at the overridden value.

    This is the CDO lesson, and it's the check that actually distinguishes a
    constructor assignment from a BeginPlay one. With every dummy left at the
    default both approaches look identical; the overridden one separates them.
    """
    unreal, actors = dummies

    overridden = [
        actor
        for actor in actors
        if float(lab.property_of(unreal, actor, "MaxHealth") or 0)
        == pytest.approx(OVERRIDDEN_MAX_HEALTH)
    ]
    assert overridden, (
        f"No dummy in the level has MaxHealth == {OVERRIDDEN_MAX_HEALTH}.\n"
        "Lvl_FirstRoom is supposed to ship one. If you rebuilt the level, "
        "select a dummy and override MaxHealth in the Details panel."
    )

    for actor in overridden:
        health = float(lab.property_of(unreal, actor, "Health") or 0)
        assert health == pytest.approx(OVERRIDDEN_MAX_HEALTH), (
            f"This dummy's MaxHealth is {OVERRIDDEN_MAX_HEALTH} but its Health "
            f"started at {health}.\n\n"
            "You set Health in the constructor. Per-instance overrides are "
            "applied *after* the constructor runs, so it read the class "
            "default instead of this dummy's value.\n\n"
            "Move the assignment to BeginPlay."
        )


# -- Part B: garbage collection -------------------------------------------


def test_gc_actually_ran(dummies) -> None:
    """A collection happened, so the survival check below means something."""
    unreal, actors = dummies
    assert _flag(unreal, actors[0], "bCollectionRan"), (
        "No collection was observed.\n"
        "ForceGarbageCollection(true) is a request, not an immediate call — it "
        "runs at the next safe point. Read your flags a tick later, or hook "
        "FCoreUObjectDelegates::GetPostGarbageCollect()."
    )


def test_damage_history_survives_gc(dummies) -> None:
    """A UPROPERTY reference keeps its object alive. A raw pointer doesn't.

    Expected to fail until you add UPROPERTY() to the member.
    """
    unreal, actors = dummies
    assert _flag(unreal, actors[0], "bHistorySurvived"), (
        "Your damage history was collected.\n\n"
        "The GC walks the reflection graph. An unmarked pointer isn't in that "
        "graph, so the collector saw no references and freed the object — "
        "while your pointer happily kept pointing at the freed memory.\n\n"
        "Add UPROPERTY() to the member and rebuild:\n"
        "    UPROPERTY()\n"
        "    TObjectPtr<UDamageHistory> History;"
    )

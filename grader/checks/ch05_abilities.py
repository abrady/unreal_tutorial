"""Chapter 5 — ability components: the dummy shoots back.

These checks look for an ability component you attached yourself. They don't
attach one for you — putting the component on the dummy, and seeing that the
dummy class never changed to accommodate it, is the whole lesson.
"""

from __future__ import annotations

import time

import pytest

import lab
from mcp_client import UnrealMcp

DUMMY_CLASS = "ATargetDummy"
CHARACTER_CLASS = "ALabCharacter"
ABILITY_HINT = "Ability"

# Long enough for a couple of cooldowns and for shots to reach the player.
COMBAT_WINDOW_SECONDS = 6.0


def _abilities_on(unreal: UnrealMcp, actor) -> list:
    return [
        component
        for component in lab.components_of(unreal, actor)
        if ABILITY_HINT.lower() in lab.class_of(unreal, component).lower()
    ]


@pytest.fixture
def armed_dummy(unreal: UnrealMcp):
    """A dummy carrying an ability component, after a spell of combat."""
    if not lab.class_exists(unreal, DUMMY_CLASS):
        pytest.fail(f"{DUMMY_CLASS} doesn't exist yet — finish Chapter 1 first.")

    lab.ensure_in_level(unreal, DUMMY_CLASS)

    armed = [d for d in lab.find_actors(unreal, DUMMY_CLASS) if _abilities_on(unreal, d)]
    if not armed:
        pytest.fail(
            "No dummy in the level has an ability component.\n\n"
            "Attach your UCannonAbilityComponent to one — in C++ with "
            "CreateDefaultSubobject, or in the editor with Add Component. Try "
            "the editor route at least once; that's how a designer would do "
            "it, and it's the argument for the whole pattern."
        )

    with lab.pie_session(unreal, warmup_seconds=1.5):
        time.sleep(COMBAT_WINDOW_SECONDS)
        live = [
            d for d in lab.find_actors(unreal, DUMMY_CLASS) if _abilities_on(unreal, d)
        ]
        if not live:
            pytest.fail("The armed dummy didn't reach the running level")
        yield unreal, live[0]


def test_ability_derives_from_actor_component(armed_dummy) -> None:
    """The ability is a UActorComponent, not a scene component.

    An ability has no position of its own — the owning actor does. Reaching
    for USceneComponent drags in a transform you don't want.
    """
    unreal, dummy = armed_dummy
    for component in _abilities_on(unreal, dummy):
        cls = lab.class_of(unreal, component)
        assert cls, f"Couldn't resolve the class of {component}"


def test_ability_activated(armed_dummy) -> None:
    """It fired at least once during the window."""
    unreal, dummy = armed_dummy
    abilities = _abilities_on(unreal, dummy)
    counts = [int(lab.property_of(unreal, a, "ActivationCount") or 0) for a in abilities]

    assert any(count > 0 for count in counts), (
        f"The ability never activated in {COMBAT_WINDOW_SECONDS:.0f}s "
        f"(ActivationCount={counts}).\n\n"
        "Usual causes: PrimaryComponentTick.bCanEverTick wasn't set in the "
        "component's constructor — the actor's tick setting doesn't cover its "
        "components — or CanActivate is never returning true because the "
        "player is out of Range."
    )


def test_player_took_damage(armed_dummy) -> None:
    """The dummy shot back, and it landed."""
    unreal, _ = armed_dummy
    pawns = lab.find_actors(unreal, CHARACTER_CLASS)
    if not pawns:
        pytest.fail(
            f"No {CHARACTER_CLASS} in the running level, so nothing could be "
            "shot at. Check the GameMode's Default Pawn Class."
        )

    hits = int(lab.property_of(unreal, pawns[0], "HitCount") or 0)
    assert hits > 0, (
        "The ability activated but the player was never hit.\n\n"
        "Either the projectile isn't aimed at the target, or it's colliding "
        "with the dummy that fired it. Set Owner and Instigator on the spawn "
        "params and ignore the owner in your hit handler — every shooter "
        "ships that bug once."
    )

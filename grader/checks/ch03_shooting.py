"""Chapter 3 — you, and you can shoot.

A note on what these checks can and can't do: the MCP exposes no way to
simulate a key press, so nothing here can literally pull your trigger.
Instead the checks verify the parts that are observable — that your character
is the pawn being possessed, that the input assets are wired up, and that
your projectile actually flies when it exists.

That's a real limitation of the tooling, not an oversight. Finding those
edges is part of what this lab is for.
"""

from __future__ import annotations

import time

import pytest

import lab
from mcp_client import UnrealMcp

CHARACTER_CLASS = "ALabCharacter"
PROJECTILE_CLASS = "AProjectile"

# A projectile at 2500 uu/s covers plenty of ground in this window.
FLIGHT_SAMPLE_SECONDS = 0.25
MIN_EXPECTED_TRAVEL = 100.0


@pytest.fixture
def player(unreal: UnrealMcp):
    """The possessed player pawn inside a running PIE session."""
    with lab.pie_session(unreal, warmup_seconds=1.5):
        pawns = lab.find_actors(unreal, CHARACTER_CLASS)
        if not pawns:
            pytest.fail(
                f"No {CHARACTER_CLASS} was possessed when play started.\n"
                "Check the GameMode's Default Pawn Class, and that the level "
                "has a PlayerStart."
            )
        yield unreal, pawns[0]


def test_player_is_possessed(player) -> None:
    """A LabCharacter exists in the running world."""
    unreal, pawn = player
    assert pawn, f"{CHARACTER_CLASS} did not spawn"


def test_input_assets_are_assigned(player) -> None:
    """The character has its mapping context and actions set.

    Enhanced Input fails silently: with no mapping context the bindings never
    fire and nothing warns you. This check makes that loud.
    """
    unreal, pawn = player
    missing = [
        name
        for name in ("DefaultMappingContext", "MoveAction", "FireAction")
        if not lab.property_of(unreal, pawn, name)
    ]
    assert not missing, (
        f"These input properties are unset on {CHARACTER_CLASS}: {missing}.\n"
        "Create the InputAction and InputMappingContext assets in the editor "
        "and assign them on the character. Without the mapping context, none "
        "of your bindings will ever fire."
    )


def test_projectile_class_exists(unreal: UnrealMcp) -> None:
    """You've written something to shoot."""
    assert lab.class_exists(unreal, PROJECTILE_CLASS), (
        f"The engine can't resolve {lab.class_path(PROJECTILE_CLASS)}.\n"
        "Create AProjectile and do a full rebuild with the editor closed."
    )


def test_projectile_is_assigned_to_the_character(player) -> None:
    """The character knows what to fire."""
    unreal, pawn = player
    assert lab.property_of(unreal, pawn, "ProjectileClass"), (
        "ProjectileClass is unset on the character, so Fire has nothing to "
        "spawn. Assign your projectile in the Details panel."
    )


def test_projectile_actually_flies(unreal: UnrealMcp) -> None:
    """A spawned projectile moves under its own power.

    Proves the UProjectileMovementComponent is present and configured — the
    most common failure is a projectile that spawns correctly and then sits
    still because InitialSpeed was never set.
    """
    if not lab.class_exists(unreal, PROJECTILE_CLASS):
        pytest.fail(f"{PROJECTILE_CLASS} doesn't exist yet")

    # High and clear of the geometry, so it isn't destroyed on impact before
    # we get a second sample.
    probe = lab.spawn(
        unreal, PROJECTILE_CLASS, name="FlightProbe", at=(-1200.0, 0.0, 900.0)
    )
    if not probe:
        pytest.fail(f"Could not place a {PROJECTILE_CLASS}")

    try:
        with lab.pie_session(unreal, warmup_seconds=0.0):
            shots = lab.find_actors(unreal, PROJECTILE_CLASS)
            if not shots:
                pytest.fail(
                    "A projectile was placed but none reached the running "
                    "level. If it's being destroyed instantly, check that it "
                    "isn't spawning inside the floor."
                )

            start = lab.transform_of(unreal, shots[0]).get("location", {})
            time.sleep(FLIGHT_SAMPLE_SECONDS)

            still_alive = lab.find_actors(unreal, PROJECTILE_CLASS)
            if not still_alive:
                # It flew off and expired, or hit something. Either way it moved.
                return

            end = lab.transform_of(unreal, still_alive[0]).get("location", {})
            travelled = (
                sum(
                    (float(end.get(axis, 0)) - float(start.get(axis, 0))) ** 2
                    for axis in ("x", "y", "z")
                )
                ** 0.5
            )

            assert travelled >= MIN_EXPECTED_TRAVEL, (
                f"The projectile moved {travelled:.0f} units in "
                f"{FLIGHT_SAMPLE_SECONDS}s — it's basically stationary.\n"
                "Check InitialSpeed and MaxSpeed on the "
                "UProjectileMovementComponent. Both default to 0."
            )
    finally:
        lab.despawn(unreal, probe)

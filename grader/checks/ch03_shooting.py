"""You, and you can shoot.

A note on what these checks can and can't do: the MCP exposes no way to
simulate a key press, so nothing here can literally pull your trigger.
Instead they verify the observable parts — that your character is the pawn
being possessed, that the input assets are wired up, and that your projectile
actually flies.

That's a real limitation of the tooling, not an oversight. Finding those
edges is part of what this lab is for.
"""

from __future__ import annotations

import time
from contextlib import contextmanager

import lab
from mcp_client import CheckFailed, UnrealMcp

CHARACTER_CLASS = "ALabCharacter"
PROJECTILE_CLASS = "AProjectile"

FLIGHT_SAMPLE_SECONDS = 0.25
MIN_EXPECTED_TRAVEL = 100.0


@contextmanager
def _player_in_pie(unreal: UnrealMcp):
    with lab.pie_session(unreal, warmup_seconds=1.5):
        pawns = lab.find_actors(unreal, CHARACTER_CLASS)
        if not pawns:
            raise CheckFailed(
                f"No {CHARACTER_CLASS} was possessed when play started.\n\n"
                "Check the GameMode's Default Pawn Class, and that the level "
                "has a PlayerStart."
            )
        yield pawns[0]


def check_player_is_possessed(unreal: UnrealMcp) -> None:
    with _player_in_pie(unreal):
        pass


def check_input_assets_are_assigned(unreal: UnrealMcp) -> None:
    """Enhanced Input fails silently — no mapping context, no bindings, no warning."""
    with _player_in_pie(unreal) as pawn:
        missing = [
            name
            for name in ("DefaultMappingContext", "MoveAction", "FireAction")
            if not lab.property_of(unreal, pawn, name)
        ]
        if missing:
            raise CheckFailed(
                f"These input properties are unset on {CHARACTER_CLASS}: "
                f"{missing}\n\n"
                "Assign the InputAction and InputMappingContext assets on the "
                "character. Without the mapping context, none of your bindings "
                "will ever fire."
            )


def check_projectile_class_exists(unreal: UnrealMcp) -> None:
    if not lab.class_exists(unreal, PROJECTILE_CLASS):
        raise CheckFailed(
            f"The engine can't resolve {lab.class_path(PROJECTILE_CLASS)}.\n\n"
            "Create AProjectile and do a full rebuild with the editor closed."
        )


def check_projectile_is_assigned_to_the_character(unreal: UnrealMcp) -> None:
    with _player_in_pie(unreal) as pawn:
        if not lab.property_of(unreal, pawn, "ProjectileClass"):
            raise CheckFailed(
                "ProjectileClass is unset on the character, so Fire has "
                "nothing to spawn.\n"
                "Assign your projectile in the Details panel."
            )


def check_projectile_actually_flies(unreal: UnrealMcp) -> None:
    """The usual failure is a projectile that spawns fine and then sits still."""
    if not lab.class_exists(unreal, PROJECTILE_CLASS):
        raise CheckFailed(f"{PROJECTILE_CLASS} doesn't exist yet.")

    # High and clear of the geometry, so it isn't destroyed on impact before
    # we get a second sample.
    probe = lab.spawn(unreal, PROJECTILE_CLASS, name="FlightProbe", at=(-1200.0, 0.0, 900.0))
    if not probe:
        raise CheckFailed(f"Could not place a {PROJECTILE_CLASS}.")

    try:
        with lab.pie_session(unreal, warmup_seconds=0.0):
            shots = lab.find_actors(unreal, PROJECTILE_CLASS)
            if not shots:
                raise CheckFailed(
                    "A projectile was placed but none reached the running "
                    "level. If it's being destroyed instantly, check it isn't "
                    "spawning inside the floor."
                )

            start = lab.transform_of(unreal, shots[0]).get("location", {})
            time.sleep(FLIGHT_SAMPLE_SECONDS)

            alive = lab.find_actors(unreal, PROJECTILE_CLASS)
            if not alive:
                return  # flew off and expired, or hit something. It moved.

            end = lab.transform_of(unreal, alive[0]).get("location", {})
            travelled = (
                sum(
                    (float(end.get(a, 0)) - float(start.get(a, 0))) ** 2
                    for a in ("x", "y", "z")
                )
                ** 0.5
            )

            if travelled < MIN_EXPECTED_TRAVEL:
                raise CheckFailed(
                    f"The projectile moved {travelled:.0f} units in "
                    f"{FLIGHT_SAMPLE_SECONDS}s — it's basically stationary.\n\n"
                    "Check InitialSpeed and MaxSpeed on the "
                    "UProjectileMovementComponent. Both default to 0."
                )
    finally:
        lab.despawn(unreal, probe)

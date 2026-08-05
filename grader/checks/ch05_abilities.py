"""Ability components: the dummy shoots back.

These checks look for an ability component you attached yourself. They don't
attach one for you — putting the component on the dummy, and seeing that the
dummy class never changed to accommodate it, is the whole lesson.
"""

from __future__ import annotations

import time
from contextlib import contextmanager

import lab
from mcp_client import CheckFailed, UnrealMcp

DUMMY_CLASS = "ATargetDummy"
CHARACTER_CLASS = "ALabCharacter"
ABILITY_HINT = "ability"

COMBAT_WINDOW_SECONDS = 6.0


def _abilities_on(unreal: UnrealMcp, actor) -> list:
    return [
        component
        for component in lab.components_of(unreal, actor)
        if ABILITY_HINT in lab.class_of(unreal, component).lower()
    ]


@contextmanager
def _after_combat(unreal: UnrealMcp):
    """An armed dummy, after a spell of shooting at the player."""
    if not lab.class_exists(unreal, DUMMY_CLASS):
        raise CheckFailed(f"{DUMMY_CLASS} doesn't exist yet — finish Chapter 1 first.")

    lab.ensure_in_level(unreal, DUMMY_CLASS)

    armed = [d for d in lab.find_actors(unreal, DUMMY_CLASS) if _abilities_on(unreal, d)]
    if not armed:
        raise CheckFailed(
            "No dummy in the level has an ability component.\n\n"
            "Attach your UCannonAbilityComponent to one — in C++ with "
            "CreateDefaultSubobject, or in the editor with Add Component.\n\n"
            "Try the editor route at least once. That's how a designer would "
            "do it, and it's the argument for the whole pattern."
        )

    with lab.pie_session(unreal, warmup_seconds=1.5):
        time.sleep(COMBAT_WINDOW_SECONDS)
        live = [d for d in lab.find_actors(unreal, DUMMY_CLASS) if _abilities_on(unreal, d)]
        if not live:
            raise CheckFailed("The armed dummy didn't reach the running level.")
        yield live[0]


def check_ability_is_resolvable(unreal: UnrealMcp) -> None:
    """The component is a real, reflected type the engine can name."""
    with _after_combat(unreal) as dummy:
        for component in _abilities_on(unreal, dummy):
            if not lab.class_of(unreal, component):
                raise CheckFailed(f"Couldn't resolve the class of {component}.")


def check_ability_activated(unreal: UnrealMcp) -> None:
    with _after_combat(unreal) as dummy:
        counts = [
            int(lab.property_of(unreal, a, "ActivationCount") or 0)
            for a in _abilities_on(unreal, dummy)
        ]
        if not any(c > 0 for c in counts):
            raise CheckFailed(
                f"The ability never activated in {COMBAT_WINDOW_SECONDS:.0f}s "
                f"(ActivationCount={counts}).\n\n"
                "Usual causes:\n"
                "  • PrimaryComponentTick.bCanEverTick wasn't set in the\n"
                "    component's constructor — the actor's tick setting\n"
                "    doesn't cover its components\n"
                "  • CanActivate never returns true because the player is\n"
                "    outside Range"
            )


def check_player_took_damage(unreal: UnrealMcp) -> None:
    with _after_combat(unreal):
        pawns = lab.find_actors(unreal, CHARACTER_CLASS)
        if not pawns:
            raise CheckFailed(
                f"No {CHARACTER_CLASS} in the running level, so nothing could "
                "be shot at. Check the GameMode's Default Pawn Class."
            )

        hits = int(lab.property_of(unreal, pawns[0], "HitCount") or 0)
        if hits < 1:
            raise CheckFailed(
                "The ability activated but the player was never hit.\n\n"
                "Either the projectile isn't aimed at the target, or it's "
                "colliding with the dummy that fired it.\n\n"
                "Set Owner and Instigator on the spawn params and ignore the "
                "owner in your hit handler — every shooter ships that bug once."
            )

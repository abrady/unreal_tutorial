"""The iteration loop, and the dummy.

Green means ATargetDummy exists, spawns, has a two-part component tree with
the head attached to the body, and turns while the game is running.
"""

from __future__ import annotations

import time

import lab
from mcp_client import CheckFailed
from mcp_client import UnrealMcp

ACTOR_CLASS = "ATargetDummy"

SAMPLE_INTERVAL_SECONDS = 1.0
MIN_EXPECTED_DEGREES = 5.0

_MISSING = (
    f"The engine can't resolve {lab.class_path(ACTOR_CLASS)}.\n\n"
    "Either the class doesn't exist yet, or the module wasn't rebuilt.\n"
    "Adding a new UCLASS needs a full rebuild with the editor closed —\n"
    "Live Coding can't do it."
)


def _dummy_in_pie(unreal: UnrealMcp):
    """Spawn into the editor world, start PIE, hand back the live copy.

    Order matters: the engine refuses to create actors while PIE is running,
    because the editor world is the template PIE duplicates from.
    """
    if not lab.class_exists(unreal, ACTOR_CLASS):
        raise CheckFailed(_MISSING)

    lab.ensure_in_level(unreal, ACTOR_CLASS)
    return lab.pie_session(unreal)


def check_class_exists(unreal: UnrealMcp) -> None:
    if not lab.class_exists(unreal, ACTOR_CLASS):
        raise CheckFailed(_MISSING)


def check_has_body_and_head(unreal: UnrealMcp) -> None:
    with _dummy_in_pie(unreal):
        dummy = lab.first_actor(unreal, ACTOR_CLASS)
        meshes = lab.components_of_type(unreal, dummy, "MeshComponent")
        if len(meshes) < 2:
            raise CheckFailed(
                f"{ACTOR_CLASS} has {len(meshes)} mesh component(s), "
                "expected 2 — a body and a head.\n\n"
                "Create both in the constructor with CreateDefaultSubobject.\n"
                "Components can't be created in BeginPlay."
            )


def check_head_is_attached_to_body(unreal: UnrealMcp) -> None:
    """The component tree is a hierarchy, not a pile of siblings."""
    with _dummy_in_pie(unreal):
        dummy = lab.first_actor(unreal, ACTOR_CLASS)
        parented = [c for c in lab.components_of(unreal, dummy) if lab.parent_of(unreal, c)]
        if not parented:
            raise CheckFailed(
                "Nothing on the dummy has a parent — the components are all "
                "sitting at the root.\n\n"
                "Attach the head to the body in the constructor:\n"
                "    Head->SetupAttachment(Body);\n\n"
                "Without it, moving the dummy leaves the head behind."
            )


def check_it_rotates(unreal: UnrealMcp) -> None:
    """Distinguishes 'compiles' from 'works'."""
    with _dummy_in_pie(unreal):
        dummy = lab.first_actor(unreal, ACTOR_CLASS)
        before = lab.yaw_of(unreal, dummy)
        time.sleep(SAMPLE_INTERVAL_SECONDS)
        after = lab.yaw_of(unreal, dummy)

        moved = abs(after - before) % 360.0
        if moved < MIN_EXPECTED_DEGREES:
            raise CheckFailed(
                f"The dummy isn't turning — yaw was {before:.1f} and is still "
                f"{after:.1f} after {SAMPLE_INTERVAL_SECONDS:.0f}s.\n\n"
                "Two usual causes:\n"
                "  • PrimaryActorTick.bCanEverTick wasn't set in the constructor\n"
                "  • Tick never applies a rotation\n\n"
                "Note that rotating the mesh component spins the mesh, not the "
                "actor."
            )

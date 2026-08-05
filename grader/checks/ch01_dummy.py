"""Chapter 1 — the iteration loop, and the dummy.

Green means: ATargetDummy exists, spawns, has a two-part component tree with
the head attached to the body, and turns while the game is running.

The rotation check samples the live actor twice during PIE, so it passes only
if Tick is actually firing — not if the code merely compiles.
"""

from __future__ import annotations

import time

import pytest

import lab
from mcp_client import UnrealMcp

ACTOR_CLASS = "ATargetDummy"

# Long enough that a slow spin still shows a measurable delta, short enough
# that the suite stays quick.
SAMPLE_INTERVAL_SECONDS = 1.0
MIN_EXPECTED_DEGREES = 5.0


@pytest.fixture
def dummy(pie: UnrealMcp):
    """A spawned ATargetDummy in a running PIE session."""
    if not lab.class_exists(pie, ACTOR_CLASS):
        pytest.fail(
            f"{ACTOR_CLASS} doesn't exist yet. Create it in "
            "Lab01_FirstRoom/Source/Lab01/ and do a full rebuild with the "
            "editor closed. See chapters/01-iteration-loop/README.md."
        )

    existing = lab.find_actors(pie, ACTOR_CLASS)
    if existing:
        return pie, existing[0]

    spawned = lab.spawn(pie, ACTOR_CLASS)
    if not spawned:
        pytest.fail(f"{ACTOR_CLASS} exists but could not be spawned into the level")
    return pie, spawned


def test_class_exists(unreal: UnrealMcp) -> None:
    """The class is compiled into the game module and the engine can see it."""
    assert lab.class_exists(unreal, ACTOR_CLASS), (
        f"The engine can't resolve {lab.class_path(ACTOR_CLASS)}.\n"
        "Either the class doesn't exist yet, or the module wasn't rebuilt. "
        "Adding a new UCLASS needs a full rebuild with the editor closed — "
        "Live Coding can't do it."
    )


def test_has_body_and_head(dummy) -> None:
    """Two mesh components, so there's a dummy to look at."""
    unreal, actor = dummy
    components = lab.components_of(unreal, actor)
    meshes = [c for c in components if "mesh" in str(c).lower()]
    assert len(meshes) >= 2, (
        f"{ACTOR_CLASS} has {len(meshes)} mesh component(s), expected at least 2 "
        "(a body and a head).\n"
        "Create both in the constructor with CreateDefaultSubobject. "
        "Components can't be created in BeginPlay."
    )


def test_head_is_attached_to_body(dummy) -> None:
    """The head is parented to the body, not floating free at the origin.

    This is the component-tree lesson: an actor is a hierarchy, and a child's
    transform is relative to its parent.
    """
    unreal, actor = dummy
    components = lab.components_of(unreal, actor)
    parented = [c for c in components if lab.parent_of(unreal, c)]
    assert parented, (
        f"No component on {ACTOR_CLASS} has a parent — they're all siblings at "
        "the root.\n"
        "Attach the head to the body in the constructor with "
        "Head->SetupAttachment(Body). Without that, moving the dummy leaves "
        "the head behind."
    )


def test_it_rotates(dummy) -> None:
    """It actually turns while the game runs.

    This is the check that distinguishes 'compiles' from 'works'. The usual
    reason it fails is that ticking was never enabled.
    """
    unreal, actor = dummy

    before = lab.yaw_of(unreal, actor)
    time.sleep(SAMPLE_INTERVAL_SECONDS)
    after = lab.yaw_of(unreal, actor)

    delta = abs(after - before) % 360.0
    assert delta >= MIN_EXPECTED_DEGREES, (
        f"{ACTOR_CLASS} isn't turning — yaw was {before:.1f} and is still "
        f"{after:.1f} after {SAMPLE_INTERVAL_SECONDS:.0f}s.\n"
        "Two usual causes: PrimaryActorTick.bCanEverTick wasn't set to true "
        "in the constructor, or Tick never applies a rotation. Note that "
        "rotating the mesh component spins the mesh, not the actor."
    )

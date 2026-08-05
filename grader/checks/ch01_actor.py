"""Chapter 1 — the iteration loop, and your first Actor.

Green means: ARotatingPlate exists, spawns, has a visible mesh, and spins
while the game is running.

The rotation check samples the live actor twice during PIE, so it passes
only if Tick is actually firing — not if the code merely compiles.
"""

from __future__ import annotations

import time

import pytest

import lab
from mcp_client import UnrealMcp

ACTOR_CLASS = "ARotatingPlate"

# Long enough that a slow tick still produces a measurable delta, short
# enough that the whole suite stays quick.
SAMPLE_INTERVAL_SECONDS = 1.0
MIN_EXPECTED_DEGREES = 5.0


@pytest.fixture
def plate(pie: UnrealMcp):
    """A spawned ARotatingPlate in a running PIE session."""
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


def test_has_a_mesh(plate) -> None:
    """It has a mesh component, so there's something to see."""
    unreal, actor = plate
    assert lab.has_component_of_type(unreal, actor, "mesh"), (
        f"{ACTOR_CLASS} has no mesh component.\n"
        "Create one in the constructor with CreateDefaultSubobject and make "
        "it the root. Components can't be created in BeginPlay."
    )


def test_it_rotates(plate) -> None:
    """It actually spins while the game runs.

    This is the check that distinguishes 'compiles' from 'works'. The most
    common reason it fails is that ticking was never enabled.
    """
    unreal, actor = plate

    before = lab.yaw_of(unreal, actor)
    time.sleep(SAMPLE_INTERVAL_SECONDS)
    after = lab.yaw_of(unreal, actor)

    delta = abs(after - before) % 360.0
    assert delta >= MIN_EXPECTED_DEGREES, (
        f"{ACTOR_CLASS} isn't rotating — yaw was {before:.1f} and is still "
        f"{after:.1f} after {SAMPLE_INTERVAL_SECONDS:.0f}s.\n"
        "Two usual causes: PrimaryActorTick.bCanEverTick wasn't set to true "
        "in the constructor, or Tick doesn't call Super::Tick and never "
        "applies a rotation."
    )

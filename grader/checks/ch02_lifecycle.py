"""Chapter 2 — lifecycle, GC, and the CDO.

Two lessons, four checks:

  Part A  your constructor runs on the Class Default Object, where there
          is no world
  Part B  the garbage collector only sees pointers marked UPROPERTY

test_tracked_object_survives_gc is expected to FAIL on your first run.
That's the exercise, not a bug in the lab.
"""

from __future__ import annotations

import time

import pytest

import lab
from mcp_client import UnrealMcp

ACTOR_CLASS = "ALifecycleProbe"

# BeginPlay runs, then a collection is requested, then the result is read a
# tick later. Give all of that room to happen.
SETTLE_SECONDS = 2.0


@pytest.fixture
def probe(pie: UnrealMcp):
    """A spawned ALifecycleProbe that has had time to run its lifecycle."""
    if not lab.class_exists(pie, ACTOR_CLASS):
        pytest.fail(
            f"{ACTOR_CLASS} doesn't exist yet. Create it in "
            "Lab01_FirstRoom/Source/Lab01/ and do a full rebuild with the "
            "editor closed. See chapters/02-lifecycle-and-gc/README.md."
        )

    actor = lab.spawn(pie, ACTOR_CLASS)
    if not actor:
        pytest.fail(f"{ACTOR_CLASS} exists but could not be spawned")

    time.sleep(SETTLE_SECONDS)
    return pie, actor


def _flag(unreal: UnrealMcp, actor, name: str) -> bool:
    value = lab.property_of(unreal, actor, name)
    if value is None:
        pytest.fail(
            f"{ACTOR_CLASS} has no readable property {name!r}.\n"
            "It needs to be a UPROPERTY() — plain C++ members aren't "
            "visible to reflection, which is the whole subject of Part B."
        )
    return bool(value)


# -- Part A: the CDO ------------------------------------------------------


def test_constructor_had_no_world(probe) -> None:
    """The constructor runs on the CDO, before any world exists."""
    unreal, actor = probe
    assert not _flag(unreal, actor, "bHadWorldInConstructor"), (
        "GetWorld() returned something in your constructor.\n"
        "That shouldn't happen — the constructor runs on the Class Default "
        "Object at editor startup. Check you're recording it in the "
        "constructor body itself, and restart the editor so a stale CDO "
        "isn't being reused."
    )


def test_begin_play_had_a_world(probe) -> None:
    """BeginPlay runs in a live world — this is where gameplay code goes."""
    unreal, actor = probe
    assert _flag(unreal, actor, "bHadWorldInBeginPlay"), (
        "GetWorld() was null in BeginPlay, which shouldn't be possible for "
        "a spawned actor. Make sure BeginPlay calls Super::BeginPlay() and "
        "that you're recording the flag there."
    )


# -- Part B: garbage collection -------------------------------------------


def test_gc_actually_ran(probe) -> None:
    """A collection happened, so the survival check below means something."""
    unreal, actor = probe
    assert _flag(unreal, actor, "bCollectionRan"), (
        "No collection was observed.\n"
        "ForceGarbageCollection(true) is a request, not an immediate call — "
        "it runs at the next safe point. Read your flags a tick later, not "
        "in the same frame."
    )


def test_tracked_object_survives_gc(probe) -> None:
    """A UPROPERTY reference keeps its object alive. A raw pointer doesn't.

    Expected to fail until you add UPROPERTY() to the member. That failure
    is the lesson.
    """
    unreal, actor = probe
    assert _flag(unreal, actor, "bTrackedObjectSurvived"), (
        "Your object was collected.\n\n"
        "The GC walks the reflection graph. An unmarked pointer isn't in "
        "that graph, so the collector saw no references and freed the "
        "object — while your pointer happily kept pointing at the freed "
        "memory.\n\n"
        "Add UPROPERTY() to the member and rebuild:\n"
        "    UPROPERTY()\n"
        "    TObjectPtr<UObject> Tracked;"
    )

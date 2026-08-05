"""Chapter 4 — hits, damage, and floating numbers.

The checks place a projectile just in front of a dummy, aimed at it, and let
PIE do the rest. If your collision and damage pipeline are wired, the dummy
loses health and records the hit.
"""

from __future__ import annotations

import time

import pytest

import lab
from mcp_client import UnrealMcp

DUMMY_CLASS = "ATargetDummy"
PROJECTILE_CLASS = "AProjectile"

IMPACT_WAIT_SECONDS = 2.0


@pytest.fixture
def impact(unreal: UnrealMcp):
    """A dummy that has just been shot.

    Deliberately doesn't sample a "before" health: the projectile can land
    during PIE warmup, so any baseline taken after play starts may already be
    stale. The assertions compare against MaxHealth instead.
    """
    for cls in (DUMMY_CLASS, PROJECTILE_CLASS):
        if not lab.class_exists(unreal, cls):
            pytest.fail(f"{cls} doesn't exist yet — finish the earlier chapters first.")

    lab.ensure_in_level(unreal, DUMMY_CLASS)
    dummy = lab.first_actor(unreal, DUMMY_CLASS)
    where = lab.transform_of(unreal, dummy).get("location", {})
    dummy_x = float(where.get("x", 0))
    dummy_y = float(where.get("y", 0))
    dummy_z = float(where.get("z", 0))

    # Just in front of the dummy, pointing at it. The projectile's own
    # movement component closes the gap once play starts.
    shot = lab.spawn(
        unreal,
        PROJECTILE_CLASS,
        name="DamageProbe",
        at=(dummy_x - 250.0, dummy_y, dummy_z),
    )
    if not shot:
        pytest.fail(f"Could not place a {PROJECTILE_CLASS} to fire at the dummy")

    with lab.pie_session(unreal, warmup_seconds=0.5):
        time.sleep(IMPACT_WAIT_SECONDS)
        yield unreal, lab.first_actor(unreal, DUMMY_CLASS)

    lab.despawn(unreal, shot)


def test_dummy_lost_health(impact) -> None:
    """The hit actually reduced health."""
    unreal, dummy = impact
    health = float(lab.property_of(unreal, dummy, "Health") or 0)
    max_health = float(lab.property_of(unreal, dummy, "MaxHealth") or 0)
    assert health < max_health, (
        f"The dummy is still at full health ({health}/{max_health}).\n\n"
        "Work the collision matrix from both ends — the projectile and the "
        "dummy each need a response that produces an event, and Simulation "
        "Generates Hit Events must be on.\n"
        "If the projectile stops but nothing happens, ApplyDamage probably "
        "got a null actor, or TakeDamage isn't overridden."
    )


def test_hit_was_recorded(impact) -> None:
    """The damage history saw it.

    Chapter 2's UDamageHistory earns its keep here — this is what Chapter 4's
    damage numbers are drawn from.
    """
    unreal, dummy = impact
    hits = lab.property_of(unreal, dummy, "HitCount")
    assert hits and int(hits) > 0, (
        "Health changed but HitCount is 0, so TakeDamage isn't recording into "
        "the damage history.\n"
        "Append to History inside TakeDamage, and mirror the totals onto "
        "reflected properties so they're readable."
    )


def test_damage_total_is_sane(impact) -> None:
    """Recorded damage matches the health that was lost."""
    unreal, dummy = impact
    health = float(lab.property_of(unreal, dummy, "Health") or 0)
    max_health = float(lab.property_of(unreal, dummy, "MaxHealth") or 0)
    recorded = float(lab.property_of(unreal, dummy, "DamageTaken") or 0)
    assert recorded == pytest.approx(max_health - health, abs=1.0), (
        f"Health dropped by {max_health - health} but DamageTaken says "
        f"{recorded}.\n"
        "These should agree. A common cause is applying damage twice — both a "
        "hit and an overlap fired, or the projectile struck again before it "
        "was destroyed."
    )

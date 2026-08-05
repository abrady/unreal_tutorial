"""Hits, damage, and floating numbers.

The checks place a projectile just in front of a dummy, aimed at it, and let
PIE do the rest. If your collision and damage pipeline are wired, the dummy
loses health and records the hit.
"""

from __future__ import annotations

import time
from contextlib import contextmanager

import lab
from mcp_client import CheckFailed, UnrealMcp

DUMMY_CLASS = "ATargetDummy"
PROJECTILE_CLASS = "AProjectile"

IMPACT_WAIT_SECONDS = 2.0


@contextmanager
def _after_impact(unreal: UnrealMcp):
    """A dummy that has just been shot.

    Deliberately takes no "before" reading: the projectile can land during PIE
    warmup, so a baseline sampled after play starts may already be stale. The
    checks compare against MaxHealth instead.
    """
    for cls in (DUMMY_CLASS, PROJECTILE_CLASS):
        if not lab.class_exists(unreal, cls):
            raise CheckFailed(f"{cls} doesn't exist yet — finish the earlier chapters.")

    lab.ensure_in_level(unreal, DUMMY_CLASS)
    dummy = lab.first_actor(unreal, DUMMY_CLASS)
    where = lab.transform_of(unreal, dummy).get("location", {})

    shot = lab.spawn(
        unreal,
        PROJECTILE_CLASS,
        name="DamageProbe",
        at=(float(where.get("x", 0)) - 250.0,
            float(where.get("y", 0)),
            float(where.get("z", 0))),
    )
    if not shot:
        raise CheckFailed(f"Could not place a {PROJECTILE_CLASS} to fire at the dummy.")

    try:
        with lab.pie_session(unreal, warmup_seconds=0.5):
            time.sleep(IMPACT_WAIT_SECONDS)
            yield lab.first_actor(unreal, DUMMY_CLASS)
    finally:
        lab.despawn(unreal, shot)


def check_dummy_lost_health(unreal: UnrealMcp) -> None:
    with _after_impact(unreal) as dummy:
        health = float(lab.property_of(unreal, dummy, "Health") or 0)
        max_health = float(lab.property_of(unreal, dummy, "MaxHealth") or 0)
        if health >= max_health:
            raise CheckFailed(
                f"The dummy is still at full health ({health:.0f}/{max_health:.0f}).\n\n"
                "Work the collision matrix from both ends — the projectile and "
                "the dummy each need a response that produces an event, and "
                "Simulation Generates Hit Events must be on.\n\n"
                "If the projectile stops but nothing happens, ApplyDamage "
                "probably got a null actor, or TakeDamage isn't overridden."
            )


def check_hit_was_recorded(unreal: UnrealMcp) -> None:
    """Chapter 2's UDamageHistory earns its keep here."""
    with _after_impact(unreal) as dummy:
        hits = lab.property_of(unreal, dummy, "HitCount")
        if not hits or int(hits) < 1:
            raise CheckFailed(
                "Health changed but HitCount is 0, so TakeDamage isn't "
                "recording into the damage history.\n\n"
                "Append to History inside TakeDamage, and mirror the totals "
                "onto reflected properties so they're readable."
            )


def check_damage_total_is_sane(unreal: UnrealMcp) -> None:
    with _after_impact(unreal) as dummy:
        health = float(lab.property_of(unreal, dummy, "Health") or 0)
        max_health = float(lab.property_of(unreal, dummy, "MaxHealth") or 0)
        recorded = float(lab.property_of(unreal, dummy, "DamageTaken") or 0)
        lost = max_health - health
        if abs(recorded - lost) > 1.0:
            raise CheckFailed(
                f"Health dropped by {lost:.0f} but DamageTaken says "
                f"{recorded:.0f}.\n\n"
                "These should agree. A common cause is applying damage twice — "
                "both a hit and an overlap fired, or the projectile struck "
                "again before it was destroyed."
            )

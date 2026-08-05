"""Lab-facing helpers over the raw MCP tools.

Chapter checks call these instead of `unreal.call(...)` directly, so that
when a tool's argument schema differs from what we expect, the fix lands
here once rather than in every chapter.

ALL SCHEMAS BELOW ARE VERIFIED against a live UE 5.8.1 editor. Four of the
seven were originally guessed wrong, which is why this layer exists.

  find_actors              root, name, actor_type, tag, bounds,
                           collision_channels  -- ALL must be present, even
                           when empty. Returns PIE-world actors during PIE.
  get_actor_transform      actor -> {location, rotation, scale}
  get_components           actor, component_type
  get_properties           instance, properties  -- you must NAME the
                           properties you want; there is no "give me all"
  add_to_scene_from_class  actor_type, name, xform (all required)
  search_subclasses        base_class, class_name -> [] when absent
  get_parent_component     component
  remove_from_scene        actor

Notes worth keeping:
  - `get_default_object` is Blueprint-only and rejects C++ classes, so class
    existence goes through `search_subclasses`.
  - `GetVisibleActors` reports the EDITOR world even during PIE. Use
    `find_actors` when you care about the running game.
  - Class soft paths omit Unreal's A/U prefix: `ATargetDummy` in C++ is
    `/Script/Lab01.TargetDummy` to the engine.
  - Actors CANNOT be spawned while PIE is running. Spawn into the editor
    world first, then start PIE, then find the duplicated instance.
  - `set_properties` wants its `values` as a JSON *string*. Passing an object
    fails silently, returning False.
  - There is no tool to create or save-as a level. `Lvl_FirstRoom.umap` is
    committed to the repo because the MCP cannot author it.
"""

from __future__ import annotations

import json
from contextlib import contextmanager
from typing import Any

from mcp_client import McpError, UnrealMcp

ACTOR_BASE = "/Script/Engine.Actor"

IDENTITY_TRANSFORM = {
    "location": {"x": 0.0, "y": 0.0, "z": 0.0},
    "rotation": {"pitch": 0.0, "yaw": 0.0, "roll": 0.0},
    "scale": {"x": 1.0, "y": 1.0, "z": 1.0},
}


def ref(path: str) -> dict[str, str]:
    """Wrap a soft object path the way the toolsets expect."""
    return {"refPath": path}


def strip_prefix(class_name: str) -> str:
    """Drop Unreal's A/U class prefix to get the reflection name.

    `ATargetDummy` in C++ is `TargetDummy` to the reflection system, so soft
    paths must omit the prefix. Only strips when a capital follows, so
    `AActor` -> `Actor` but `Ability` stays `Ability`.
    """
    if (
        len(class_name) > 2
        and class_name[0] in ("A", "U", "F", "I")
        and class_name[1].isupper()
    ):
        return class_name[1:]
    return class_name


def class_path(class_name: str, module: str = "Lab01") -> str:
    """Soft path for a C++ class in the project's game module.

    Accepts either spelling - `ATargetDummy` or `TargetDummy` - and emits the
    prefix-free form the engine expects.
    """
    return f"/Script/{module}.{strip_prefix(class_name)}"


def transform(x: float = 0.0, y: float = 0.0, z: float = 0.0) -> dict[str, Any]:
    """An identity transform at a location. `xform` is required on spawn."""
    return {**IDENTITY_TRANSFORM, "location": {"x": x, "y": y, "z": z}}


# -- classes --------------------------------------------------------------


def class_exists(unreal: UnrealMcp, class_name: str, module: str = "Lab01") -> bool:
    """True if the engine can resolve the class.

    Uses search_subclasses rather than get_default_object, which only accepts
    Blueprints and rejects C++ classes outright.
    """
    try:
        found = unreal.call(
            "search_subclasses",
            {"base_class": ref(ACTOR_BASE), "class_name": strip_prefix(class_name)},
        )
    except McpError:
        return False
    return bool(found)


# -- actors ---------------------------------------------------------------


def spawn(
    unreal: UnrealMcp,
    class_name: str,
    name: str | None = None,
    at: tuple[float, float, float] = (0.0, 0.0, 100.0),
    module: str = "Lab01",
) -> Any:
    """Spawn an actor of a project class into the current level."""
    return unreal.call(
        "add_to_scene_from_class",
        {
            "actor_type": ref(class_path(class_name, module)),
            "name": name or f"{class_name}_Check",
            "xform": transform(*at),
            "parent": None,
            "snap_to_ground": False,
        },
    )


def despawn(unreal: UnrealMcp, actor: Any) -> None:
    """Remove an actor. Best effort — teardown must never mask a failure."""
    try:
        unreal.call("remove_from_scene", {"actor": _as_ref(actor)})
    except McpError:
        pass


def ensure_in_level(
    unreal: UnrealMcp, class_name: str, module: str = "Lab01"
) -> None:
    """Make sure at least one of these exists in the EDITOR world.

    Must be called before PIE starts. The engine refuses to create actors
    while PIE is active ("Cannot create actors while PIE is active") because
    the editor world is the template PIE duplicates from.
    """
    if not find_actors(unreal, class_name, module):
        spawn(unreal, class_name, module=module)


@contextmanager
def pie_session(unreal: UnrealMcp, warmup_seconds: float = 1.0):
    """Run a block inside PIE, stopping it even if the block raises.

    Spawn anything you need *before* entering this.
    """
    if unreal.is_pie_running():
        unreal.stop_pie()
    unreal.start_pie(warmup_seconds=warmup_seconds)
    try:
        yield unreal
    finally:
        try:
            unreal.stop_pie()
        except Exception:  # noqa: BLE001 - teardown must not mask the failure
            pass


def first_actor(
    unreal: UnrealMcp, class_name: str, module: str = "Lab01"
) -> Any | None:
    """The first actor of a class in the current world, or None."""
    actors = find_actors(unreal, class_name, module)
    return actors[0] if actors else None


def find_actors(
    unreal: UnrealMcp, class_name: str | None = None, module: str = "Lab01"
) -> list[Any]:
    """Actors in the current world, optionally filtered by project class.

    During PIE this reports the PIE world, which is what checks want.
    """
    args: dict[str, Any] = {
        "root": None,
        "name": "",
        "actor_type": ref(class_path(class_name, module)) if class_name else None,
        "tag": "",
        "bounds": None,
        "collision_channels": [],
    }
    result = unreal.call("find_actors", args)
    return result if isinstance(result, list) else []


def transform_of(unreal: UnrealMcp, actor: Any) -> dict[str, Any]:
    """World transform as {location, rotation, scale}."""
    return unreal.call("get_actor_transform", {"actor": _as_ref(actor)})


def yaw_of(unreal: UnrealMcp, actor: Any) -> float:
    """Just the yaw, in degrees. Convenience for rotation checks."""
    return float(transform_of(unreal, actor).get("rotation", {}).get("yaw", 0.0))


# -- components -----------------------------------------------------------


def components_of(unreal: UnrealMcp, actor: Any) -> list[Any]:
    """Every component on an actor."""
    result = unreal.call(
        "get_components", {"actor": _as_ref(actor), "component_type": None}
    )
    return result if isinstance(result, list) else []


def parent_of(unreal: UnrealMcp, component: Any) -> Any:
    """The component this one is attached to, or None if it's the root."""
    try:
        return unreal.call("get_parent_component", {"component": _as_ref(component)})
    except McpError:
        return None


def class_of(unreal: UnrealMcp, obj: Any) -> str:
    """The object's class path, e.g. `/Script/Engine.StaticMeshComponent`.

    Needed because a component's refPath carries its *name* (`...Actor.Body`),
    not its type — so you can't identify a component by its path.
    """
    try:
        result = unreal.call("get_class", {"instance": _as_ref(obj)})
    except McpError:
        return ""
    if isinstance(result, dict):
        return str(result.get("refPath", ""))
    return str(result)


def components_of_type(
    unreal: UnrealMcp, actor: Any, type_substring: str
) -> list[Any]:
    """Components whose class name contains the substring, case-insensitively.

    Deliberately loose: a learner may reasonably pick any mesh component
    subclass, and a chapter check shouldn't care which.
    """
    wanted = type_substring.lower()
    return [
        component
        for component in components_of(unreal, actor)
        if wanted in class_of(unreal, component).lower()
    ]


# -- properties -----------------------------------------------------------


def properties_of(unreal: UnrealMcp, obj: Any, names: list[str]) -> dict[str, Any]:
    """Read named reflected properties.

    The tool has no "give me everything" mode — you must ask for specific
    names, so callers pass the ones they care about.
    """
    result = unreal.call(
        "get_properties", {"instance": _as_ref(obj), "properties": names}
    )
    return result if isinstance(result, dict) else {}


def property_of(unreal: UnrealMcp, obj: Any, name: str, default: Any = None) -> Any:
    """One reflected property by name, tolerating case differences.

    The toolsets sometimes report camelCase where the C++ declares
    PascalCase; a chapter check shouldn't fail over that.
    """
    try:
        values = properties_of(unreal, obj, [name])
    except McpError:
        return default
    if name in values:
        return _coerce(values[name])
    folded = {key.lower(): value for key, value in values.items()}
    if name.lower() in folded:
        return _coerce(folded[name.lower()])
    return default


def set_properties(unreal: UnrealMcp, obj: Any, values: dict[str, Any]) -> bool:
    """Write reflected properties.

    The tool wants `values` as a JSON *string*, not an object. Passing a dict
    fails silently with False, so the encoding happens here once.
    """
    result = unreal.call(
        "set_properties", {"instance": _as_ref(obj), "values": json.dumps(values)}
    )
    return bool(result)


def _coerce(value: Any) -> Any:
    """Turn the toolset's stringly-typed scalars into Python values."""
    if not isinstance(value, str):
        return value
    lowered = value.strip().lower()
    if lowered in ("true", "false"):
        return lowered == "true"
    if lowered in ("none", "null", ""):
        return None
    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        return value


def _as_ref(obj: Any) -> dict[str, str]:
    """Accept a refPath string, a raw dict, or a wrapped reference."""
    if isinstance(obj, str):
        return ref(obj)
    if isinstance(obj, dict) and "refPath" in obj:
        return {"refPath": obj["refPath"]}
    raise McpError(f"cannot turn {obj!r} into an object reference")

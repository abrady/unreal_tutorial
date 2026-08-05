"""Lab-facing helpers over the raw MCP tools.

Chapter checks call these instead of `unreal.call(...)` directly, so that
when a tool's argument schema turns out to differ from what we expect, the
fix lands here once rather than in every chapter.

VERIFIED against a live UE 5.8 editor:
  - tool names are fully qualified `<Plugin>.<Toolset>.<Tool>`; the client
    resolves short names
  - object references are `{"refPath": "<soft path string>"}`
  - `GetVisibleActors` returns a list of those reference objects
  - `StartPIE` requires bSimulate / playMode / warmupSeconds
  - `CaptureViewport` requires TOptional args passed explicitly as null

INFERRED, NOT YET VERIFIED (expect these to need adjustment on first run):
  - `find_actors` argument names (`actor_type`, `name`, `root`)
  - `add_to_scene_from_class` argument names
  - the response shape of `get_actor_transform` and `get_components`
"""

from __future__ import annotations

from typing import Any

from mcp_client import McpError, UnrealMcp


def ref(path: str) -> dict[str, str]:
    """Wrap a soft object path the way the toolsets expect."""
    return {"refPath": path}


def class_path(class_name: str, module: str = "Lab01") -> str:
    """Soft path for a C++ class living in the project's game module."""
    return f"/Script/{module}.{class_name}"


def class_exists(unreal: UnrealMcp, class_name: str, module: str = "Lab01") -> bool:
    """True if the engine can resolve the class by soft path.

    Used by chapter checks to give 'you haven't written it yet' a clearer
    failure than 'spawn returned nothing'.
    """
    try:
        result = unreal.call("get_default_object", {"cls": ref(class_path(class_name, module))})
    except McpError:
        return False
    return bool(result)


def spawn(unreal: UnrealMcp, class_name: str, module: str = "Lab01") -> Any:
    """Spawn an actor of a project class into the current level."""
    return unreal.call(
        "add_to_scene_from_class",
        {"actor_class": ref(class_path(class_name, module))},
    )


def find_actors(unreal: UnrealMcp, class_name: str, module: str = "Lab01") -> list[Any]:
    """Every actor of the given project class in the current world."""
    result = unreal.call(
        "find_actors",
        {"actor_type": ref(class_path(class_name, module))},
    )
    return result if isinstance(result, list) else []


def transform_of(unreal: UnrealMcp, actor: Any) -> dict[str, Any]:
    """World transform of an actor, as {location, rotation, scale}."""
    return unreal.call("get_actor_transform", {"actor": _as_ref(actor)})


def yaw_of(unreal: UnrealMcp, actor: Any) -> float:
    """Just the yaw, in degrees. Convenience for rotation checks."""
    rotation = transform_of(unreal, actor).get("rotation", {})
    return float(rotation.get("yaw", 0.0))


def components_of(unreal: UnrealMcp, actor: Any) -> list[Any]:
    """Every component on an actor."""
    result = unreal.call("get_components", {"actor": _as_ref(actor)})
    return result if isinstance(result, list) else []


def properties_of(unreal: UnrealMcp, obj: Any) -> dict[str, Any]:
    """Every readable reflected property on an object."""
    result = unreal.call("get_properties", {"obj": _as_ref(obj)})
    return result if isinstance(result, dict) else {}


def property_of(unreal: UnrealMcp, obj: Any, name: str, default: Any = None) -> Any:
    """One reflected property by name, case-insensitively.

    Case folding is deliberate: the toolsets tend to report camelCase while
    the C++ declares PascalCase, and a chapter check shouldn't fail over it.
    """
    properties = properties_of(unreal, obj)
    if name in properties:
        return properties[name]
    folded = {key.lower(): value for key, value in properties.items()}
    return folded.get(name.lower(), default)


def has_component_of_type(unreal: UnrealMcp, actor: Any, type_substring: str) -> bool:
    """True if any component's class name contains the substring.

    Deliberately loose: a learner may reasonably pick StaticMeshComponent
    for the mesh, and the check shouldn't care which exact subclass.
    """
    for component in components_of(unreal, actor):
        described = str(component)
        if type_substring.lower() in described.lower():
            return True
    return False


def _as_ref(actor: Any) -> dict[str, str]:
    """Accept a refPath string, a raw dict, or a wrapped reference."""
    if isinstance(actor, str):
        return ref(actor)
    if isinstance(actor, dict) and "refPath" in actor:
        return {"refPath": actor["refPath"]}
    raise McpError(f"cannot turn {actor!r} into an object reference")

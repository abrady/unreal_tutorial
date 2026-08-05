"""Your environment is ready.

Green here is your ticket into the session. Everything these checks cover is
something that, left broken, will quietly waste your morning.
"""

from __future__ import annotations

import lab
from mcp_client import CheckFailed
from mcp_client import UnrealMcp

REQUIRED_TOOLS = ("StartPIE", "StopPIE", "IsPIERunning", "GetVisibleActors")


def check_editor_is_reachable(unreal: UnrealMcp) -> None:
    if not unreal.session_id:
        raise CheckFailed("The handshake produced no session id.")


def check_tools_are_available(unreal: UnrealMcp) -> None:
    if not unreal.tools():
        raise CheckFailed(
            "The server exposed no tools at all. Check that the "
            "EditorToolset plugin is enabled, then restart the editor."
        )


def check_required_tools_are_registered(unreal: UnrealMcp) -> None:
    missing = [name for name in REQUIRED_TOOLS if not unreal.has_tool(name)]
    if missing:
        raise CheckFailed(
            f"Missing tools: {missing}\n"
            "Enable the EditorToolset plugin in Edit > Plugins and restart.\n"
            f"({len(unreal.tools())} tools are currently registered.)"
        )


def check_pie_can_start_and_stop(unreal: UnrealMcp) -> None:
    if unreal.is_pie_running():
        unreal.stop_pie()

    unreal.start_pie(warmup_seconds=1.0)
    try:
        if not unreal.is_pie_running():
            raise CheckFailed("StartPIE returned, but IsPIERunning says otherwise.")
    finally:
        unreal.stop_pie()

    if unreal.is_pie_running():
        raise CheckFailed("PIE didn't shut down cleanly.")


def check_live_inspection_works(unreal: UnrealMcp) -> None:
    """The capability the whole grader rests on."""
    with lab.pie_session(unreal, warmup_seconds=1.0):
        actors = unreal.call("GetVisibleActors")
        if not isinstance(actors, list) or not actors:
            raise CheckFailed(
                "PIE is running but no actors are visible, so the grader "
                "can't see what your code does."
            )
        if not any("refPath" in a for a in actors):
            raise CheckFailed(f"Actor entries look wrong: {actors[0]!r}")

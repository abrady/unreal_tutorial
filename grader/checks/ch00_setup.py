"""Chapter 0 — your environment is ready.

Green here is your ticket into the session. Everything these checks cover is
something that, left broken, will silently waste your morning.
"""

from __future__ import annotations

import pytest

from mcp_client import UnrealMcp

# Tools the lab actually leans on. The engine registers these fully qualified
# as <Plugin>.<Toolset>.<Tool>; the client resolves short names for us.
REQUIRED_TOOLS = ("StartPIE", "StopPIE", "IsPIERunning", "GetVisibleActors")


def test_editor_is_reachable(unreal: UnrealMcp) -> None:
    """The MCP server is up and completed a handshake."""
    assert unreal.session_id, "handshake produced no Mcp-Session-Id"


def test_tools_are_available(unreal: UnrealMcp) -> None:
    """tools/list returns something we can work with."""
    names = {tool["name"] for tool in unreal.list_tools()}
    assert names, "the server exposed no tools at all"


def test_required_tools_are_registered(unreal: UnrealMcp) -> None:
    """The tools the lab depends on are reachable."""
    missing = [name for name in REQUIRED_TOOLS if not unreal.has_tool(name)]
    assert not missing, (
        f"missing tool(s): {missing}. Enable the EditorToolset plugin in "
        f"Edit > Plugins and restart the editor. See SETUP.md. "
        f"({len(unreal.tools())} tools currently registered.)"
    )


def test_pie_can_start_and_stop(unreal: UnrealMcp) -> None:
    """PIE is drivable over MCP — every later chapter depends on this."""
    if unreal.is_pie_running():
        unreal.stop_pie()

    unreal.start_pie(warmup_seconds=1.0)
    try:
        assert unreal.is_pie_running(), "StartPIE returned but IsPIERunning is false"
    finally:
        unreal.stop_pie()

    assert not unreal.is_pie_running(), "PIE did not shut down cleanly"


def test_live_inspection_reports_actors(pie: UnrealMcp) -> None:
    """Live inspection works: we can see what's actually in the running world.

    This is the capability the whole grader rests on. If this passes, the
    lab can ask the editor what actually happened rather than trusting you.
    """
    actors = pie.call("GetVisibleActors")
    assert isinstance(actors, list), f"expected a list of actors, got {type(actors)}"
    assert actors, "PIE is running but no actors are visible"
    assert any("refPath" in actor for actor in actors), (
        f"actor entries have no refPath; first entry was {actors[0]!r}"
    )

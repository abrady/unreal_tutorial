"""Shared fixtures for the lab checks."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

from mcp_client import DEFAULT_URL, EditorNotRunning, UnrealMcp

MCP_URL = os.environ.get("UNREAL_MCP_URL", DEFAULT_URL)


@pytest.fixture(scope="session")
def unreal() -> Iterator[UnrealMcp]:
    """A connected MCP client, shared across every check in the run."""
    client = UnrealMcp(MCP_URL)
    try:
        client.connect()
    except EditorNotRunning as exc:
        pytest.skip(str(exc))
    yield client
    client.close()


@pytest.fixture
def pie(unreal: UnrealMcp) -> Iterator[UnrealMcp]:
    """Run a check inside a Play-In-Editor session.

    Stops PIE afterwards even if the check fails, so one bad assertion
    doesn't leave the editor stuck in play mode for every later check.
    """
    unreal.start_pie(warmup_seconds=1.0)
    try:
        yield unreal
    finally:
        try:
            unreal.stop_pie()
        except Exception:  # noqa: BLE001 - teardown must never mask the failure
            pass

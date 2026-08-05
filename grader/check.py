#!/usr/bin/env python3
"""Run a chapter's checks against a running Unreal editor.

    python3 check.py           # every chapter
    python3 check.py ch01      # one chapter
    python3 check.py ch01 ch02

No installs. Standard library only, using whatever python3 you have.

Checks are plain functions in checks/chNN_*.py named `check_*`. Each takes a
connected UnrealMcp and either returns (pass) or raises CheckFailed with a
message written for the person reading it — the message is the teaching, so
it gets printed in full rather than buried in a traceback.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp_client import (  # noqa: E402
    DEFAULT_URL,
    CheckFailed,
    EditorNotRunning,
    UnrealMcp,
)

CHECKS_DIR = Path(__file__).parent / "checks"
MCP_URL = os.environ.get("UNREAL_MCP_URL", DEFAULT_URL)

# Colour only when we're attached to a terminal.
_TTY = sys.stdout.isatty()
GREEN = "\033[32m" if _TTY else ""
RED = "\033[31m" if _TTY else ""
DIM = "\033[2m" if _TTY else ""
BOLD = "\033[1m" if _TTY else ""
OFF = "\033[0m" if _TTY else ""


def load_suites(wanted: list[str]) -> list[tuple[str, object]]:
    suites = []
    for path in sorted(CHECKS_DIR.glob("ch*.py")):
        chapter = path.stem.split("_")[0]
        if wanted and chapter not in wanted:
            continue
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suites.append((path.stem, module))
    return suites


def checks_in(module: object) -> list[tuple[str, object]]:
    """Every check in the module, in the order it appears in the file.

    Source order, not alphabetical - the checks build on each other and the
    first failure should be the earliest thing that's wrong.
    """
    found = [
        (name, getattr(module, name))
        for name in vars(module)
        if name.startswith("check_") and callable(getattr(module, name))
    ]
    found.sort(key=lambda pair: getattr(pair[1], "__code__", None).co_firstlineno)
    return [(name[len("check_") :].replace("_", " "), fn) for name, fn in found]


def indent(text: str, prefix: str = "      ") -> str:
    return "\n".join(prefix + line for line in str(text).strip().split("\n"))


def main(argv: list[str]) -> int:
    wanted = [a.lower() for a in argv[1:] if not a.startswith("-")]
    suites = load_suites(wanted)
    if not suites:
        print(f"No checks matched {wanted}. Available: "
              f"{', '.join(sorted(p.stem.split('_')[0] for p in CHECKS_DIR.glob('ch*.py')))}")
        return 2

    try:
        unreal = UnrealMcp(MCP_URL).connect()
    except EditorNotRunning as exc:
        print(f"\n{RED}Can't reach Unreal.{OFF}\n")
        print(indent(exc, "  "))
        print()
        return 2

    passed = failed = 0
    first_failing = None
    started = time.time()

    try:
        for suite_name, module in suites:
            title = (module.__doc__ or suite_name).strip().split("\n")[0]
            print(f"\n{BOLD}{suite_name}{OFF} {DIM}{title}{OFF}")

            for label, fn in checks_in(module):
                try:
                    fn(unreal)
                except CheckFailed as exc:
                    failed += 1
                    first_failing = first_failing or suite_name.split("_")[0]
                    print(f"  {RED}✗{OFF} {label}")
                    print(indent(exc))
                    print()
                except Exception as exc:  # noqa: BLE001
                    failed += 1
                    first_failing = first_failing or suite_name.split("_")[0]
                    print(f"  {RED}✗{OFF} {label} {DIM}(the check itself errored){OFF}")
                    print(indent(exc))
                    if os.environ.get("GRADER_TRACEBACK"):
                        print(indent(traceback.format_exc()))
                    print()
                else:
                    passed += 1
                    print(f"  {GREEN}✓{OFF} {label}")
    finally:
        unreal.close()

    elapsed = time.time() - started
    print()
    if failed:
        print(f"{RED}{failed} to go{OFF}, {passed} passing  {DIM}({elapsed:.0f}s){OFF}")
        if first_failing:
            print(f"{DIM}Start here: python3 check.py {first_failing}{OFF}")
    else:
        print(f"{GREEN}All {passed} passing.{OFF}  {DIM}({elapsed:.0f}s){OFF}")
    print()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

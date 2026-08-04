# Unreal, the hard way (with an AI that won't do it for you)

A half-day lab that takes a strong engineer who has never opened Unreal to a
first-person room with a working door, a pressure plate, and a pickup — written
in C++, verified by an automated grader, and debugged with an AI agent wired
directly into the running editor.

> **Status: in development.** The design is settled
> ([docs/plans](docs/plans/2026-08-04-unreal-mcp-tutorial-design.md)); the lab
> itself is being built. Chapter 0 is the first thing that will work.

**You do not need a VR headset.** You need a PC that can run Unreal.

---

## Why this exists

DRE engineers support partners shipping real Unreal titles. That job needs UE
fluency, and there is currently no internal Unreal course — the Eng Bootcamp
Immersive 3D path lists exactly one hands-on engine course, and it's Unity.

This has been proposed three times since 2022 and never shipped, each time as a
full curriculum. So this is deliberately **one lab**, complete and useful on its
own. Extra chapters are take-home and optional. If the half day lands, we earn
the rest.

## What makes it different

**The lab is a test suite.** Every chapter ships failing checks. You're done
when they're green.

```console
$ pytest grader/checks/ch04_interaction.py
FAILED  test_plate_opens_door       - BP_Door yaw was 0.0, expected ~90.0
FAILED  test_pickup_is_consumed     - Pickup still present after overlap
```

The grader isn't reading your source. It boots your project, starts PIE, walks
the player onto the plate, and asks the live editor what the door actually did.
You cannot fake it, and you always know exactly how close you are.

**The AI is your debugger, not your author.** Unreal 5.8 ships an MCP server
*inside the engine* — Epic's `ModelContextProtocol` plugin. You enable a
checkbox and your agent is wired into the running editor: it can start PIE,
inspect live actors, capture an annotated viewport with every actor's world
position, and read real compiler errors. Same interface the grader uses. Ask
it *"why is check 3 failing?"* and it can actually go look.

You'll also add `UFUNCTION(meta = (AICallable))` to your own C++ and watch it
appear as a tool the agent can call. The agent isn't a thing being done to
you — it's a thing you extend.

What it will not do is write your chapter for you. That's a rule in
[`AGENTS.md`](AGENTS.md), and there's a reason.

## The reason

Bastani et al. (2024) gave ~1000 students one of three things: no AI, GPT-4, or
a guardrailed tutor that gave hints instead of answers.

| | Practice | Unassisted exam |
|---|---|---|
| No AI | — | — |
| **Unrestricted GPT-4** | **+48%** | **−17%** |
| Guardrailed tutor | positive | no harm |

Unrestricted AI made people dramatically better right up until you took it
away, at which point they were *worse than if they'd never had it*. The
guardrailed version kept the gains.

Watching an agent build your game is the −17% condition. So during a chapter the
agent explains, inspects, and diagnoses. Once your checks are green, the gloves
come off — go compare your solution to the reference and ask it to tear yours
apart.

Enforcement is a config file and an honour system. We're telling you the study
result instead of pretending the guardrail is airtight.

## What you'll build

A room. You walk into it, step on a plate, a door opens, you grab a thing.

It is not impressive to look at. It is four hours of the specific concepts that
make Unreal confusing to people who are already good at C++:

| Ch | Topic | The thing that actually bites |
|---|---|---|
| 0 | Setup *(pre-work — do this first)* | The build takes longer than you think |
| 1 | Iteration loop, your first `AActor` | `.generated.h` ordering; live coding vs. full rebuild |
| 2 | Lifecycle, GC, the CDO trap | Your constructor runs on an object that isn't your object |
| 3 | Gameplay framework, Enhanced Input | Which of the six classes owns this, and why |
| 4 | Collision, overlap, `IInteractable` | The response matrix, and the C++/Blueprint boundary |

Requires **Unreal 5.8 or newer** — the in-engine MCP plugin landed in 5.8.
Works on vanilla Epic or the Meta fork; the plugin is Epic's, so both have it.

Chapter 2 is the one that matters. Every C++ engineer gets burned by UObject
lifetime exactly once, and it's the line between copying Unreal tutorials and
understanding Unreal. You'll get burned on purpose, in a controlled setting,
with a grader that tells you when you've actually fixed it.

## About the VR part

There isn't one, in the half day. Vanilla Unreal, desktop PIE, no MetaXR
plugin, no Android toolchain.

But Chapter 4 has you write interaction behind an `IInteractable` interface
rather than in the pawn. That's not decoration — it's the reason the optional
take-home capstone can swap in a VR pawn and change *zero* interaction code.
The lesson about writing VR-ready systems is architectural, and you can learn it
without owning a headset.

## Take-home chapters

Optional, self-serve, after the half day: delegates and game state · UMG HUD
from C++ · AI patrol with NavMesh, Behavior Trees and Blackboards (the best
showcase of what live MCP inspection is for) · audio · packaging a standalone
build · the VR pawn swap (headset required).

## Getting started

1. Read [`SETUP.md`](SETUP.md) and do it **before** the session — the engine
   install and first compile are long, and showing up unbuilt means showing up
   unable to participate.
2. Confirm you're ready:
   ```console
   $ pytest grader/checks/ch00_setup.py
   ```
   Green is your ticket in.
3. Start at [`chapters/01-iteration-loop`](chapters/01-iteration-loop/).

## Repo map

| Path | What |
|---|---|
| `SETUP.md` | Chapter 0 — gated pre-work |
| `chapters/` | One README per chapter. **Steps.** |
| `docs/slides/` | The deck. **Concepts.** |
| `Lab01_FirstRoom/` | The Unreal project |
| `grader/` | MCP client and check suites |
| `AGENTS.md` | Tutor-mode rules for your AI client |
| `docs/plans/` | Why the lab is shaped like this |

Chapter checkpoints are git tags: branch from `chNN-start`, and diff against
`chNN-solution` when you're stuck. Try not to look early — the checkpoint is
the only honest signal you'll get about whether it stuck.

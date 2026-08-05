# Unreal, the hard way (with an AI that won't do it for you)

Build a combat gym. Shoot a target dummy, watch damage numbers pop off it,
then attach a component and watch the dummy shoot back.

In C++, from an empty project, verified by an automated grader, debugged with
an AI agent wired directly into the running editor.

> **Status: chapters 1–5 are playable.** All seven chapters are written, the
> grader runs green against a live 5.8.1 editor, and reference solutions exist
> for 1–5. Design rationale lives in
> [docs/plans](docs/plans/2026-08-04-unreal-mcp-tutorial-design.md).

**You do not need a VR headset.** You need a PC or Mac that can run Unreal.

---

## Why this exists

DRE engineers support partners shipping real Unreal titles. That job needs UE
fluency, and there is currently no internal Unreal course — the Eng Bootcamp
Immersive 3D path lists exactly one hands-on engine course, and it's Unity.

This has been proposed three times since 2022 and never shipped, each time as
a full curriculum. So this is deliberately **one lab**, complete and useful on
its own. Extra chapters are take-home and optional.

## What makes it different

**The lab is a test suite.** Every chapter ships failing checks. You're done
when they're green.

```console
$ python3 check.py ch04

ch04_damage Hits, damage, and floating numbers.
  ✗ dummy lost health
      The dummy is still at full health (100/100).
      Work the collision matrix from both ends — the projectile and the
      dummy each need a response that produces an event.
  ✗ hit was recorded
      Health changed but HitCount is 0, so TakeDamage isn't recording
      into the damage history.
```

The grader isn't reading your source. It boots your project, starts PIE, fires
a projectile at a dummy, and asks the live editor what actually happened. You
can't fake it, and you always know exactly how close you are.

**Your agent is inside the editor.** Unreal 5.8 ships Epic's
`ModelContextProtocol` plugin. Enable a checkbox and your agent can start PIE,
inspect live actors, and read real compiler errors — the same interface the
grader uses. Ask it *"why is check 3 failing?"* and it can go look.

You'll also add `UFUNCTION(meta = (AICallable))` to your own C++ and watch it
appear as a tool the agent can call. The agent isn't something done to you —
it's something you extend.

What it won't do is write your chapter. That's a rule in
[`AGENTS.md`](AGENTS.md), and there's a reason.

## The reason

Bastani et al. (2024) gave ~1000 students one of three things: no AI, GPT-4,
or a guardrailed tutor that gave hints instead of answers.

| | Practice | Unassisted exam |
|---|---|---|
| No AI | — | — |
| **Unrestricted GPT-4** | **+48%** | **−17%** |
| Guardrailed tutor | positive | no harm |

Unrestricted AI made people dramatically better right up until you took it
away, at which point they were *worse than if they'd never had it*. The
guardrailed version kept the gains.

Watching an agent build your game is the −17% condition. So during a chapter
the agent explains, inspects, and diagnoses. Once your checks are green, the
gloves come off.

Enforcement is a config file and an honour system. We're telling you the study
result instead of pretending the guardrail is airtight.

## But you *should* delegate the repetition

The rule above isn't "don't use the agent." It's "don't let it do the part
you haven't learned yet."

Once you've done something **once, by hand**, doing it four more times isn't
learning — it's typing. Hand that over:

> You wire `IA_Fire` yourself. Then you ask the agent to add `IA_Reload` and
> `IA_Dash` the same way.
>
> You place one target dummy. Then you ask it to place four more in a firing
> line.

Every chapter ends with something to delegate. That's the working pattern the
lab is actually teaching: **understand it once, then hand off the grind.**

And when the agent *can't* do it — that's worth knowing too. The 255 tools
have edges. Finding them is part of why you're here, because a partner is
going to ask you where they are.

## What you'll build

| Ch | Build | The thing that actually bites |
|---|---|---|
| 0 | Setup *(pre-work — do this first)* | The install is bigger than you think |
| 1 | A target dummy, turning slowly | `.generated.h` order; components and attachment |
| 2 | Give it health | Your constructor runs on an object that isn't your object |
| 3 | You, and you can shoot | Which of six framework classes owns this |
| 4 | Hits land, damage numbers pop | The collision matrix has two sides |
| 5 | The dummy shoots back | Composition — the pattern Unreal is built on |

**Chapters 1–5 are the session: roughly 5 hours.** Not a half day — 1 and 2
run ~45 minutes, 3 through 5 run 60–90. Better to know that now.

Then, take-home and substantial (60–90 min each):

| Ch | Build |
|---|---|
| 6 | Three dummies: AOE, homing missiles, spread shot |
| 7 | Attacks driven by animation timing, via montage notifies |

**Chapter 2 is the one that matters.** Every C++ engineer gets burned by
UObject lifetime exactly once, and it's the line between copying Unreal
tutorials and understanding Unreal. You'll get burned on purpose, with a
grader that tells you when you've actually fixed it.

## About the VR part

There isn't one, in the lab. Vanilla Unreal, desktop PIE, no MetaXR plugin, no
Android toolchain, no headset.

But by Chapter 5 your ability components don't know what triggered them, your
damage pipeline doesn't know what dealt the damage, and your firing code
doesn't know what device sent `IA_Fire`. Swap the desktop pawn for a VR pawn
and the combat layer is untouched.

That's the real lesson about writing VR-ready systems, and it's architectural
— you can learn it without owning a headset. The optional capstone does the
swap if you have one.

## Getting started

1. Read [`SETUP.md`](SETUP.md) and do it **before** the session — the engine
   install and first compile are long, and showing up unbuilt means showing up
   unable to participate.
2. Confirm you're ready:
   ```console
   $ cd grader && python3 check.py ch00
   ```
   Green is your ticket in. No pip install — the grader is standard library
   only, and runs on whatever `python3` you already have.
3. Start at [`chapters/01-iteration-loop`](chapters/01-iteration-loop/).

## Repo map

| Path | What |
|---|---|
| `SETUP.md` | Chapter 0 — gated pre-work |
| `chapters/` | One README per chapter. **Steps.** |
| `docs/slides/` | The deck. **Concepts.** |
| `Lab01_FirstRoom/` | The Unreal project |
| `grader/` | MCP client and check suites. `python3 check.py` |
| `AGENTS.md` | Tutor-mode rules for your AI client |
| `docs/plans/` | Why the lab is shaped like this |

Chapters 1–6 need **zero binary assets** — the gym is built from engine
primitives. Chapter 7 pulls animation content from the engine template, and
it's gitignored.

Chapter checkpoints are git tags: branch from `chNN-start`, diff against
`chNN-solution` when you're stuck. Try not to look early — the checkpoint is
the only honest signal you'll get about whether it stuck.

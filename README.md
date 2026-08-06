# Unreal, the hard way (with an AI that won't do it for you)

Build a combat gym. Shoot a target dummy, watch damage numbers pop off it,
then attach a component and watch the dummy shoot back.

In C++, from an empty project, with an AI assistant wired directly into the
running editor — checking your work against live state, and refusing to write
it for you.

> **Status: chapters 1–5 are playable.** All seven are written, verified
> against a live 5.8.1 editor, with reference solutions for 1–5. Design
> rationale lives in
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

**Your agent is inside the editor.** Unreal 5.8 ships Epic's
`ModelContextProtocol` plugin. Enable a checkbox and your agent can start PIE,
inspect live actors, and read real compiler errors — Ask it *"why isn't this working?"* and it can go look, rather than guess
from your source.

You'll also add `UFUNCTION(meta = (AICallable))` to your own C++ and watch it
appear as a tool the agent can call. The agent isn't something done to you —
it's something you extend.

What it won't do is write your chapter. That's a rule in
[`AGENTS.md`](AGENTS.md), and there's a reason.


## Practice, but you *should* delegate the repetition

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
assistant that checks the running editor to tell you when you've actually
fixed it.

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

See [`START_HERE.md`](START_HERE.md). It's three steps, and the third is
saying "start lesson one" to your assistant.

If you'd rather drive it yourself, [`SETUP.md`](SETUP.md) has the manual
version.

## Repo map

| Path | What |
|---|---|
| `START_HERE.md` | Begin here |
| `chapters/` | One README per chapter (**steps**) plus `CHECKS.md` (the rubric) |
| `docs/slides/` | The deck. **Concepts.** |
| `Lab01_FirstRoom/` | The Unreal project |
| `AGENTS.md` | Tutor-mode rules for your AI assistant |
| `docs/MCP_NOTES.md` | How to drive the editor over MCP — for your assistant |
| `docs/plans/` | Why the lab is shaped like this |

Chapters 1–6 need **zero binary assets** — the gym is built from engine
primitives. Chapter 7 pulls animation content from the engine template, and
it's gitignored.

Chapter checkpoints are git tags: branch from `chNN-start`, diff against
`chNN-solution` when you're stuck. Try not to look early — the checkpoint is
the only honest signal you'll get about whether it stuck.

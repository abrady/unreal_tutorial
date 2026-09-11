# Unreal with an AI tutor

Build a combat gym. Shoot a target dummy, watch damage numbers pop off it,
then attach a component and watch the dummy shoot back.

In C++, from an empty project, with an AI assistant wired directly into the
running editor — checking your work against live state, and refusing to write
it for you.

> **Status: chapters 1–5 are playable.** All seven are written, verified
> against a live 5.8.1 editor, with reference solutions for 1–5.

**You do not need a VR headset.** You need a PC or Mac that can run Unreal.

---

## Why this exists

People are slow in Unreal because Unreal has about six idioms
that just need practice to get used to: Reflection, the build loop, the Class Default
Object, garbage collection, the gameplay framework, and a few others.

## How to use it

The best way to learn with this is to do the labs with your agent that has full editor access and to treat it like a tutor helping to verify what you did and explaining concepts you're not grasping.

Unreal 5.8 ships Epic's `ModelContextProtocol` plugin. Enable a checkbox and your agent can start PIE,
inspect live actors, and read real compiler errors — Ask it *"why isn't this working?"* and it can go look.

## The Labs

| Ch | Build | key bits |
|---|---|---|
| 0 | Setup *(pre-work — do this first)* | The install is bigger than you think |
| 1a | A target dummy, turning slowly | `.generated.h` order; components and attachment |
| 1b | The dummy's meshes move to a Blueprint | C++ owns behaviour, Blueprint owns data |
| 2 | Give it health | lifecycle methods vs. the ctor |
| 3 | You, and you can shoot | Which of six framework classes owns this |
| 4 | Hits land, damage numbers pop | The collision matrix has two sides |
| 5 | The dummy shoots back | Composition |
| 6 | Three dummies: AOE, homing missiles, spread shot |
| 7 | Attacks driven by animation timing, via montage notifies |

Chapter 0 through 2 are the most important.

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
| `CombatGym/` | The Unreal project |
| `AGENTS.md` | Tutor-mode rules for your AI assistant |
| `MCP_NOTES.md` | How to drive the editor over MCP — for your assistant |

Chapters 1–6 need **zero binary assets** — the gym is built from engine
primitives. Chapter 7 pulls animation content from the engine template, and
it's gitignored.

Chapter checkpoints are git tags: branch from `chNN-start`, diff against
`chNN-solution` when you're stuck. Try not to look early — the checkpoint is
the only honest signal you'll get about whether it stuck.

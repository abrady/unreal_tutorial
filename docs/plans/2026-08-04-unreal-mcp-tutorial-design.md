# Unreal + MCP Tutorial — Design

**Date:** 2026-08-04
**Author:** Aaron Brady (abrady)
**Audience:** DRE (Developer Relations Engineering), Games
**Status:** Draft — design agreed in brainstorming, two open risks below

---

## Goal

Get DRE engineers from zero Unreal to competent enough to debug a partner's
project, using the engine's built-in MCP as the primary learning instrument.

Success is **not** "they finished the lab." Success is "three weeks later they
can open an unfamiliar UE project and orient themselves."

---

## Audience

Strong engineers, near-zero Unreal. DRE roles are defined internally as
*"similar to a Forward Deployed Engineer… the caliber of engineer you would
find as a technical director or CTO at a game studio."*

This is the single most important design constraint. It means:

- **No scaffolding on programming.** They know C++, callbacks, composition.
- **Heavy scaffolding on Unreal-specific idioms.** Reflection, GC, the CDO,
  the gameplay framework class carousel, the build loop.
- **C++ first.** Confirmed with the team. Blueprint enters only at the
  C++/BP boundary, which is itself a lesson.
- Expertise reversal effect applies: worked examples help them on UE
  specifics and *hurt* them on general architecture. Fade fast.

---

## Prior art (why this design, and why it's small)

### The failure history

This project has been proposed and abandoned three times:

| When | What | Outcome |
|---|---|---|
| May 2022 | "Unreal Training - information request" (unrealquestions) | Nothing shipped |
| Mar 2023 | "XR Game Engine Fundamentals Bootcamp" (xr.tech.team) | **Shipped — in Unity.** 120+ completions |
| Oct 2023 | "Unreal Engine Fundamentals Bootcamp - Gauging interest" | Never ran |
| Sep 2023 | "Unreal bootcamp?" (dreteam — our own team) | Nothing shipped |

There is still no Unreal course in the Eng Bootcamp library. The Immersive 3D
Learning Path lists exactly one hands-on engine course: Intro to **Unity**.

**The pattern: single labs shipped. Curricula died.** All three Unreal attempts
were framed as syllabus/bootcamp/curriculum. Both Unity wins were one
self-contained lab.

This design is therefore deliberately scoped as **one half-day lab that is
complete and useful on its own**, with take-home chapters as optional
extension. We earn chapters 5+ with evidence from chapters 1–4.

### Formats to copy

- **Unity Bootcamp Lab** (internal wiki) — linear, ends with "controller fires
  balls," then *"Congratulations! You have finished the lab."*
- **"Meta XR Unity MCP — Let's make a game"** (Aug 2025, Connect workshop) —
  Whack-A-Mole built with Claude Code + Unity MCP. This is essentially our
  project, in Unity, already shipped. **Read before building.**

### Adjacent tooling

- **UnrealMCP** (VR Integrations, May 2026) — internal Unreal editor MCP.
  Believed VR-focused. Superseded as a decision by the first-party finding below.
- **AI Agentic Loop for Unreal Rendering Optimization on Quest 3**
  (VR Integrations, Apr 2026) — Claude driving cook/deploy/profile loops.

---

## Which MCP: Epic's first-party, verified on the local 5.8 tree

**Decision: use the engine's built-in MCP, not Possess.**

UE 5.8 ships `Engine/Plugins/Experimental/ModelContextProtocol` — *"Anthropic MCP
(Model Context Protocol) server implementation for Unreal Engine,"* by Epic Games.
Verified directly against `~/ue58-fresh` (`MajorVersion 5, MinorVersion 8`,
branch `Partner-Oculus-UE5`).

What was confirmed by reading the source:

| Property | Value |
|---|---|
| Transport | HTTP + JSON-RPC 2.0, plus SSE and DELETE routes |
| Default endpoint | `http://localhost:8000/mcp` |
| Config | `UModelContextProtocolSettings`, `EditorPerProjectUserSettings` |
| Auto-start | `bAutoStartServer = false` — **must be enabled** |
| Tool discovery | `bEnableToolSearch = true` — `tools/list` returns only `list_toolsets`, `describe_toolset`, `call_tool` |
| Toolsets shipped | 26, including Editor, AIModule, GAS, UMG, StateTree, LiveCoding, AutomationTest, Niagara, PCG, Physics |
| PIE control | `StartPIE`, `StopPIE`, `IsPIERunning` — all `AICallable` |
| Inspection | `CaptureViewport` returns a screenshot *plus* per-actor labels, classes, screen coords, and world positions |
| Extensibility | Python (`unreal.ToolsetDefinition` + `@toolset_registry.tool_call`) and C++ (`UFUNCTION(meta=(AICallable))`) |

### Why this beats Possess for a tutorial

1. **Setup friction collapses.** No plugin clone, no plugin build, no
   `Plugins/` directory. Enable a checkbox and set two ini values. Chapter 0
   was the single biggest threat to the half day; this removes most of it.
2. **It survives engine bumps.** Epic maintains it. The grader will still be
   brittle, but it won't rot the way a third-party plugin does.
3. **It resolves the org question.** First-party is the neutral choice — no
   consolidation risk against VR Integrations' UnrealMCP, and no dependency on
   a personal GitHub repo.
4. **It's portable across vanilla Epic and the Meta fork,** because it's an
   Epic plugin rather than a Meta addition. The lab runs on either.
5. **It's what partners will use.** Teaching the first-party tool is directly
   on-mission for DRE.

### What we give up

Possess is more mature — ~1000 dogfooded actions, richer Blueprint authoring,
live Behavior Tree and Blackboard readback, structured UBT build polling. If a
take-home chapter needs something first-party can't do, Possess remains
available as an add-on. It is not a half-day dependency.

### New constraint this introduces

`bEnableToolSearch` defaults to `true`, so tools are **not** natively
registered — they're discovered via `list_toolsets` / `describe_toolset` and
invoked through `call_tool`. The grader must either set it to `false` or
dispatch through `call_tool`. Pin this in `SETUP.md`; a mismatch here looks
like "the tool doesn't exist."

### Teaching hook worth exploiting

Adding `UFUNCTION(meta = (AICallable))` to a C++ method exposes it as an MCP
tool. That means a learner can extend the agent's capabilities from inside
their own code, in Chapter 1, and immediately see it appear. That flips the
agent from something done *to* them into something they build on — which is
exactly the active engagement the learning research asks for, and it is a
question DRE will field from partners.

---

## Learning-science basis

The obvious design — "watch the MCP build a game, learn by reading along" —
is the one the evidence says fails.

**Bastani et al. 2024** (Wharton, ~1000 students, three arms):

| Arm | Practice performance | Unassisted exam |
|---|---|---|
| No AI | baseline | baseline |
| Unrestricted GPT-4 | **+48%** | **−17%** |
| Guardrailed "GPT Tutor" | positive | no harm |

Unrestricted AI assistance produced large gains that evaporated — and
reversed — once the assistance was removed. The guardrailed tutor, which gave
hints instead of answers, preserved the gains.

Supporting literature, all pointing the same way:

- **Worked example → completion problem → independent problem**
  (Sweller; van Merriënboer). Faded guidance beats both full worked examples
  and unsupported problem-solving for novices.
- **Expertise reversal** (Kalyuga) — scaffolding that helps novices hurts the
  competent. Fade per-topic, not globally.
- **Productive failure** (Kapur) — attempt-then-instruct beats
  instruct-then-practice for conceptual transfer. Requires relevant prior
  knowledge to activate, which this audience has.
- **Retrieval practice** (Roediger & Karpicke) — the "did I learn it" check
  must be unassisted and effortful.
- **Guided discovery > pure discovery** (Mayer 2004) — and neither is
  "watching someone else do it."

### Design consequences

1. **The MCP's safe superpower is inspection, not authoring.** Using an agent
   to observe, explain, and diagnose does not produce the Bastani effect.
   Using it to author does. The first-party toolsets are strong here — PIE
   control, per-actor viewport capture with world positions, live compiler
   errors via the LiveCoding toolset.
2. **Guardrail the agent during chapters, unleash it after.** This is the
   GPT-Tutor arm, implemented as a repo-level agent instruction file.
3. **Every chapter ends in an unassisted, objectively-graded checkpoint.**

---

## Core idea: the lab is a test suite

Each chapter ships **failing automated checks**. The chapter is done when they
go green.

The grader is a plain HTTP client speaking MCP JSON-RPC to
`localhost:8000/mcp` — the same protocol the AI client uses, with no AI in the
loop. Written as pytest tests, because this audience already speaks that.

```
pytest grader/checks/ch01_actor.py
```

A check looks like:

```
system_control  start_pie
control_actor   teleport  <PlayerPawn> -> PressurePlate
inspect         actor     BP_Door  -> assert Rotation.Yaw ~= 90
system_control  stop_pie
```

Why this works:

- **Unassisted retrieval practice** with objective feedback, no instructor.
- **Bounded productive failure** — you always know how close you are, so
  struggle stays productive instead of becoming despair.
- The grader and the learner's agent hit the *same* interface, so
  "why is check 3 failing?" is answerable from live PIE state, not guesswork.
- It doubles as **Kirkpatrick Level 2 (learning) telemetry** — per-chapter
  pass/fail data that no internal engineering training program currently
  produces. Internal measurement today is Bootcamp "would you recommend"
  smile-sheets.

It is also, incidentally, a harness that drives a real UE editor through
scripted scenarios and asserts on live state — i.e. a partner-repro tool
wearing a tutorial costume. That reusability is part of the pitch.

---

## No headset required

Hard requirement for the half day.

- Vanilla Epic Unreal. **No MetaXR plugin, no Android/Quest toolchain** in the
  half day — that alone saves substantial setup time and disk.
- Desktop PIE only.
- Stated plainly in the README: *you need a PC that can run Unreal. You do not
  need a headset.*
- All VR content lives behind a clearly-marked optional take-home appendix.

The VR bridge is architectural, not incidental: Chapter 4 introduces an
`IInteractable` interface. The optional VR capstone swaps the pawn and leaves
every interaction implementation untouched. That is the actual lesson about
building VR-ready code, and it's teachable without a headset.

---

## Structure

### Chapter 0 — Setup (async pre-work, gated)

**This must be done before the half day starts or the attendee is dead.**

Unreal install is enormous and the first compile is long. Setup gets its own
verification script; a green `pytest grader/checks/ch00_setup.py` is the
ticket to the session.

Covers: engine acquisition, repo clone, first full build, enabling the
built-in `ModelContextProtocol` plugin, setting `bAutoStartServer=True` and
`bEnableToolSearch=False`, client registration against `localhost:8000/mcp`,
handshake confirmed.

Materially lighter than it would have been with a third-party plugin — no
plugin clone and no plugin build. The engine build is still the long pole.

### Half day — 4 chapters

Roughly 45 minutes each plus breaks.

**Ch 1 — The iteration loop and your first Actor**
Reflection macros (`UCLASS`/`UPROPERTY`/`UFUNCTION`), the `.generated.h`
ordering rule, `AActor`, components, live coding vs. full rebuild.
Build: `ARotatingPlate` — an actor with a mesh that rotates on Tick.
Front-loads the #1 newcomer killer (the build loop) while the task is trivial
enough that any failure is diagnosable.
*MCP role:* the `LiveCodingToolset` for hot-patching, and the first experience
of the agent explaining a real compiler error.
*Stretch:* mark one method `UFUNCTION(meta = (AICallable))`, restart the
client, and watch your own C++ show up as a tool the agent can call. Cheap to
do, and it reframes the agent as something you extend.
*Grader:* class exists, spawns, has a mesh component, rotation changes across
two PIE samples.

**Ch 2 — Lifecycle, GC, and the CDO trap**
Constructor vs `BeginPlay` vs `Tick` vs `OnConstruction`. Why the constructor
runs on the Class Default Object. `UPROPERTY()` vs. raw pointer and garbage
collection. `TObjectPtr`.
Build: deliberately break it — a raw pointer member that gets collected —
then fix it. **Productive failure, explicitly staged.**
This is *the* chapter for this audience. Everyone with a C++ background gets
burned here, and it's the line between copying Unreal tutorials and
understanding Unreal.
*Grader:* object survives a forced GC; a specific value is set in `BeginPlay`,
not the constructor.

**Ch 3 — Gameplay framework and Enhanced Input**
`GameMode` / `GameState` / `PlayerController` / `Pawn` / `Character`,
possession. Enhanced Input: InputAction assets, mapping contexts, C++ binding.
Build: a first-person character you can walk around with.
Much is template-provided; the learning is *which class owns what*.
*Grader:* PIE, inject input, assert pawn location changed.
*Risk:* most likely chapter to overrun. Ship the Character largely done and
have them wire only the input binding.

**Ch 4 — Collision, overlap, and the interaction interface**
Collision channels/profiles/responses (the response matrix genuinely confuses
people), overlap events, `IInteractable` as a `UINTERFACE`,
`BlueprintNativeEvent` and the C++/Blueprint boundary.
Build: pressure plate opens the door; a pickup implements the same interface.
*Grader:* PIE, teleport pawn onto plate, assert door yaw; overlap the pickup,
assert consumed.
*Payoff:* "Congratulations, you built a thing."

### Take-home chapters (optional, self-serve)

Delegates and game state · UMG HUD from C++ · AI patrol with NavMesh /
Behavior Tree / Blackboard (the best showcase of MCP live inspection) ·
audio · packaging a standalone build · **optional VR pawn swap** (headset
required, explicitly marked).

---

## Repo layout

```
unreal_tutorial/
  README.md                     front door
  SETUP.md                      Chapter 0, gated pre-work
  AGENTS.md / CLAUDE.md         tutor-mode guardrail
  docs/
    plans/                      this document
    facilitator-guide.md        for whoever runs the half day
    slides/                     deck source
  chapters/
    01-iteration-loop/README.md
    02-lifecycle-and-gc/README.md
    03-framework-and-input/README.md
    04-collision-and-interaction/README.md
  Lab01_FirstRoom/              the UE project
    Lab01.uproject
    Source/Lab01/
    Content/
    Config/                     MCP plugin + server settings live here
  grader/
    mcp_client.py               thin JSON-RPC/HTTP MCP client
    conftest.py
    checks/
      ch00_setup.py … ch04_interaction.py
```

**Chapter checkpoints as git tags:** `ch01-start`, `ch01-solution`, …
Learners branch from `chNN-start`; when stuck, diff against `chNN-solution`.

**Deliberately content-light.** Use engine primitives (Cube, Cylinder) and
near-zero binary assets so the repo stays git-friendly and needs no LFS. This
is a real constraint on lab design, not an afterthought.

---

## Tutor-mode guardrail

Repo-root `AGENTS.md` / `CLAUDE.md`, implementing the Bastani GPT-Tutor arm.

**During a chapter, the agent may:**
explain concepts · inspect live editor and PIE state · diagnose compile
errors · point at documentation · ask Socratic questions.

**During a chapter, the agent may not:**
write the chapter's solution · edit files under `Source/` for the current
chapter · read or check out `chNN-solution`.

**After the chapter's checks pass:** no restrictions. Compare against the
reference, ask for a critique, refactor. This is deliberate — the point is not
to keep people away from AI, it's to sequence it so the learning survives.

**Honest limitation:** enforcement is soft. Nothing stops someone typing "make
the checks pass." This is a norm backed by a config file, for a willing
internal audience. The reference-solution tags reduce accidental spoiling;
they don't prevent deliberate shortcutting. That tradeoff is acceptable and
should be stated to learners rather than hidden — the study result itself is
the persuasive argument.

---

## Deliverables

1. `README.md` — front door, honest about time and prerequisites
2. `SETUP.md` — gated pre-work with its own green check
3. Four chapter READMEs — **steps only**
4. Grader: MCP client + check suites
5. Slide deck — **concepts only** (see split below)
6. Facilitator guide

**Deck vs. README split, strictly observed:** the deck carries the mental
model (what a `UObject` is, what the CDO is, the collision response matrix).
The README carries the steps. Never both — duplication guarantees drift.

---

## Open questions / risks

| # | Risk | Impact | Status |
|---|---|---|---|
| 1 | ~~Possess on UE 5.8~~ | — | **Resolved.** Moot — using the engine's first-party MCP. |
| 2 | ~~Does 5.8 ship a first-party MCP?~~ | — | **Resolved — yes.** Verified in `~/ue58-fresh`. See the MCP section. |
| 3 | ~~UnrealMCP overlap~~ | — | **Resolved.** First-party is the neutral choice; no consolidation exposure. |
| 3a | **First-party MCP is Experimental** (`IsExperimentalVersion: true`, `NoRedist`). API churn is likely between engine versions. | Grader and chapter text may break on upgrade | Accepted. Pin the engine version in `SETUP.md`. `NoRedist` is fine — internal only. |
| 3b | **`bEnableToolSearch` / `bAutoStartServer` defaults** are both wrong for our use. | Silent "tool not found" confusion | Pin both in `SETUP.md` and assert them in `ch00_setup.py`. |
| 4 | **Why did this fail three times?** | Highest-value de-risking conversation available | Find the XR Game Engine Fundamentals owners and ask. |
| 5 | **Grader fragility.** Driving a live editor is brittle; engine version bumps will break checks. | Ongoing maintenance | Keep assertions coarse. Budget maintenance explicitly. |
| 6 | **Ch 3 overrun.** Most content-dense chapter. | Blows the half-day budget | Pre-build the Character; learner wires input only. |
| 7 | **Meta Training Governance** (wiki updated 2026-07-20) may impose course-category / registration obligations. | Process | Check before launch. |
| 8 | **Vanilla Epic vs. Meta fork.** Local tree is `Partner-Oculus-UE5`. | Lower than assumed | **Largely resolved.** The MCP plugin is an Epic first-party plugin present in both, so the lab is portable. Target whatever the team already has built; note portability in `SETUP.md`. |

---

## Measurement

Since the auto-grader produces per-chapter completion data, commit to
measuring properly — no internal engineering program currently does.

- **Level 1 (reaction):** post-lab survey. Copy the Bootcamp Live Results
  format.
- **Level 2 (learning):** per-chapter checkpoint pass rate and time-to-green,
  straight from the grader. This is the differentiator.
- **Level 3 (behavior):** the real test. At 4–6 weeks, can they orient in an
  unfamiliar UE project? Kirkpatrick guidance warns behavior change requires
  manager reinforcement and organizational conditions — so this needs
  Matt's buy-in, not just attendance.

Instrument time-to-green per chapter from day one. It tells us which chapter
to cut or split before we invest in chapters 5+.

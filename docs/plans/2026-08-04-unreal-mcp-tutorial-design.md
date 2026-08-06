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

## What they build: a combat gym

A room with target dummies. You shoot them, damage numbers pop off, and the
dummies shoot back with different attacks.

This replaces an earlier design (a first-person room with a pressure plate and
a door). The gym is better for three concrete reasons:

1. **Components become the centre of the design, not a bolt-on.** An ability
   component attached to a dummy is the canonical composition example — swap
   the component, swap the behaviour, never touch the dummy class. The door
   design had no natural home for the component model, which is arguably the
   single most important architectural pattern in Unreal.
2. **Nothing is throwaway.** Every chapter's output survives into the final
   gym. The door design opened with a rotating plate that got abandoned.
3. **The CDO lesson gains real stakes.** "Why does setting Health in the
   constructor change every dummy, but setting it in BeginPlay change only
   one?" is a consequence someone will actually hit, unlike a synthetic flag.

It is also closer to what DRE partners actually ship, and it translates to VR
more naturally than a pressure plate does.

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
2. **It survives engine bumps.** Epic maintains it, so it won't rot the way a
   third-party plugin would.
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
invoked through `call_tool`. Either set it to `false` or dispatch through
`call_tool`. Pin this in `SETUP.md`; a mismatch here looks
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
4. **Delegate the repetition, not the learning.** Once a learner has done
   something once by hand, doing it four more times teaches nothing — that's
   the agent's job, and every chapter ends with something to hand off.
   This resolves the tension between the guardrail and the project's actual
   goal (*"most importantly I want people to use the MCP to learn"*): the
   effortful first pass is preserved, and the agent becomes the thing you
   graduate to rather than something withheld.
   It also surfaces the MCP's limits, which is first-hand knowledge DREs will
   be asked for. "Can it author an InputAction asset?" is better answered by
   someone who tried — and the answer to "can it create a level?" is no.

---

## Core idea: every chapter has explicit, checkable criteria

Each chapter ships a `CHECKS.md` next to its README — a short rubric the
learner's assistant verifies against the running editor with its own MCP
tools.

```markdown
**4. It rotates.**

    get_actor_transform → note rotation.yaw
    wait ~1 second
    get_actor_transform → yaw must have changed by ≥5°

Two usual causes when it fails:
  • PrimaryActorTick.bCanEverTick was never set in the constructor
  • Tick doesn't actually apply a rotation
```

The criteria are specific and numeric, so "looks good to me" isn't available
— the assistant has to read a yaw value twice and compare them. And the
verdict comes from the engine rather than from either party's opinion.

Each rubric doubles as documentation of the MCP behaviours that chapter needs,
so the assistant doesn't rediscover them live. The full set is in
[`docs/MCP_NOTES.md`](../MCP_NOTES.md).

### Why not a program that grades

The first version of this was 1,750 lines of Python: an MCP client, a helper
layer, and six suites of assertions. It worked — 21 checks green against a
live 5.8.1 editor. It was deleted, for two reasons.

**It required Python.** Windows doesn't ship `python3`, and Unreal work is
Windows-heavy, so the grader would have added an install step on the platform
most of the audience uses. For a lab whose entire on-ramp is "install Unreal,
say start lesson one," that's a bad trade.

**It was the most fragile thing in the repo.** Getting it working took hours
of fixing schema mismatches, PIE-ordering constraints, JSON double-parsing and
timing races. Every one of those is a bug a learner could hit alone on a
Thursday night. A grader that breaks is worse than no grader, and this one had
more moving parts than the lab it graded.

**What we gave up:** machine-enforced objectivity. An agreeable assistant can
be lenient in a way `assert` can't. That's a real loss, and the mitigation is
only partial — the criteria are written down and numeric, so leniency has to
be deliberate rather than accidental.

It's a smaller loss than it first appears, though. The original argument for
an independent grader assumed a facilitated session with an *unassisted*
checkpoint. In the delivery model this actually has — mostly self-guided,
days later, with the assistant as the learner's only companion — there was
never an unassisted moment to protect.

**Also considered:** Unreal's own automation tests. They can't work here.
They compile as part of the learner's module, so a test asserting "does
`ATargetDummy` exist" won't compile when the answer is no.

### What this costs the measurement story

The Python grader would have produced per-chapter pass/fail and time-to-green
automatically — Kirkpatrick Level 2 data that no internal engineering program
currently has. Without it, that has to come from the assistant reporting
progress, or from a lightweight self-report at the end.

That's a genuine downgrade in rigour and it should be stated plainly rather
than quietly dropped from the pitch.

---

## No headset required

Hard requirement for the session.

- Vanilla Epic Unreal. **No MetaXR plugin, no Android/Quest toolchain** in the
  session — that alone saves substantial setup time and disk.
- Desktop PIE only.
- Stated plainly in the README: *you need a PC that can run Unreal. You do not
  need a headset.*
- All VR content lives behind a clearly-marked optional take-home appendix.

The VR bridge is architectural, not incidental. Chapter 5 puts attacks behind
an **ability component**, and Chapter 3 puts firing behind an **Enhanced Input
action**. Neither knows what triggered it. Swapping the desktop pawn for VR
hands changes the pawn and the mapping context, and touches no combat code.
That is the actual lesson about building VR-ready systems, and it is teachable
without a headset.

Combat also translates to VR far more naturally than a pressure plate does,
which makes the claim more honest than it was under the previous design.

---

## Structure

### Chapter 0 — Setup (async pre-work, gated)

**This must be done before the session starts or the attendee is dead.**

Unreal install is enormous and the first compile is long. Setup gets its own
verification script; a green ask your assistant to check your work is the
ticket to the session.

Covers: engine acquisition, repo clone, first full build, enabling the
built-in `ModelContextProtocol` plugin, setting `bAutoStartServer=True` and
`bEnableToolSearch=False`, client registration against `localhost:8000/mcp`,
handshake confirmed.

Materially lighter than it would have been with a third-party plugin — no
plugin clone and no plugin build. The engine build is still the long pole,
which is why the Epic Launcher binary is strongly recommended over a source
engine (see the BuildId note under Risks).

### The session — 5 chapters, ~5 hours

**Not a half day.** Chapters 1–2 run ~45 minutes; 3–5 run 60–90. Called out
honestly in the README rather than discovered at hour four.

**Ch 1 — The iteration loop, and the dummy**
Reflection macros (`UCLASS`/`UPROPERTY`/`UFUNCTION`), the `.generated.h`
ordering rule, `AActor`, **components and attachment**, tick opt-in, live
coding vs. full rebuild.
Build: `ATargetDummy` — a cylinder body with a sphere head **attached** to it,
rotating slowly so you can practise hitting a moving target.
The two-component build is deliberate: it forces `SetupAttachment`, root
component semantics, and the transform hierarchy while the task is still
trivial enough that any failure is diagnosable. Front-loads the #1 newcomer
killer (the build loop) at the same time.
*MCP role:* the `LiveCodingToolset` for hot-patching, and the first experience
of the agent explaining a real compiler error.
*Stretch:* mark one method `UFUNCTION(meta = (AICallable))`, restart the
client, and watch your own C++ show up as a tool the agent can call.
*Grader:* class exists, spawns, has a two-node component tree with the head
parented to the body, and rotation changes across two PIE samples.

**Ch 2 — Health, the CDO, and the collector**
Constructor vs `BeginPlay` vs `Tick` vs `OnConstruction`. Why the constructor
runs on the Class Default Object. `UPROPERTY()` vs. raw pointer and garbage
collection. `TObjectPtr`, `TWeakObjectPtr`.
Build: give the dummy `Health`/`MaxHealth`, and a `UDamageHistory` object that
records hits.
Part A is the CDO with stakes: setting health in the constructor changes the
default for *every* dummy; setting it in `BeginPlay` changes one.
Part B is staged failure: store the damage history in a plain pointer, force a
collection, watch it vanish. Then add `UPROPERTY()`.
This is *the* chapter for this audience. The damage history also carries
forward — Chapter 4 reads it to draw damage numbers.
*Grader:* constructor saw no world; `BeginPlay` did; a collection ran; the
damage history survived it.

**Ch 3 — You, and you can shoot**
`GameMode` / `GameState` / `PlayerController` / `PlayerState` / `Pawn` /
`Character`, possession, and the server/client ownership split. Enhanced
Input: InputAction assets, mapping contexts, C++ binding. `SpawnActor`.
Build: firing. The `ALabCharacter` (camera, movement) is **given**; the
learner wires `IA_Fire` and spawns an `AProjectile` with a
`UProjectileMovementComponent`.
Pre-building the character is a deliberate scope cut — character boilerplate
teaches little and eats the clock. The projectile reinforces components.
*Grader:* PIE, inject fire input, assert a projectile exists in the world.

**Ch 4 — Hits, damage, and floating numbers**
Collision channels/profiles/responses (the response matrix genuinely confuses
people), hit vs. overlap events, `ApplyDamage`/`TakeDamage`, `DrawDebugString`.
Build: projectiles damage dummies, and debug damage numbers pop off the hit.
The payoff moment — the first time the gym feels like a game.
*Grader:* PIE, fire at a dummy, assert health decreased and the damage history
recorded the hit.

**Ch 5 — Ability components: the dummy shoots back**
`UActorComponent` vs `USceneComponent`, component lifecycle and
`TickComponent`, spawning from a component, and **composition over
inheritance** as Unreal's central architectural pattern.
Build: a `UAbilityComponent` base and a `UCannonAbilityComponent` that fires
back at the player on a cooldown. Attach it to a dummy and the dummy is
suddenly dangerous — without editing `ATargetDummy` at all.
This is the components chapter and the session climax. It is also the chapter
that makes the VR claim true: the ability doesn't know what triggered it.
*Grader:* PIE, wait past the cooldown, assert a dummy-spawned projectile
exists and the player took damage.

### Take-home chapters (optional, self-serve)

Substantial — 60–90 minutes each, not a quick afternoon. Said plainly in the
README.

**Ch 6 — Three dummies, three powers.** An AOE dummy, a homing-missile dummy,
and a spread-shot dummy over the Chapter 5 base. Virtual dispatch,
data-driven configuration, and `UPROPERTY(EditAnywhere)` for designer-tunable
values.

**Ch 7 — Montages and AnimNotify.** Drive attacks off animation timing rather
than a cooldown timer. Copies Epic's `Variant_Combat` montages
(`AM_ComboAttack`, `AM_ChargedAttack`) from `TP_ThirdPerson`; the learner
writes their own `AnimNotify` classes and wires them to the ability system.
Epic's `AnimNotify_DoAttackTrace` is shown as the reference implementation
**after** they build theirs.

Also available: UMG health bars · AI with NavMesh / Behavior Trees /
Blackboards (the best showcase of MCP live inspection) · audio · packaging ·
**optional VR pawn swap** (headset required, explicitly marked).

### Asset strategy

**Chapters 1–5 require zero binary assets.** The gym is `Plane` + `Cube`; the
dummy is `Cylinder` + `Sphere`; projectiles are `Sphere`. All from
`/Engine/BasicShapes`. The repo stays git-friendly and needs no LFS.

Binary content enters only at **Chapter 7**, which is take-home, so the 7.8 MB
of `TP_ThirdPerson` combat content is opt-in for the people who want it.

Verified: the engine ships no mannequin in `Engine/Content` (only
`SkeletalCube` and `DefaultSkeletalMesh`, neither animated). The mannequin and
montages live in `Templates/TP_ThirdPerson/Content/Variant_Combat/`.

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
    02-health-and-gc/README.md
    03-shooting/README.md
    04-damage/README.md
    05-ability-components/README.md
    06-powers/README.md            take-home
    07-montage-notifies/README.md  take-home
  Lab01_FirstRoom/              the UE project
    Lab01.uproject
    Source/Lab01/
    Content/
    Config/                     MCP plugin + server settings live here
  chapters/NN-name/
    README.md                   the chapter, for the learner
    CHECKS.md                   the rubric, for the assistant
  docs/MCP_NOTES.md             how to drive the editor, for the assistant
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
| 3b | **`bEnableToolSearch` / `bAutoStartServer` defaults** are both wrong for our use. | Silent "tool not found" confusion | Pin both in `SETUP.md` and check them in `chapters/00-setup/CHECKS.md`. |
| 3c | **The MCP cannot create or save-as a level.** Verified against 5.8.1: `save_assets` can't see a temp map, `load_level` needs an existing asset, and `create_level_instance` references one. There is no `new_level`. | Level authoring is a manual editor step | Accepted. `Lvl_FirstRoom.umap` is committed to the repo so nobody has to recreate it. Worth surfacing to learners as a real edge of the tool. |
| 3d | **Property writes need a saved level.** `set_properties` returns `False` for actors in an unsaved temp map. | Ch 2's per-instance override check needs a real level | Resolved by 3c — the committed level carries a dummy with `MaxHealth` pre-overridden. |
| 4 | **Why did this fail three times?** | Highest-value de-risking conversation available | Find the XR Game Engine Fundamentals owners and ask. |
| 5 | **Grader fragility.** Driving a live editor is brittle; engine version bumps will break checks. | Ongoing maintenance | Keep assertions coarse. Budget maintenance explicitly. |
| 6 | **Ch 3–5 overrun.** The three combat chapters are 60–90 min each, not 45. | Session runs ~5h, not a half day | Accepted and stated plainly. `ALabCharacter` is pre-built; if it still slips, Ch 5 moves to take-home. |
| 9 | **Scope creep from the gym.** Combat invites "just one more power." | Session bloat | Ch 6–7 are firmly take-home. The in-session gym is one dummy, one player weapon, one enemy ability. |
| 7 | **Meta Training Governance** (wiki updated 2026-07-20) may impose course-category / registration obligations. | Process | Check before launch. |
| 8 | **Vanilla Epic vs. Meta fork.** Local tree is `Partner-Oculus-UE5`. | Lower than assumed | **Largely resolved.** The MCP plugin is an Epic first-party plugin present in both, so the lab is portable. Target whatever the team already has built; note portability in `SETUP.md`. |

---

## Measurement

No internal engineering program currently measures beyond a smile sheet, and
we should still try — but note the caveat under "Core idea": without an
automated grader, per-chapter data now depends on the assistant reporting it
rather than being produced as a side effect.

- **Level 1 (reaction):** post-lab survey. Copy the Bootcamp Live Results
  format.
- **Level 2 (learning):** per-chapter completion, reported by the assistant
  as learners work through the checks. Weaker than the automated version
  would have been — see the note above — but still more than a smile sheet.
- **Level 3 (behavior):** the real test. At 4–6 weeks, can they orient in an
  unfamiliar UE project? Kirkpatrick guidance warns behavior change requires
  manager reinforcement and organizational conditions — so this needs
  Matt's buy-in, not just attendance.

Instrument time-to-green per chapter from day one. It tells us which chapter
to cut or split before we invest in chapters 5+.

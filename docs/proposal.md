# Demystifying Unreal

**A one-day lab for experienced engineers.**

Aaron Brady (abrady), DRE Games. 5 August 2026.

> Also lives as a Google Doc:
> https://docs.google.com/document/d/19fW-rh3JKgqkSAE9vCuiSmpHUuk3YRdisy2Xp-v5zqA/edit
> Keep the two in sync, or delete one.

## The ask

**Schedule a pilot: 6–8 DRE engineers, one session of roughly 5 hours, on a
date you pick.** The lab is built and the grader runs green. What it needs now
is learners, plus about two days of polish. I am not asking for headcount or
budget.

## The problem

DRE engineers support partners shipping real Unreal titles, and we have no
internal Unreal course. The Eng Bootcamp Immersive 3D learning path lists
exactly one hands-on engine course, and it is Unity.

This has been proposed three times since 2022 and never shipped: May 2022,
October 2023, and once by our own team in September 2023. Each attempt was
framed as a bootcamp or a curriculum.

The one adjacent effort that *did* ship, XR Game Engine Fundamentals in March
2023 with 120+ completions, was a single self-contained lab. **Labs ship.
Curricula die.** So this is deliberately one lab, complete and useful on its
own, with everything else marked optional take-home.

## Why experienced engineers stall on Unreal

DRE roles are speced at the caliber of a technical director or CTO at a game
studio. These people know C++, callbacks and composition cold. They are slow
in Unreal because Unreal has roughly six idioms that no tutorial names out
loud, and most public tutorials teach around them rather than through them.

| The idiom | What it costs you until someone names it |
| --- | --- |
| Reflection and the build loop | Header ordering rules, and Live Coding versus a full rebuild |
| The Class Default Object | Your constructor runs on an object that is not your object |
| Garbage collection | A raw pointer compiles, works, then vanishes mid-session |
| The gameplay framework | Six classes, and no obvious rule for which one owns a given thing |
| The collision matrix | Two actors must independently agree before a hit registers |
| Composition over inheritance | Unreal's central architectural pattern, usually discovered late |

Each of the five in-session chapters is one of these, taught as a consequence
the learner hits on purpose rather than a fact they are told. They build a
combat gym: shoot a target dummy, watch damage numbers pop, then attach a
component and the dummy shoots back.

## What makes it verifiable: the lab is a test suite

Every chapter ships failing automated checks, and you are done when they go
green. The grader does not read the learner's source. It boots their project,
starts Play-In-Editor, fires a projectile at a dummy, and asks the live editor
what actually happened, over the Model Context Protocol server that Epic ships
first-party in UE 5.8.

That produces something no internal engineering training program currently
has: **objective per-chapter pass/fail and time-to-green for every attendee.**
Kirkpatrick Level 2 learning data, not a post-session smile sheet. It tells us
which chapter to cut or split before we invest another hour in it.

Incidentally, the grader is a harness that drives a real UE editor through
scripted scenarios and asserts on live state. That is a partner-repro tool
wearing a tutorial costume, and it outlives the lab.

## The AI angle, stated honestly

The learner's agent is wired into the same live editor the grader uses, so
"why is check 3 failing?" is answerable from real state. But during a chapter
the agent is guardrailed to explain, inspect and diagnose. It will not write
the solution.

That is not a preference. Bastani et al. (2024) ran roughly 1,000 students
across three arms. Unrestricted GPT-4 lifted practice performance **+48%** and
then dropped unassisted exam performance **−17%**, leaving those students worse
off than if they had never had it. A guardrailed hint-giving tutor kept the
gains with no harm. We are building the third arm, and once the checks are
green the restrictions lift entirely.

The complement matters just as much: **delegate the repetition, not the
learning.** Wire the first input action by hand, then have the agent add the
next two. That is the working pattern DRE engineers will actually use, and
pushing on it surfaces where the tooling breaks, which is exactly what
partners will ask them about.

## Status

| Component | State |
| --- | --- |
| Chapters 1–5 (in-session) and 6–7 (take-home) | Written |
| Grader: MCP client plus six check suites | 21 checks green against a live UE 5.8.1 editor |
| Unreal project: level, lighting, player character, input assets | Committed |
| Reference solutions, chapters 1–5 | Committed and tagged |
| Slide deck (concepts) | Drafted, needs a cleanup pass |
| Facilitator guide, per-chapter start tags, grader instrumentation | Remaining, about two days |

No headset, no MetaXR plugin and no Android toolchain are required. Vanilla
Epic UE 5.8+ and the Meta fork both work, because the MCP plugin is Epic's.
Attendees need a machine that runs Unreal and a completed Chapter 0, which has
its own green check as the ticket in.

## Risks, and what I have done about them

| Risk | Mitigation |
| --- | --- |
| The session runs about 5 hours, not a half day | Stated plainly up front. The player character is pre-written to buy back time. If it still slips, Chapter 5 moves to take-home. |
| Epic's MCP plugin is marked Experimental, so its API will churn | Accepted. The engine version is pinned in setup and grader assertions are kept coarse. Maintenance is budgeted, not assumed away. |
| Driving a live editor is inherently brittle | Every schema was verified against a real 5.8.1 editor rather than the docs. Known tool limitations are documented and taught as content. |
| Meta Training Governance may impose registration obligations | To be checked before launch. Flagging it now rather than at launch. |
| Three prior attempts failed for reasons I may be repeating | **Open.** I want to talk to the XR Game Engine Fundamentals owners before the pilot. This is the highest-value de-risking conversation available. |

## What I need from you

1. **A pilot date and a nod to the cohort.** 6–8 volunteers, one block of
   roughly 5 hours, Chapter 0 done beforehand.
2. **Endorsement of the 4–6 week follow-up.** The real success measure is not
   "they finished the lab." It is "three weeks later they can open an
   unfamiliar UE project and orient themselves." Kirkpatrick is explicit that
   behavior change needs manager reinforcement, so that measurement needs your
   backing, not just attendance.
3. **An introduction to whoever owned the 2023 bootcamp attempt**, if you have
   one.

*Full design rationale, prior-art analysis and the complete risk register are
in [docs/plans](plans/2026-08-04-unreal-mcp-tutorial-design.md).*

# Start here

---

### 1. Install Unreal 5.8 or newer

From the [Epic Games Launcher](https://store.epicgames.com/en-US/download).
Big download, so start it now and read on while it runs.

In the install options you can safely deselect **Editor symbols for
debugging** and every target platform except your own — that typically halves
the download.

### 2. Clone and open this folder in VS Code, with your AI assistant

```
git clone https://github.com/abrady/unreal_tutorial.git ~/unreal_tutorial_run
cd ~/unreal_tutorial_run
```


### 3. A quick Unreal architecture intro

Unreal has to make your C++ code work in several unusual contexts:

- The editor needs to expose objects and properties so you can place things
  and tune their behavior.
- The engine needs to serialize the large amount of data associated with
  those objects.
- The build system needs to package the game for platforms such as macOS,
  Windows, Android, and Quest.

Suppose you have a minion enemy. Its core AI and combat behavior might be
implemented as C++ components. You could then create specialized Blueprints
from that C++ class, choose their weapons and aggression settings, and place
them into encounters in the editor. Unreal loads and saves that configuration,
creates the instances during play, and tracks references to Unreal objects for
garbage collection.

That’s why Unreal projects come with some unusual machinery: Unreal Build Tool
(UBT), Unreal Header Tool (UHT), and macros such as `UCLASS`, `UPROPERTY`, and
`GENERATED_BODY`. Together, they connect ordinary C++ to Unreal’s build,
reflection, serialization, editor, and garbage-collection systems. You don’t
need to understand all of that yet; [`Chapter 0`](chapters/00-setup/README.md)
explains the important pieces.

### 4. Read each chapter's README

Each chapter begins with a README that explains what you're building and
introduces the relevant concepts:

- [Before you start](chapters/00-setup/README.md) introduces the lab workflow
  and the machinery behind Unreal C++.
- [Chapter 1a — The iteration loop, and the dummy](chapters/01a-iteration-loop/README.md)
  introduces the compile loop and component model.
- [Chapter 1b — C++ owns behaviour. Blueprint owns data.](chapters/01b-blueprint-boundary/README.md)
  separates C++ behavior from designer-configurable Blueprint data.
- [Chapter 2 — Health, the CDO, and the collector](chapters/02-health-and-gc/README.md)
  explores object lifetimes, the Class Default Object, and garbage collection.
- [Chapter 3 — You, and you can shoot](chapters/03-shooting/README.md)
  introduces the gameplay framework, player input, and projectiles.
- [Chapter 4 — Hits, damage, and floating numbers](chapters/04-damage/README.md)
  covers collision, damage, and gameplay feedback.
- [Chapter 5 — Ability components: the dummy shoots back](chapters/05-ability-components/README.md)
  teaches composition through reusable ability components.
- [Chapter 6 — Three dummies, three powers](chapters/06-powers/README.md)
  extends that component design with three different abilities.
- [Chapter 7 — Montages and AnimNotify](chapters/07-montage-notifies/README.md)
  synchronizes attacks with animation timing.

You don't need to memorize these now, but come back to them as you're learning.

### 5. Use an AI assistant

Devmate, Claude Code, or Cursor. Fire it up and say:

> start lesson one

That's it. Your assistant will find your Unreal installation, read the lesson
plan, and guide you.

If something's wrong, ask it for help. It'll tell you what to do next.

---

## What you're getting into

You'll build a combat gym in C++: a target dummy you can shoot, damage numbers
popping off it, and eventually a dummy that shoots back.

**You do not need a VR headset.** You need a machine that runs Unreal.

**You are not expected to finish in one sitting.** Chapters stand alone and
the lab remembers where you are — come back whenever and tell your assistant:

> Check my work.

It will check your progress, so picking up cold three days later takes about
ten seconds.

## The one rule

Your assistant is wired into the running editor. It can inspect live actors,
read compiler errors, and answer "why is this failing?" from real state.

**It won't write your chapters for you** — see [`AGENTS.md`](AGENTS.md) for
why, and for the one important exception: once you've done something *once*,
delegating the repetition is encouraged.

## If you'd rather do it by hand

[`SETUP.md`](SETUP.md) has the manual version of everything the setup script
does. You shouldn't need it, but it's there when something goes sideways.

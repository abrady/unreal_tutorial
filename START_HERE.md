# Start here

You need three things. Two of them are downloads.

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


### 3. Read the README.md

This tees up the goal of the chapter and is a good reference to come back to

### 4. Use the llm

Devmate, Claude Code, Cursor. Fire it up and say:

> start lesson one

That's it. Your assistant will find your Unreal install, read the lesson plan and help guide you.

If something's wrong, ask it for help, it'll tell you what to do about it.

---

## What you're getting into

You'll build a combat gym in C++: a target dummy you can shoot, damage numbers
popping off it, and eventually a dummy that shoots back.

**You do not need a VR headset.** You need a machine that runs Unreal.

**You are not expected to finish in one sitting.** Chapters stand alone and
the lab remembers where you are — come back whenever, and run:

```bash
ask your assistant to check your work
```

That prints every chapter's state, so picking up cold three days later takes
about ten seconds.

## The one rule

Your assistant is wired into the running editor. It can inspect live actors,
read compiler errors, and answer "why is this failing?" from real state.

**It won't write your chapters for you** — see [`AGENTS.md`](AGENTS.md) for
why, and for the one important exception: once you've done something *once*,
delegating the repetition is encouraged.

## If you'd rather do it by hand

[`SETUP.md`](SETUP.md) has the manual version of everything the setup script
does. You shouldn't need it, but it's there when something goes sideways.

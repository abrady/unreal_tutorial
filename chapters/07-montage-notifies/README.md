# Chapter 7 — Montages and AnimNotify

*Take-home. ~90 minutes. The only chapter that needs binary assets.*

**Goal:** attacks that fire on animation timing instead of a cooldown timer.

Every chapter so far has used a stopwatch: *has the cooldown elapsed? then
shoot.* That's not how action games work. Real attacks fire on a specific
frame of a specific animation — the moment the sword is at the top of its
arc, the instant the arm snaps forward.

This chapter closes that gap, and it's the single most useful thing here for
anyone supporting a partner building action combat.

---

## Assets

This is the one chapter that needs real animation content. Epic ships exactly
what we need in the third-person template:

```bash
# from your engine root
cp -r Templates/TP_ThirdPerson/Content/Variant_Combat/Anims \
      <repo>/Lab01_FirstRoom/Content/Lab01/Anims
```

That gives you `AM_ComboAttack` and `AM_ChargedAttack` — real montages with
notify tracks already laid out — plus `ABP_Manny_Combat`. You'll also need the
mannequin skeletal mesh from `TP_ThirdPerson/Content/Characters/`.

**These are gitignored in this repo.** Chapters 1–6 need zero binary assets
and that's deliberate; this chapter is opt-in, so the content stays out of
version control.

---

## The concepts

### A montage is an animation you can trigger and interrupt

Regular animations live in a state machine and play when state says so. A
**montage** is played on demand — `PlayAnimMontage(AM_ComboAttack)` — and can
be blended, interrupted, and jumped around within.

That's what attacks need. An attack isn't a state you're in; it's a thing you
did.

### AnimNotify is a callback on a timeline

A montage carries **notify tracks**. Place a notify at 0.4s and something
fires 0.4 seconds in, every time it plays, at whatever play rate.

Two flavours:

| | Fires | Use for |
|---|---|---|
| `AnimNotify` | once, at a point | spawn the projectile, play a sound |
| `AnimNotifyState` | begin + tick + end over a window | hit-detection windows, i-frames |

The second is the one people miss, and it's how weapon traces actually work —
the blade is "hot" for a window, not an instant.

### Why this beats a timer

Change the animation and the timing follows automatically. Slow the montage
for a heavy attack and the hit slows with it. The animator owns the feel of
the attack, not the programmer — which is the correct division of labour and
the reason every serious action game does it this way.

---

## Your task

**1. `UAnimNotify_FireAbility : public UAnimNotify`.** Override `Notify()`,
find the owning actor's ability component, and activate it. Place it on
`AM_ComboAttack` at the frame where the swing looks right.

**2. `UAnimNotifyState_DamageWindow : public UAnimNotifyState`.** Override
`NotifyBegin` / `NotifyTick` / `NotifyEnd`. Sweep for overlaps during the
window and damage anything found. Track what you've already hit so a single
swing doesn't damage the same target on every tick — that bug is a rite of
passage.

**3. Rewire an ability** to play a montage instead of spawning directly. The
notify does the spawning now.

**4. Give a dummy a mannequin mesh** and an anim blueprint so you can see it.

---

## Then read Epic's version

Once yours works, look at:

```
Templates/TP_ThirdPerson/Source/TP_ThirdPerson/Variant_Combat/Animation/
    AnimNotify_DoAttackTrace.h / .cpp
    AnimNotify_CheckCombo.h / .cpp
    AnimNotify_CheckChargedAttack.h / .cpp
```

This is Epic's own implementation of the pattern you just built, in a shipping
template. Compare their trace handling and combo-window logic to yours.

**Read it after, not before.** Reading it first turns the chapter into
transcription, and you'd lose the thing you came for.

---

## Stuck?

<details>
<summary>The notify never fires</summary>

Check it's actually placed on the montage's notify track, and that the montage
is genuinely playing — `PlayAnimMontage` returns the duration, and 0 means it
didn't play. Usually the skeleton doesn't match the mesh.
</details>

<details>
<summary>Notify fires but I can't reach my ability component</summary>

`MeshComp->GetOwner()` gets you the actor, then
`FindComponentByClass<UAbilityComponent>()`. Both can be null — this runs on
preview meshes in the animation editor too, where there is no game actor.
Guard for it or the asset editor will crash on you.
</details>

<details>
<summary>The damage window hits the same target repeatedly</summary>

`NotifyTick` runs every frame of the window. Keep a `TSet` of already-hit
actors, populated in `NotifyBegin`, cleared in `NotifyEnd`.
</details>

<details>
<summary>Everything fires at the wrong time</summary>

Notify positions are in montage-local time and scale with play rate. If you
retimed the montage the notify moved with it — usually correct, occasionally
not what you meant.
</details>

---

## What just happened

You moved the authority over attack timing out of code and into the animation
asset. That's not a small thing — it's the boundary that lets animators and
designers iterate on combat feel without a programmer in the loop, and it's
why montage notifies are load-bearing in essentially every action game.

It's also, concretely, the thing a partner is most likely to be doing wrong
when they ask why their hits feel bad.

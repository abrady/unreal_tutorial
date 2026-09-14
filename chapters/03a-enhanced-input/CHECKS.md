# Checks — Chapter 3a: Enhanced Input

*For the assistant. Five checks.*

**State the tooling boundary first:** MCP cannot press a key or trigger an
Input Action. Inspect configuration and runtime possession yourself, then ask
the learner to perform the final movement test. Do not claim you injected
input.

---

**1. The Blueprint boundary is complete.**

Confirm:

- `/Game/CombatGym/BP_LabCharacter` derives from
  `/Script/CombatGym.LabCharacter`.
- `/Game/CombatGym/BP_LabGameMode` derives from
  `/Script/CombatGym.LabGameMode`.
- `BP_LabGameMode.DefaultPawnClass` is `BP_LabCharacter_C`.

If the native `ALabCharacter` is still the default pawn, its input-asset
properties will remain null.

**2. The player possesses the intended pawn.**

Start PIE, then `find_actors` for `/Script/CombatGym.LabCharacter`. At least
one must exist, its class must be `BP_LabCharacter_C`, and its controller must
be non-null.

No pawn usually means the active GameMode is wrong or there is no Player Start.

**3. Every input asset is assigned.**

Read these properties from the PIE pawn:

- `DefaultMappingContext` → `IMC_Default`
- `MoveAction` → `IA_Move`
- `LookAction` → `IA_Look`
- `JumpAction` → `IA_Jump`
- `FireAction` → `IA_Fire`

`None` is a failure. Enhanced Input silently skips null actions and contexts.

**4. The mapping context contains the expected controls.**

Read `DefaultKeyMappings` from `IMC_Default`. Confirm:

- Space Bar → `IA_Jump`
- W/S/A/D → `IA_Move`
- Mouse XY → `IA_Look`
- Left Mouse Button → `IA_Fire`

Also inspect the Move modifiers: W/S feed Y, S/A are negative, and D is
positive X. A successful property-write response is not enough; read the array
back.

**5. The learner can move, look, and jump.**

Tell the learner to run PIE and try WASD, the mouse, and Space. This final check
is intentionally manual because MCP cannot synthesize input. If something
fails, use checks 1–4 to narrow the cause before reading code.

Stop PIE when finished.

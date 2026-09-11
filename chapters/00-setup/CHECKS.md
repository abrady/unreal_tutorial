# Checks — Chapter 0: the environment works

*For the assistant. Verify all five with your Unreal tools before teaching
anything. If any fail, fix the setup — don't start Chapter 1 on a broken
environment.*

---

**1. The editor is reachable.**
Your Unreal tools exist and respond. If they don't, the editor is closed or
the client wasn't restarted after the config was written.

**2. Tools are registered.**
`tools/list` returns a substantial set — expect ~255. A handful means some
toolset plugins didn't load.

**3. The tools the lab needs are present.**
`StartPIE`, `StopPIE`, `IsPIERunning`, `GetVisibleActors`, `find_actors`,
`get_components`, `get_properties`, `add_to_scene_from_class`.

Missing ones usually mean the `EditorToolset` plugin is disabled.

**4. PIE starts and stops on command.**

```
IsPIERunning        → if true, StopPIE first
StartPIE            → {"options": {"bSimulate": false,
                       "playMode": "PlayMode_InViewPort", "warmupSeconds": 1.0}}
IsPIERunning        → must be true
StopPIE
IsPIERunning        → must be false
```

**5. Live inspection works.**
With PIE running, `find_actors` returns actors from the running world. This
is the capability every later check depends on — if it fails, nothing else
can be verified.

---

Once all five hold, tell them they're set up and open
[Chapter 1a](../01a-iteration-loop/README.md).

# CSC-59 — Sprint 4 Proposed Control Logic Demonstration

This is a standalone Python terminal simulation of proposed control behaviour for the SPN pH Correction Skid Design Tool. **Simulation only — does not operate real equipment.** It is not integrated into the team's main application.

## Requirements

- Python 3 (standard library only; no additional packages)

## Run

Open a terminal in this folder and run:

```bash
python3 control_demo.py
```

Select a menu option from `0` to `6`.

## Demonstration scenarios

| Option | Scenario | Expected demonstration |
|---|---|---|
| 1 | Normal operation | Pump and agitator shown running; no dosing request or alarm |
| 2 | Low pH | Base dosing request; alarm AL-06 |
| 3 | High pH | Acid dosing request; alarm AL-05 |
| 4 | Tank 1 low-low level | Fault/safe state; pump stopped; interlock active; AL-02 |
| 5 | pH sensor fault | Fault/safe state; dosing prevented; interlock active; AL-07 |
| 6 | Shutdown | Pump, agitator, and dosing response stopped |
| 0 | Exit | Ends the demonstration |

The pH readings and control responses are illustrative scenario values, **not approved engineering setpoints or operating instructions**. Engineering thresholds, equipment integration, and safety behaviour require separate validation by the project team and SPN.

## Project integration

This Python demonstration is a separate prototype. Uploading it to the team repository does not connect it to the React/Node application or actual equipment.

# CSC-39 — Calculation Engine Validation & Refinement

## Jira-ready summary

### User Story
As a user, I want the calculation engine to provide reliable design outputs based on realistic wastewater conditions so that equipment sizing and selection are defensible.

### Sprint 3 outcome
The Sprint 2 calculation engine was refined, extended, and validated for preliminary pH-correction skid sizing.

## Work completed

- Retained the modular calculation structure.
- Reclassified pH-only neutralisation as a **preliminary screening method**.
- Added **titration-based dosing** for cases where representative laboratory data is available.
- Added acid/base compatibility checks.
- Added chemical equivalent-capacity handling through `equivalents_per_mole`.
- Added complete/partial chemical-property validation.
- Added configurable operating hours per day.
- Updated chemical-storage sizing to use actual operating hours.
- Removed fixed/assumed pump pressure from calculated outputs.
- Added preliminary velocity-based pipe sizing.
- Added SPN wastewater-flow scenario conversion from kL/day to L/min.
- Added sensitivity/scenario analysis for flow and pH.
- Added a 10-case validation suite.
- Moved demonstration/validation execution under the main program block so importing the engine does not automatically run tests.

## SPN flow data used

Using the supplied five-day wastewater volumes and a 24 h/day averaging basis:

| Day | Wastewater volume (kL/day) | Average flow (L/min) |
|---|---:|---:|
| 1 | 132.70 | 92.15 |
| 2 | 207.41 | 144.03 |
| 3 | 175.57 | 121.92 |
| 4 | 36.72 | 25.50 |
| 5 | 34.82 | 24.18 |

The 24 h/day basis is an averaging assumption only and does not imply continuous discharge.

## Sensitivity analysis

The engine evaluates the five SPN flow cases together with four explicit initial-pH scenarios:

- pH 4.0
- pH 4.5
- pH 5.0
- pH 5.5

Total scenarios:

**5 flow cases × 4 pH cases = 20 scenarios**

### Output ranges

| Output | Minimum | Maximum |
|---|---:|---:|
| Reaction tank total volume | 580.33 L | 3456.83 L |
| Transfer pump design capacity | 2176.25 L/h | 12963.13 L/h |
| Preliminary required pipe diameter | 22.65 mm | 55.29 mm |
| pH-screening dosing rate | 0.00106 L/h | 0.20003 L/h |
| Chemical storage total volume | 0.213 L | 40.326 L |
| Dosing pump design capacity | 0.00159 L/h | 0.30004 L/h |

### Sensitivity interpretation

- Flow rate has a direct effect on reaction-tank volume and transfer-pump flow requirement.
- Required pipe diameter increases more slowly than flow because diameter is related to the square root of flow at fixed velocity.
- pH-screening chemical dose changes strongly with pH because pH is logarithmic.
- pH-only dosing results must not be treated as final dairy-wastewater chemical demand because wastewater buffering is not represented.

## Validation results

The current engine passes all 10 Sprint 3 validation checks:

1. Acidic wastewater requires a base and produces a positive dose.
2. Alkaline wastewater requires an acid and produces a positive dose.
3. Initial pH equal to target pH gives zero dose.
4. Incorrect acid/base chemical selection is rejected.
5. Incomplete chemical-property inputs are rejected.
6. Titration dose scales correctly with wastewater flow.
7. SPN low-flow case converts and sizes correctly.
8. SPN high-flow case converts and sizes correctly.
9. Preliminary pipe sizing selects DN50 for the 100 L/min test case.
10. SPN sensitivity analysis returns 20 valid scenarios.

**Validation result: 10/10 passed, 0 failed.**

## Example titration validation

Test basis:

- Wastewater flow = 100 L/min
- Titration dose = 2 mL/L
- Operating time = 8 h/day

Engine result:

- Dosing rate = **12.00 L/h**
- Daily chemical volume = **96.00 L/day**

## Engineering limitations

- The `ph_screening` method uses free-ion pH calculations only.
- It does not represent real dairy-wastewater buffering capacity.
- Final chemical dose should be verified using representative titration or acidity/alkalinity data.
- Titration mode assumes the laboratory titrant and full-scale dosing solution have the same effective strength unless additional scaling is added.
- Pipe sizing is preliminary and does not yet include material-specific internal diameter, friction losses, fittings, or full hydraulic verification.
- Pump flow capacity is calculated, but final pump selection still requires TDH/back-pressure information.
- The 24 h/day SPN flow conversion is an averaging basis, not a confirmed plant operating schedule.
- SPN P&ID values are used as concept references only, not values the engine must reproduce.

## Acceptance criteria status

| Acceptance criterion | Status |
|---|---|
| Sprint 2 engine reviewed/refined | Complete |
| SPN wastewater flow data used for realistic scenarios | Complete |
| SPN pH acceptance range incorporated | Complete |
| Tank/pump outputs compared against concept/reference basis | Complete |
| pH-only dosing limitation documented | Complete |
| Basic sensitivity analysis for flow/pH | Complete |
| 5–10 validation cases documented | Complete — 10 cases |

## Suggested Jira completion comment

Sprint 3 calculation-engine refinement is complete. The engine now includes improved input validation, pH-only screening and titration-based dosing modes, equivalent-capacity handling, operating-hour-based chemical storage sizing, preliminary pipe sizing, SPN flow scenarios, and flow/pH sensitivity analysis. The five SPN wastewater-volume cases were converted to average flow rates on a 24 h/day comparison basis and evaluated across four pH scenarios, giving 20 sensitivity cases. A 10-case validation suite was added and all 10 tests pass. Remaining limitations are explicitly documented: pH-only dose is preliminary because wastewater buffering is not represented, final pump selection requires TDH/back-pressure data, and final pipe sizing requires full hydraulic verification.

## Definition of Done

CSC-39 can be moved to **Done** once:
- the updated engine is committed to the team repository,
- this validation note is attached or linked in Jira,
- the test output/screenshot is attached as evidence,
- the final commit or pull request is reviewed by the team.

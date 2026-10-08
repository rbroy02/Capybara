# CSC-61 Sprint 5 — Requirements Traceability


| SPN requirement / project need | Sprint 5 status | Evidence / owner | Final validation note |
|---|---|---|---|
| Generalised computer-based pH-correction skid design | Implemented in calculation/integration layer | `pH correction calc.py`, CSC-56 schema | Calculation and integrated-output workflow available for variable flow/pH inputs. |
| Engineering calculations for chemical dosing | Implemented, preliminary | Calculation engine | Supports `ph_screening` and `titration`; pH-only method remains screening-level. |
| Size equipment requirements | Implemented for design requirements | Calculation engine | Reaction tank, chemical storage tank, transfer pump, dosing pump and preliminary pipe requirements are produced. |
| Select actual equipment | Pending final module integration | CSC-63 / Yuvraj | Calculation engine supplies requirements; final equipment matching must be verified separately. |
| Pumps and pipelines sizing | Implemented, preliminary | Calculation engine | Flow-capacity and preliminary DN sizing available; final hydraulic head/pressure-drop design is outside current data. |
| Questionnaire for preliminary equipment selection | Pending final application integration | CSC-62 / Lovejot | Must be demonstrated through the user-facing application. |
| Rough equipment pricing | Pending final verification | CSC-63 / Yuvraj | Requires final equipment database and pricing evidence. |
| 2D/3D layout based on input data | Pending final integration evidence | CSC-62 / layout module | Calculation branch does not validate the layout module. |
| 20-ft-container skid constraint | Partially addressed / pending layout verification | Layout + equipment-feasibility modules | Final physical fit must be demonstrated by layout/feasibility evidence. |
| Automation for accurate pH correction | Pending final controls verification | CSC-64 / Marwah | Calculation engine provides dosing requirements; control behaviour must be verified separately. |
| Electrical inputs and outputs | Pending final controls verification | CSC-64 / Marwah | Final I/O schedule belongs to the controls deliverable. |
| Skid communication with personnel | Pending final controls/security evidence | CSC-64 / CSC-65 | Must be demonstrated/documented by the communications/security work. |
| Trade-waste pH acceptance criterion | Implemented as design-target check | `trade_waste_ph_status()` | Default configured range is 6.0–10.0; this is not measured discharge certification. |
| SPN five-day wastewater scenarios | Implemented | `run_spn_integrated_flow_scenarios()` | All five daily-volume cases are processed on a 24 h/day averaging basis. |
| Sensitivity to flow and pH | Implemented | Integrated sensitivity output | Five SPN flows × four pH values = 20 scenarios. |

## Release-readiness interpretation

For the calculation-engine scope, the system is ready for final release-candidate validation.

The overall capstone should only be described as fully release-ready once the final UI, equipment/pricing, layout, controls and security evidence has been integrated and demonstrated. 
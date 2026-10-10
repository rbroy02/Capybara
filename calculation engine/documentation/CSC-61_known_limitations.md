# CSC-61 Sprint 5 — Known Engineering Limitations

1. **pH-only chemical demand is a screening estimate.** It uses free-ion pH behaviour and does not represent the buffering capacity of real dairy wastewater. Representative titration or acidity/alkalinity data should be used for final chemical dosing.

2. **Titration scaling assumes equivalent chemical strength.** The laboratory titrant and full-scale dosing solution are assumed to have the same effective neutralising strength unless the input basis is adjusted accordingly.

3. **Pump pressure / TDH is not calculated automatically.** Transfer-pump and dosing-pump flow capacities are estimated, but final selection requires pipe lengths, elevations, fittings, downstream pressure and injection/back-pressure data.

4. **Pipe sizing is preliminary.** The engine uses `Q = A × v` and selects the next nominal DN from a small built-in list. It does not calculate detailed pressure loss or verify actual internal diameter for a selected material/schedule.

5. **SPN daily-volume conversion is an averaging basis.** The five daily wastewater volumes are converted to L/min using 24 h/day for scenario comparison; this does not prove that the plant operates or discharges continuously for 24 hours.

6. **Trade-waste status is a design-target check.** The default configured pH range is 6.0–10.0. The engine does not certify actual discharge compliance; measured outlet pH and any customer-specific acceptance conditions remain necessary.

7. **The calculation engine is not the complete application.** Equipment matching/pricing, physical layout, control logic/I/O, security and user-interface behaviour are separate team modules and require final integration evidence.

8. **This is a preliminary design-support tool.** It is not a substitute for detailed process, hydraulic, mechanical, electrical or safety design and engineering review.

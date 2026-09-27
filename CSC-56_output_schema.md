# CSC-56 Integrated Design Output Schema

The UI, equipment-selection, layout, controls and reporting modules should call:

```python
run_integrated_design_output(base_inputs, ...)
```

Top-level output:

- `schema_version` — currently `CSC-56-v1`
- `design_status` — preliminary design-output status
- `design_summary` — flow, pH values, calculation mode, sizing and dosing summary
- `compliance` — design-target pH check against the configured trade-waste range
- `equipment_requirements` — reaction tank, transfer pump, process pipe, chemical tank and dosing pump requirements
- `sensitivity_summary` — optional sensitivity-analysis summary; otherwise `None`
- `warnings` — engineering/input/design warnings
- `raw_calculation` — original calculation-engine output for traceability

The compliance block checks the **design target pH** only. Actual discharge compliance requires measured outlet pH.

SPN five-day flow cases can be run with:

```python
run_spn_integrated_flow_scenarios(base_inputs)
```

Focused Sprint 4 checks can be run with:

```python
run_sprint4_csc56_validation()
```

The integration layer reuses the existing engineering functions and does not duplicate the calculation equations.

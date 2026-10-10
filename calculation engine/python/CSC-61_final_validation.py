from pathlib import Path
import importlib.util
import hashlib
import json
import sys

ENGINE_FILE = Path(__file__).with_name("pH correction calc.py")
REPORT_FILE = Path(__file__).with_name("CSC-61_validation_report.json")
RELEASE_ID = "CSC-61-RC1"

def load_engine():
    spec = importlib.util.spec_from_file_location("ph_calc_engine", ENGINE_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run_final_validation():
    engine = load_engine()
    checks = []

    def record(name, fn):
        try:
            detail = fn()
            checks.append({"name": name, "status": "PASS", "detail": detail})
        except Exception as exc:
            checks.append({"name": name, "status": "FAIL", "detail": str(exc)})

    def check_sprint3():
        result = engine.run_validation_suite()
        assert result["total"] == 10
        assert result["passed"] == 10
        assert result["failed"] == 0
        return "10/10 Sprint 3 validation cases passed."

    def check_sprint4():
        result = engine.run_sprint4_csc56_validation()
        assert result["total"] == 6
        assert result["passed"] == 6
        assert result["failed"] == 0
        return "6/6 CSC-56 integration validation cases passed."

    screening_inputs = {
        "flow_rate_lpm": 100.0,
        "initial_ph": 5.0,
        "target_ph": 8.0,
        "operating_hours_per_day": 16.0,
        "molar_mass": 40.0,
        "solution_concentration": 0.32,
        "solution_density": 1.35,
        "chemical_role": "base",
        "equivalents_per_mole": 1.0,
        "calculation_mode": "ph_screening",
    }

    def check_screening_mode():
        output = engine.run_integrated_design_output(screening_inputs)
        assert output["schema_version"] == "CSC-56-v1"
        assert output["design_summary"]["calculation_mode"] == "ph_screening"
        assert output["design_summary"]["dosing_rate_L_per_hour"] is not None
        assert output["equipment_requirements"]["reaction_tank"] is not None
        assert output["equipment_requirements"]["transfer_pump"] is not None
        assert output["equipment_requirements"]["process_pipe"] is not None
        return "pH-screening workflow produced integrated sizing and dosing output."

    def check_titration_mode():
        inputs = {
            "flow_rate_lpm": 100.0,
            "initial_ph": 5.0,
            "target_ph": 7.0,
            "operating_hours_per_day": 8.0,
            "calculation_mode": "titration",
            "titration_dose_ml_per_L": 2.0,
        }
        output = engine.run_integrated_design_output(inputs)
        assert output["design_summary"]["calculation_mode"] == "titration"
        assert abs(output["design_summary"]["dosing_rate_L_per_hour"] - 12.0) < 1e-9
        assert abs(output["design_summary"]["dosing_rate_L_per_day"] - 96.0) < 1e-9
        return "Titration workflow verified at 12 L/h and 96 L/day."

    def check_trade_waste_status():
        inside = engine.trade_waste_ph_status(8.0)
        outside = engine.trade_waste_ph_status(5.5)
        assert inside["within_range"] is True
        assert outside["within_range"] is False
        assert inside["accepted_range"]["minimum_ph"] == 6.0
        assert inside["accepted_range"]["maximum_ph"] == 10.0
        return "Design-target pH status verified for inside and outside the configured 6.0–10.0 range."

    def check_spn_flows():
        result = engine.run_spn_integrated_flow_scenarios(screening_inputs)
        assert result["scenario_count"] == 5
        flows = [s["average_flow_L_per_min"] for s in result["scenarios"]]
        assert abs(min(flows) - 24.1805555556) < 1e-8
        assert abs(max(flows) - 144.0347222222) < 1e-8
        return "All five SPN daily-volume cases ran through the integrated output."

    def check_sensitivity():
        daily_volumes_kl = [132.70, 207.41, 175.57, 36.72, 34.82]
        flows = [engine.kl_per_day_to_lpm(v, 24.0) for v in daily_volumes_kl]
        result = engine.run_integrated_design_output(
            base_inputs=screening_inputs,
            sensitivity_flow_rates_lpm=flows,
            sensitivity_initial_ph_values=[4.0, 4.5, 5.0, 5.5],
        )
        summary = result["sensitivity_summary"]
        assert summary["scenario_count"] == 20
        assert summary["output_ranges"]["reaction_tank_total_volume_L"] is not None
        assert summary["output_ranges"]["transfer_pump_capacity_L_per_hour"] is not None
        return "20-case SPN flow × pH sensitivity analysis verified."

    def check_warning_and_limitations():
        output = engine.run_integrated_design_output(screening_inputs)
        warnings = output["warnings"]
        assert any("pH-only" in w for w in warnings)
        assert any("pressure/TDH" in w for w in warnings)
        assert any("internal diameter" in w or "hydraulic design" in w for w in warnings)
        return "Expected engineering limitation warnings are present."

    record("Sprint 3 regression validation", check_sprint3)
    record("Sprint 4 CSC-56 regression validation", check_sprint4)
    record("pH-screening final workflow", check_screening_mode)
    record("Titration final workflow", check_titration_mode)
    record("Trade-waste target-pH status", check_trade_waste_status)
    record("Five SPN flow scenarios", check_spn_flows)
    record("SPN sensitivity analysis", check_sensitivity)
    record("Engineering warning coverage", check_warning_and_limitations)

    passed = sum(c["status"] == "PASS" for c in checks)
    failed = len(checks) - passed

    report = {
        "release_candidate": RELEASE_ID,
        "engine_file": ENGINE_FILE.name,
        "engine_sha256": file_sha256(ENGINE_FILE),
        "integrated_schema": "CSC-56-v1",
        "total_checks": len(checks),
        "passed": passed,
        "failed": failed,
        "checks": checks,
        "release_note": (
            "Calculation-engine release candidate for Sprint 5 validation. "
            "Final project release still depends on integration evidence from the UI, "
            "equipment-selection/pricing, layout, controls and security modules."
        ),
    }

    REPORT_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report

if __name__ == "__main__":
    report = run_final_validation()
    print(f"Release candidate: {report['release_candidate']}")
    print(f"Engine SHA-256: {report['engine_sha256']}")
    print(f"Schema: {report['integrated_schema']}")
    print()
    for check in report["checks"]:
        print(f"{check['status']} - {check['name']}: {check['detail']}")
    print()
    print(
        f"CSC-61 validation summary: {report['passed']}/{report['total_checks']} passed, "
        f"{report['failed']} failed."
    )
    if report["failed"]:
        sys.exit(1)

import math

# -----------------------------
# Input validation
# -----------------------------
# Runs at the start of the master function.
# Splits issues into hard errors (block the calc) and soft warnings (allow it but flag).


def validate_inputs(
    flow_rate_lpm: float,
    initial_ph: float,
    target_ph: float,
    safety_factor: float,
    residence_time_min: float,
    supply_days: float,
    pump_headroom: float,
    molar_mass: float = None,
    solution_concentration: float = None,
    solution_density: float = None,
    chemical_role: str = None,
    equivalents_per_mole: float = 1.0,
    operating_hours_per_day: float = 24.0,
    pipe_design_velocity_m_s: float = 1.0,
    calculation_mode: str = "ph_screening",
    titration_dose_ml_per_L: float = None,
) -> list:

    errors = []
    warnings = []

    # Calculation mode validation.
    normalised_mode = None
    if not isinstance(calculation_mode, str):
        errors.append("Calculation mode must be 'ph_screening' or 'titration'.")
    else:
        normalised_mode = calculation_mode.strip().lower()
        if normalised_mode not in ("ph_screening", "titration"):
            errors.append(
                "Calculation mode must be 'ph_screening' or 'titration'."
            )

    if normalised_mode == "titration":
        if titration_dose_ml_per_L is None:
            errors.append(
                "titration_dose_ml_per_L is required when using titration mode."
            )
        elif titration_dose_ml_per_L < 0:
            errors.append("Titration dose cannot be negative.")

    # Hard errors — invalid, unsupported, or nonsensical values.
    if flow_rate_lpm <= 0:
        errors.append(f"Flow rate must be positive (got {flow_rate_lpm} L/min).")

    # The engine supports the conventional 0–14 design range.
    if initial_ph < 0 or initial_ph > 14:
        errors.append(f"Initial pH must be between 0 and 14 (got {initial_ph}).")

    if target_ph < 0 or target_ph > 14:
        errors.append(f"Target pH must be between 0 and 14 (got {target_ph}).")

    if safety_factor <= 0:
        errors.append(f"Safety factor must be positive (got {safety_factor}).")

    if residence_time_min <= 0:
        errors.append(
            f"Residence time must be positive (got {residence_time_min} min)."
        )

    if supply_days <= 0:
        errors.append(f"Supply days must be positive (got {supply_days}).")

    if pump_headroom <= 0:
        errors.append(f"Pump headroom must be positive (got {pump_headroom}).")

    if operating_hours_per_day <= 0 or operating_hours_per_day > 24:
        errors.append(
            "Operating hours per day must be greater than 0 and no more than 24 "
            f"(got {operating_hours_per_day})."
        )

    if pipe_design_velocity_m_s <= 0:
        errors.append(
            "Pipe design velocity must be positive "
            f"(got {pipe_design_velocity_m_s} m/s)."
        )

    # Chemical-property checks.
    if molar_mass is not None and molar_mass <= 0:
        errors.append(f"Molar mass must be positive (got {molar_mass}).")

    if solution_concentration is not None:
        if solution_concentration <= 0 or solution_concentration > 1.0:
            errors.append(
                "Solution concentration must be between 0 and 1 "
                f"(got {solution_concentration})."
            )

    if solution_density is not None and solution_density <= 0:
        errors.append(
            f"Solution density must be positive (got {solution_density})."
        )

    if equivalents_per_mole <= 0:
        errors.append(
            "Equivalents per mole must be positive "
            f"(got {equivalents_per_mole})."
        )

    # Chemical data must be either completely supplied or completely omitted.
    chemical_inputs = [
        molar_mass,
        solution_concentration,
        solution_density,
    ]
    provided_count = sum(value is not None for value in chemical_inputs)

    if provided_count not in (0, 3):
        errors.append(
            "Chemical properties are incomplete. Provide molar mass, solution "
            "concentration, and solution density together."
        )

    # If chemical properties are provided, the engine must know whether the
    # selected chemical is an acid or a base so it can check compatibility.
    normalised_role = None
    if chemical_role is not None:
        if not isinstance(chemical_role, str):
            errors.append("Chemical role must be 'acid' or 'base'.")
        else:
            normalised_role = chemical_role.strip().lower()
            if normalised_role not in ("acid", "base"):
                errors.append("Chemical role must be either 'acid' or 'base'.")

    if provided_count == 3 and chemical_role is None:
        errors.append(
            "Chemical role is required when chemical properties are supplied. "
            "Use 'acid' or 'base'."
        )

    if provided_count == 0 and chemical_role is not None:
        errors.append(
            "Chemical role was supplied without chemical properties. Either provide "
            "all chemical properties or omit the chemical role."
        )

    # Direction check: acidic wastewater needs a base to raise pH; alkaline
    # wastewater needs an acid to lower pH.
    if normalised_role in ("acid", "base") and initial_ph != target_ph:
        if initial_ph < target_ph and normalised_role != "base":
            errors.append("A base is required to raise the wastewater pH.")
        elif initial_ph > target_ph and normalised_role != "acid":
            errors.append("An acid is required to lower the wastewater pH.")

    # Any hard errors — stop here and raise all of them at once.
    if errors:
        raise ValueError("Invalid inputs:\n  - " + "\n  - ".join(errors))

    # Soft warnings — unusual but not impossible; calculation still runs.
    if initial_ph == target_ph:
        if normalised_mode == "titration" and titration_dose_ml_per_L not in (None, 0):
            warnings.append(
                f"Initial and target pH are equal ({initial_ph}), but a non-zero "
                "titration dose was supplied. Confirm the lab result and target pH."
            )
        else:
            warnings.append(
                f"Initial and target pH are equal ({initial_ph}) — no dosing required."
            )

    if flow_rate_lpm > 5000:
        warnings.append(
            f"Flow rate {flow_rate_lpm} L/min is very high — check units "
            "(expected L/min)."
        )

    if initial_ph <= 1 or initial_ph >= 13:
        warnings.append(
            f"Initial pH {initial_ph} is extreme — verify the measurement and units."
        )

    # SPN-supplied trade-waste acceptance range.
    if target_ph < 6.0 or target_ph > 10.0:
        warnings.append(
            f"Target pH {target_ph} is outside the SPN trade-waste acceptance "
            "range of 6.0–10.0."
        )

    if safety_factor > 5:
        warnings.append(
            f"Safety factor {safety_factor}x is very conservative — may oversize "
            "chemical demand/equipment."
        )

    if safety_factor < 1:
        warnings.append(
            f"Safety factor {safety_factor}x is below 1 — may understate design demand."
        )

    if residence_time_min < 5 or residence_time_min > 60:
        warnings.append(
            f"Residence time {residence_time_min} min is outside the current "
            "screening range of 5–60 min. Verify the design basis."
        )

    if supply_days > 30:
        warnings.append(
            f"Supply days {supply_days} is very long — check that the chemical "
            "storage tank fits the skid/plant constraints."
        )

    # Important limitation of the pH-only screening model.
    if normalised_mode == "ph_screening" and initial_ph != target_ph:
        warnings.append(
            "Neutralisation demand is a pH-only screening estimate. "
            "It does not model wastewater buffering; verify final chemical dosing "
            "with titration or acidity/alkalinity data."
        )

    if normalised_mode == "ph_screening" and titration_dose_ml_per_L is not None:
        warnings.append(
            "A titration dose was supplied but calculation_mode is 'ph_screening'; "
            "the titration value was ignored."
        )

    return warnings


# -----------------------------
# Core chemistry
# -----------------------------
# Works out the free H+ or OH- difference per litre from pH.
# This is intentionally retained as a preliminary screening method only.


def moles_to_neutralise_per_L(initial_ph: float, target_ph: float) -> dict:

    if initial_ph < target_ph:
        # Acidic effluent — remove free H+ by adding a base.
        h_initial = 10 ** (-initial_ph)
        h_target = 10 ** (-target_ph)
        return {
            "moles_per_L": h_initial - h_target,
            "species": "H+",
            "direction": "base required (raise pH)",
        }

    if initial_ph > target_ph:
        # Alkaline effluent — remove free OH- by adding an acid.
        oh_initial = 10 ** (-(14 - initial_ph))
        oh_target = 10 ** (-(14 - target_ph))
        return {
            "moles_per_L": oh_initial - oh_target,
            "species": "OH-",
            "direction": "acid required (lower pH)",
        }

    # Already at target pH — no dosing needed.
    return {
        "moles_per_L": 0.0,
        "species": None,
        "direction": "no dosing required (already at target)",
    }


# Applies a configurable screening/design factor to the free-ion result.
# IMPORTANT: this factor is NOT a substitute for measured buffering capacity.


def neutralisation_load_per_L(
    initial_ph: float,
    target_ph: float,
    safety_factor: float = 2.5,
) -> dict:

    result = moles_to_neutralise_per_L(initial_ph, target_ph)

    return {
        "species": result["species"],
        "direction": result["direction"],
        "stoichiometric_moles_per_L": result["moles_per_L"],
        "adjusted_moles_per_L": result["moles_per_L"] * safety_factor,
        "safety_factor_applied": safety_factor,
        "calculation_method": "pH-only screening",
        "design_status": "preliminary",
        "limitation": (
            "Does not account for wastewater buffering. Final chemical dosing should "
            "be verified with titration or acidity/alkalinity data."
        ),
    }


# -----------------------------
# Dosing solution volume (chemical-dependent)
# -----------------------------
# Uses the chemical's neutralising capacity through equivalents_per_mole.
# Examples: NaOH/HCl = 1 equivalent per mole; H2SO4/Ca(OH)2 can provide 2.


def dosing_solution_volume_per_L(
    adjusted_moles_per_L: float,
    molar_mass: float,
    solution_concentration: float,
    solution_density: float,
    equivalents_per_mole: float = 1.0,
) -> dict:

    # Convert equivalent neutralisation demand into required chemical moles.
    chemical_moles_per_L = adjusted_moles_per_L / equivalents_per_mole

    # Mass of pure chemical needed per L of wastewater.
    mass_pure_g_per_L = chemical_moles_per_L * molar_mass

    # Grams of pure chemical contained in each L of dosing solution.
    # concentration is mass fraction (w/w), density is kg/L.
    g_chem_per_L_solution = solution_concentration * solution_density * 1000

    # Volume of dosing solution needed per L of wastewater.
    dose_volume_L_per_L = mass_pure_g_per_L / g_chem_per_L_solution

    return {
        "chemical_moles_per_L_wastewater": chemical_moles_per_L,
        "mass_pure_chemical_g_per_L_wastewater": mass_pure_g_per_L,
        "dose_volume_L_per_L_wastewater": dose_volume_L_per_L,
        "dose_volume_mL_per_L_wastewater": dose_volume_L_per_L * 1000,
        "equivalents_per_mole": equivalents_per_mole,
    }


def titration_based_dose(
    flow_rate_lpm: float,
    titration_dose_ml_per_L: float,
    operating_hours_per_day: float = 24.0
) -> dict:

    if flow_rate_lpm <= 0:
        raise ValueError("Flow rate must be greater than 0.")

    if titration_dose_ml_per_L < 0:
        raise ValueError("Titration dose cannot be negative.")

    if operating_hours_per_day <= 0 or operating_hours_per_day > 24:
        raise ValueError("Operating hours must be between 0 and 24.")

    # Wastewater flow converted from L/min to L/hour
    wastewater_flow_lph = flow_rate_lpm * 60

    # Convert lab titration dose from mL/L to L/L
    chemical_L_per_L_wastewater = titration_dose_ml_per_L / 1000

    # Full-scale chemical dosing rate
    dosing_rate_lph = (
        wastewater_flow_lph
        * chemical_L_per_L_wastewater
    )

    daily_chemical_volume_L = (
        dosing_rate_lph
        * operating_hours_per_day
    )

    return {
        "titration_dose_mL_per_L": titration_dose_ml_per_L,
        "dosing_rate_L_per_h": dosing_rate_lph,
        "daily_chemical_volume_L": daily_chemical_volume_L,
        "calculation_method": "titration-based",
        "design_status": "preferred when representative lab data is available",
    }

# -----------------------------
# Tank sizing
# -----------------------------
# Reaction tank — preliminary hydraulic-residence-time sizing.


def reaction_tank_size(
    flow_rate_lpm: float,
    residence_time_min: float = 20.0,
    headspace_factor: float = 1.2,
) -> dict:

    working_volume_L = flow_rate_lpm * residence_time_min
    total_volume_L = working_volume_L * headspace_factor

    return {
        "working_volume_L": working_volume_L,
        "total_volume_L": total_volume_L,
        "residence_time_min": residence_time_min,
        "headspace_factor": headspace_factor,
        "calculation_status": "preliminary",
    }


# Chemical storage tank — sized on actual operating hours per day rather than
# automatically assuming 24-hour dosing.


def chemical_storage_tank_size(
    dosing_rate_lph: float,
    supply_days: float = 7.0,
    operating_hours_per_day: float = 24.0,
    headspace_factor: float = 1.2,
) -> dict:

    working_volume_L = dosing_rate_lph * operating_hours_per_day * supply_days
    total_volume_L = working_volume_L * headspace_factor

    return {
        "working_volume_L": working_volume_L,
        "total_volume_L": total_volume_L,
        "supply_days": supply_days,
        "operating_hours_per_day": operating_hours_per_day,
        "headspace_factor": headspace_factor,
        "calculation_status": "preliminary",
    }


# -----------------------------
# Pump sizing
# -----------------------------
# These functions size pump FLOW capacity only. Pressure/head is not invented:
# it must come from a separate hydraulic assessment or a user-supplied value.


def dosing_pump_size(
    dosing_rate_lph: float,
    headroom_factor: float = 1.5,
    pressure_bar: float = None,
) -> dict:

    if dosing_rate_lph < 0:
        raise ValueError("Dosing rate cannot be negative.")
    if headroom_factor <= 0:
        raise ValueError("Headroom factor must be positive.")
    if pressure_bar is not None and pressure_bar <= 0:
        raise ValueError("Pressure must be positive when supplied.")

    pump_capacity_lph = dosing_rate_lph * headroom_factor

    return {
        "pump_capacity_L_per_hour": pump_capacity_lph,
        "required_pressure_bar": pressure_bar,
        "pressure_basis": (
            "user-supplied hydraulic requirement"
            if pressure_bar is not None
            else "not calculated — hydraulic/injection pressure data required"
        ),
        "headroom_factor": headroom_factor,
        "calculation_status": "preliminary flow-capacity sizing",
    }


# Transfer pump — flow capacity from wastewater flow + headroom. Hydraulic head
# is intentionally left uncalculated until pipework/elevation data are available.


def transfer_pump_size(
    flow_rate_lpm: float,
    headroom_factor: float = 1.5,
    pressure_bar: float = None,
) -> dict:

    if flow_rate_lpm < 0:
        raise ValueError("Flow rate cannot be negative.")
    if headroom_factor <= 0:
        raise ValueError("Headroom factor must be positive.")
    if pressure_bar is not None and pressure_bar <= 0:
        raise ValueError("Pressure must be positive when supplied.")

    flow_lph = flow_rate_lpm * 60
    pump_capacity_lph = flow_lph * headroom_factor

    return {
        "pump_capacity_L_per_hour": pump_capacity_lph,
        "required_pressure_bar": pressure_bar,
        "pressure_basis": (
            "user-supplied hydraulic requirement"
            if pressure_bar is not None
            else "not calculated — pipework/elevation/hydraulic data required"
        ),
        "headroom_factor": headroom_factor,
        "calculation_status": "preliminary flow-capacity sizing",
    }


# -----------------------------
# Preliminary pipe sizing
# -----------------------------
# Uses Q = A*v to estimate the internal diameter required at a selected
# design velocity. The DN selection is preliminary only because nominal DN
# does not equal exact internal diameter for every material/schedule.


def preliminary_pipe_size(
    flow_rate_lpm: float,
    design_velocity_m_s: float = 1.0,
) -> dict:

    if flow_rate_lpm <= 0:
        raise ValueError("Flow rate must be positive for pipe sizing.")
    if design_velocity_m_s <= 0:
        raise ValueError("Design velocity must be positive for pipe sizing.")

    # L/min -> m^3/s
    flow_m3_s = flow_rate_lpm / 1000.0 / 60.0

    # Q = A*v -> A = Q/v
    required_area_m2 = flow_m3_s / design_velocity_m_s

    # A = pi*D^2/4 -> D = sqrt(4A/pi)
    required_diameter_m = math.sqrt((4.0 * required_area_m2) / math.pi)
    required_diameter_mm = required_diameter_m * 1000.0

    # Common nominal sizes used only for a preliminary nearest-up selection.
    standard_dn_sizes = [15, 20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200]

    selected_dn = next(
        (dn for dn in standard_dn_sizes if dn >= required_diameter_mm),
        None,
    )

    return {
        "required_internal_diameter_mm": round(required_diameter_mm, 2),
        "selected_nominal_DN": selected_dn,
        "design_velocity_m_s": design_velocity_m_s,
        "flow_m3_s": flow_m3_s,
        "calculation_status": "preliminary",
        "selection_note": (
            "Verify actual internal diameter, material, schedule, pressure drop, "
            "fittings, and allowable velocity during hydraulic design."
            if selected_dn is not None
            else "Required diameter exceeds the built-in DN200 preliminary range; "
            "further hydraulic design is required."
        ),
    }


# -----------------------------
# Master function
# -----------------------------
# One entry point that ties the existing calculation blocks together.


def run_full_calculation(
    flow_rate_lpm: float,
    initial_ph: float,
    target_ph: float = 8.0,
    safety_factor: float = 2.5,
    residence_time_min: float = 20.0,
    supply_days: float = 7.0,
    operating_hours_per_day: float = 24.0,
    calculation_mode: str = "ph_screening",
    titration_dose_ml_per_L: float = None,
    pump_headroom: float = 1.5,
    molar_mass: float = None,
    solution_concentration: float = None,
    solution_density: float = None,
    chemical_role: str = None,
    equivalents_per_mole: float = 1.0,
    pipe_design_velocity_m_s: float = 1.0,
) -> dict:

    calculation_mode_normalised = (
        calculation_mode.strip().lower()
        if isinstance(calculation_mode, str)
        else calculation_mode
    )

    warnings = validate_inputs(
        flow_rate_lpm=flow_rate_lpm,
        initial_ph=initial_ph,
        target_ph=target_ph,
        safety_factor=safety_factor,
        residence_time_min=residence_time_min,
        supply_days=supply_days,
        pump_headroom=pump_headroom,
        molar_mass=molar_mass,
        solution_concentration=solution_concentration,
        solution_density=solution_density,
        chemical_role=chemical_role,
        equivalents_per_mole=equivalents_per_mole,
        operating_hours_per_day=operating_hours_per_day,
        pipe_design_velocity_m_s=pipe_design_velocity_m_s,
        calculation_mode=calculation_mode_normalised,
        titration_dose_ml_per_L=titration_dose_ml_per_L,
    )

    reaction_tank = reaction_tank_size(flow_rate_lpm, residence_time_min)
    transfer_pump = transfer_pump_size(flow_rate_lpm, pump_headroom)
    preliminary_pipe = preliminary_pipe_size(
        flow_rate_lpm,
        pipe_design_velocity_m_s,
    )

    # The pH-only neutralisation load is used only in screening mode.
    if calculation_mode_normalised == "ph_screening":
        load = neutralisation_load_per_L(
            initial_ph,
            target_ph,
            safety_factor,
        )
    else:
        load = None

    result = {
        "inputs": {
            "flow_rate_lpm": flow_rate_lpm,
            "initial_ph": initial_ph,
            "target_ph": target_ph,
            "operating_hours_per_day": operating_hours_per_day,
            "pipe_design_velocity_m_s": pipe_design_velocity_m_s,
            "calculation_mode": calculation_mode_normalised,
            "titration_dose_ml_per_L": titration_dose_ml_per_L,
        },
        "calculation_mode": calculation_mode_normalised,
        "neutralisation_load": load,
        "reaction_tank": reaction_tank,
        "transfer_pump": transfer_pump,
        "preliminary_pipe": preliminary_pipe,
        "assumptions": {
            "safety_factor": safety_factor,
            "safety_factor_note": (
                "Used only for pH-only screening; it does not represent measured "
                "wastewater buffering capacity."
            ),
            "residence_time_min": residence_time_min,
            "supply_days": supply_days,
            "operating_hours_per_day": operating_hours_per_day,
            "pump_headroom": pump_headroom,
            "pipe_design_velocity_m_s": pipe_design_velocity_m_s,
            "pipe_sizing_note": (
                "Pipe sizing uses Q = A*v and selects the next nominal DN from a "
                "small built-in list. Final hydraulic design must verify actual ID, "
                "material, pressure loss, fittings, and operating conditions."
            ),
            "dosing_basis": (
                "Representative lab titration dose scaled to process flow. The lab "
                "titrant and full-scale dosing solution are assumed to have the same "
                "effective strength."
                if calculation_mode_normalised == "titration"
                else "Free-ion pH-only screening estimate; preliminary only."
            ),
            "note": (
                "Preliminary design-basis calculation. Final chemical dosing and "
                "equipment specification require appropriate process verification."
            ),
            "standards_referenced": [
                "WSAA Australian Wastewater Quality Management Guidelines",
                "National Water Quality Management Strategy (NWQMS)",
                "EPA Victoria and applicable water authority/local council requirements",
                "Relevant AS/AS-NZS standards to be confirmed for selected equipment/design scope",
            ],
            "trade_waste_ph_range": "6.0-10.0 (per SPN trade waste agreement)",
        },
    }

    chemical_values = [molar_mass, solution_concentration, solution_density]
    chemical_data_complete = all(value is not None for value in chemical_values)

    # ---------------------------------------------------------
    # Dosing method 1: pH-only screening
    # ---------------------------------------------------------
    if calculation_mode_normalised == "ph_screening":
        if chemical_data_complete:
            dose = dosing_solution_volume_per_L(
                adjusted_moles_per_L=load["adjusted_moles_per_L"],
                molar_mass=molar_mass,
                solution_concentration=solution_concentration,
                solution_density=solution_density,
                equivalents_per_mole=equivalents_per_mole,
            )

            dosing_rate_lph = (
                dose["dose_volume_L_per_L_wastewater"] * flow_rate_lpm * 60
            )
        else:
            dose = None
            dosing_rate_lph = None

    # ---------------------------------------------------------
    # Dosing method 2: measured titration dose
    # ---------------------------------------------------------
    else:
        dose = titration_based_dose(
            flow_rate_lpm=flow_rate_lpm,
            titration_dose_ml_per_L=titration_dose_ml_per_L,
            operating_hours_per_day=operating_hours_per_day,
        )
        dosing_rate_lph = dose["dosing_rate_L_per_h"]

    # Common downstream sizing once a dosing rate is available.
    if dosing_rate_lph is not None:
        storage_tank = chemical_storage_tank_size(
            dosing_rate_lph=dosing_rate_lph,
            supply_days=supply_days,
            operating_hours_per_day=operating_hours_per_day,
        )
        dosing_pump = dosing_pump_size(dosing_rate_lph, pump_headroom)

        result["dosing"] = dose
        result["dosing_rate_L_per_hour"] = dosing_rate_lph
        result["dosing_rate_L_per_day"] = (
            dosing_rate_lph * operating_hours_per_day
        )
        result["chemical_storage_tank"] = storage_tank
        result["dosing_pump"] = dosing_pump
    else:
        result["dosing"] = None
        result["note_on_dosing"] = (
            "Dosing volume, chemical storage, and dosing-pump sizing were not "
            "calculated because chemical properties were not supplied for the "
            "pH-only screening method."
        )

    # Chemical metadata is retained when supplied, regardless of dosing mode.
    if chemical_data_complete:
        result["chemical_properties_provided"] = {
            "chemical_role": chemical_role.strip().lower(),
            "molar_mass_g_per_mol": molar_mass,
            "solution_concentration_w_w": solution_concentration,
            "solution_density_kg_per_L": solution_density,
            "equivalents_per_mole": equivalents_per_mole,
        }

    result["warnings"] = warnings
    return result



def kl_per_day_to_lpm(
    volume_kl_per_day: float,
    operating_hours_per_day: float = 24.0
) -> float:

    if volume_kl_per_day <= 0:
        raise ValueError("Daily wastewater volume must be positive.")

    if operating_hours_per_day <= 0 or operating_hours_per_day > 24:
        raise ValueError("Operating hours must be between 0 and 24.")

    return (
        volume_kl_per_day * 1000
        / (operating_hours_per_day * 60)
    )

def run_sensitivity_analysis(
    base_inputs: dict,
    flow_rates_lpm: list = None,
    initial_ph_values: list = None
) -> dict:

    if flow_rates_lpm is None and initial_ph_values is None:
        raise ValueError(
            "Provide at least one flow-rate list or initial-pH list."
        )

    base_flow = base_inputs["flow_rate_lpm"]
    base_ph = base_inputs["initial_ph"]

    flows = flow_rates_lpm if flow_rates_lpm is not None else [base_flow]
    ph_values = (
        initial_ph_values if initial_ph_values is not None else [base_ph]
    )

    scenarios = []

    for flow in flows:
        for initial_ph in ph_values:

            scenario_inputs = base_inputs.copy()

            scenario_inputs["flow_rate_lpm"] = flow
            scenario_inputs["initial_ph"] = initial_ph

            result = run_full_calculation(**scenario_inputs)

            scenario = {
                "flow_rate_lpm": flow,
                "initial_ph": initial_ph,
                "target_ph": scenario_inputs.get("target_ph", 8.0),
                "calculation_mode": result["calculation_mode"],

                "reaction_tank_total_volume_L":
                    result["reaction_tank"]["total_volume_L"],

                "transfer_pump_capacity_L_per_hour":
                    result["transfer_pump"]["pump_capacity_L_per_hour"],

                "pipe_required_diameter_mm":
                    result["preliminary_pipe"]["required_internal_diameter_mm"],

                "selected_pipe_DN":
                    result["preliminary_pipe"]["selected_nominal_DN"],
            }

            # Chemical-dependent outputs only exist when dosing is calculated.
            if result.get("dosing_rate_L_per_hour") is not None:

                scenario["dosing_rate_L_per_hour"] = (
                    result["dosing_rate_L_per_hour"]
                )

                scenario["chemical_storage_total_volume_L"] = (
                    result["chemical_storage_tank"]["total_volume_L"]
                )

                scenario["dosing_pump_capacity_L_per_hour"] = (
                    result["dosing_pump"]["pump_capacity_L_per_hour"]
                )

            else:
                scenario["dosing_rate_L_per_hour"] = None
                scenario["chemical_storage_total_volume_L"] = None
                scenario["dosing_pump_capacity_L_per_hour"] = None

            scenarios.append(scenario)

    def numeric_range(key):
        values = [
            scenario[key]
            for scenario in scenarios
            if scenario.get(key) is not None
        ]

        if not values:
            return None

        return {
            "minimum": min(values),
            "maximum": max(values),
        }

    ranges = {
        "reaction_tank_total_volume_L":
            numeric_range("reaction_tank_total_volume_L"),

        "transfer_pump_capacity_L_per_hour":
            numeric_range("transfer_pump_capacity_L_per_hour"),

        "pipe_required_diameter_mm":
            numeric_range("pipe_required_diameter_mm"),

        "dosing_rate_L_per_hour":
            numeric_range("dosing_rate_L_per_hour"),

        "chemical_storage_total_volume_L":
            numeric_range("chemical_storage_total_volume_L"),

        "dosing_pump_capacity_L_per_hour":
            numeric_range("dosing_pump_capacity_L_per_hour"),
    }

    return {
        "scenario_count": len(scenarios),
        "scenario_results": scenarios,
        "output_ranges": ranges,
        "analysis_note": (
            "pH scenarios are evaluated using explicit pH values rather than "
            "percentage changes because the pH scale is logarithmic."
        ),
    }

# -----------------------------
# Sprint 3 validation suite
# -----------------------------
# Kept in the same engine file for the current capstone structure. These tests
# check calculation behaviour, input validation, SPN flow cases, pipe sizing,
# titration scaling, and sensitivity output ranges.


def run_validation_suite() -> dict:
    results = []

    def record(name, test_function):
        try:
            test_function()
            results.append({"name": name, "status": "PASS", "detail": None})
        except Exception as exc:
            results.append({"name": name, "status": "FAIL", "detail": str(exc)})

    def assert_raises_value_error(function, expected_text=None):
        try:
            function()
        except ValueError as exc:
            if expected_text is not None:
                assert expected_text.lower() in str(exc).lower(), (
                    f"Expected error containing {expected_text!r}, got: {exc}"
                )
            return
        raise AssertionError("Expected ValueError, but no error was raised.")

    # 1. Normal acidic wastewater case: base must be required and dose > 0.
    def test_acidic_case():
        result = run_full_calculation(
            flow_rate_lpm=100,
            initial_ph=4.5,
            target_ph=8.0,
            molar_mass=40.0,
            solution_concentration=0.32,
            solution_density=1.35,
            chemical_role="base",
            equivalents_per_mole=1.0,
        )
        assert "base required" in result["neutralisation_load"]["direction"]
        assert result["dosing_rate_L_per_hour"] > 0

    record("Acidic case selects base and produces positive dose", test_acidic_case)

    # 2. Alkaline wastewater case: acid must be required and dose > 0.
    def test_alkaline_case():
        result = run_full_calculation(
            flow_rate_lpm=100,
            initial_ph=11.0,
            target_ph=8.0,
            molar_mass=36.46,
            solution_concentration=0.30,
            solution_density=1.15,
            chemical_role="acid",
            equivalents_per_mole=1.0,
        )
        assert "acid required" in result["neutralisation_load"]["direction"]
        assert result["dosing_rate_L_per_hour"] > 0

    record("Alkaline case selects acid and produces positive dose", test_alkaline_case)

    # 3. Same initial and target pH should give zero chemical demand.
    def test_same_ph_zero_dose():
        result = run_full_calculation(
            flow_rate_lpm=100,
            initial_ph=7.5,
            target_ph=7.5,
            molar_mass=40.0,
            solution_concentration=0.32,
            solution_density=1.35,
            chemical_role="base",
            equivalents_per_mole=1.0,
        )
        assert result["neutralisation_load"]["adjusted_moles_per_L"] == 0.0
        assert result["dosing_rate_L_per_hour"] == 0.0

    record("Same-pH case gives zero dose", test_same_ph_zero_dose)

    # 4. Incorrect acid/base selection must be rejected.
    def test_wrong_chemical_role():
        assert_raises_value_error(
            lambda: run_full_calculation(
                flow_rate_lpm=100,
                initial_ph=4.5,
                target_ph=8.0,
                molar_mass=36.46,
                solution_concentration=0.30,
                solution_density=1.15,
                chemical_role="acid",
                equivalents_per_mole=1.0,
            ),
            "base is required",
        )

    record("Wrong chemical role is rejected", test_wrong_chemical_role)

    # 5. Partial chemical-property data must be rejected.
    def test_partial_chemical_data():
        assert_raises_value_error(
            lambda: run_full_calculation(
                flow_rate_lpm=100,
                initial_ph=4.5,
                molar_mass=40.0,
            ),
            "chemical properties are incomplete",
        )

    record("Incomplete chemical data is rejected", test_partial_chemical_data)

    # 6. Titration scaling: 2 mL/L at 100 L/min = 12 L/h.
    def test_titration_scaling():
        result = run_full_calculation(
            flow_rate_lpm=100,
            initial_ph=5.0,
            target_ph=7.0,
            operating_hours_per_day=8.0,
            calculation_mode="titration",
            titration_dose_ml_per_L=2.0,
        )
        assert abs(result["dosing_rate_L_per_hour"] - 12.0) < 1e-9
        assert abs(result["dosing_rate_L_per_day"] - 96.0) < 1e-9

    record("Titration dose scales correctly", test_titration_scaling)

    # 7. SPN low-flow case: 34.82 kL/day averaged over 24 h.
    def test_spn_low_flow_case():
        flow = kl_per_day_to_lpm(34.82, 24.0)
        result = run_full_calculation(flow_rate_lpm=flow, initial_ph=7.5, target_ph=7.5)
        assert abs(flow - 24.1805555556) < 1e-8
        assert abs(result["reaction_tank"]["total_volume_L"] - 580.3333333333) < 1e-6

    record("SPN low-flow case converts and sizes correctly", test_spn_low_flow_case)

    # 8. SPN high-flow case: 207.41 kL/day averaged over 24 h.
    def test_spn_high_flow_case():
        flow = kl_per_day_to_lpm(207.41, 24.0)
        result = run_full_calculation(flow_rate_lpm=flow, initial_ph=7.5, target_ph=7.5)
        assert abs(flow - 144.0347222222) < 1e-8
        assert abs(result["reaction_tank"]["total_volume_L"] - 3456.8333333333) < 1e-6

    record("SPN high-flow case converts and sizes correctly", test_spn_high_flow_case)

    # 9. Known pipe-sizing case: 100 L/min at 1 m/s -> about 46.07 mm -> DN50.
    def test_pipe_sizing():
        pipe = preliminary_pipe_size(100, 1.0)
        assert abs(pipe["required_internal_diameter_mm"] - 46.07) <= 0.01
        assert pipe["selected_nominal_DN"] == 50

    record("Preliminary pipe sizing selects DN50 at 100 L/min", test_pipe_sizing)

    # 10. SPN sensitivity analysis should cover 5 flows x 4 pH values = 20 cases
    # and reproduce the expected hydraulic min/max range.
    def test_sensitivity_ranges():
        daily_volumes_kl = [132.70, 207.41, 175.57, 36.72, 34.82]
        flows = [kl_per_day_to_lpm(volume, 24.0) for volume in daily_volumes_kl]
        base_case = {
            "flow_rate_lpm": flows[0],
            "initial_ph": 5.0,
            "target_ph": 8.0,
            "operating_hours_per_day": 24.0,
            "molar_mass": 40.0,
            "solution_concentration": 0.32,
            "solution_density": 1.35,
            "chemical_role": "base",
            "equivalents_per_mole": 1.0,
            "calculation_mode": "ph_screening",
        }
        sensitivity = run_sensitivity_analysis(
            base_inputs=base_case,
            flow_rates_lpm=flows,
            initial_ph_values=[4.0, 4.5, 5.0, 5.5],
        )
        assert sensitivity["scenario_count"] == 20
        tank_range = sensitivity["output_ranges"]["reaction_tank_total_volume_L"]
        pump_range = sensitivity["output_ranges"]["transfer_pump_capacity_L_per_hour"]
        assert abs(tank_range["minimum"] - 580.3333333333) < 1e-6
        assert abs(tank_range["maximum"] - 3456.8333333333) < 1e-6
        assert abs(pump_range["minimum"] - 2176.25) < 1e-6
        assert abs(pump_range["maximum"] - 12963.125) < 1e-6

    record("SPN sensitivity range returns 20 valid scenarios", test_sensitivity_ranges)

    passed = sum(item["status"] == "PASS" for item in results)
    failed = len(results) - passed

    return {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "results": results,
    }


# -----------------------------
# Demonstration and validation
# -----------------------------
if __name__ == "__main__":
    print("=== CORE CHEMISTRY CHECKS ===")
    result1 = moles_to_neutralise_per_L(4.5, 7.5)
    print(
        f"pH 4.5 → 7.5: {result1['moles_per_L']:.6f} mol/L of "
        f"{result1['species']} ({result1['direction']})"
    )

    result2 = moles_to_neutralise_per_L(11.0, 7.5)
    print(
        f"pH 11.0 → 7.5: {result2['moles_per_L']:.6f} mol/L of "
        f"{result2['species']} ({result2['direction']})"
    )

    result3 = moles_to_neutralise_per_L(7.5, 7.5)
    print(f"pH 7.5 → 7.5: {result3['direction']}")

    print("\n=== TITRATION DEMO ===")
    titration_case = run_full_calculation(
        flow_rate_lpm=100,
        initial_ph=5.0,
        target_ph=7.0,
        operating_hours_per_day=8.0,
        calculation_mode="titration",
        titration_dose_ml_per_L=2.0,
    )
    print(f"Mode: {titration_case['calculation_mode']}")
    print(f"Dosing rate: {titration_case['dosing_rate_L_per_hour']:.2f} L/h")
    print(f"Daily chemical volume: {titration_case['dosing_rate_L_per_day']:.2f} L/day")

    print("\n=== SPN FLOW SENSITIVITY ANALYSIS ===")
    spn_daily_volumes_kl = [132.70, 207.41, 175.57, 36.72, 34.82]
    spn_flow_rates_lpm = [
        kl_per_day_to_lpm(volume, 24.0)
        for volume in spn_daily_volumes_kl
    ]

    print("SPN average flow rates (24 h/day averaging basis):")
    for day, flow in enumerate(spn_flow_rates_lpm, start=1):
        print(f"Day {day}: {flow:.2f} L/min")

    base_case = {
        "flow_rate_lpm": spn_flow_rates_lpm[0],
        "initial_ph": 5.0,
        "target_ph": 8.0,
        "operating_hours_per_day": 24.0,
        "molar_mass": 40.0,
        "solution_concentration": 0.32,
        "solution_density": 1.35,
        "chemical_role": "base",
        "equivalents_per_mole": 1.0,
        "calculation_mode": "ph_screening",
    }

    spn_sensitivity = run_sensitivity_analysis(
        base_inputs=base_case,
        flow_rates_lpm=spn_flow_rates_lpm,
        initial_ph_values=[4.0, 4.5, 5.0, 5.5],
    )

    print("Scenario count:", spn_sensitivity["scenario_count"])
    print("Output ranges:")
    print(spn_sensitivity["output_ranges"])

    print("\n=== SPRINT 3 VALIDATION SUITE ===")
    validation = run_validation_suite()
    for item in validation["results"]:
        if item["status"] == "PASS":
            print(f"PASS - {item['name']}")
        else:
            print(f"FAIL - {item['name']}: {item['detail']}")

    print(
        f"Validation summary: {validation['passed']}/{validation['total']} passed, "
        f"{validation['failed']} failed."
    )

    if validation["failed"]:
        raise AssertionError("One or more Sprint 3 validation cases failed.")

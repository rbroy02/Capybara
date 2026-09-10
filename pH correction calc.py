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
) -> list:
    
    errors = []
    warnings = []

    # Hard errors — physically impossible or nonsensical values
    if flow_rate_lpm <= 0:
        errors.append(f"Flow rate must be positive (got {flow_rate_lpm} L/min).")

    if initial_ph <= 0 or initial_ph > 14:
        errors.append(f"Initial pH must be between 0 and 14 (got {initial_ph}).")

    if target_ph <= 0 or target_ph > 14:
        errors.append(f"Target pH must be between 0 and 14 (got {target_ph}).")

    if safety_factor <= 0:
        errors.append(f"Safety factor must be positive (got {safety_factor}).")

    if residence_time_min <= 0:
        errors.append(f"Residence time must be positive (got {residence_time_min} min).")

    if supply_days <= 0:
        errors.append(f"Supply days must be positive (got {supply_days}).")

    if pump_headroom <= 0:
        errors.append(f"Pump headroom must be positive (got {pump_headroom}).")

    # Chemical property checks only run if the user actually supplied those inputs
    if molar_mass is not None and molar_mass <= 0:
        errors.append(f"Molar mass must be positive (got {molar_mass}).")

    if solution_concentration is not None:
        if solution_concentration <= 0 or solution_concentration > 1.0:
            errors.append(f"Solution concentration must be between 0 and 1 (got {solution_concentration}).")

    if solution_density is not None and solution_density <= 0:
        errors.append(f"Solution density must be positive (got {solution_density}).")

    # Any hard errors — stop here and raise all of them at once
    if errors:
        raise ValueError("Invalid inputs:\n  - " + "\n  - ".join(errors))

    # Soft warnings — unusual but not impossible, calc still runs
    if initial_ph == target_ph:
        warnings.append(f"Initial and target pH are equal ({initial_ph}) — no dosing required.")

    if flow_rate_lpm > 5000:
        warnings.append(f"Flow rate {flow_rate_lpm} L/min is very high — check units (should be L/min, not L/h).")

    if initial_ph < 1 or initial_ph > 13:
        warnings.append(f"Initial pH {initial_ph} is extreme — verify the reading.")

    if target_ph < 6.0 or target_ph > 10.0:
        warnings.append(f"Target pH {target_ph} is outside typical trade waste range (6.0–10.0).")

    if safety_factor > 5:
        warnings.append(f"Safety factor {safety_factor}x is very conservative — may oversize equipment.")

    if safety_factor < 1:
        warnings.append(f"Safety factor {safety_factor}x is below 1 — may under-dose.")

    if residence_time_min < 5 or residence_time_min > 60:
        warnings.append(f"Residence time {residence_time_min} min is outside typical 5–60 min range.")

    if supply_days > 30:
        warnings.append(f"Supply days {supply_days} is very long — check storage tank fits within skid footprint.")

    return warnings


# -----------------------------
# Core chemistry
# -----------------------------
# Works out how many moles of H+ or OH- need to be neutralised per litre.
# Uses log-scale pH math: [H+] = 10^-pH.
# Also decides direction (acid or base needed) so downstream functions don't have to.

def moles_to_neutralise_per_L(initial_ph: float, target_ph: float) -> dict:

    if initial_ph < target_ph:
        # Acidic effluent — remove H+ by adding a base
        h_initial = 10 ** (-initial_ph)
        h_target = 10 ** (-target_ph)
        return {
            "moles_per_L": h_initial - h_target,
            "species": "H+",
            "direction": "base required (raise pH)",
        }
    elif initial_ph > target_ph:
        # Alkaline effluent — remove OH- by adding an acid
        oh_initial = 10 ** (-(14 - initial_ph))
        oh_target = 10 ** (-(14 - target_ph))
        return {
            "moles_per_L": oh_initial - oh_target,
            "species": "OH-",
            "direction": "acid required (lower pH)",
        }
    else:
        # Already at target pH — no dosing needed
        return {
            "moles_per_L": 0.0,
            "species": None,
            "direction": "no dosing required (already at target)",
        }


# Applies a safety factor to the stoichiometric moles.
# Safety factor covers buffering capacity and real-world variability of dairy effluent.

def neutralisation_load_per_L(initial_ph: float, target_ph: float, safety_factor: float = 2.5) -> dict:

    result = moles_to_neutralise_per_L(initial_ph, target_ph)

    return {
        "species": result["species"],
        "direction": result["direction"],
        "stoichiometric_moles_per_L": result["moles_per_L"],
        "adjusted_moles_per_L": result["moles_per_L"] * safety_factor,
        "safety_factor_applied": safety_factor,
    }


# Quick sanity check on the chemistry functions above.
if __name__ == "__main__":

    # Acidic case
    result1 = moles_to_neutralise_per_L(4.5, 7.5)
    print(f"pH 4.5 → 7.5: {result1['moles_per_L']:.6f} mol/L of {result1['species']} to neutralise ({result1['direction']})")

    # Alkaline case
    result2 = moles_to_neutralise_per_L(11.0, 7.5)
    print(f"pH 11.0 → 7.5: {result2['moles_per_L']:.6f} mol/L of {result2['species']} to neutralise ({result2['direction']})")

    # Edge case — same pH, no dosing needed
    result3 = moles_to_neutralise_per_L(7.5, 7.5)
    print(f"pH 7.5 → 7.5: {result3['direction']}")

    # Full load with safety factor applied
    load = neutralisation_load_per_L(4.5, 7.5)
    print(f"\nFull load calc: {load}")


# -----------------------------
# Dosing solution volume (chemical-dependent)
# -----------------------------
# Only usable when the user supplies chemical properties.
# No assumptions about which chemical is used — user provides molar mass,
# solution concentration, and density.

def dosing_solution_volume_per_L(
    adjusted_moles_per_L: float,
    molar_mass: float,
    solution_concentration: float,
    solution_density: float,
) -> dict:

    # Mass of pure chemical needed per L of wastewater
    mass_pure_g_per_L = adjusted_moles_per_L * molar_mass

    # Grams of pure chemical inside each L of the dosing solution
    g_chem_per_L_solution = solution_concentration * solution_density * 1000

    # Volume of dosing solution needed per L of wastewater
    dose_volume_L_per_L = mass_pure_g_per_L / g_chem_per_L_solution

    return {
        "mass_pure_chemical_g_per_L_wastewater": mass_pure_g_per_L,
        "dose_volume_L_per_L_wastewater": dose_volume_L_per_L,
        "dose_volume_mL_per_L_wastewater": dose_volume_L_per_L * 1000,
    }


# Quick sanity check for the dosing volume calc.
# Uses example numbers only — not a claim that this chemical is used.
if __name__ == "__main__":

    load = neutralisation_load_per_L(4.5, 7.5)
    dose = dosing_solution_volume_per_L(
        adjusted_moles_per_L=load["adjusted_moles_per_L"],
        molar_mass=40.0,              # example value only
        solution_concentration=0.32,  # example value only
        solution_density=1.35,        # example value only
    )

    print(f"\nDosing volume (example inputs): {dose}")


# -----------------------------
# Tank sizing
# -----------------------------
# Reaction tank — sized on residence time (how long wastewater sits and mixes with dose).
# Headspace factor adds ~20% extra volume for safety.

def reaction_tank_size(flow_rate_lpm: float, residence_time_min: float = 20.0, headspace_factor: float = 1.2) -> dict:

    working_volume_L = flow_rate_lpm * residence_time_min
    total_volume_L = working_volume_L * headspace_factor

    return {
        "working_volume_L": working_volume_L,
        "total_volume_L": total_volume_L,
        "residence_time_min": residence_time_min,
        "headspace_factor": headspace_factor,
    }


# Chemical storage tank — sized on days of chemical supply (interval between refills).

def chemical_storage_tank_size(dosing_rate_lph: float, supply_days: float = 7.0, headspace_factor: float = 1.2) -> dict:

    working_volume_L = dosing_rate_lph * 24 * supply_days
    total_volume_L = working_volume_L * headspace_factor

    return {
        "working_volume_L": working_volume_L,
        "total_volume_L": total_volume_L,
        "supply_days": supply_days,
        "headspace_factor": headspace_factor,
    }


# -----------------------------
# Pump sizing
# -----------------------------
# Dosing pump — pushes chemical solution into the wastewater line.
# Sized on dosing rate + headroom. Pressure is a typical value, not a hydraulic calculation.

def dosing_pump_size(dosing_rate_lph: float, headroom_factor: float = 1.5, pressure_bar: float = 5.0) -> dict:

    pump_capacity_lph = dosing_rate_lph * headroom_factor

    return {
        "pump_capacity_L_per_hour": pump_capacity_lph,
        "recommended_pressure_bar": pressure_bar,
        "headroom_factor": headroom_factor,
    }


# Transfer pump — moves wastewater into the reaction tank.
# Same idea as dosing pump but sized on wastewater flow. Lower default pressure.

def transfer_pump_size(flow_rate_lpm: float, headroom_factor: float = 1.5, pressure_bar: float = 2.0) -> dict:

    flow_lph = flow_rate_lpm * 60
    pump_capacity_lph = flow_lph * headroom_factor

    return {
        "pump_capacity_L_per_hour": pump_capacity_lph,
        "recommended_pressure_bar": pressure_bar,
        "headroom_factor": headroom_factor,
    }


# Quick sanity check for tank + pump sizing at a sample flow and dosing rate.
if __name__ == "__main__":

    print("\n--- Sizing calculations ---")

    flow_lpm = 100
    dosing_lph = 5.0

    tank = reaction_tank_size(flow_lpm)
    print(f"Reaction tank: {tank}")

    storage = chemical_storage_tank_size(dosing_lph)
    print(f"Chemical storage tank: {storage}")

    dpump = dosing_pump_size(dosing_lph)
    print(f"Dosing pump: {dpump}")

    tpump = transfer_pump_size(flow_lpm)
    print(f"Transfer pump: {tpump}")


# -----------------------------
# Master function
# -----------------------------
# One entry point that ties everything together.
# Always calculates: neutralisation load, reaction tank, transfer pump.
# Only calculates dosing volume, chemical storage, dosing pump if chemical properties are supplied.
# All assumptions and warnings are attached to the returned result.

def run_full_calculation(
    flow_rate_lpm: float,
    initial_ph: float,
    target_ph: float = 8.0,
    safety_factor: float = 2.5,
    residence_time_min: float = 20.0,
    supply_days: float = 7.0,
    pump_headroom: float = 1.5,
    molar_mass: float = None,
    solution_concentration: float = None,
    solution_density: float = None,
) -> dict:

    # Validate first — raises if anything is invalid, returns warnings otherwise
    warnings = validate_inputs(
        flow_rate_lpm, initial_ph, target_ph, safety_factor,
        residence_time_min, supply_days, pump_headroom,
        molar_mass, solution_concentration, solution_density,
    )

    # Chemistry + sizing calcs that don't depend on the chemical
    load = neutralisation_load_per_L(initial_ph, target_ph, safety_factor)
    reaction_tank = reaction_tank_size(flow_rate_lpm, residence_time_min)
    transfer_pump = transfer_pump_size(flow_rate_lpm, pump_headroom)

    # Base result dict — always populated
    result = {
        "inputs": {
            "flow_rate_lpm": flow_rate_lpm,
            "initial_ph": initial_ph,
            "target_ph": target_ph,
        },
        "neutralisation_load": load,
        "reaction_tank": reaction_tank,
        "transfer_pump": transfer_pump,
        "assumptions": {
            "safety_factor": safety_factor,
            "residence_time_min": residence_time_min,
            "supply_days": supply_days,
            "pump_headroom": pump_headroom,
            "note": "Design basis calculation only. Verify with titration data before final specification.",
            "standards_referenced": [
                "WSAA Australian Wastewater Quality Management Guidelines",
                "National Water Quality Management Strategy (NWQMS)",
                "AS/NZS applicable codes",
                "EPA Victoria and local water authority guidelines",
            ],
            "trade_waste_ph_range": "6.0-10.0 (per SPN trade waste agreement)",
        },
    }

    # Chemical-dependent calcs — only run if the user supplied chemical properties
    if molar_mass and solution_concentration and solution_density:
        dose = dosing_solution_volume_per_L(
            adjusted_moles_per_L=load["adjusted_moles_per_L"],
            molar_mass=molar_mass,
            solution_concentration=solution_concentration,
            solution_density=solution_density,
        )
        dosing_rate_lph = dose["dose_volume_L_per_L_wastewater"] * flow_rate_lpm * 60

        storage_tank = chemical_storage_tank_size(dosing_rate_lph, supply_days)
        dosing_pump = dosing_pump_size(dosing_rate_lph, pump_headroom)

        result["dosing"] = dose
        result["dosing_rate_L_per_hour"] = dosing_rate_lph
        result["dosing_rate_L_per_day"] = dosing_rate_lph * 24
        result["chemical_storage_tank"] = storage_tank
        result["dosing_pump"] = dosing_pump
        result["chemical_properties_provided"] = {
            "molar_mass_g_per_mol": molar_mass,
            "solution_concentration_w_w": solution_concentration,
            "solution_density_kg_per_L": solution_density,
        }
    else:
        # No chemical info — leave dosing empty and explain why in the output
        result["dosing"] = None
        result["note_on_dosing"] = (
            "Dosing volume, storage tank, and dosing pump not calculated — "
            "chemical properties not provided. Supply molar_mass, "
            "solution_concentration, and solution_density to include these."
        )

    # Attach warnings from validation to the final result
    result["warnings"] = warnings
    return result


# End-to-end test — runs full calc for two scenarios.
if __name__ == "__main__":
    # Case 1 — no chemical info supplied, dosing calcs skipped
    print("=== CASE 1: Chemical-agnostic (SPN hasn't confirmed chemical yet) ===")
    result1 = run_full_calculation(
        flow_rate_lpm=100,
        initial_ph=4.5,
    )
    for k, v in result1.items():
        print(f"{k}: {v}")

    # Case 2 — full calc with example chemical properties
    print("\n=== CASE 2: With chemical properties provided ===")
    result2 = run_full_calculation(
        flow_rate_lpm=100,
        initial_ph=7.5,
        molar_mass=40.0,             # example value only
        solution_concentration=0.32, # example value only
        solution_density=1.35,       # example value only
    )
    for k, v in result2.items():
        print(f"{k}: {v}")


# Input validation tests — covers both errors (raises) and warnings (returns).
if __name__ == "__main__":
    print("\n--- Input validation tests ---")

    # Negative flow — should raise
    try:
        run_full_calculation(flow_rate_lpm=-50, initial_ph=4.5)
    except ValueError as e:
        print(f"Caught error: {e}")

    # pH out of physical range — should raise
    try:
        run_full_calculation(flow_rate_lpm=100, initial_ph=15)
    except ValueError as e:
        print(f"Caught error: {e}")

    # Same initial and target pH — should warn, not fail
    r = run_full_calculation(flow_rate_lpm=100, initial_ph=7.5, target_ph=7.5)
    print(f"Same pH — warnings: {r['warnings']}")

    # Extreme but valid pH — should warn
    r = run_full_calculation(flow_rate_lpm=100, initial_ph=0.5)
    print(f"Extreme pH — warnings: {r['warnings']}")

    # Multiple bad inputs at once — should raise and list them all
    try:
        run_full_calculation(flow_rate_lpm=0, initial_ph=-1, target_ph=20, safety_factor=-2)
    except ValueError as e:
        print(f"Caught multiple errors:\n{e}")
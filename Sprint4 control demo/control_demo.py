# ============================================================
# SPN pH Correction Skid
# Sprint 4 - Proposed Control Logic Demonstration
#
# This program demonstrates the proposed control behaviour
# developed from the Sprint 3 control requirements.
#
# This is a simulation only.
# It does NOT control real equipment.
# ============================================================


# -------------------------
# SYSTEM STATES
# -------------------------

STOPPED = "STOPPED"
STARTUP = "STARTUP"
NORMAL = "NORMAL OPERATION"
SHUTDOWN = "SHUTDOWN"
FAULT = "FAULT / SAFE STATE"


# -------------------------
# PROPOSED I/O TAGS
# -------------------------

PH_TAG = "100T01PH01"
LEVEL_TAG = "100T01LT01"
LOW_LOW_TAG = "100T01LSLL01"
HIGH_LEVEL_TAG = "100T01LSHL01"

AGITATOR_TAG = "100T01AG01"
PUMP_TAG = "100PU01"


# -------------------------
# DISPLAY FUNCTION
# -------------------------

def display_result(
    system_state,
    ph_value,
    ph_status,
    level_status,
    low_low,
    high_level,
    agitator,
    pump,
    dosing_request,
    active_alarm,
    interlock,
    control_status,
    ph_sensor_fault=False
):

    print()
    print("======================================")
    print(" SPN pH CORRECTION SKID")
    print(" SPRINT 4 CONTROL DEMONSTRATION")
    print("======================================")

    print()
    print("System State:", system_state)

    print()
    print("--- SENSOR INPUTS ---")
    print("Tank 1 pH:", ph_value, "-", PH_TAG)
    print("pH Status:", ph_status)
    print("pH Sensor Fault:", ph_sensor_fault)
    print("Tank 1 Level:", level_status, "-", LEVEL_TAG)
    print("Tank 1 Low-Low:", low_low, "-", LOW_LOW_TAG)
    print("Tank 1 High Level:", high_level, "-", HIGH_LEVEL_TAG)

    print()
    print("--- ACTUATOR OUTPUTS ---")
    print("Tank 1 Agitator:", agitator, "-", AGITATOR_TAG)
    print("Pump 1:", pump, "-", PUMP_TAG)
    print("Dosing Request:", dosing_request)

    print()
    print("--- CONTROL STATUS ---")
    print("Active Alarm:", active_alarm)
    print("Interlock:", interlock)
    print("Control Status:", control_status)

    print("======================================")


# -------------------------
# CONTROL DEMONSTRATION
# -------------------------

def run_scenario(option):

    # Default simulated conditions
    system_state = STARTUP

    ph_value = 7.0
    ph_status = "NORMAL"

    level_status = "NORMAL"
    low_low = False
    high_level = False
    ph_sensor_fault = False

    agitator = "STOPPED"
    pump = "STOPPED"

    dosing_request = "NONE"
    active_alarm = "NONE"
    interlock = "INACTIVE"

    control_status = "Startup checks in progress."


    # -------------------------
    # SCENARIO 1
    # NORMAL OPERATION
    # -------------------------

    if option == "1":

        system_state = NORMAL

        agitator = "RUNNING"
        pump = "RUNNING"

        control_status = (
            "Startup completed. "
            "System is operating normally."
        )


    # -------------------------
    # SCENARIO 2
    # LOW pH
    # -------------------------

    elif option == "2":

        system_state = NORMAL

        ph_value = 5.5
        ph_status = "LOW"

        agitator = "RUNNING"
        pump = "RUNNING"

        dosing_request = "BASE"

        active_alarm = "AL-06 - LOW pH"

        control_status = (
            "Low pH detected. "
            "Base dosing response requested."
        )


    # -------------------------
    # SCENARIO 3
    # HIGH pH
    # -------------------------

    elif option == "3":

        system_state = NORMAL

        ph_value = 10.5
        ph_status = "HIGH"

        agitator = "RUNNING"
        pump = "RUNNING"

        dosing_request = "ACID"

        active_alarm = "AL-05 - HIGH pH"

        control_status = (
            "High pH detected. "
            "Acid dosing response requested."
        )


    # -------------------------
    # SCENARIO 4
    # TANK LOW-LOW LEVEL
    # -------------------------

    elif option == "4":

        system_state = FAULT

        level_status = "LOW-LOW"
        low_low = True

        agitator = "STOPPED"
        pump = "STOPPED"

        dosing_request = "NONE"

        active_alarm = (
            "AL-02 - TANK 1 LOW-LOW LEVEL"
        )

        interlock = "ACTIVE"

        control_status = (
            "Tank 1 low-low level detected. "
            "Pump operation is prevented."
        )


    # -------------------------
    # SCENARIO 5
    # pH SENSOR FAULT
    # -------------------------

    elif option == "5":

        system_state = FAULT

        ph_status = "FAULT"
        ph_sensor_fault = True

        agitator = "STOPPED"
        pump = "STOPPED"

        dosing_request = "NONE"

        active_alarm = (
            "AL-07 - pH INSTRUMENT FAULT"
        )

        interlock = "ACTIVE"

        control_status = (
            "pH sensor fault detected. "
            "Automatic dosing is prevented."
        )


    # -------------------------
    # SCENARIO 6
    # SHUTDOWN
    # -------------------------

    elif option == "6":

        system_state = SHUTDOWN

        agitator = "STOPPED"
        pump = "STOPPED"

        dosing_request = "NONE"

        control_status = (
            "Shutdown completed. "
            "Pump, agitator and dosing response are stopped."
        )


    # -------------------------
    # DISPLAY RESULT
    # -------------------------

    display_result(
        system_state,
        ph_value,
        ph_status,
        level_status,
        low_low,
        high_level,
        agitator,
        pump,
        dosing_request,
        active_alarm,
        interlock,
        control_status,
        ph_sensor_fault
    )


# -------------------------
# MAIN MENU
# -------------------------

while True:

    print()
    print("======================================")
    print(" SPN pH CORRECTION SKID")
    print(" SPRINT 4 CONTROL DEMONSTRATION")
    print("======================================")

    print()
    print("Select Demonstration Scenario:")
    print()
    print("1. Normal Operation")
    print("2. Low pH")
    print("3. High pH")
    print("4. Tank 1 Low-Low Level")
    print("5. pH Sensor Fault")
    print("6. Shutdown")
    print("0. Exit")

    print()

    option = input("Enter option: ")

    if option == "0":
        print()
        print("Control demonstration ended.")
        break

    elif option in ["1", "2", "3", "4", "5", "6"]:
        run_scenario(option)

    else:
        print()
        print("Invalid option. Please select 0 to 6.")
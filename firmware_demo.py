"""
EAE Firmware Optional Demonstration
Section 7.1 - CAN Simulation, State Machine, and Command Line Setpoints

Author: Esi Afariwa Otoo

This file extends the cooling controller by demonstrating:
1. A PLC-style state machine
2. Simulated CAN transmit messages
3. Command-line arguments for temperature setpoints
"""

from enum import Enum
import argparse
import time


class SystemState(Enum):
    OFF = "OFF"
    NORMAL = "NORMAL"
    COOLING = "COOLING"
    HIGH_TEMP = "HIGH_TEMP"
    FAULT = "FAULT"


SENSOR_MIN = -40.0
SENSOR_MAX = 150.0


def sensor_fault(*temperatures):
    """Return True if any temperature sensor is outside the valid range."""
    return any(temp < SENSOR_MIN or temp > SENSOR_MAX for temp in temperatures)


def send_can_message(state, pump_cmd, fan_cmd, alarm_cmd, hottest_temp):
    """
    Simulate CAN transmission to a display or vehicle controller.
    This does not use real CAN hardware; it emulates the message content.
    """
    print(
        f"CAN TX | ID: 0x180 | "
        f"STATE={state.value:<10} "
        f"PUMP={int(pump_cmd)} "
        f"FAN={int(fan_cmd)} "
        f"ALARM={int(alarm_cmd)} "
        f"TEMP={hottest_temp:.1f}C"
    )


def cooling_controller(
    ignition_on,
    level_ok,
    temp_inv_in,
    temp_inv_out,
    temp_dcdc_out,
    fan_previous,
    fan_on_temp,
    fan_off_temp,
    high_temp_alarm
):
    """PLC-style cooling controller with state machine logic."""

    hottest_temp = max(temp_inv_in, temp_inv_out, temp_dcdc_out)

    if not level_ok:
        return SystemState.FAULT, False, False, True, "Low coolant level"

    if sensor_fault(temp_inv_in, temp_inv_out, temp_dcdc_out):
        return SystemState.FAULT, False, False, True, "Temperature sensor fault"

    if not ignition_on:
        return SystemState.OFF, False, False, False, "Ignition OFF"

    pump_cmd = True

    if hottest_temp >= fan_on_temp:
        fan_cmd = True
    elif hottest_temp <= fan_off_temp:
        fan_cmd = False
    else:
        fan_cmd = fan_previous

    if hottest_temp >= high_temp_alarm:
        return SystemState.HIGH_TEMP, pump_cmd, True, True, "High temperature warning"

    if fan_cmd:
        return SystemState.COOLING, pump_cmd, fan_cmd, False, "Cooling active"

    return SystemState.NORMAL, pump_cmd, fan_cmd, False, "Normal operation"


def run_demo(args):
    """Run emulated firmware test cases."""

    test_cases = [
        (False, True, 25.0, 26.0, 27.0, "Ignition OFF"),
        (True, True, 30.0, 35.0, 36.0, "Normal operation"),
        (True, True, 38.0, 46.0, 44.0, "Fan ON threshold reached"),
        (True, True, 42.0, 43.0, 44.0, "Fan hysteresis region"),
        (True, True, 35.0, 39.0, 38.0, "Fan OFF threshold reached"),
        (True, True, 50.0, 61.0, 58.0, "High temperature"),
        (True, False, 30.0, 35.0, 36.0, "Low coolant fault"),
        (True, True, 30.0, 200.0, 36.0, "Sensor fault"),
    ]

    fan_previous = False

    print("EAE Optional Firmware Demonstration")
    print("Features: State Machine, Simulated CAN, Command-Line Setpoints")
    print("-" * 95)
    print(f"Fan ON: {args.fan_on} C | Fan OFF: {args.fan_off} C | Alarm: {args.alarm} C")
    print("-" * 95)

    for i, case in enumerate(test_cases, start=1):
        ignition, level, tin, tout, tdcdc, description = case

        state, pump, fan, alarm, message = cooling_controller(
            ignition,
            level,
            tin,
            tout,
            tdcdc,
            fan_previous,
            args.fan_on,
            args.fan_off,
            args.alarm
        )

        fan_previous = fan
        hottest_temp = max(tin, tout, tdcdc)

        print(f"\nCase {i}: {description}")
        print(f"State: {state.value} | Pump: {pump} | Fan: {fan} | Alarm: {alarm}")
        print(f"Message: {message}")

        send_can_message(state, pump, fan, alarm, hottest_temp)

        time.sleep(0.2)


def parse_arguments():
    """Read command-line setpoints."""
    parser = argparse.ArgumentParser(description="EAE Cooling Firmware Demo")

    parser.add_argument(
        "--fan_on",
        type=float,
        default=45.0,
        help="Fan turn-on temperature in degC"
    )

    parser.add_argument(
        "--fan_off",
        type=float,
        default=40.0,
        help="Fan turn-off temperature in degC"
    )

    parser.add_argument(
        "--alarm",
        type=float,
        default=60.0,
        help="High temperature alarm threshold in degC"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    run_demo(args)
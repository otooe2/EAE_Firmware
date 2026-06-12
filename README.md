# EAE_Firmware

Optional firmware demonstration for the EAE Electrical and Controls Challenge.

## Implemented Features

* PLC-style state machine
* Simulated CAN bus transmission
* Command-line configurable temperature setpoints
* Cooling system fault handling
* Fan hysteresis control

## Files

### firmware_demo.py

Demonstrates:

* CAN message simulation
* State machine operation
* Temperature-based cooling control
* Safety monitoring

## Example Usage

```bash
python firmware_demo.py
```

```bash
python firmware_demo.py --fan_on 50 --fan_off 45 --alarm 65
```

## Author

Esi Afariwa Otoo

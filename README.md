# OpenPLC Sample

Basic OpenPLC project for temperature-based fan control using Structured Text and Modbus TCP.

## Documentation

The project documentation is available here:

https://docs.page/cutamar/openplc-sample

## Project Overview

This project demonstrates a simple PLC/ICS temperature control scenario:

- Simulated temperature sensor input
- Cooling fan ON/OFF output
- Structured Text control logic
- OpenPLC Runtime deployment
- Modbus TCP communication for testing
- Validation of threshold and hysteresis behavior

## Project Files

| Path | Description |
|---|---|
| [`projects/st-learning`](projects/st-learning) | Small Structured Text learning project using basic Boolean latch logic |
| [`projects/temp-control`](projects/temp-control) | Main temperature control PLC project |
| [`scripts/test_temperature_control.py`](scripts/test_temperature_control.py) | Basic pymodbus test script for writing simulated temperature values and reading the fan output |
| [`scripts/validate_temperature_control.py`](scripts/validate_temperature_control.py) | Extended validation script with threshold, edge-case, and hysteresis tests |

## Goal

The goal is to set up OpenPLC, write and deploy basic control logic, communicate with the PLC through Modbus TCP, and validate that the PLC responds correctly to simulated temperature values.

## Main Scenario

The main project simulates a temperature-based fan control system.

The PLC reads a simulated temperature sensor value and controls a cooling fan:

- Fan turns **ON** at or above `86.0 °F`
- Fan turns **OFF** at or below `77.0 °F`
- Between both thresholds, the fan keeps its previous state to provide hysteresis

## Validation

The validation scripts use `pymodbus` to communicate with OpenPLC Runtime over Modbus TCP.

They write simulated temperature values to the PLC and read back the `Cooling_Fan` output to confirm that the control logic behaves as expected.
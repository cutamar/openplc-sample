import struct
import time
from dataclasses import dataclass
from pymodbus.client import ModbusTcpClient


PLC_HOST = "127.0.0.1"
PLC_PORT = 502

# OpenPLC mappings
TEMPERATURE_SENSOR_ADDR = 2048  # %MD0
HIGH_THRESHOLD_ADDR = 2050      # %MD1
LOW_THRESHOLD_ADDR = 2052       # %MD2
COOLING_FAN_COIL_ADDR = 0       # %QX0.0


@dataclass
class TestCase:
    step: int
    temperature: float
    expected_fan: bool
    description: str


def float_to_registers(value: float) -> list[int]:
    """Convert a 32-bit float/REAL into two 16-bit Modbus registers."""
    packed = struct.pack(">f", value)
    return list(struct.unpack(">HH", packed))


def registers_to_float(registers: list[int]) -> float:
    """Convert two 16-bit Modbus registers back into a 32-bit float/REAL."""
    packed = struct.pack(">HH", registers[0], registers[1])
    return struct.unpack(">f", packed)[0]


def write_real(client: ModbusTcpClient, address: int, value: float) -> None:
    registers = float_to_registers(value)
    result = client.write_registers(address=address, values=registers)

    if result.isError():
        raise RuntimeError(f"Failed to write REAL value {value} to address {address}: {result}")


def read_real(client: ModbusTcpClient, address: int) -> float:
    result = client.read_holding_registers(address=address, count=2)

    if result.isError():
        raise RuntimeError(f"Failed to read REAL value from address {address}: {result}")

    return registers_to_float(result.registers)


def read_fan_state(client: ModbusTcpClient) -> bool:
    result = client.read_coils(address=COOLING_FAN_COIL_ADDR, count=1)

    if result.isError():
        raise RuntimeError(f"Failed to read Cooling_Fan coil: {result}")

    return bool(result.bits[0])


def run_test(client: ModbusTcpClient, test: TestCase) -> bool:
    write_real(client, TEMPERATURE_SENSOR_ADDR, test.temperature)

    # Give OpenPLC at least a few scan cycles to process the new value.
    time.sleep(0.2)

    observed_fan = read_fan_state(client)
    passed = observed_fan == test.expected_fan

    print(
        f"{test.step:02d} | "
        f"{test.temperature:6.1f} °F | "
        f"expected={str(test.expected_fan):5s} | "
        f"observed={str(observed_fan):5s} | "
        f"{'PASS' if passed else 'FAIL'} | "
        f"{test.description}"
    )

    return passed


def main() -> None:
    tests = [
        TestCase(1, 68.0, False, "normal low temperature"),
        TestCase(2, 76.9, False, "just below low threshold"),
        TestCase(3, 77.0, False, "exact low threshold"),
        TestCase(4, 82.4, False, "between thresholds before fan turns on"),
        TestCase(5, 85.9, False, "just below high threshold"),
        TestCase(6, 86.0, True, "exact high threshold"),
        TestCase(7, 95.0, True, "above high threshold"),
        TestCase(8, 86.1, True, "just above high threshold"),
        TestCase(9, 82.4, True, "between thresholds after fan turned on"),
        TestCase(10, 77.1, True, "just above low threshold"),
        TestCase(11, 77.0, False, "exact low threshold turns fan off"),
        TestCase(12, 68.0, False, "back to low temperature"),
    ]

    client = ModbusTcpClient(PLC_HOST, port=PLC_PORT)

    if not client.connect():
        raise RuntimeError(f"Could not connect to OpenPLC Runtime at {PLC_HOST}:{PLC_PORT}")

    try:
        print("Connected to OpenPLC Runtime")
        print(f"High_Threshold = {read_real(client, HIGH_THRESHOLD_ADDR):.1f} °F")
        print(f"Low_Threshold  = {read_real(client, LOW_THRESHOLD_ADDR):.1f} °F")
        print()
        print("Step | Temp     | Expected       | Observed       | Result | Description")
        print("-----|----------|----------------|----------------|--------|-------------------------------")

        passed_count = 0

        for test in tests:
            if run_test(client, test):
                passed_count += 1

        print()
        print(f"Summary: {passed_count}/{len(tests)} tests passed")

        if passed_count != len(tests):
            raise SystemExit(1)

    finally:
        client.close()
        print("Connection closed")


if __name__ == "__main__":
    main()

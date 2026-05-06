import struct
import time
from pymodbus.client import ModbusTcpClient


PLC_HOST = "127.0.0.1"
PLC_PORT = 502

# OpenPLC mappings
TEMPERATURE_SENSOR_ADDR = 2048   # %MD0
HIGH_THRESHOLD_ADDR = 2050       # %MD1
LOW_THRESHOLD_ADDR = 2052        # %MD2
COOLING_FAN_COIL_ADDR = 0     # %QX0.0


def float_to_registers(value: float) -> list[int]:
    """
    Convert a 32-bit float/REAL into two 16-bit Modbus registers.

    This uses big-endian byte order.
    If your values look wrong in OpenPLC, try swapping the two registers.
    """
    packed = struct.pack(">f", value)
    return list(struct.unpack(">HH", packed))


def registers_to_float(registers: list[int]) -> float:
    """
    Convert two 16-bit Modbus registers back into a 32-bit float/REAL.
    """
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


def run_test(client: ModbusTcpClient, temperature: float, expected_fan: bool | None = None) -> None:
    print(f"\nSetting Temperature_Sensor to {temperature:.1f} °F")

    write_real(client, TEMPERATURE_SENSOR_ADDR, temperature)

    # Give OpenPLC at least a few scan cycles to process the new value
    time.sleep(0.2)

    fan_state = read_fan_state(client)

    print(f"Cooling_Fan = {fan_state}")

    if expected_fan is not None:
        result = "PASS" if fan_state == expected_fan else "FAIL"
        print(f"Expected Cooling_Fan = {expected_fan} -> {result}")


def main() -> None:
    client = ModbusTcpClient(PLC_HOST, port=PLC_PORT)

    if not client.connect():
        raise RuntimeError(f"Could not connect to OpenPLC Runtime at {PLC_HOST}:{PLC_PORT}")

    try:
        print("Connected to OpenPLC Runtime")

        # Optional: write thresholds through Modbus
        #write_real(client, HIGH_THRESHOLD_ADDR, 86.0)
        #write_real(client, LOW_THRESHOLD_ADDR, 77.0)

        print(f"High_Threshold = {read_real(client, HIGH_THRESHOLD_ADDR):.1f} °F")
        print(f"Low_Threshold  = {read_real(client, LOW_THRESHOLD_ADDR):.1f} °F")

        # Test sequence for hysteresis
        run_test(client, 68.0, expected_fan=False)
        run_test(client, 86.0, expected_fan=True)
        run_test(client, 82.4, expected_fan=True)
        run_test(client, 77.0, expected_fan=False)

    finally:
        client.close()
        print("\nConnection closed")


if __name__ == "__main__":
    main()

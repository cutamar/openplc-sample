PROGRAM main
VAR
	Temperature_Sensor : real AT %MD0 := 68.0;
	Cooling_Fan : bool AT %QX0.0 := FALSE;
	High_Threshold : real AT %MD1 := 86.0;
	Low_Threshold : real AT %MD2 := 77.0;
END_VAR

IF Temperature_Sensor >= High_Threshold THEN
    Cooling_Fan := TRUE;
ELSIF Temperature_Sensor <= Low_Threshold THEN
    Cooling_Fan := FALSE;
END_IF;

END_PROGRAM
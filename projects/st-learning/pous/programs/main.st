PROGRAM main
VAR
	Start_Button : bool := FALSE;
	Stop_Button : bool := FALSE;
	Motor_Output : bool := FALSE;
END_VAR

Motor_Output := (Start_Button OR Motor_Output) AND NOT Stop_Button;

END_PROGRAM
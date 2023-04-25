[ control info ]
control_cycle = 8   # milliseconds

[ port info ]
# PORT NAME  | BAUDRATE  | DEFAULT JOINT
/dev/ttyACM0 | 2000000   | r_hip_yaw

[ device info ]
# TYPE    | PORT NAME    | ID  | MODEL          | PROTOCOL | DEV NAME       | BULK READ ITEMS
#dynamixel | /dev/ttyACM0 | 1   | MX-28          | 2.0      | r_sho_pitch    | present_position, position_p_gain, position_i_gain, position_d_gain
#dynamixel | /dev/ttyACM0 | 2   | MX-28          | 2.0      | l_sho_pitch    | present_position, position_p_gain, position_i_gain, position_d_gain
#dynamixel | /dev/ttyACM0 | 3   | MX-28          | 2.0      | r_sho_roll     | present_position, position_p_gain, position_i_gain, position_d_gain
#dynamixel | /dev/ttyACM0 | 4   | MX-28          | 2.0      | l_sho_roll     | present_position, position_p_gain, position_i_gain, position_d_gain
#dynamixel | /dev/ttyACM0 | 5   | MX-28          | 2.0      | r_el           | present_position, position_p_gain, position_i_gain, position_d_gain
#dynamixel | /dev/ttyACM0 | 6   | MX-28          | 2.0      | l_el           | present_position, position_p_gain, position_i_gain, position_d_gain
dynamixel | /dev/ttyACM0 | 7   | MX-28          | 2.0      | r_hip_yaw      | present_position, position_p_gain, position_i_gain, position_d_gain
dynamixel | /dev/ttyACM0 | 8   | MX-28          | 2.0      | l_hip_yaw      | present_position, position_p_gain, position_i_gain, position_d_gain
dynamixel | /dev/ttyACM0 | 9   | MX-64          | 2.0      | r_hip_roll     | present_position, position_p_gain, position_i_gain, position_d_gain
dynamixel | /dev/ttyACM0 | 10  | MX-64          | 2.0      | l_hip_roll     | present_position, position_p_gain, position_i_gain, position_d_gain
dynamixel | /dev/ttyACM0 | 11  | MX-64          | 2.0      | r_hip_pitch    | present_position, position_p_gain, position_i_gain, position_d_gain
dynamixel | /dev/ttyACM0 | 12  | MX-64          | 2.0      | l_hip_pitch    | present_position, position_p_gain, position_i_gain, position_d_gain
dynamixel | /dev/ttyACM0 | 13  | MX-64          | 2.0      | r_knee         | present_position, position_p_gain, position_i_gain, position_d_gain
dynamixel | /dev/ttyACM0 | 14  | MX-64          | 2.0      | l_knee         | present_position, position_p_gain, position_i_gain, position_d_gain
dynamixel | /dev/ttyACM0 | 15  | MX-64          | 2.0      | r_ank_pitch    | present_position, position_p_gain, position_i_gain, position_d_gain
dynamixel | /dev/ttyACM0 | 16  | MX-64          | 2.0      | l_ank_pitch    | present_position, position_p_gain, position_i_gain, position_d_gain
dynamixel | /dev/ttyACM0 | 17  | MX-64          | 2.0      | r_ank_roll     | present_position, position_p_gain, position_i_gain, position_d_gain
dynamixel | /dev/ttyACM0 | 18  | MX-64          | 2.0      | l_ank_roll     | present_position, position_p_gain, position_i_gain, position_d_gain
dynamixel | /dev/ttyACM0 | 19  | MX-28          | 2.0      | head_pan       | present_position, position_p_gain, position_i_gain, position_d_gain
dynamixel | /dev/ttyACM0 | 20  | MX-28          | 2.0      | head_tilt      | present_position, position_p_gain, position_i_gain, position_d_gain
sensor    | /dev/ttyACM0 | 200 | OPEN-CR        | 2.0      | open-cr        | button, present_voltage, gyro_x, gyro_y, gyro_z, acc_x, acc_y, acc_z, roll, pitch, yaw
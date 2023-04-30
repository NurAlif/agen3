import math
from simple_pid import PID

pid_x = PID(0.4, 0.001, 0.0001, setpoint=0)
pid_y = PID(0.23, 0.001, 0.0001, setpoint=0.7)

# stall movement

pid_x.output_limits = (-1.0, 1.0)
pid_y.output_limits = (-1.0, 1.0)

pitch = 0.0
yaw = 0.0

errorPitch = 0.0
out_scale_x = 0.2
out_scale_y = 0.18

ball_track = None

isEnabled = False

####
search_state = 0
s_max_angle = 0.8
s_speed = 0.03
s_2_count = 0

def track(error):
    global pid_x
    global yaw
    global pid_y
    global pitch
    global s_2_count
    global search_state

    # ex = error.x
    # if(ex > 0.1 or ex < -0.1):
    #     ex -= 0.11

    # out_x = (ex) * out_scale
    # out_y = pid_y(error.y) * out_scale
    # out_y = 0.0

    # # print(out_x)

    # pitch += out_y
    # yaw += max(min(-out_x, 0.1), -0.1)


    out_x = -pid_x(error.x)*out_scale_x

    out_y = -pid_y(error.y)*out_scale_y

    if(search_state == 2):
        s_2_count += 1
        pitch += out_y * 0.1
        yaw += out_x * 0.1
        if(s_2_count == 13):
            search_state = 0
    else:
        pitch += out_y
        yaw += out_x

    pitch = max(min(pitch, 1), -1)
    yaw = max(min(yaw, 1), -1)

def search():
    global search_state
    global yaw
    global s_max_angle
    global s_speed
    if(search_state == 0):
        if(yaw < s_max_angle):
            yaw += s_speed
        else:
            search_state = 1
    if(search_state == 1):
        if(yaw > -s_max_angle):
            yaw -= s_speed
        else:
            search_state = 0
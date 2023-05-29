#        1        |
#-1      |       1|
#        |        |
#_______0,0_______|
#       /|\
#        |
#        0 deg

pos_x = 0.0
pos_y = 0.0
yaw = 0.0

target = -1

span_to_rad = 0.1
grad_to_alpha = 0.1
theta_to_beta = 0.23


def locallize_from_goal(goal):
    global pos_x
    global pos_y
    global yaw

    rad = goal.span * span_to_rad
    alpha = goal.grad * grad_to_alpha
    beta = goal.theta * theta_to_beta
    
def walk():
    print()


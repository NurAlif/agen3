# find ball
# chase ball, while do localization (regular goal check) when 
# catch ball, move ball towards goal
# shoot

from walking import Vector2yaw

# repeat



BALL_SEARCHING = 0
BALL_APPROACH = 1
SHOOTING = 4
GOAL_ALIGN = 2
GOAL_ALIGN_2 = 3
GOAL_ALIGN_POST = 5
GOAL_ALIGN_DELAY = 6
GOAL_ALIGN_INIT = 7
GOAL_ALIGN_ANGLE = 8

state = 0

yaw_dead_area = 0.15

last_yaw = 0.0
yaw = 0.0

gt = None
infer = None
bt = None
walk = None

enabled = True
goal_align_time = 0.0
start_align_turn = 0

gt_on_ball_search_last = 0
gt_on_ball_search_interval = 10
gt_on_ball_search_dead_yaw = 0.2
gt_on_ball_search_last_head_pos = [0,0]

setwalkparams = None

interval_checking = 10

goal_align_post_interval = 10
goal_align_post_start = 0
goal_align_angle_start = 0
goal_align_angle_time = 0

show_head_angle = False

def init(goal_tracker, inference, ball_tracker, walking, _setwalkparams):
    global gt
    global infer
    global bt
    global walk
    global setwalkparams
    gt = goal_tracker
    infer = inference
    bt = ball_tracker
    walk = walking
    setwalkparams = _setwalkparams

def run(time, dets, track_ball, head_control):
    global gt_on_ball_search_last
    global gt_on_ball_search_last_head_pos
    global state
    global goal_align_time
    global start_align_turn
    global goal_align_post_start
    global goal_align_angle_start
    global goal_align_angle_time
    
    if show_head_angle:
        print("head py:"+str(head_control[0])+", "+str(head_control[1]))

    if state == BALL_SEARCHING:
        if bt.isEnabled and not gt.enabled and infer.ball_lock:
            move = 0.1
            if head_control[0] > -0.16: 
                move = 0.8
            elif head_control[0] < -0.20 and abs(head_control[1]) < 0.1 :
                state = GOAL_ALIGN_INIT
                return
            walk.setTarget(Vector2yaw(0.0, move, head_control[1]))

    elif state == GOAL_ALIGN_INIT: # init scan
        gt.enabled = True
        gt.pre_head_pos[0] = head_control[0]
        gt.pre_head_pos[1] = head_control[1]
        walk.setTarget(Vector2yaw(0.0, 0.1, 0.0))
        state = GOAL_ALIGN
    elif state == GOAL_ALIGN: # done scan & init turning
        goal = gt.goal
        if not gt.enabled and goal.found:
            goal_align_time = abs(goal.theta.item(0)) * 7
            start_align_turn = time
            turn_gain = -1.5
            if(goal.theta.item(0) > 0.0): turn_gain = 1.5
            x_gain = turn_gain
            yaw_gain = max(min(turn_gain, 0.25), -0.25)
            walk.setTarget(Vector2yaw(-x_gain , 0.0, yaw_gain))
            state = GOAL_ALIGN_2
            setwalkparams(["z_move_amplitude", 0.03])
            print("X_GAIN: ", str(-x_gain))
    elif state == GOAL_ALIGN_2: # turning
        goal = gt.goal
        if time - start_align_turn > goal_align_time:
            walk.setTarget(Vector2yaw(0.0, 0.6, 0.0))
            setwalkparams(["z_move_amplitude", 0.02])
            state = GOAL_ALIGN_POST

    elif state == GOAL_ALIGN_POST:
        if head_control[0] > -0.20 and head_control[1] > 2:
            walk.setTarget(Vector2yaw(0.0, 0.05, head_control[1]))
            goal_align_angle_time = abs(head_control[1])
            goal_align_post_start = time + 1
            state = GOAL_ALIGN_ANGLE

    elif state == GOAL_ALIGN_ANGLE:
        if time - goal_align_angle_start > goal_align_angle_time:
            state = GOAL_ALIGN_INIT

    # elif state == GOAL_ALIGN_DELAY:
    #     # if time - goal_align_post_start > goal_align_post_interval:
    #     #     gt.enabled = True
    #     #     gt.pre_head_pos[0] = head_control[0]
    #     #     gt.pre_head_pos[1] = head_control[1]
    #     #     walk.setTarget(Vector2yaw(0.0, 0.1, 0.0))
    #     #     state = GOAL_ALIGN

    #     # move = 0.1
    #     # if head_control[0] > -0.20: 
    #     move = 0.8
    #     # walk.setTarget(Vector2yaw(0.0, move, head_control[1]))
        
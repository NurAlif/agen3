# find ball
# chase ball, while do localization (regular goal check) when 
# catch ball, move ball towards goal
# shoot

# convention:
# PRE - > ING -> mas juga

from walking import Vector2yaw
import time

# repeat

BALL_SEARCHING = 0

PAUSE = 1

AUTO_READY_INIT = 2
AUTO_READY_INIT_STARTING = 3
AUTO_READY_POSITIONING = 4
AUTO_READY_POST = 5
AUTO_READY_TURNING = 6

AUTO_PLAY = 7

WALK_2_SHOOT_INIT_1 = 8
WALK_2_SHOOT_INIT_2 = 9
WALK_2_SHOOT_INIT_3 = 10

GOAL_SCAN_INIT = 11
GOAL_SCANING = 12


WALK_INIT = 13
WALK_INIT_STARTING = 14

WALK_STOP_INIT = 15
WALK_STOPING = 16

SHOOTING_INIT = 17
SHOOTING = 18
SHOOTING_POST = 19

SHOOTING_2_WALK = 20
SHOOTING_2_WALK_POST = 21

GOAL_ALIGN_BY_YAW_INIT = 22
GOAL_ALIGN_BY_YAW_TURNING = 23

states_dict = {
    0 : "BALL_SEARCHING",
    1 : "PAUSE",
    2 : "AUTO_READY_INIT",
    3 : "AUTO_READY_INIT_STARTING",
    4 : "AUTO_READY_POSITIONING",
    5 : "AUTO_READY_POST",
    6 : "AUTO_READY_TURNING",
    7 : "AUTO_PLAY",
    8 : "WALK_2_SHOOT_INIT_1",
    9 : "WALK_2_SHOOT_INIT_2",
    10 : "WALK_2_SHOOT_INIT_3",
    11 : "GOAL_SCAN_INIT",
    12 : "GOAL_SCANING",
    13 : "WALK_INIT",
    14 : "WALK_INIT_STARTING",
    15 : "WALK_STOP_INIT",
    16 : "WALK_STOPING",
    17 : "SHOOTING_INIT",
    18 : "SHOOTING",
    19 : "SHOOTING_POST",
    20 : "SHOOTING_2_WALK",
    21 : "SHOOTING_2_WALK_POST",
    22 : "GOAL_ALIGN_BY_YAW_INIT",
    23 : "GOAL_ALIGN_BY_YAW_TURNING",
}

state = PAUSE

yaw_dead_area = 0.15

last_yaw = 0.0
yaw = 0.0

gt = None
infer = None
bt = None
walk = None

pubMotionIndex = None
isActionRunning = None
pubEnaMod = None
pubEnableOffset = None

enabled = True
goal_align_time = 0.0
start_align_turn = 0

gt_on_ball_search_last = 0
gt_on_ball_search_interval = 10
gt_on_ball_search_dead_yaw = 0.2
gt_on_ball_search_last_head_pos = [0,0]

setwalkparams = None
setwalkcmd = None

interval_checking = 10

goal_align_post_interval = 10
goal_align_post_start = 0
goal_align_angle_start = 0
goal_align_angle_time = 0

show_head_angle = False

timed_start = 0
timed_delay = 0

initialized = False

actionEnabled = False
ready_time = 15
play_delay = 4

turn_yaw_max_rate = 0.65

time_play_start = 0
max_time_from_play = 1000

def clamp(val, _min, _max):
    return max(min(val, _max), _min)

def plus_or_min(val, out):
    if val > 0: return out
    return -out

def set_state(new_state, _timed_delay = 0):
    global state
    global timed_start
    global timed_delay
    state = new_state
    timed_delay = _timed_delay
    timed_start = time.time()
    print("NEW STATE: "+states_dict[new_state])

def init_action(_pubMotionIndex, _isActionRunning, _pubEnaMod, _pubEnableOffset):
    global pubMotionIndex
    global isActionRunning
    global pubEnaMod
    global pubEnableOffset
    pubMotionIndex = _pubMotionIndex
    isActionRunning = _isActionRunning
    pubEnaMod = _pubEnaMod
    pubEnableOffset = _pubEnableOffset

def enableWalk():
    global actionEnabled
    actionEnabled = False
    pubEnaMod.publish("walking_module")
    pubEnaMod.publish("head_control_module")

def enableAction():
    global actionEnabled
    actionEnabled = True
    pubEnaMod.publish("action_module")
    pubEnaMod.publish("head_control_module")

def playAction(index):
    pubMotionIndex.publish(index)

def stopAction():
    pubMotionIndex.publish(-2)

def init(goal_tracker, inference, ball_tracker, walking, _setwalkparams, _setwalkcmd):
    global gt
    global infer
    global bt
    global walk
    global setwalkparams
    global setwalkcmd
    global initialized

    gt = goal_tracker
    infer = inference
    bt = ball_tracker
    walk = walking
    setwalkcmd = _setwalkcmd
    setwalkparams = _setwalkparams
    initialized = True

def run(time, dets, track_ball, head_control):
    global gt_on_ball_search_last
    global gt_on_ball_search_last_head_pos
    global state
    global goal_align_time
    global start_align_turn
    global goal_align_post_start
    global goal_align_angle_start
    global goal_align_angle_time
    global yaw
    global time_play_start

    deltaT = time - timed_start
    timedEnd = deltaT > timed_delay

    head_pitch = head_control[0]
    head_yaw = head_control[1]
    goal = gt.goal
    goal_theta = goal.theta.item(0)

    if show_head_angle:
        print("head py:"+str(head_pitch)+", "+str(head_yaw))

    if state == BALL_SEARCHING:
        move = 0.65
        if bt.isEnabled and not gt.enabled and infer.ball_lock: 
            if head_control[0] < -0.5: move = 0.25
            if head_control[0] < -0.57 and abs(head_yaw) < 0.1 :
                if abs(yaw) < 0.25:
                    set_state(GOAL_SCAN_INIT)
                elif time - time_play_start < max_time_from_play:
                    set_state(GOAL_ALIGN_BY_YAW_INIT)
                else:
                    set_state(GOAL_SCAN_INIT)
                return 
        yaw_control = plus_or_min(head_yaw, 0.55)
        if abs(head_yaw) < 0.1:
            yaw_control = plus_or_min(head_yaw, 0.25)
        walk.setTarget(0.0, move, yaw_control)

    elif state == GOAL_SCAN_INIT: # init scan
        gt.enabled = True
        gt.set_pre_head_pos(head_control)
        walk.setTarget()
        set_state(GOAL_SCANING)
    
    elif state == GOAL_ALIGN_BY_YAW_INIT:
        turn_gain = plus_or_min(-yaw, 1.4)
        yaw_gain = clamp(turn_gain, -0.4, 0.4)
        walk.setTarget(-turn_gain , 0.0, yaw_gain)
        setwalkparams(["z_move_amplitude", 0.03])
        set_state(GOAL_ALIGN_BY_YAW_TURNING, abs(yaw) * 6)

    elif state == GOAL_ALIGN_BY_YAW_TURNING:
        if timedEnd:
            yaw = 0.0
            set_state(GOAL_SCAN_INIT)

    elif state == GOAL_SCANING:
        if not gt.enabled and goal.found:
            turn_gain = plus_or_min(goal_theta, 1.5)

            yaw_gain = clamp(turn_gain, -0.4, 0.4)
            walk.setTarget(-turn_gain , 0.0, yaw_gain)
            setwalkparams(["z_move_amplitude", 0.03])
            set_state(WALK_2_SHOOT_INIT_1, abs(goal_theta) * 6)
    
    elif state == WALK_2_SHOOT_INIT_1:
        if timedEnd:
            walk.setTarget()
            setwalkcmd("stop")
            set_state(WALK_2_SHOOT_INIT_2, 3)
    
    elif state == WALK_2_SHOOT_INIT_2:
        if timedEnd:
            enableAction()
            set_state(WALK_2_SHOOT_INIT_3, 1)

    elif state == WALK_INIT:
        setwalkcmd("start")
        yaw = 0.0
        walk.setTarget()
        set_state(WALK_INIT_STARTING, play_delay)

    elif state == WALK_INIT_STARTING:
        if timedEnd:
            set_state(BALL_SEARCHING)

    elif state == WALK_STOP_INIT:
        walk.setTarget()
        set_state(WALK_STOPING, 1)
    elif state == WALK_STOPING:
        if timedEnd:
            setwalkcmd("stop")
            set_state(PAUSE)
        
    elif state == WALK_2_SHOOT_INIT_3:
        if timedEnd:
            set_state(SHOOTING_INIT)

    elif state == SHOOTING_2_WALK:
        if timedEnd:
            setwalkcmd("start")
            set_state(SHOOTING_2_WALK_POST, 0.5)
    
    elif state == SHOOTING_POST:
        if timedEnd:
            enableWalk()
            set_state(SHOOTING_2_WALK, 2)

    elif state == SHOOTING_INIT:
        playAction(12)
        set_state(SHOOTING, 6)
    
    elif state == SHOOTING:
        if timedEnd:
            stopAction()
            set_state(SHOOTING_POST, 1)

    elif state == SHOOTING_2_WALK_POST:
        walk.setTarget()
        set_state(WALK_INIT_STARTING, 3)
    
    elif state == AUTO_READY_INIT:
        setwalkcmd("start")
        yaw = 0.0
        walk.setTarget()
        set_state(AUTO_READY_INIT_STARTING, 3)

    elif state == AUTO_READY_INIT_STARTING:
        if timedEnd:
            walk.setTarget(y=0.7)
            set_state(AUTO_READY_POSITIONING, ready_time)
    
    elif state == AUTO_READY_POSITIONING:
        if timedEnd:
            walk.setTarget(yaw=0.5)
            set_state(AUTO_READY_TURNING, 3)

    elif state == AUTO_READY_TURNING:
        if timedEnd:
            walk.setTarget()
            set_state(AUTO_READY_POST, 1 )

    elif state == AUTO_READY_POST:
        if timedEnd:
            set_state(WALK_STOPING, 1)
    
    elif state == AUTO_PLAY:
        setwalkcmd("start")
        time_play_start = time
        set_state(WALK_INIT, play_delay)

    elif state == PAUSE:
        if timedEnd:
            return

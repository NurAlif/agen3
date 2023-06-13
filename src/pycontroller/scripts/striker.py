# find ball
# chase ball, while do localization (regular goal check) when 
# catch ball, move ball towards goal
# shoot

from walking import Vector2yaw

# repeat



AUTO_READY = 21
AUTO_READY_2 = 22
AUTO_READY_FINAL = 23
AUTO_PLAY = 24
AUTO_READY_3 = 27

BALL_SEARCHING = 0
BALL_APPROACH = 1
GOAL_ALIGN = 2
GOAL_ALIGN_2_PUSH = 3
GOAL_ALIGN_2_SHOOT = 25
GOAL_ALIGN_2_SHOOT_2 = 26
GOAL_ALIGN_POST = 5
GOAL_ALIGN_DELAY = 6
GOAL_ALIGN_INIT = 7
GOAL_ALIGN_ANGLE = 8

PAUSE = 10

WALK_STARTING = 11
WALK_STOPING = 12

WALK_2_SHOOTING = 13
WALK_2_SHOOTING_2 = 18
INIT_SHOOTING = 14
SHOOTING = 15
FINISH_SHOOTING = 16
SHOOTING_2_WALK = 17
SHOOTING_2_WALK_2 = 19
SHOOTING_2_WALK_FINISH = 20

GOAL_ALIGN_BY_YAW = 28
GOAL_ALIGN_BY_YAW_2 = 29

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

def set_state(new_state, _timed_start = 0, _timed_delay = 0):
    global state
    global timed_start
    global timed_delay
    state = new_state
    timed_delay = _timed_delay
    timed_start = _timed_start
    print("NEW STATE:"+str(new_state))

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

    deltaT = time - timed_start
    timedEnd = deltaT > timed_delay

    if show_head_angle:
        print("head py:"+str(head_control[0])+", "+str(head_control[1]))

    if state == BALL_SEARCHING:
        move = 0.1
        if bt.isEnabled and not gt.enabled and infer.ball_lock: 
            if head_control[0] >= -0.57:
                move = 0.6
            if head_control[0] < -0.57 and abs(head_control[1]) < 0.1 :
                if abs(yaw) < 0.25:
                    set_state(GOAL_ALIGN_INIT)
                    print("goaling")
                else:
                    print("yawing")
                    set_state(GOAL_ALIGN_BY_YAW)
                return
        yaw_control = min(max(head_control[1], -turn_yaw_max_rate), turn_yaw_max_rate)
        walk.setTarget(Vector2yaw(0.0, move, yaw_control))

    elif state == GOAL_ALIGN_INIT: # init scan
        gt.enabled = True
        gt.pre_head_pos[0] = head_control[0]
        gt.pre_head_pos[1] = head_control[1]
        walk.setTarget(Vector2yaw(0.0, 0.11, 0.0))
        set_state(GOAL_ALIGN)
    
    elif state == GOAL_ALIGN_BY_YAW:
        goal = gt.goal
        turn_gain = -1.4
        if(-yaw > 0.0): turn_gain = 1.4
        x_gain = turn_gain
        yaw_gain = max(min(turn_gain, 0.4), -0.4)
        walk.setTarget(Vector2yaw(-x_gain , 0.13, yaw_gain))
        setwalkparams(["z_move_amplitude", 0.03])
        print("yaw : "+str(yaw))
        print("time : "+str(abs(yaw) * 10))
        set_state(GOAL_ALIGN_BY_YAW_2, time, abs(yaw) * 6)

    elif state == GOAL_ALIGN_BY_YAW_2:
        if timedEnd:
            yaw = 0.0
            set_state(GOAL_ALIGN_INIT)

    elif state == GOAL_ALIGN: # done scan & init turning
        goal = gt.goal
        if not gt.enabled and goal.found:
            # if goal.span < 

            turn_gain = -1.5
            if(goal.theta.item(0) > 0.0): turn_gain = 1.5
            x_gain = turn_gain
            yaw_gain = max(min(turn_gain, 0.4), -0.4)
            walk.setTarget(Vector2yaw(-x_gain , 0.11, yaw_gain))
            setwalkparams(["z_move_amplitude", 0.03])
            print("X_GAIN: ", str(-x_gain))
            set_state(GOAL_ALIGN_2_SHOOT, time, abs(goal.theta.item(0)) * 6)

    elif state == GOAL_ALIGN_2_PUSH: # turning
        goal = gt.goal
        if timedEnd:
            walk.setTarget(Vector2yaw(0.0, 0.8, 0.0))
            setwalkparams(["z_move_amplitude", 0.02])
            set_state(GOAL_ALIGN_POST)
    
    elif state == GOAL_ALIGN_2_SHOOT: # turning
        if timedEnd:
            setwalkcmd("stop")
            set_state(GOAL_ALIGN_2_SHOOT_2, time, 2.1)
    
    elif state == GOAL_ALIGN_2_SHOOT_2:
        if timedEnd:
            enableAction()
            set_state(WALK_2_SHOOTING, time, 1)
 
    elif state == GOAL_ALIGN_POST:
        current_head_yaw = head_control[1]
        if abs(current_head_yaw) > 0.9:
            goal = gt.goal
            turn_gain = -0.8
            head_control[1] = current_head_yaw * 0.3
            if(goal.theta.item(0) > 0.0): turn_gain = 0.8
            yaw_gain = max(min(turn_gain, 0.4), -0.4)
            walk.setTarget(Vector2yaw(0.0, 0.11, yaw_gain))
            set_state(GOAL_ALIGN_ANGLE, time + 1, abs(current_head_yaw*2))

    elif state == GOAL_ALIGN_ANGLE: # yaw turning
        if timedEnd:
            set_state(GOAL_ALIGN_INIT)

    elif state == WALK_STARTING:
        if timedEnd:
            set_state(BALL_SEARCHING)
            
    elif state == WALK_STOPING:
        walk.setTarget(Vector2yaw(0.0, 0.1, 0.0))
        if timedEnd:
            setwalkcmd("stop")
            set_state(PAUSE)
        
    elif state == WALK_2_SHOOTING:
        if timedEnd:
            set_state(INIT_SHOOTING, time, 0.5)

    elif state == SHOOTING_2_WALK:
        if timedEnd:
            enableWalk()
            set_state(SHOOTING_2_WALK_FINISH, time, 0.02)
    
    elif state == FINISH_SHOOTING:
        if timedEnd:
            set_state(SHOOTING_2_WALK, time, 0)

    elif state == INIT_SHOOTING:
        playAction(12)
        set_state(SHOOTING, time, 6)
    
    elif state == SHOOTING:
        if timedEnd:
            stopAction()
            set_state(FINISH_SHOOTING, time, 0.1)

    elif state == SHOOTING_2_WALK_FINISH:
        setwalkcmd("start")
        walk.setTarget(Vector2yaw(0.0, 0.1, 0.0))
        set_state(WALK_STARTING, time, 3)
    
    elif state == AUTO_READY:
        setwalkcmd("start")
        walk.setTarget(Vector2yaw(0.0, 0.1, 0.0))
        if timedEnd:
            walk.setTarget(Vector2yaw(0.0, 0.7, 0.0))
            set_state(AUTO_READY_2, time, ready_time)
    
    elif state == AUTO_READY_2:
        if timedEnd:
            walk.setTarget(Vector2yaw(0.0, 0.1, 0.5))
            set_state(AUTO_READY_3, time, 3)

    elif state == AUTO_READY_3:
        if timedEnd:
            walk.setTarget(Vector2yaw(0.0, 0.1, 0.0))
            set_state(AUTO_READY_FINAL, time, 1 )

    elif state == AUTO_READY_FINAL:
        if timedEnd:
            set_state(WALK_STOPING, time, 1)
    
    elif state == AUTO_PLAY:
        setwalkcmd("start")
        yaw = 0.0
        walk.setTarget(Vector2yaw(0.0, 0.1, 0.0))
        set_state(WALK_STARTING, time, play_delay)

    elif state == PAUSE:
        if timedEnd:
            set_state(PAUSE, time, 3)
        
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
        
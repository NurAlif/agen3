import time
import numpy as np

SEARCHING = 0
FOUND = 1
LOST = 2
SCANING_PRE_HOLD = 7
SCANING_HOLD_PAN = 3
SCANING_POST_HOLD = 6
SCANING_PANING = 4
SCAN_DONE = 5

state = SEARCHING

horizon_angle = 0.6

#    0
# 1.5 x -1.5
#  -2/2

fov = 0.85
offset_x = -0.40

direction = 0 
head_pan = 0
scan_tilt = 0.6
scan_subdivision = 6

min_scan = -1.5
max_scan = 1.5
scan_pos = -1

#searching param
interval_pan = 0.4 #sec
hold_pan = 0.2 #sec
pad_pan = 0.1 #sec
lastTic = 0

current_pos = 0

frame_size = None

head_target_x = 0.0
head_target_y = 0.0


unclustered_goals = []

class Goal:
    def __init__(self):
        self.x = 0.0
        self.theta = 0.0
        self.found = False
    def setall(self, _x, _theta, _found):
        self.x = _x
        self.theta = _theta
        self.found = _found

goal = Goal()

def scan(dets):
    in_goals = dets.goals
    global lastTic 
    global scan_pos
    global current_pos
    global state
    global unclustered_goals
    toc = time.time()
    delta_t = toc - lastTic

    if(state == SCANING_HOLD_PAN):
        if(delta_t > hold_pan):
            lastTic = toc
            state = SCANING_POST_HOLD
            scan_step = (max_scan - min_scan)/scan_subdivision
            current_pos = (scan_step*scan_pos+min_scan)
            
            found = len(in_goals)
            print("goals : "+str(found)+" "+str(current_pos))
            if(found > 0):
                for goal in in_goals:
                    goalPosInFrame = (goal[0]/frame_size[0]*fov-(fov/2))*-1
                    goal = (current_pos+goalPosInFrame+offset_x, goal[1]/frame_size[1])
                    unclustered_goals.append(goal) 
            if scan_pos >= scan_subdivision:
                state = SCAN_DONE
            #insert
                if(found > 0):
                    track(unclustered_goals)
            scan_pos+=1
        # else: dets.goals = []
    elif(state == SCANING_PANING):
        if(delta_t > interval_pan):
            lastTic = toc
            state = SCANING_PRE_HOLD
    elif(state == SCANING_PRE_HOLD):
        if(delta_t > pad_pan):
            lastTic = toc
            dets.goals = []
            state = SCANING_HOLD_PAN
    elif(state == SCANING_POST_HOLD):
        if(delta_t > pad_pan):
            lastTic = toc
            state = SCANING_PANING
            
    else:
        state = SCANING_PRE_HOLD
        unclustered_goals = []
        scan_pos = 0
        


def track(unclustered_goals):
    global goal 
    np_goals = np.array(unclustered_goals)
    max_goal_x, max_goal_y = np_goals.max(axis=0)
    min_goal_x, min_goal_y = np_goals.min(axis=0)
    delta = max_goal_x - min_goal_x
    mid = delta/2 + min_goal_x
    
    left = []
    right = []

    for goal in np_goals.tolist():
        if goal[0] > mid:
            right.append(goal[1])
        else:
            left.append(goal[1])

    if len(left)>0 and len(right)>0:
        goal.setall(mid, 0.0, True)
    else: goal.found = False
    print(mid)
    for i in np_goals:
        print(i) 
import time
import numpy as np

SEARCHING = 0
FOUND = 1
LOST = 2
SCANING_HOLD_PAN = 3
SCANING_PANING = 4
SCAN_DONE = 5

state = SEARCHING

horizon_angle = 0.6

#    0
# -1 x 1
#  -2/2

fov = 0.5

direction = 0 
head_pan = 0

scan_tilt = 0.6

scan_subdivision = 6

min_scan = -1
max_scan = 1

scan_pos = 0

#searching param
interval_pan = 0.4 #sec
hold_pan = 0.2 #sec
lastTic = 0

current_pos = 0

frame_size = None

head_target_x = 0.0
head_target_y = 0.0

unclustered_goals = []

def scan(in_goals):
    global lastTic 
    global scan_pos
    global current_pos
    global state
    unclustered_goals
    toc = time.time()
    delta_t = toc - lastTic

    if(state == SCANING_HOLD_PAN):
        print("SCANING_HOLD_PAN")
        if(delta_t > hold_pan):
            print("SCANING_HOLD_PAN pass")
            lastTic = toc
            state = SCANING_PANING
            scan_step = (max_scan - min_scan)/scan_subdivision
            current_pos = scan_step*scan_pos+min_scan
            scan_pos+=1
            if scan_pos >= scan_subdivision:
                state = SCAN_DONE
            #insert
                found = len(in_goals)
                print("goals : "+str(found))
                if(found > 0):
                    for goal in in_goals:
                        goal = (goal[0]/frame_size[0]*0.5-0.25+current_pos, goal[1]/frame_size[1])
                        unclustered_goals.append(goal)
                    track(unclustered_goals)
    elif(state == SCANING_PANING):
        print("SCANING_PANING")
        if(delta_t > interval_pan):
            print("SCANING_PANING pass")
            lastTic = toc
            state = SCANING_HOLD_PAN
    else:
        scan_pos = 0
        state = SCANING_PANING
        unclustered_goals = []
        


def track(unclustered_goals):
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
        print("goal found")
        print(mid)
        for i in np_goals:
            print(i) 
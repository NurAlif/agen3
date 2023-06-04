# find ball
# chase ball, while do localization (regular goal check) when 
# catch ball, move ball towards goal
# shoot

# repeat
BALL_SEARCHING = 0
BALL_APPROACH = 1
GOAL_ALIGN = 2
SHOOTING = 3

state = 0

x_dead_area = 0.15

yaw = 0.0

gt = None
infer = None
bt = None
def init(goal_tracker, inference, ball_tracker):
    global gt
    global infer
    global bt
    gt = goal_tracker
    infer = inference
    bt = ball_tracker

def run(head_pitch, head_yaw, dets, ball_track, head_control):
    if not gt.enabled:
        head_control
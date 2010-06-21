"""
Here we house all of the state methods used for chasing the ball
"""
import ChaseBallTransitions as transitions
import GoalieTransitions as goalTran
from ..playbook.PBConstants import GOALIE

def chase(player):
    """
    Method to determine which chase state should be used.
    We dump the robot into this state when we are switching from something else.
    """
    player.isChasing = True
    player.hasAlignedOnce = False

    if player.brain.play.isRole(GOALIE):
        return player.goNow('goalieChase')

    if transitions.shouldScanFindBall(player):
        return player.goNow('scanFindBall')
    elif transitions.shouldApproachBall(player):
        return player.goNow('approachBall')
    elif transitions.shouldKick(player):
        return player.goNow('waitBeforeKick')
    else:
        return player.goNow('scanFindBall')

def goalieChase(player):
    """
    TODO: make goalie more aggressive (different transitions?)
    """
    if transitions.shouldScanFindBall(player):
        return player.goNow('scanFindBall')
    elif transitions.shouldApproachBall(player):
        return player.goNow('approachBall')
    elif transitions.shouldKick(player):
        return player.goNow('waitBeforeKick')
    else:
        return player.goNow('scanFindBall')

def chaseAfterKick(player):
    player.brain.tracker.trackBall()
    return player.goLater('chase')

def approachBall(player):
    """
    Once we are aligned with the ball, approach it
    """
    if player.firstFrame():
        player.brain.nav.chaseBall()
        player.hasAlignedOnce = False

    if transitions.shouldActiveLoc(player):
        player.brain.tracker.activeLoc()

    else:
        player.brain.tracker.trackBall()

    # Switch to other states if we should
    if player.penaltyKicking and \
           player.brain.ball.inOppGoalBox():
        return player.goNow('penaltyBallInOppGoalbox')

    elif player.brain.play.isRole(GOALIE) and goalTran.dangerousBall(player):
        return player.goNow('approachDangerousBall')

    elif transitions.shouldDribble(player):
        return player.goNow('dribble')

    elif transitions.shouldKick(player) or \
             transitions.shouldPositionForKick(player):
        return player.goNow('positionForKick')

    if player.brain.tracker.activeLocOn:
        if transitions.shouldScanFindBallActiveLoc(player):
            return player.goLater('scanFindBall')
    else:
        if transitions.shouldScanFindBall(player):
            return player.goLater('scanFindBall')

    return player.stay()

PFK_BALL_CLOSE_ENOUGH = 30
PFK_BALL_VISION_FRAMES = 15
BUFFER_FRAMES_THRESHOLD = 3

def positionForKick(player):
    """
    State to align on the ball once we are near it
    """
    if player.firstFrame():
        kick = player.brain.kickDecider.decideKick()
        player.brain.nav.kickPosition(kick)
        player.inKickingState = True
        player.ballTooFar = 0

    if player.brain.nav.walkX <= 0:
        player.brain.tracker.activeLoc()
    else:
        player.brain.tracker.trackBall()

    # something has gone wrong, maybe the ball was moved?
    if (player.brain.ball.dist > PFK_BALL_CLOSE_ENOUGH or
        player.brain.ball.framesOff > PFK_BALL_VISION_FRAMES):
        player.ballTooFar += 1
        if player.ballTooFar > BUFFER_FRAMES_THRESHOLD:
            return player.goNow('chase')
    else:
        player.ballTooFar = 0

    # Leave this state if necessary
    if transitions.shouldKick(player):
        return player.goNow('kickBallExecute')

    if player.brain.tracker.activeLocOn:
        if transitions.shouldScanFindBallActiveLoc(player):
            player.inKickingState = False
            return player.goLater('scanFindBall')
    else:
        if transitions.shouldScanFindBall(player):
            player.inKickingState = False
            return player.goLater('scanFindBall')

    if transitions.shouldApproachFromPositionForKick(player):
        player.inKickingState = False
        return player.goLater('approachBall')

    if not player.brain.play.isRole(GOALIE):
        if transitions.shouldDribble(player):
            return player.goNow('dribble')

    return player.stay()

def dribble(player):
    """
    Keep running at the ball, but dribble
    """
    if player.firstFrame():
        player.brain.nav.dribble()

    # if we should stop dribbling, see what else we should do
    if transitions.shouldStopDribbling(player):

        # may not be appropriate due to turned out feet...
        if transitions.shouldPositionForKick(player):
            return player.goNow('positionForKick')
        elif transitions.shouldApproachBall(player):
            return player.goNow('approachBall')

    return player.stay()

# TODO
def approachDangerousBall(player):
    if player.firstFrame():
        player.stopWalking()
    #print "approach dangerous ball"
    #single steps towards ball and goal with spin
    player.stopWalking()

    if not goalTran.dangerousBall(player):
        return player.goLater('approachBall')
    if transitions.shouldScanFindBall(player):
        return player.goLater('scanFindBall')
    elif transitions.shouldSpinFindBall(player):
        return player.goLater('spinFindBall')

    return player.stay()

import kicks
import KickInformation
import KickingConstants as constants
from .. import NogginConstants

class KickDecider(object):
    """
    Uses current info gathered by KickInformation to determine the
    best possible kick and where we should position when called
    """

    def __init__(self, brain):
        self.brain = brain
        self.info = KickInformation.KickInformation(brain)

    def resetInfo(self):
        """
        resets kickInfo so we can decide on next kick
        """
        self.info = KickInformation.KickInformation(self.brain)

    def getKick(self):
        """
        returns the kick we have decided. If None, then orbit for Loc.
        """
        if self.info.kick is None:
            self.info.kick = kicks.CENTER_KICK_POSITION
            self.info.kick.nullKick = True
        return self.info.kick

    def setKick(self, k):
        """
        sets a particular kick
        """
        self.info.kick = k

    def getSweetMove(self):
        """
        returns the sweet move required for motion to kick
        """
        kick = self.info.kick
        # TODO make this check unneccessary by making all kicks dynamic.
        if kick == kicks.LEFT_DYNAMIC_STRAIGHT_KICK or \
                kick == kicks.RIGHT_DYNAMIC_STRAIGHT_KICK:
            ball = self.brain.ball
            dist = ball.distTo(kick.dest)
            return kick.sweetMove(ball.relY, dist)
        else:
            return kick.sweetMove

    def getKickObjective(self):
        self.info.kickObjective

    def setKickOff(self):
        """
        sets the kick we should do in the kickOff situation
        """
        smallTeam = self.brain.playbook.pb.numActiveFieldPlayers < 3

        # if there are too few players on the field to do a side kick pass.
        if smallTeam:
            print "Kickoff!"
            self.setKick(self.info.chooseShortQuickKick())
        # do a side kick pass depending on where the offender is.
        elif self.brain.playbook.pb.kickoffFormation == 0:
            self.setKick(kicks.RIGHT_SIDE_KICK)
            print "Kickoff RIGHT_SIDE_KICK"
        else:
            self.setKick(kicks.LEFT_SIDE_KICK)
            print "Kickoff LEFT_SIDE_KICK"

        self.info.kickObjective = constants.OBJECTIVE_KICKOFF

    def decideKick(self):
        """
        using objective and heuristics and localization determines best kick
        """
        # Re-initialize to clear data
        self.resetInfo()

        # Check localization to make sure it's good enough.
        if self.brain.my.locScore == NogginConstants.BAD_LOC:
            print "BAD_LOC!"
            self.info.kick = None # TODO set this to "Null Kick" for orbiting.
            return

        if self.info.canScoreAll():
            self.score()
        elif self.info.canScoreSome():
            self.chooseScoringKick()
        if self.info.openTeammateCanScore():
            self.chooseOneTimerKick()
        elif self.info.openTeammate():
            self.choosePassingKick()
        if self.info.canClear():
            self.chooseClearingKick()
        """Don't use these for now. just clearing is simpler??"""
        #if self.info.canAdvance():
        #    self.chooseAdvancingKick()
        #if self.info.canCross():
        #    self.chooseCrossingKick()
        if self.info.canPassBack():
            self.choosePassBackKick()

        self.info.kick = self.chooseKick()
        print "Chose: {0}".format(self.info.kick)
        return self.info.kick

    def score(self):
        """
        We are confident we can score with any kick.
        """

        # First we want to figure out which aim point is better.
        # For now just worry about which is faster to kick for,
        # Don't worry about open field yet (6/28/11)

        kickDest = self.info.bestAlignedDest([constants.SHOOT_RIGHT_AIM_POINT,
                                              constants.SHOOT_LEFT_AIM_POINT])

        # Next we want to find the best kick that will hit that point.
        # Since we know any kick will score, we don't have to worry about
        # any range determinations.

        self.info.kickChoices['scoringKick'] = self.info.bestAlignedKick(kickDest)

    def chooseScoringKick(self):
        return

    def chooseOneTimerKick(self):
        return

    def choosePassingKick(self):
        return

    def chooseClearingKick(self):
        return

    def chooseAdvancingKick(self):
        return

    def chooseCrossingKick(self):
        return

    def choosePassBackKick(self):
        return


    def chooseKick(self):
        """
        Chooses out of all possibilities, which kick to do.
        Currently preferences by speed of dividends
        (i.e. Scoring, passing, clearing). Passing comes before
        clearing because the ball travels faster than robots.
        """
        # Since this order is the order of the dictionary,
        # iterate through and find the first that isn't None.
        for kind, kick in self.info.kickChoices.iteritems():
            if kick == None:
                continue
            return kick


        """
        # Note: may want to use headingTo(yglp) etc...
        oppLeftPost = self.brain.oppGoalLeftPost
        oppRightPost = self.brain.oppGoalRightPost

        if (my.headingTo(oppLeftPost, forceCalc = True) > my.h >
            my.headingTo(oppRightPost, forceCalc = True)):
            return self.chooseDynamicKick()
        elif (my.headingTo(oppLeftPost, forceCalc = True) > -1*my.h >
              my.headingTo(oppRightPost, forceCalc = True)):
            return self.chooseShortBackKick()
        elif (my.h > 0):
            print "LEFT_SIDE"
            return kicks.LEFT_SIDE_KICK
        else:
            print "RIGHT_SIDE"
            return kicks.RIGHT_SIDE_KICK
        """

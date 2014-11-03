__author__ = 'SirGippy'

from numpy import random
from math import log2, pow


PARENTS = 50
SPAWN = 1
GENERATIONS = 5

VOLATILITY = 0.1

HOME_FIELD_ADVANTAGE = 0.3
HFA_FACTOR = log2(1 + HOME_FIELD_ADVANTAGE)

QUALITY_WIN_FACTOR = 0.05
QUALITY_WIN_LOWER_BOUND = 7
QUALITY_WIN_UPPER_BOUND = 24

STRENGTH_OF_SCHEDULE_FACTOR = 0.1


class Team:
    def __init__(self, name):
        self.name = name
        self.season = []

    def addGame(self, game):
        self.season.append(game)

    def __eq__(self, other):
        return self.name == other.name


class Game:
    def __init__(self, homeTeam, homeScore, awayTeam, awayScore, neutral=False):
        self.homeTeam = homeTeam
        self.homeScore = homeScore
        self.awayTeam = awayTeam
        self.awayScore = awayScore
        self.neutral = neutral

    def getQwf(self, mov):
        if mov >= QUALITY_WIN_UPPER_BOUND:
            thisQwf = 0
        elif mov <= QUALITY_WIN_LOWER_BOUND:
            thisQwf = QUALITY_WIN_FACTOR
        else:
            thisQwf = (1 - mov / (QUALITY_WIN_UPPER_BOUND - QUALITY_WIN_LOWER_BOUND)) * QUALITY_WIN_FACTOR
        return thisQwf

    def probability(self, ratingSet):

        if self.homeScore > self.awayScore:
            winProbability = self.probabilityHomeWin(ratingSet)
            loseProbability = self.probabilityAwayWin(ratingSet)
            mov = self.homeScore - self.awayScore
        else:
            winProbability = self.probabilityAwayWin(ratingSet)
            loseProbability = self.probabilityHomeWin(ratingSet)
            mov = self.awayScore - self.homeScore

        qwf = self.getQwf(mov)

        return pow(winProbability, 1 - qwf - STRENGTH_OF_SCHEDULE_FACTOR) * \
               pow(loseProbability, qwf + STRENGTH_OF_SCHEDULE_FACTOR)

    def probabilityHomeWin(self,ratingSet):
        awayRating = ratingSet.getRating(self.awayTeam)
        homeRating = ratingSet.getRating(self.homeTeam)

        if not self.neutral:
            homeRating += HFA_FACTOR

        return 2**homeRating / (2**homeRating + 2**awayRating)

    def probabilityAwayWin(self,ratingSet):
        awayRating = ratingSet.getRating(self.awayTeam)
        homeRating = ratingSet.getRating(self.homeTeam)

        if not self.neutral:
            homeRating += HFA_FACTOR

        return 2**awayRating / (2**homeRating + 2**awayRating)

    def probabilityTeamWin(self,ratingSet,team):
        if self.homeTeam == team:
            return self.probabilityHomeWin(ratingSet)
        else:
            return self.probabilityAwayWin(ratingSet)



class RatingSet:
    def __init__(self, teamList):
        self.ratings = {}
        self.teams = teamList

    def setRating(self, team, rating):
        self.ratings[team] = rating

    def getRating(self, team):
        return self.ratings[team]

    def spawn(self):
        newSet = RatingSet(self.teamList)
        for team in self.teamList:
            newSet.ratings[team] = self.ratings[team] + random.normal(0, VOLATILITY)
        return newSet



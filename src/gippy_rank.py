__author__ = 'SirGippy'


from numpy import random
from math import log2


PARENTS = 50
SPAWN = 1
GENERATIONS = 5

VOLATILITY = 0.1

HOME_FIELD_ADVANTAGE = 0.3
HFA_FACTOR = log2(1+HOME_FIELD_ADVANTAGE)
QUALITY_WIN = 0.05
STRENGTH_OF_SCHEDULE = 0.1


class Team:
    def __init__(self,name):
        self.name = name
        self.season = []

    def addGame(self,game):
        self.season.append(game)


class Game:
    def __init__(self,homeTeam,homeScore,awayTeam,awayScore,neutral=False):
        self.homeTeam = homeTeam
        self.homeScore = homeScore
        self.awayTeam = awayTeam
        self.awayScore = awayScore
        self.neutral = neutral


class RatingSet:
    def __init__(self,teamList):
        self.ratings = {}
        self.teams = teamList

    def setRating(self,team,rating):
        self.ratings[team] = rating

    def getRating(self,team):
        return self.ratings[team]

    def spawn(self):
        newSet = RatingSet(self.teamList)
        for team in self.teamList:
            newSet.ratings[team] = self.ratings[team] + random.normal(0,VOLATILITY)
        return newSet



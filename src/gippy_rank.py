__author__ = 'SirGippy'

from numpy import random
from math import log2, pow


PARENTS = 50
SPAWN = 1
GENERATIONS = 5

VOLATILITY = 0.1

HOME_FIELD_ADVANTAGE = 0.3
HFA_FACTOR = log2(1 + HOME_FIELD_ADVANTAGE)

QWF = 0.05
QWLB = 7
QWUB = 24

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
        if mov >= QWUB:
            thisQwf = 0
        elif mov <= QWLB:
            thisQwf = QWF
        else:
            thisQwf = (1 - (mov -  QWLB) / (QWUB - QWLB)) * QWF
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
        self.ratings[team.name] = rating

    def getRating(self, team):
        return self.ratings[team.name]

    def spawn(self):
        newSet = RatingSet(self.teams)
        for team in self.teams:
            newSet.ratings[team.name] = self.ratings[team.name] + random.normal(0, VOLATILITY)
        return newSet

class GamesList:
    def __init__(self,file):
        games = []
        with open(file,'r') as scoresFile:
            for line in scoresFile:
                awayTeam = line[10:38].strip()
                awayScore = int(line[38:40].strip())
                homeTeam = line[41:69].strip()
                homeScore = int(line[69:71].strip())
                if len(line) > 72:
                    neutral = True
                else:
                    neutral = False
                games.append(Game(awayTeam,awayScore,homeTeam,homeScore,neutral))
        self.games = games


def parseTeamListFile(file):
    teams = {}
    with open(file,'r') as teamFile:
        for line in teamFile:
            teams[line.strip()] = Team(line.strip())
    return teams

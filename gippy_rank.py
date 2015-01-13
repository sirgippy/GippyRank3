__author__ = 'SirGippy'

from numpy import random
from math import log2, pow
from operator import itemgetter


PARENTS = 100
SPAWN = 3
TOTAL_SIZE = PARENTS * (1 + SPAWN)

GENERATIONS = 200

VOLATILITY = 1
MUTATION_RATE = 0.2

HOME_FIELD_ADVANTAGE = 0.3
HFA_FACTOR = log2(1 + HOME_FIELD_ADVANTAGE)

QWF = 0.05
QWLB = 7
QWUB = 24

STRENGTH_OF_SCHEDULE_FACTOR = 0.1


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
        self.score = 0

    def setRating(self, team, rating):
        self.ratings[team] = rating

    def getRating(self, team):
        return self.ratings[team]

    def spawn(self):
        newSet = RatingSet(self.teams)
        newSet.ratings = self.ratings.copy()
        for team in self.teams:
            if random.random() < MUTATION_RATE:
                newSet.ratings[team] = self.ratings[team] + random.normal(0, VOLATILITY)
        return newSet

    def evaluateProbability(self,gamesList):
        self.score = 0
        for game in gamesList:
            self.score = self.score - log2(game.probability(self))

    def print(self):
        sortedRatings = sorted(self.ratings.items(), key=itemgetter(1), reverse=True)
        for rating in sortedRatings:
            print(rating[0] + ' ' + "{:.3f}".format(rating[1]))


class GamesList:
    def __init__(self,file=None,tl=None):
        games = []
        ii = 0
        if file is not None:
            with open(file,'r',encoding='utf-8') as scoresFile:
                for line in scoresFile:
                    awayTeam = line[10:38].strip()
                    awayScore = int(line[38:40].strip())
                    homeTeam = line[41:69].strip()
                    homeScore = int(line[69:71].strip())
                    if len(line) > 72:
                        neutral = True
                    else:
                        neutral = False

                    if tl is None or (tl.hasTeam(homeTeam) and tl.hasTeam(awayTeam)):
                        games.append(Game(awayTeam,awayScore,homeTeam,homeScore,neutral))
        self.games = games

    def getSeason(self,team):
        gl = GamesList()
        for game in self.games:
            if game.homeTeam == team.name or game.awayTeam == team.name:
                gl.games.append(game)
        return gl

    def __iter__(self):
        return iter(self.games)


class TeamList:
    def __init__(self,file=None):
        teams = []
        if file is not None:
            with open(file,'r') as teamFile:
                for line in teamFile:
                    teams.append(line.strip())
        self.teams = teams

    def merge(self,other):
        tl = TeamList()
        tl.teams = self.teams + other.teams
        return tl

    def hasTeam(self,name):
        for team in self.teams:
            if team == name:
                return True
        return False

    def __iter__(self):
        return iter(self.teams)


class RatingSetPool:
    def __init__(self,teamList,gamesList):
        self.pool = []
        self.teamList = teamList
        self.gamesList = gamesList
        rs = RatingSet(self.teamList)
        for team in teamList:
            rs.setRating(team,0)
        rs.evaluateProbability(self.gamesList)
        for i in range(0,TOTAL_SIZE):
            newRs = rs.spawn()
            newRs.evaluateProbability(self.gamesList)
            self.pool.append(newRs)
        self.sortPool()

    def gradeNewMembers(self):
        for i in range(PARENTS,TOTAL_SIZE):
            self.pool[i].evaluateProbability(self.gamesList)

    def sortPool(self):
        self.pool = sorted(self.pool, key=lambda rs: rs.score)

    def spawnNewMembers(self):
        for i in range(0,PARENTS):
            for j in range(1,SPAWN+1):
                self.pool[i+j*PARENTS] = self.pool[i].spawn()

    def __iter__(self):
        return iter(self.pool)

    def nextGeneration(self):
        self.spawnNewMembers()
        self.gradeNewMembers()
        self.sortPool()


def run():
    # fbs = TeamList('1A.txt')
    # fcs = TeamList('1AA.txt')
    # div1 = fbs.merge(fcs)
    # gl = GamesList('scores.txt',div1)
    div1 = TeamList('1A.txt')
    gl = GamesList('scores.txt',div1)
    rsp = RatingSetPool(div1,gl)
    for i in range(0,GENERATIONS):
        rsp.nextGeneration()
    rs = rsp.pool[0]
    rs.print()


if __name__ == '__main__':
    run()
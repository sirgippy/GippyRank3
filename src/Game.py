__author__ = 'SirGippy'

class Game:
    def __init__(self,homeTeam,homeScore,awayTeam,awayScore,neutral=False):
        self.homeTeam = homeTeam
        self.homeScore = homeScore
        self.awayTeam = awayTeam
        self.awayScore = awayScore
        self.neutral = neutral

    def location(self,team):
        if self.neutral:
            return 2
        elif self.homeTeam == team:
            return 1
        else:
            return 0
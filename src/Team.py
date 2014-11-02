__author__ = 'SirGippy'

class Team:
    def __init__(self,name):
        self.name = name
        self.season = []

    def addGame(self,game):
        self.season.append(game)
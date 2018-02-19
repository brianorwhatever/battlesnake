from game import Game
from funcs import playMatchesBetweenVersions
import loggers as lg

player_1_version = -1
player_2_version = input('version number?')

env = Game()
playMatchesBetweenVersions(env, 2, player_1_version, player_2_version, 10, lg.logger_play, 0)

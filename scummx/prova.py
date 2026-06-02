from .game import Game

import sys


g=Game(sys.argv[1])
cost = g.read_costume(3)
cost.create_animation([1])
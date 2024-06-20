"""
    Python Dungeon Crawler: Reborn | RPINerd, 06/19/24

    A rogue-like dungeon crawler written in pure Python; in the process of being updated to run on Python 3

    Original Author: Dominic Kexel <dk@evil-monkey-in-my-closet.com>

    This program is free software; you can redistribute it and/or modify it under the terms of the GNU General
    Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option)
    any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
    implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
    License for more details.

    Part of (or All) the graphic tiles used in this program is the public domain roguelike tileset "RLTiles".
    Some of the tiles have been modified by [Dominic].
    You can find the original tileset at: http://rltiles.sf.net
"""

import gzip
import os
import pickle
import sys

import pygame

if "--profile" in sys.argv:
    import profile

sys.path.append(os.path.join(".", "src"))

import engine
import pdcglobal

for file in os.listdir("."):
    if file[0:3] == "MAP":
        os.remove(file)

pygame.init()
screen = pygame.display.set_mode((1024, 768))

ts = True

if "--newgame" not in sys.argv:
    if os.access("save.gz", os.F_OK):
        FILE = gzip.open("save.gz", "r")
        game = pickle.load(FILE)
        game.screen = screen
        game.re_init()
        FILE.close()
        ts = False
    else:
        game = engine.Engine()
else:
    game = engine.Engine()

s = game.start

if "--profile" in sys.argv:
    profile.run("quit_mes = s(ts)")
else:
    quit_mes = s(ts)

if quit_mes == pdcglobal.SAVE:
    data = game
    FILE = gzip.open("save.gz", "w")
    pickle.dump(data, FILE, 2)
    FILE.close()
else:
    if os.access("save.gz", os.F_OK):
        os.remove("save.gz")

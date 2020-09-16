#make exe
# import cx_Freeze
import math
# executables = [cx_Freeze.Executable("mainmenu.py")]
#
# cx_Freeze.setup(
#     name="RTS game",
#     options={"build_exe": {"packages":["pygame"]}},
#     executables = executables
#     )

## random map generator (https://dxprog.com/files/randmaps.html)
## https://www.redblobgames.com/maps/terrain-from-noise/

import random
import sys
import os
import csv
import pygame
from pygame.transform import scale
from pygame.locals import *

main_dir = os.path.dirname(os.path.abspath(__file__))

gradelist = {}
# with open(main_dir + "\data" + '\\unit_grade.csv', 'r') as unitfile:
#     rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
#     for row in rd:
#         for n, i in enumerate(row):
#             if i.isdigit() == True:
#                 row[n] = float(i)
#         gradelist[row[0]] = row[1:]
#
#
# for grade in range(len(gradelist)):
#     if 0 in gradelist:
#         print(gradelist)

# options = {0:"Broken", 1:"Retreating", 2:"Breaking", 3:"Poor", 4:"Wavering",  5:"Balanced", 6:"Steady", 7:"Fine", 8:"Confident", 9:"Eager", 10:"Ready"}
# if 0 in options:
#     print(options[0])

import sys
import numpy as np

# skilllist = {}
# with open(main_dir + "\data" + '\\unit_ability.csv', 'r') as unitfile:
#   rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
#   for row in rd:
#     for n, i in enumerate(row):
#       if i.isdigit() == True:
#         row[n] = float(i)
#       if i == "":
#         row[n] = 100
#       if "," in i: row[n] = [row[n]]
#     skilllist[row[0]] = row[1:]
# # print(self.gradelist[0])
# unitfile.close()
# k = [21,36]
# d = []
# n = []
# k = "Swordsmen are the most basic and balanced unit in most armies. They can fight well in most situation and can hold their lines well enough. Truly the Jack of all trade of all units that are safest to pick in unknown situations. But of course, a jack of all trade lack specialities that make them excellent in a specific situation. If you by some means manage to learn the enemy composition from in and out, it will be better to employed troops that are more specialised or you can still pick swordsmen if you like well-balanced units."
# print(len(k),k.split())
# while len(k) > 0:
#     for i in k:
#         if len(n)>50:
import pygame
import timeit

# whoarray = [np.array([20000, 20001, 20002, 20003,     1]), np.array([20005, 20000]), np.array([    1, 20009]), np.array([20005, 20006, 20007, 20008, 20009])]
# squadalive = np.array([1,1,1,2,2])
# print(squadalive[np.where(armysquad == 1)[0][0]] )
# squadalive[np.where(armysquad == 1)[0][0]] = 5
# list = [0,1,2,3,4,5,6,7,8,9,10]
# starttime = timeit.default_timer()
# print("The start time is :",starttime)
# run = 0
# while run != 100:
#     for k in list:
#            if k == 5: print(k)
#     run += 1
# print("The time difference is :", timeit.default_timer() - starttime)
neartarget = {}
qlist = []
test = pygame.Vector2(900,300)
thisposlist = {1:pygame.Vector2(0,0), 2:pygame.Vector2(1000,1000)}
for n, thisside in thisposlist.items(): neartarget[n] = pygame.Vector2(thisside).distance_to(test)
for i in test:
    qlist.append(abs(i-1000))
    qlist.append(abs(i))
print(qlist.index(min(qlist)),qlist)

#[100.0, 900.0, 700.0, 300.0]
#0 = X 1000, 1 = X 0, 2 = Y 1000, 3 = Y 0
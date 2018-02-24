# # import pygame
# #
# # fontList = pygame.font.get_fonts()
# #
# # # print fontList
# #
# # if "consola" in fontList:
# #     #print True
# #
# # else:
# #     #print False
#
# import cv2
# import numpy as np
# # lower_blue = np.uint8([[[0, 141, 182]]])
# # hsv_green = cv2.cvtColor(lower_blue,cv2.COLOR_BGR2HSV)
# # print hsv_green
#
# image = cv2.imread("data/images/blueMonster_forStart.png")
# flipped = cv2.flip(image, 1)
# cv2.imwrite("data/images/lala.png",flipped)
import time
import networkx as nx
# G = nx.Graph()
# L = [(0,0),(0,1),(1,0),(1,1),(1,2),(2,1)]
# startTime = time.time()
# G.add_nodes_from(L)
# while(len(L) > 0):
#     (x, y) = L[0]
#     if (x, y - 1) in L:
#         G.add_edge((x, y-1), (x,y), weight = 1)
#         #L.remove((x-1,y-1))
#     if (x - 1, y) in L:
#         G.add_edge((x-1, y), (x,y), weight = 1)
#         #L.remove((x-1, y+1))
#     if (x, y + 1) in L:
#         G.add_edge((x, y+1), (x,y), weight = 1)
#         #L.remove((x+1, y-1))
#     if (x + 1, y) in L:
#         G.add_edge((x+1, y), (x,y), weight = 1)
#         #L.remove((x+1, y+1))
#     L.remove((x,y))
#
# shortest = nx.shortest_path(G,(0,0),(2,1),1)
# endTime = time.time()
# print (endTime-startTime) * 1000000
# print shortest

# graph = nx.grid_2d_graph(20,15)
# graph.remove_nodes_from([(0,3),(1,1),(2,2)])
# start = time.time()
# shortest = nx.shortest_path(graph,(14,14),(0,0))
# #shortest = nx.shortest_path(graph,(1,2),(2,0))
# end = time.time()
# print (end-start)*1000
# print shortest

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

# writeFile("highScores.txt", "100,200,300")
# writeFile("highScores.txt", "100")

import datetime

# now = datetime.datetime.now()
# print "Current date and time using str method of datetime object:"
# print str(now)
#
# print
# print "Current date and time using instance attributes:"
# print "Current year: %d" % now.year
# print "Current month: %d" % now.month
# print "Current day: %d" % now.day
# print "Current hour: %d" % now.hour

def recordTime():
    now = datetime.datetime.now()
    year = now.year #int
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    return "%d.%d.%02d %02d:%02d" % (year, month, day, hour, minute)
#print recordGameTime()

# l = ["hi mom", "i am here", "how are you"]
# s = ",".join(l)
# print s
def writeScores(path,score):
    time = recordTime()
    scores = readFile(path)
    if scores == "" and score > 0:
        contentsToWrite = "%05d   %s" % (score, time)
        writeFile(path, contentsToWrite)
    else:
        scoresList = scores.split(",")
        if len(scoresList) < 3:
            numList = []
            for i in range(len(scoresList)):
                items = scoresList[i].split(" ")
                numList.append(int(items[0]))
            if score not in numList and score > 0:
                scoresList.append("%05d   %s" % (score, time))
                contentsToWrite = ",".join(scoresList)
                writeFile(path, contentsToWrite)
        if len(scoresList) == 3:
            numList = []
            for i in range(len(scoresList)):
                items = scoresList[i].split(" ")
                numList.append(int(items[0]))
            minimum = min(numList)
            if score > min(numList):
                index = numList.index(minimum)
                scoresList.pop(index)
                scoresList.append("%05d  %s" % (score, time))
                contentsToWrite = ",".join(scoresList)
                writeFile(path, contentsToWrite)

#writeScores("highScores.txt", 225)

highScores = []

def readScores(path):
    global highScores
    scores = readFile(path)
    if scores == "":
        highScores = []
    else:
        scoresList = scores.split(",")
        if len(scoresList) == 1:
            highScores = [scoresList[0], "XXXXX", "XXXXX"]
        if len(scoresList) == 2:
            numList = []
            for i in range(2):
                items = scoresList[i].split(" ")
                numList.append(int(items[0]))
            maxIndex = numList.index(max(numList))
            minIndex = numList.index(min(numList))
            highScores = [scoresList[maxIndex], scoresList[minIndex], "XXXXX"]
        if len(scoresList) == 3:
            numList = []
            for i in range(3):
                items = scoresList[i].split(" ")
                numList.append(int(items[0]))
            maxIndex = numList.index(max(numList))
            minIndex = numList.index(min(numList))
            mediumIndex = 3 - maxIndex - minIndex
            highScores = [scoresList[maxIndex], scoresList[mediumIndex], scoresList[minIndex]]

readScores("highScores.txt")
print highScores

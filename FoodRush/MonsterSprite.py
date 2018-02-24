import pygame
from pygame.locals import *
import networkx as nx

DIR_UP=0
DIR_LEFT=1
DIR_DOWN=2
DIR_RIGHT=3


class MonsterSprite(pygame.sprite.Sprite):
    def __init__(self, size, position, frames, speed, dir):
        # call into pygame base class
        pygame.sprite.Sprite.__init__(self)
        
        #init vars used between updates
        self.deltaX = 0
        self.deltaY = 0

        self.initialPos = position
        self.size = size
        self.position = (position[0] * self.size + self.size / 2,
                       position[1] * self.size + self.size / 2)
        self.frames = frames
        self.speed = speed
        if dir == "up":
            self.direct = DIR_UP
        elif dir == "down":
            self.direct = DIR_DOWN
        elif dir == "left":
            self.direct = DIR_LEFT
        elif dir == "right":
            self.direct = DIR_RIGHT
        
        self.image = self.frames[self.direct]
        # the passed in position is (row, col)
        
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        self.shortestPath = None

    def setpos(self,position):
        self.position= ( position[0] * self.size + self.size/2,
                       position[1] * self.size + self.size/2  )
        self.rect.center = self.position

    # returns(col, row)
    def getpos(self):
        pos = self.rect.center
        return (pos[0] // self.size, pos[1] // self.size)

    def update(self, heroSprite, wallGroup, heroGroup, graph):
        # if pygame.sprite.spritecollide(self, heroGroup, False):
        #     self.setpos(self.initialPos)
        #     print self.initialPos
        #     self.shortestPath = None
        #     self.deltaX = 0
        #     self.deltaY = 0
        #
        #     #heroSprite.heroMoved = False
        #     return
        currPos = self.getpos()
        currPosPixel = self.rect.center
        if (currPosPixel[0] - (currPos[0]*self.size + self.size/2)) >= self.speed * 1\
            or (currPosPixel[1] - (currPos[1]*self.size + self.size/2)) >= self.speed * 1:
            self.rect.move_ip(self.deltaX, self.deltaY)
            return
        else:
            self.deltaX, self.deltaY = 0, 0
        if (heroSprite.heroMoved == True):
            try:
                self.shortestPath = nx.dijkstra_path(graph, currPos, heroSprite.getpos())
                # print self.shortestPath
                heroSprite.heroMoved = False
            except:
                pass
        if pygame.sprite.spritecollide(self, wallGroup, False, collided = pygame.sprite.collide_rect):
            self.rect.center = (currPos[0] * self.size + self.size/2, currPos[1] * self.size + self.size/2)
            #currPos = self.getpos()
        if self.shortestPath != None and len(self.shortestPath) != 0:
            index = self.shortestPath.index(currPos)
            if index == len(self.shortestPath) - 1:
                return
            nextPos = self.shortestPath[index + 1]
            if nextPos[0] - currPos[0] > 0:
                self.deltaX = self.speed
                self.direct = DIR_RIGHT
            elif nextPos[0] - currPos[0] < 0:
                self.deltaX = -self.speed
                self.direct = DIR_LEFT
            elif nextPos[1] - currPos[1] > 0:
                self.deltaY = self.speed
                self.direct = DIR_DOWN
            elif nextPos[1] - currPos[1] < 0:
                self.deltaY = -self.speed
                self.direct = DIR_UP
            #self.setpos(nextPos)

            self.image = self.frames[self.direct]

            self.rect.move_ip(self.deltaX, self.deltaY)





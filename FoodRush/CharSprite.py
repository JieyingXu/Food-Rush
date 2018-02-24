import pygame
from pygame.locals import *

class CharSprite(pygame.sprite.Sprite):
    def __init__(self, size, position, image):
        pygame.sprite.Sprite.__init__(self)

        self.size = size
        #passed-in position is (row, col).
        self.centerPos = (position[0] * self.size + self.size / 2, position[1] * self.size + self.size / 2)
        self.deltaX = 0
        self.deltaY = 0
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = self.centerPos

    def setpos(self, position):
        self.position = (position[0] * self.size + self.size / 2,
                         position[1] * self.size + self.size / 2)
        self.rect.center = self.position

    def getpos(self):
        pos = self.rect.center
        return (pos[0] // self.size, pos[1] // self.size)


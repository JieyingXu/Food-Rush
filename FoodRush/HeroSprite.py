import pygame
from pygame.locals import *
from CharSprite import *

class HeroSprite(CharSprite):
    def __init__(self, size, position, image):
        CharSprite.__init__(self, size, position, image)
        self.heroMoved = False

    def update(self, deltaT, wallGroup, monsterGroup, leafGroup, foodGroup, status):
        CharSprite.update(self, deltaT)
        # Update the position
        self.rect.move_ip(self.deltaX * self.size, self.deltaY * self.size)

        flagCollision = pygame.sprite.spritecollide(self, leafGroup, False)
        unDone = False
        if len(flagCollision) > 0:
            if flagCollision[0].color == "yellow":
                for food in foodGroup:
                    # If there are still required food not eaten, level is not done.
                    if (food.required):
                        unDone = True
                        break
                status.levelDone = not unDone

        # "undo" the move if the hero hit a wall
        if pygame.sprite.spritecollide(self, wallGroup, False):
            self.rect.move_ip(-self.deltaX * self.size, -self.deltaY * self.size)

        #If hit a badGuy, Kill & Go back to Start position
        if pygame.sprite.spritecollide(self, monsterGroup, False):
            status.killLife()
            self.setpos(status.startPos)
            self.heroMoved = False
            for sprite in monsterGroup:
                sprite.setpos(sprite.initialPos)
                sprite.deltaX, sprite.deltaY = 0, 0
                sprite.shortestPath = None
        # Collect any prizes, and update score
        for food in pygame.sprite.spritecollide(self, foodGroup, True):
            status.addPoints(food.points)

        self.deltaX, self.deltaY = 0, 0

    def handleKeyEvent(self, event):
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                self.deltaX = 1
                self.heroMoved = True
            elif event.key == K_LEFT:
                self.deltaX = -1
                self.heroMoved = True
            elif event.key == K_UP:
                self.deltaY = -1
                self.heroMoved = True
            elif event.key == K_DOWN:
                self.deltaY = 1
                self.heroMoved = True
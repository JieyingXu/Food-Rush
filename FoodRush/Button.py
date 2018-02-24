import pygame

class Button(object):
    def __init__(self, upImg, downImg, position):
        self.upImg = upImg
        self.downImg = downImg
        self.position = position
        self.buttonOut = True

    def isOver(self):
        mouseX,mouseY = pygame.mouse.get_pos()
        x, y = self. position
        w, h = self.upImg.get_size()

        boolX = (x - w/2) < mouseX < (x + w/2)
        boolY = (y - h/2) < mouseY < (y + h/2)
        return boolX and boolY

    def render(self, surface):
        w, h = self.upImg.get_size()
        x, y = self.position

        if self.isOver():
            surface.blit(self.downImg, (x - w / 2, y - h / 2))
        else:
            surface.blit(self.upImg, (x - w / 2, y - h / 2))


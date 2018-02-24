import pygame
from foodRush import *
from pygame.locals import *


class WallSprite(pygame.sprite.Sprite):
    def __init__(self, position, image):
        # wallImg = imageCache.get(image)
        # self.image = wallImg
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = pygame.Rect(self.image.get_rect())
        self.rect.center = (position[0] * BLOCKSIZE + BLOCKSIZE / 2,
                            position[1] * BLOCKSIZE + BLOCKSIZE / 2)

class FoodSprite(pygame.sprite.Sprite):
    def __init__(self, position, image, points, req):
        pygame.sprite.Sprite.__init__(self)
        self.required = req
        self.points = points
        self.image = image
        self.rect = pygame.Rect(self.image.get_rect())
        self.rect.center = (position[0] * BLOCKSIZE + BLOCKSIZE / 2,
                            position[1] * BLOCKSIZE + BLOCKSIZE / 2)

class LeafSprite(pygame.sprite.Sprite):
   def __init__(self,position,color):
      pygame.sprite.Sprite.__init__(self)
      self.color = color
      if color == "blue":
         self.image = imageCache.get('startLeaf.png')
      else:
         self.image = imageCache.get('endLeaf.png')
      self.rect = pygame.Rect(self.image.get_rect())
      self.rect.center = (position[0] * BLOCKSIZE + BLOCKSIZE / 2,
                          position[1] * BLOCKSIZE + BLOCKSIZE / 2)




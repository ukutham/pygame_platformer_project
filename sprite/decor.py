import pygame
from settings import *

class DecorSprite(pygame.sprite.Sprite):
	def __init__(self, pos, group, surface = pygame.Surface((TILESIZE, TILESIZE))) :
		super().__init__(group)
		self.image = pygame.transform.scale(surface, (TILESIZE, TILESIZE))
		self.rect = self.image.get_rect(topleft = (pos[0] * TILESIZE, pos[1] * TILESIZE))
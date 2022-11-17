# free module #
import pygame
from settings import *

class ObstacleSprite(pygame.sprite.Sprite):
	def __init__(self, pos, group, surface = pygame.Surface((TILESIZE, TILESIZE))) :
		super().__init__(group)
		self.image = pygame.transform.scale(surface, (TILESIZE, TILESIZE))
		self.rect = self.image.get_rect(topleft = (pos[0] * TILESIZE, pos[1] * TILESIZE))

		self.hitbox = pygame.Rect( self.rect.topleft, self.rect.size )
		self.mask = pygame.mask.from_surface(self.image)

		self.pixel_hitbox = []
		for point in self.mask.outline():
			self.pixel_hitbox.append( pygame.Rect( (point[0] + self.rect.topleft[0], point[1] + self.rect.topleft[1]), (1, 1) ) )

	def draw_pixel_hitbox(self, offset):
		for rect in self.pixel_hitbox:
			offset_rect = pygame.Rect ( (rect.topleft[0] - offset[0], rect.topleft[1] - offset[1]), (1, 1) )
			pygame.draw.rect(pygame.display.get_surface(), 'Red', offset_rect)


	def collide_with_pixel_hitbox(self, player_hitbox):
		collide_rect = []
		for rect in self.pixel_hitbox:
			if rect.colliderect(player_hitbox):
				collide_rect.append(rect)

		return collide_rect
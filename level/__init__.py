import os

# free module #
import pygame
from pytmx.util_pygame import load_pygame
from pytmx import TiledMap

# my module #
from settings import *

from sprite.player import *
from sprite.obstacle import *

if DEBUG:
	from debug import *

class Level():
	def __init__(self, level):
		self.visible_sprite = SurfaceCameraGroup()
		self.obstacle_sprite = pygame.sprite.Group()
		self.movable_sprite = pygame.sprite.Group()

		self.tmx_data = load_pygame(level)
		self.surface_layers = []
		self.surface_layers_group = {}

		for layer in self.tmx_data.layers :
			if layer.name != 'obstacle':
				self.surface_layers.append(layer)
				self.surface_layers_group[layer.name] = SurfaceCameraGroup()

		self.collision_object_layer = self.tmx_data.get_layer_by_name('obstacle')
		self.collision_object_group = pygame.sprite.Group()

		self.create_map()

	def create_map(self):
		for surface_layer in self.surface_layers:
			for x, y, surf in surface_layer.tiles():
				if surface_layer.name == 'player_spawn':
					self.player = PlayerSprite((x * TILESIZE, y * TILESIZE), [self.visible_sprite, self.movable_sprite], self.obstacle_sprite, pygame.image.load(f"{PATH}/sprite_image/player/player_test.png"), pygame.image.load(f"{PATH}/sprite_image/player/patron.png"),speed = 2, movement_intensity = 1)
				else:
					ObstacleSprite((x, y), [self.visible_sprite], surf)

		for x, y, surf in self.collision_object_layer.tiles():
			ObstacleSprite((x, y), [self.collision_object_group,self.obstacle_sprite], surf)


	def run(self, delta_time):
		if DEBUG:
			self.visible_sprite.draw(self.player)
			self.movable_sprite.update(delta_time)
		else:
			self.movable_sprite.update(delta_time)
			self.visible_sprite.draw(self.player)

class SurfaceCameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()

		self.offset = pygame.math.Vector2()

	def draw(self, player):
		width = player.camera_half_width - player.direction.x * player.movement_intensity
		height = player.camera_half_height - player.direction.y * player.movement_intensity

		self.offset.x = player.rect.centerx - width
		self.offset.y = player.rect.centery - height

		for sprite in self.sprites():
			offset_position = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image, offset_position)
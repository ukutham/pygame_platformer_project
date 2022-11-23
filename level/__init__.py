import os

# free module #
import pygame
from pytmx.util_pygame import load_pygame
from pytmx import TiledMap

# my module #
from settings import *

from sprite.player import *
from sprite.obstacle import *
from sprite.decor import *

if DEBUG:
	from debug import *

class Level():
	def __init__(self, level, level_pos = [0, 0], display_surface = pygame.display.get_surface()):
		self.visible_sprite = SurfaceCameraGroup(display_surface)
		self.obstacle_sprite = pygame.sprite.Group()
		self.updatable_sprite = pygame.sprite.Group()
		self.in_front_of_player_sprite = pygame.sprite.Group()
		self.ray_cast_obstacle_sprite = pygame.sprite.Group()

		self.tmx_data = load_pygame(level)
		self.surface_layers = []
		self.surface_layers_group = {}

		for layer in self.tmx_data.layers :
			if layer.name not in ['obstacle', 'in_front_of_player', 'ray_cast_obstacle']:
				self.surface_layers.append(layer)
				self.surface_layers_group[layer.name] = pygame.sprite.Group()

		self.collision_object_layer = self.tmx_data.get_layer_by_name('obstacle')
		self.in_front_of_player_layer = self.tmx_data.get_layer_by_name('in_front_of_player')
		self.ray_cast_obstacle_layer = self.tmx_data.get_layer_by_name('ray_cast_obstacle')

		self.create_map(level_pos)

	def create_map(self, level_pos):
		level_topleft = [level_pos[0] * LEVEL_SIZE[0], level_pos[1] * LEVEL_SIZE[1]]

		for surface_layer in self.surface_layers:
			for x, y, surf in surface_layer.tiles():
				DecorSprite((level_topleft[0] + x,level_topleft[1] + y), [self.visible_sprite, self.surface_layers_group[surface_layer.name]], surf)

		for x, y, surf in self.collision_object_layer.tiles():
			ObstacleSprite((level_topleft[0] + x,level_topleft[1] + y), [self.obstacle_sprite], surf)

		for x, y, surf in self.in_front_of_player_layer.tiles():
			DecorSprite((level_topleft[0] + x,level_topleft[1] + y), [self.in_front_of_player_sprite], surf)

		for x, y, surf in self.ray_cast_obstacle_layer.tiles():
			ObstacleSprite((level_topleft[0] + x,level_topleft[1] + y), [self.ray_cast_obstacle_sprite], surf)


	def run(self, player, offset, delta_time):
		self.updatable_sprite.update(delta_time)
		self.visible_sprite.draw(player, offset)

class SurfaceCameraGroup(pygame.sprite.Group):
	def __init__(self, display_surface):
		super().__init__()
		self.display_surface = display_surface

	def draw(self, player, offset):
		for sprite in self.sprites():
			if player.rect.center[0] - WIDTH < sprite.rect.center[0] < player.rect.center[0] + WIDTH and player.rect.center[1] - HEIGHT < sprite.rect.center[1] < player.rect.center[1] + HEIGHT:
				offset_position = sprite.rect.topleft - offset
				self.display_surface.blit(sprite.image, offset_position)
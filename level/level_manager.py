import pygame

from level import Level
from settings import *
from sprite.player import PlayerSprite

if DEBUG:
	from debug import *

class LevelManager():
	def __init__(self, player_pos):
		self.loaded_level = {}
		self.view_level = {}

		self.important_sprite = pygame.sprite.Group()
		self.obstacle_sprite = pygame.sprite.Group()
		self.in_front_of_player_sprite = pygame.sprite.Group()
		self.ray_cast_obstacle_sprite = pygame.sprite.Group()

		self.player = PlayerSprite(player_pos, [self.important_sprite], pygame.image.load(f"{PATH}/sprite_image/player/player_test.png"), pygame.image.load(f"{PATH}/sprite_image/player/patron.png"),speed = 2, movement_intensity = 1)
		self.set_actual_level_pos()
		self.previous_tick_level_pos = None

		self.camera = LevelManagerCamera()
		self.display_surface = pygame.display.get_surface()
		self.offset = pygame.math.Vector2()

	def add_level(self, level_coord):
		key = f'{level_coord[0]}_{level_coord[1]}'
		if key in self.view_level:
			return
		elif key in self.loaded_level:
			self.view_level[key] = self.loaded_level[key]
		else:
			try:
				self.loaded_level[key] = Level(f"{PATH}/level_sheet/map_{key}.tmx", level_coord, self.display_surface)
				self.view_level[key] = self.loaded_level[key]
			except:
				pass

	def set_actual_level_pos(self):
		self.actual_level_pos = [self.player.rect.topleft[0] // TILESIZE // LEVEL_SIZE[0], self.player.rect.topleft[1] // TILESIZE // LEVEL_SIZE[1]]

	def view_level_actualisation(self):
		self.view_level = {}

		for x in range( self.actual_level_pos[0] - LEVEL_VIEW_RANGE, self.actual_level_pos[0] + LEVEL_VIEW_RANGE + 1 ):
			for y in range ( self.actual_level_pos[1] - LEVEL_VIEW_RANGE, self.actual_level_pos[1] + LEVEL_VIEW_RANGE + 1 ):
				self.add_level( [x, y] )

		self.obstacle_sprite.empty()
		self.in_front_of_player_sprite.empty()
		self.ray_cast_obstacle_sprite.empty()

		for level_pos, level in self.view_level.items():
			for obstacle_sprite in level.obstacle_sprite:
				self.obstacle_sprite.add(obstacle_sprite)

			for in_front_of_player_sprite in level.in_front_of_player_sprite:
				self.in_front_of_player_sprite.add(in_front_of_player_sprite)

			for ray_cast_obstacle_sprite in level.ray_cast_obstacle_sprite:
				self.ray_cast_obstacle_sprite.add(ray_cast_obstacle_sprite)


	def run(self, delta_time):
		self.set_actual_level_pos()

		if self.actual_level_pos != self.previous_tick_level_pos:
			self.previous_tick_level_pos = self.actual_level_pos

			self.view_level_actualisation()

		for sprite in self.important_sprite:
			sprite.update(self.obstacle_sprite ,delta_time)

		self.camera.draw(self.important_sprite, self.player, self.view_level, self.in_front_of_player_sprite, self.obstacle_sprite, self.ray_cast_obstacle_sprite, delta_time)

class LevelManagerCamera():
	def __init__(self):
		self.display_surface = pygame.display.get_surface()
		self.offset = pygame.math.Vector2()

	def draw(self, important_sprite, player, view_level, in_front_of_player_sprite, obstacle_sprite, ray_cast_obstacle_sprite, delta_time):

		width = player.camera_half_width - player.direction.x * player.movement_intensity
		height = player.camera_half_height - player.direction.y * player.movement_intensity

		self.offset.x = player.rect.centerx - width
		self.offset.y = player.rect.centery - height

		for key_level, level in view_level.items():
			level.run(player, self.offset, delta_time)

		for sprite in important_sprite:
			self.display_surface.blit( sprite.image, sprite.rect.topleft - self.offset )

		for sprite in in_front_of_player_sprite:
			if player.rect.center[0] - WIDTH < sprite.rect.center[0] < player.rect.center[0] + WIDTH and player.rect.center[1] - HEIGHT < sprite.rect.center[1] < player.rect.center[1] + HEIGHT:
				self.display_surface.blit( sprite.image, sprite.rect.topleft - self.offset )

		self.visibility_mask(obstacle_sprite, ray_cast_obstacle_sprite, player)

		if DEBUG:
			for sprite in important_sprite:
				sprite.debug(self.offset)

	def visibility_mask(self, obstacle_sprite, ray_cast_obstacle_sprite, player):
		ray_casts = []

		for sprite in ray_cast_obstacle_sprite:
			if player.rect.center[0] - WIDTH/2 < sprite.rect.center[0] < player.rect.center[0] + WIDTH/2 and player.rect.center[1] - HEIGHT/2 < sprite.rect.center[1] < player.rect.center[1] + HEIGHT/2:
				ray_casts.append( pygame.math.Vector2( sprite.hitbox.topleft[0] - player.hitbox.centerx, sprite.hitbox.topleft[1] - player.hitbox.centery ) )

				ray_casts.append( pygame.math.Vector2( sprite.hitbox.bottomleft[0] - player.hitbox.centerx, sprite.hitbox.bottomleft[1] - player.hitbox.centery ) )

				ray_casts.append( pygame.math.Vector2( sprite.hitbox.topright[0] - player.hitbox.centerx, sprite.hitbox.topright[1] - player.hitbox.centery ) )

				ray_casts.append( pygame.math.Vector2( sprite.hitbox.bottomright[0] - player.hitbox.centerx, sprite.hitbox.bottomright[1] - player.hitbox.centery ) )

		n_constant_ray = 32
		for i in range(0, n_constant_ray):
			ray_casts.append( pygame.math.Vector2( 0, -WIDTH ).rotate(i * (360/n_constant_ray) ) )


		for ray_cast in ray_casts:
			cliped_lines = []
			for sprite in obstacle_sprite:
				clip = sprite.hitbox.clipline( player.hitbox.center, (ray_cast.x + player.hitbox.centerx,  ray_cast.y + player.hitbox.centery) )
				if clip:
					cliped_lines.append(clip[0])
					cliped_lines.append(clip[1])


			if cliped_lines:
				cliped_lines = sorted(cliped_lines, key=lambda clip: pygame.math.Vector2( (clip[0] - player.hitbox.centerx, clip[1] - player.hitbox.centery) ).length() )
				ray_casts[ray_casts.index(ray_cast)].update( (cliped_lines[0][0] - player.hitbox.centerx, cliped_lines[0][1] - player.hitbox.centery) )

		zero_deg_vector = pygame.math.Vector2( 0, -1 )
		ray_casts = sorted( ray_casts, key= lambda ray_cast: ray_cast.angle_to(zero_deg_vector) )

		"""for ray_cast in ray_casts:
			pygame.draw.line(self.display_surface, 'Pink', player.hitbox.center - self.offset, (ray_cast.x + player.hitbox.centerx,  ray_cast.y + player.hitbox.centery) - self.offset )"""

		pygame.draw.polygon(self.display_surface, 'Pink', [ (ray_cast.x + player.hitbox.centerx,  ray_cast.y + player.hitbox.centery) - self.offset for ray_cast in ray_casts], 1)


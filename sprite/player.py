# free module #
import pygame
import numpy

# my module
from settings import *

if DEBUG:
	from debug import *

class PlayerSprite(pygame.sprite.Sprite):
	def __init__(self, pos, group, base_image, image_patron,speed = 5, masse = 80, movement_intensity = 1,):
		super().__init__(group)

		self.image = pygame.Surface((TILESIZE, TILESIZE))
		self.base_image = base_image
		self.image_patron = image_patron

		self.rect = self.image.get_rect(topleft = pos)

		self.hitbox = pygame.Rect(pos[0] + 15, pos[1] + 16, 23, 34)
		self.mask = None
		self.delta_hitbox = None

		self.direction = pygame.math.Vector2()
		self.speed = speed
		self.force = []
		self.text_force = ''
		self.masse = masse
		self.poid = masse * 9.8

		self.air_friction = 0.98
		self.floor_friction = 0.85
		self.wall_friction = 0.6

		if DEBUG:
			self.offset = pygame.math.Vector2()
			self.debug_force = self.force
			self.potential_sprite_obstacle = []

		self.movement_intensity = movement_intensity
		self.camera_half_width = pygame.display.get_surface().get_size()[0] // 2
		self.camera_half_height = pygame.display.get_surface().get_size()[1] // 2

		self.mouse_vector = pygame.math.Vector2()

		self.jump = pygame.K_SPACE
		self.jump_pressed_last_tick = False

		self.left = pygame.K_q
		self.right = pygame.K_d
		self.up = pygame.K_z
		self.down = pygame.K_s

		self.sprint = False
		self.sprint_input = pygame.K_LSHIFT
		self.sprint_input_pressed = False

		self.on_floor = False
		self.touch_floor_last_tick = False

		self.on_left_wall = False
		self.touch_left_wall_last_tick = False

		self.on_right_wall = False
		self.touch_right_wall_last_tick = False

		self.in_wall_jump = False
		self.in_wall_jump_time = 0.5
		self.in_wall_jump_counter_time = self.in_wall_jump_time

	def reset_wall_jump(self):
		self.in_wall_jump = False
		self.in_wall_jump_counter_time = self.in_wall_jump_time

	def move(self, obstacle_sprite):
		for force in self.force:
			self.direction += force
			self.text_force += str(force)

		if DEBUG:
			self.debug_force = self.force

		self.force = []

		if self.on_floor:
			self.direction.x = round(self.direction.x * self.floor_friction, 3)
			self.direction.y = round(self.direction.y * self.floor_friction, 3)
		elif self.on_left_wall or self.on_right_wall:
			self.direction.x = round(self.direction.x * self.wall_friction, 3)
			self.direction.y = round(self.direction.y * self.wall_friction, 3)
		else:
			self.direction.x = round(self.direction.x * self.air_friction, 3)
			self.direction.y = round(self.direction.y * self.air_friction, 3)

		if round(self.direction.x) == 0:
			self.direction.x = 0
		if round(self.direction.y) == 0:
			self.direction.y = 0

		#limiteur
		if self.direction.length() >= (TILESIZE / 2) - 1 and not self.in_wall_jump:
			self.direction = self.direction.normalize()
			self.direction *= ( (TILESIZE / 2) - 1)

		self.hitbox.x += self.direction.x
		self.collision('horizontal', obstacle_sprite)
		self.hitbox.y += self.direction.y
		self.collision('vertical', obstacle_sprite)

		hitbox_with_rect_dimension = pygame.Rect( (self.hitbox.topleft[0] - self.delta_hitbox.topleft[0], self.hitbox.topleft[1] - self.delta_hitbox.topleft[1]) , self.rect.size)

		self.rect.center = (hitbox_with_rect_dimension.centerx, hitbox_with_rect_dimension.centery)

	def gravity_effect(self):
		if not GOD_MODE:
			self.force.append(pygame.math.Vector2(0, 1))

	def input(self, delta_time):
		keys = pygame.key.get_pressed()

		if not GOD_MODE:
			self.force.append(pygame.math.Vector2())

			if keys[self.jump] and not self.jump_pressed_last_tick and self.on_floor:
				self.force[-1] = pygame.math.Vector2(0, -15) * self.speed

			elif keys[self.jump] and not self.jump_pressed_last_tick and self.on_left_wall:
				self.force[-1] = pygame.math.Vector2(20, -20) * self.speed
				self.reset_wall_jump()
				self.in_wall_jump = True

			elif keys[self.jump] and not self.jump_pressed_last_tick and self.on_right_wall:
				self.force[-1] = pygame.math.Vector2(-20, -20) * self.speed
				self.reset_wall_jump()
				self.in_wall_jump = True

			if self.in_wall_jump:
				self.in_wall_jump_counter_time -= delta_time
				if self.in_wall_jump_counter_time <= 0:
					self.reset_wall_jump()

		self.force.append(pygame.math.Vector2())

		if keys[self.left] and self.on_floor:
			self.force[-1] = pygame.math.Vector2(-1, 0) * self.speed
		elif keys[self.left] and not self.in_wall_jump:
			self.force[-1] = pygame.math.Vector2(-0.5, 0) * self.speed

		self.force.append(pygame.math.Vector2())
		
		if keys[self.right] and self.on_floor:
			self.force[-1] = pygame.math.Vector2(1, 0) * self.speed
		elif keys[self.right] and not self.in_wall_jump:
			self.force[-1] = pygame.math.Vector2(0.5, 0) * self.speed


		if GOD_MODE:
			if keys[self.left]:
				self.force[-1] = pygame.math.Vector2(-1, 0) * self.speed
			
			elif keys[self.right]:
				self.force[-1] = pygame.math.Vector2(1, 0) * self.speed

			if keys[self.up]:
				self.force[-1] = pygame.math.Vector2(0, -1) * self.speed
		
			elif keys[self.down]:
				self.force[-1] = pygame.math.Vector2(0, 1) * self.speed

		if keys[self.jump]:
			self.jump_pressed_last_tick = True
		else:
			self.jump_pressed_last_tick = False


	def collision(self, direction, obstacle_sprite):
		keys = pygame.key.get_pressed()

		if direction == 'horizontal' and not GOD_MODE:
			self.on_right_wall = False
			self.on_left_wall = False

			for sprite in obstacle_sprite:
				if self.rect.center[0] - HITBOX_SIZE_FILTER < sprite.rect.center[0] < self.rect.center[0] + HITBOX_SIZE_FILTER and self.rect.center[1] - HITBOX_SIZE_FILTER < sprite.rect.center[1] < self.rect.center[1] + HITBOX_SIZE_FILTER:
					if DEBUG:
						self.potential_sprite_obstacle.append(sprite)

					if sprite.hitbox.colliderect(self.hitbox):

						sprite_rects = sprite.collide_with_pixel_hitbox(self.hitbox)

						for sprite_rect in sprite_rects:

							if sprite_rect.colliderect(self.hitbox):
								if self.direction.x > 0:
									self.hitbox.right = sprite_rect.left

									if keys[self.right]:
										self.touch_right_wall_last_tick = True
										self.on_right_wall = True
									
								if self.direction.x < 0:
									self.hitbox.left = sprite_rect.right

									if keys[self.left]:
										self.touch_left_wall_last_tick = True
										self.on_left_wall = True

			if not self.on_right_wall and self.touch_right_wall_last_tick:
				self.touch_right_wall_last_tick = False
				self.on_right_wall = True
			if self.on_right_wall and self.in_wall_jump:
				self.reset_wall_jump()

			if not self.on_left_wall and self.touch_left_wall_last_tick:
				self.touch_left_wall_last_tick = False
				self.on_left_wall = True
			if self.on_left_wall and self.in_wall_jump:
				self.reset_wall_jump()

		if direction == 'vertical' and not GOD_MODE:
			self.on_floor = False

			for sprite in obstacle_sprite:
				if self.rect.center[0] - HITBOX_SIZE_FILTER < sprite.rect.center[0] < self.rect.center[0] + HITBOX_SIZE_FILTER and self.rect.center[1] - HITBOX_SIZE_FILTER < sprite.rect.center[1] < self.rect.center[1] + HITBOX_SIZE_FILTER:
					if DEBUG:
						self.potential_sprite_obstacle.append(sprite)

					if sprite.hitbox.colliderect(self.hitbox):

						sprite_rects = sprite.collide_with_pixel_hitbox(self.hitbox)

						bottom_collision = False
						for sprite_rect in sprite_rects:
							if sprite_rect.colliderect(self.hitbox):
								if self.direction.y > 0:
									self.hitbox.bottom = sprite_rect.top

									self.touch_floor_last_tick = True
									self.on_floor = True

								if self.direction.y < 0:
									self.hitbox.top = sprite_rect.bottom
									bottom_collision = True


						if bottom_collision:
							self.direction.y = 0

			if not self.on_floor and self.touch_floor_last_tick:
				self.touch_floor_last_tick = False
				self.on_floor = True

			if self.on_floor and self.in_wall_jump:
				self.reset_wall_jump()

	def animation(self):
		""" pixel art colorisation """

		image_array = pygame.surfarray.pixels3d(self.base_image)
		patron_array = pygame.surfarray.pixels3d(self.image_patron)

		for pixel_array,x in zip(image_array,range(len(image_array))):
			for y in range(len(pixel_array)):
				ancien_color = pygame.Color(image_array[x,y])
				try:
					new_color = pygame.Color(patron_array[ancien_color[0], ancien_color[1]])
				except:
					pass
				else:
					image_array[x,y] = new_color[0:3]

		alpha_calque = pygame.surfarray.array_alpha(self.base_image)

		self.image = pygame.transform.scale(pygame.surfarray.make_surface(image_array), (TILESIZE, TILESIZE))
		self.image.blit(pygame.transform.scale(pygame.surfarray.make_surface(alpha_calque), (TILESIZE, TILESIZE)), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
		self.image.set_colorkey((0, 0, 0))


	def set_hitbox(self):

		self.mask = pygame.mask.from_surface(self.image)

		self.delta_hitbox = self.mask.get_bounding_rects()
		self.delta_hitbox.sort(key=lambda r: (r.width, r.height) )
		self.delta_hitbox = self.delta_hitbox[-1]

		self.hitbox = pygame.Rect( (self.delta_hitbox.topleft[0] + self.rect.topleft[0], self.delta_hitbox.topleft[1] + self.rect.topleft[1]), self.delta_hitbox.size )


	def update(self, obstacle_sprite, delta_time):
		self.input(delta_time)
		self.gravity_effect()
		self.animation()
		self.set_hitbox()

		self.move(obstacle_sprite)


	def debug(self, offset):
		width = self.camera_half_width - self.direction.x * self.movement_intensity
		height = self.camera_half_height - self.direction.y * self.movement_intensity

		self.offset.x = self.rect.centerx - width
		self.offset.y = self.rect.centery - height

		for sprite in self.potential_sprite_obstacle:
			sprite.draw_pixel_hitbox(self.offset)

		self.potential_sprite_obstacle = []

		pygame.draw.line(pygame.display.get_surface(), 'Red', self.rect.center - self.offset, (self.rect.center[0] + self.direction.x * DEBUG_VECTOR_SIZE, self.rect.center[1] + self.direction.y * DEBUG_VECTOR_SIZE) - self.offset)

		for force in self.debug_force:
			pygame.draw.line(pygame.display.get_surface(), 'Green', self.rect.center - self.offset, (self.rect.center[0] + force.x * DEBUG_VECTOR_SIZE * 10, self.rect.center[1] + force.y * DEBUG_VECTOR_SIZE * 10) - self.offset)

		pygame.draw.polygon(pygame.display.get_surface(), 'Blue', [self.hitbox.topleft - self.offset, self.hitbox.topright - self.offset, self.hitbox.bottomright - self.offset, self.hitbox.bottomleft - self.offset], 1)


		debug('player_position : ', [self.rect.center[0], self.rect.center[1]])
		debug('player_force : ', self.text_force, 30, 10)
		self.text_force = ''
		debug('on_floor : ', self.on_floor, 50, 10)
		debug('on_left_wall : ', self.on_left_wall, 70, 10)
		debug('on_right_wall : ', self.on_right_wall, 90, 10)
		debug('level_pos : ', [ self.rect.topleft[0] // TILESIZE // LEVEL_SIZE[0], self.rect.topleft[1] // TILESIZE // LEVEL_SIZE[1]], 110, 10)

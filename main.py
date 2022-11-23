# basic module #
import sys

# free module #
import pygame

# my module #
from settings import *

if DEBUG:
	from debug import *

from level.level_manager import LevelManager

class Game():
	def __init__(self):
		pygame.init()

		pygame.mouse.set_visible(False)

		pygame.display.set_caption("Behind this little moon")
		self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
		self.clock = pygame.time.Clock()
		self.clock_second_convertor = 15000 / FPS

		self.level_manager = LevelManager(PLAYER_LAST_POSITION)

	def run(self):
		running = True
		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False

			self.screen.fill((113, 221, 235))
			delta_time = self.clock.tick(FPS) / self.clock_second_convertor
			self.level_manager.run(delta_time)

			if DEBUG:
				debug('FPS : ', self.clock.get_fps(), 130, 10)

			pygame.display.update()


		pygame.quit()

if __name__ == '__main__':
	game = Game()
	game.run()
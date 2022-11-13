# basic module #
import sys

# free module #
import pygame

# my module #
from settings import *

from level import *

class Game():
	def __init__(self):
		pygame.init()

		pygame.mouse.set_visible(False)

		pygame.display.set_caption("Behind this little moon")
		self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
		self.clock = pygame.time.Clock()
		self.clock_second_convertor = 15000 / FPS

		self.level = Level(f"{PATH}/level_sheet/level_1.tmx")

	def run(self):
		running = True
		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False

			self.screen.fill((113, 221, 235))
			delta_time = self.clock.tick(FPS) / self.clock_second_convertor
			self.level.run(delta_time)
			pygame.display.update()

		pygame.quit()

if __name__ == '__main__':
	game = Game()
	game.run()
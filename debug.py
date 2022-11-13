import pygame
from settings import *

pygame.init()
font = pygame.font.Font(None, 20)

def debug(desc, info, y = 10, x = 10):
	display_surface = pygame.display.get_surface()
	debug_text = font.render(desc+str(info), True, 'White')
	debug_rect = debug_text.get_rect(topleft = (x,y))
	pygame.draw.rect(display_surface, 'Black', debug_rect)
	display_surface.blit(debug_text, debug_rect)
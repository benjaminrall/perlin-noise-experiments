import pygame
import os
import random
from world import World
from world import Camera

WIN_WIDTH = 800
WIN_HEIGHT = 600
ICON_IMG = pygame.image.load(os.path.join("imgs", "icon.png"))

pygame.display.set_caption("Terrain Generator")
pygame.display.set_icon(ICON_IMG)
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

clock = pygame.time.Clock()
cam = Camera(0, 0, 1, screen)
world = World(0)

world.render_world(cam)

moving_map = False

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                cam.toggle_debug()
                world.render_world(cam)
            elif event.key == pygame.K_r:
                world = None
                world = World(random.randrange(0,100000000))
                world.render_world(cam)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2:
                moving_map = True
                pygame.mouse.get_rel()
            elif event.button == 4:
                cam.zoom_in()
                world.render_world(cam)
            elif event.button == 5:
                cam.zoom_out()
                world.render_world(cam)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                moving_map = False
        elif event.type == pygame.MOUSEMOTION and moving_map:
            cam.pan(pygame.mouse.get_rel())
            world.render_world(cam)
    
    pygame.display.update()
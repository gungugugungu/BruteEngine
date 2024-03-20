import pygame
from pymunk import Vec2d
import screeninfo
import brute as brute

brute.init((512, 512), "Brute Testing")

clock = pygame.time.Clock()
brute.clock = clock

texture = brute.load_texture("shapes/circle.png")

fpsCap = 60
running = True
while running:
    keys_pressed = pygame.key.get_pressed()
    mouse_pressed = pygame.mouse.get_pressed()

    brute.draw_rect((0, 255, 120), (16, 16, 16, 16))
    brute.blit(texture, (64, 64), (128, 128))

    brute.update()
    brute.dt = clock.tick(fpsCap) / 1000
pygame.quit()
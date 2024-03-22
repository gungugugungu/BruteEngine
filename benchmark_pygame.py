import random
import pygame

pygame.init()
screen = pygame.display.set_mode((512, 512))
pygame.display.set_caption("Pygame Testing")

textures = [pygame.image.load("shapes/red.png").convert_alpha(), pygame.image.load("shapes/blue.png").convert_alpha(), pygame.image.load("shapes/green.png").convert_alpha(), pygame.image.load("shapes/yellow.png").convert_alpha()]
objects = []

clock = pygame.Clock()

def RenderText(text="Secret text", font='', textcolor=(0, 0, 0), fontsize=16, aa=True):
    return pygame.font.Font(f'data/{font}.ttf', fontsize).render(text, aa, textcolor)

fpsCap = 60
running = True
while running:
    screen.fill((125, 125, 255))
    keys_pressed = pygame.key.get_pressed()
    mouse_pressed = pygame.mouse.get_pressed()
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if mouse_pressed[0]:
        objects.append({"x": random.randrange(0, 512), "y": random.randrange(0, 512), "image": random.choice(textures)})
    if mouse_pressed[1]:
        objects.append({"x": random.randrange(0, 512), "y": random.randrange(0, 512), "image": random.choice(textures)})
        objects.append({"x": random.randrange(0, 512), "y": random.randrange(0, 512), "image": random.choice(textures)})
        objects.append({"x": random.randrange(0, 512), "y": random.randrange(0, 512), "image": random.choice(textures)})
        objects.append({"x": random.randrange(0, 512), "y": random.randrange(0, 512), "image": random.choice(textures)})
        objects.append({"x": random.randrange(0, 512), "y": random.randrange(0, 512), "image": random.choice(textures)})

    for o in objects:
        screen.blit(pygame.transform.scale(o["image"], (16, 16)), (o["x"], o["y"]))

    pygame.draw.rect(screen, (0, 0, 0), (0, 0, 256, 32))
    screen.blit(RenderText(f"FPS: {clock.get_fps()}", "font", (255, 255, 255)), (0, 0))
    screen.blit(RenderText(f"Objects: {len(objects)}", "font", (255, 255, 255)), (0, 16))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
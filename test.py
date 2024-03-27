import math
import brute

brute.init((512, 512), "Brute Testing")

texture_red = brute.load_texture("shapes/red.png")
texture_blue = brute.load_texture("shapes/blue.png")
angle = 0

while True:
    keys_pressed = brute.keyboard_down()
    mouse_pressed = brute.mouse_down()
    brute.fill((125, 125, 255))

    angle += 1
    if angle >= 361:
        angle = 0

    brute.draw_rect((0, 255, 120), (16, 16, 16, 16))
    brute.blit_rotate_texture(texture_blue, (64, 160), angle, (64, 64))
    brute.blit(texture_red, ((math.sin(brute.time * 0.1)*128)+128+64, 64), (math.sin(brute.time * 0.2) * 64, math.sin(brute.time * 0.2) * 64))

    brute.update()
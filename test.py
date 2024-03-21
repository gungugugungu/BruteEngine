import brute as brute

brute.init((512, 512), "Brute Testing")

texture = brute.load_texture("shapes/circle.png")

fpsCap = 60
running = True
while running:
    keys_pressed = brute.keyboard_down()
    mouse_pressed = brute.mouse_down()

    brute.draw_rect((0, 255, 120), (16, 16, 16, 16))
    brute.blit(texture, (64, 64), (128, 128))

    brute.update()
brute.quit()
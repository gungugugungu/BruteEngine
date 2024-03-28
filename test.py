import math
import brute

brute.init((1920, 1080), "Brute Testing", fullscreen=True)

texture_red = brute.load_texture("shapes/red.png")
texture_blue = brute.load_texture("shapes/blue.png")
angle = 0
map = brute.Tilemap("data/devmap.tmx", ["col", "nocol"], [])

while True:
    keys_pressed = brute.keyboard_down()
    mouse_pressed = brute.mouse_down()
    brute.fill((123, 175, 251))

    angle += 1
    if angle >= 361:
        angle = 0

    map.draw("nocol")
    map.draw("col")

    brute.update()
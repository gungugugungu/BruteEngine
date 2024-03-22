import random
import brute as brute

brute.init((512, 512), "Brute Testing")

textures = [brute.load_texture("shapes/red.png"), brute.load_texture("shapes/blue.png"), brute.load_texture("shapes/green.png"), brute.load_texture("shapes/yellow.png")]
objects = []

brute.debugProperties.append("Objects: 0")

while True:
    brute.fill((125, 125, 255))
    keys_pressed = brute.keyboard_down()
    mouse_pressed = brute.mouse_down()
    mx, my = brute.get_mouse_position()

    if mouse_pressed[0]:
        objects.append({"x": random.randrange(0, 512), "y": random.randrange(0, 512), "image": random.choice(textures)})
    if mouse_pressed[1]:
        objects.append({"x": random.randrange(0, 512), "y": random.randrange(0, 512), "image": random.choice(textures)})
        objects.append({"x": random.randrange(0, 512), "y": random.randrange(0, 512), "image": random.choice(textures)})
        objects.append({"x": random.randrange(0, 512), "y": random.randrange(0, 512), "image": random.choice(textures)})
        objects.append({"x": random.randrange(0, 512), "y": random.randrange(0, 512), "image": random.choice(textures)})
        objects.append({"x": random.randrange(0, 512), "y": random.randrange(0, 512), "image": random.choice(textures)})

    brute.debugProperties[0] = f"Objects: {len(objects)}"

    for o in objects:
        brute.blit(o["image"], (o["x"], o["y"]), (16, 16))

    brute.debugMenuEnabled = True

    brute.update()
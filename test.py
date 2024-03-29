import brute
import random

brute.init((1920, 1080), "Brute Testing", fullscreen=True)

texture_red = brute.load_texture("shapes/red.png")
texture_blue = brute.load_texture("shapes/blue.png")
texture_green = brute.load_texture("shapes/green.png")
texture_yellow = brute.load_texture("shapes/yellow.png")
angle = 0
map = brute.Tilemap("data/devmap.tmx", ["col", "nocol"], [])
map_col_objects = []
boxes = []
particles = []
for r in map.draw("col"):
    map_col_objects.append(brute.PhysicsObject(brute.transparent_img, brute.Vec2d(r.x, r.y), 0, brute.Vec2d(r.w, r.h), kinematic=True))
brute.debug_properties.append("")

while True:
    keys_pressed = brute.keyboard_down()
    mouse_pressed = brute.mouse_down()
    mx, my = brute.get_mouse_position()
    brute.fill((123, 175, 251))

    angle += 1
    if angle >= 361:
        angle = 0

    if mouse_pressed[0]:
        boxes.append(brute.PhysicsObject(random.choice([texture_yellow, texture_green, texture_red]), brute.Vec2d(mx, my), 0, brute.Vec2d(32, 32)))
    elif mouse_pressed[1]:
        particles.append(brute.ParticleSystem(10, (-5, -5), (5, 5), 0.1, (mx, my), 4, (random.randrange(100, 200), random.randrange(100, 200), random.randrange(100, 200)), 2, 40))
    elif mouse_pressed[2]:
        remove_list = [o for o in boxes if (o.body.position.x+o.scale.x >= mx >= o.body.position.x) and (o.body.position.y+o.scale.y >= my >= o.body.position.y)]
        for ro in remove_list:
            brute.space.remove(ro.body)
            brute.space.remove(ro.shape)
            boxes.remove(ro)

    map.draw("nocol")
    map.draw("col")
    [o for o in map_col_objects if o.update()]
    [o for o in boxes if o.update()]
    [p for p in particles if p.update()]
    for p in particles:
        if p.shouldDie:
            particles.remove(p)
    brute.debug_properties[0] = f"Objects: {len(boxes)}"

    brute.update()
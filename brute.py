import random
import pygame
from pygame.math import Vector2
from pytmx import load_pygame
import numpy as np
import math
import pymunk
from pymunk.vec2d import Vec2d
import sys
import pymunk.pygame_util
from pygame._sdl2.video import Window, Texture, Image, Renderer
import pygame._sdl2.video as _video

renderer: Renderer
window: Window
_window_surf:pygame.Surface
fps_cap = 60
clock:pygame.time.Clock
space:pymunk.Space
cam:Vector2
screenshake:Vector2
transparent_img:Texture

Surface = pygame.Surface
Clock = pygame.Clock
Rect = pygame.Rect

_version = "1.4.1"

def init(size, title, max_fps=60, fullscreen=False):
    global window
    global renderer
    global _window_surf
    global fps_cap
    global clock
    global cam
    global screenshake
    global space
    global transparent_img
    pygame.init()
    window = Window(title, size)
    renderer = Renderer(window)
    _window_surf = window.get_surface()
    if fullscreen:
        window.set_fullscreen()

    fps_cap = max_fps
    clock = Clock()

    space = pymunk.Space(True)
    space.threads = 4
    space.gravity = (0, 981)

    screenshake = Vector2(0, 0)
    cam = Vector2(0, 0)

    transparent_img = load_texture("shapes/transparent.png")

    print(f"Initalized Brute Engine (version {_version}, pygame version {pygame.version.ver})")

cCheckRes = 4
iterations = 10

debug_properties = []
debug_menu_enabled = False
time = 1

dt = 0

### RENDERING ###
def draw_rect(color, rect:tuple[int, int, int, int]):
    renderer.draw_color = color
    renderer.fill_rect(rect)

def blit(texture:Texture, position, size=(-1, -1)):
    renderer.draw_color = (255, 255, 255)
    px, py = position
    if size == (-1, -1):
        w, h = texture.width, texture.height
    else:
        w, h = size
    dest = pygame.Rect(px, py, w, h)
    renderer.blit(texture, dest)

def blit_surface(surface:pygame.Surface, position, size=(-1, -1)):
    renderer.draw_color = (255, 255, 255)
    px, py = position
    if size == (-1, -1):
        w, h = surface.get_size()
    else:
        w, h = size
    dest = pygame.Rect(px, py, w, h)
    renderer.blit(Texture.from_surface(renderer, surface), dest)

def fill(color):
    renderer.draw_color = color
    renderer.clear()

def load_texture(image_path):
    return Texture.from_surface(renderer, pygame.image.load(image_path).convert_alpha())

def load_surface(image_path):
    return pygame.image.load(image_path).convert_alpha()

def blit_rotate_texture(texture:Texture, pos:tuple[int, int], angle:int, size=(-1, -1)):
    if size == (-1, -1):
        size = (texture.width, texture.height)
    dist = (pos[0], pos[1], size[0], size[1])
    texture.draw(dstrect=dist, angle=angle)

### SOME OTHER FUNCTIONS I DON'T KNOW A GENERAL NAME FOR THEM ###
def angleBetween(vector1, vector2):
    dot_product = vector1.dot(vector2)

    magnitude1 = vector1.length()
    magnitude2 = vector2.length()

    angle_radians = math.acos(dot_product / (magnitude1 * magnitude2))

    angle_degrees = math.degrees(angle_radians)

    return angle_degrees

def quit():
    pygame.quit()
    sys.exit()

def min(num, min):
    if num < min:
        return min
    else:
        return num

def max(num, max):
    if num > max:
        return max
    else:
        return num

def min_max(num, minn, maxn):
    return min(max(num, maxn), minn)

def render_text(text="Secret text", font='', textcolor=(0, 0, 0), fontsize=16, aa=True):
    return Texture.from_surface(renderer, pygame.font.Font(f'data/{font}.ttf', fontsize).render(text, aa, textcolor))

def shake_screen(power:int):
    global screenshake
    screenshake = Vector2(random.randrange(-power, power), random.randrange(-power, power))

def move_towards(pos: float, targetPos: float, speed: float):
    return Vector2(pos, 0).move_towards(Vector2(targetPos), speed).x

def update():
    global screenshake
    global debug_menu_enabled
    global dt
    global time
    physics_objects.clear()
    collision_objects.clear()
    screenshake = screenshake.move_towards(Vector2(0, 0), 1)
    space.step(dt)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAUSE:
                debug_menu_enabled = not debug_menu_enabled
    if debug_menu_enabled:
        draw_rect((0, 0, 0), (0,0,256,(len(debug_properties)+1)*16))
        blit(render_text('fps: '+str(int(clock.get_fps())), 'font', (0, 255, 0), 16), (0, 0))
        for i, d in enumerate(debug_properties):
            blit(render_text(d, 'font', (0, 255, 0), 16), (0, (i+1)*16))
    renderer.present()
    dt = clock.tick(fps_cap)/1000
    time += 1

def colorImg(image, color, newColor):
    newImg = image.copy()
    paxalaray = pygame.PixelArray(newImg)
    paxalaray.replace(color, newColor)
    return paxalaray.surface

### INPUT ###
def mouse_down():
    return pygame.mouse.get_pressed()

def keyboard_down():
    return pygame.key.get_pressed()

def get_mouse_position():
    return pygame.mouse.get_pos()

class Timer:
    def __init__(self, timer_int_ticks: int):
        self.time = timer_int_ticks
        self.paused = False
        self.done = False
    def update(self):
        if self.paused is True:
            return

        if self.time > 0:
            self.time -= 1 * dt
        self.done = self.time <= 0

class Animator:
    def __init__(self, time_between_frames:int, frames:list[Texture]):
        self.time_between_frames = time_between_frames
        self.frames = frames
        self.timer = Timer(time_between_frames)
        self.image = self.frames[0]
    def update(self):
        self.timer.update()
        if self.timer.done:
            self.timer.time = self.time_between_frames
            if self.frames.index(self.image) >= len(self.frames)-1:
                self.image = self.frames[0]
            else:
                self.image = self.frames[self.frames.index(self.image)+1]

class Tilemap:
    def __init__(self, file_path:str, layers:list[str], object_layers:list[str], scaleBy=1):
        self.path = file_path
        self.file = load_pygame(file_path)
        self.scale_by = scaleBy
        self.layer_dictionaries = []
        self.obj_layer_dictionaries = []
        for layer_name in layers:
            self.layer_dictionaries.append({"name":layer_name, "tiles":[]})
            for x, y, surf in self.file.get_layer_by_name(layer_name).tiles():
                    self.layer_dictionaries[len(self.layer_dictionaries)-1]["tiles"].append({"x": x, "y": y, "texture": Texture.from_surface(renderer, surf.convert_alpha())})
        for obj_layer_name in object_layers:
            self.layer_dictionaries.append({"name":obj_layer_name, "objects":[]})
            for obj in self.file.get_layer_by_name(obj_layer_name):
                self.layer_dictionaries[obj_layer_name]["objects"].append(obj)

    def reload(self):
        self.file = load_pygame(self.path)
    def get_obj_by_name(self, name, layer_name):
        for layer in self.obj_layer_dictionaries:
            if layer["name"] == layer_name:
                for obj in layer["objects"]:
                    if obj.name == name:
                        return obj
    def get_obj_by_type(self, type, layer_name):
        for layer in self.obj_layer_dictionaries:
            if layer["name"] == layer_name:
                for obj in layer["objects"]:
                    if obj.type == type:
                        return obj
    def draw_all_objects(self, layer_name):
        for layer in self.obj_layer_dictionaries:
            if layer["name"] == layer_name:
                for obj in layer["objects"]:
                    blit_rotate_texture(Texture.from_surface(renderer, obj.image.convert_alpha()), ((obj.x-cam.x+screenshake.x)*self.scale_by, (obj.y-cam.y+screenshake.y)*self.scale_by), obj.rotation, (obj.width*self.scale_by, obj.height*self.scale_by))
    def draw(self, layer_name):
        colobs = []
        for layer in self.layer_dictionaries:
            if layer["name"] == layer_name:
                for obj in layer["tiles"]:
                    blit(obj["texture"], ((obj["x"]*obj["texture"].width-cam.x+screenshake.x)*self.scale_by, (obj["y"]*obj["texture"].height-cam.y+screenshake.y)*self.scale_by), (obj["texture"].width*self.scale_by, obj["texture"].height*self.scale_by))
                    colobs.append(Rect(obj["x"]*obj["texture"].width*self.scale_by, obj["y"]*obj["texture"].height*self.scale_by, obj["texture"].width*self.scale_by, obj["texture"].height*self.scale_by))
        return colobs

class PhysicsObject:
    def __init__(self, image:Texture, pos: Vec2d, rot: int, scale: Vec2d, isTrigger=False, kinematic=False, mass=1, drag=0.005, hasGravity=True, gravity=0.1, friction=1.0, layer='base'):
        self.image = image
        self.pos = pos
        self.rot = rot
        self.scale = scale
        self.isTrigger = isTrigger
        self.kinematic = kinematic
        self.drag = drag
        self.mass = mass
        self.canMoveUp = True
        self.canMoveDown = True
        self.canMoveLeft = True
        self.canMoveRight = True
        self.hasGravity = hasGravity
        self.gravity = gravity
        self.friction = friction
        if kinematic:
            body_type = pymunk.Body.KINEMATIC
        else:
            body_type = pymunk.Body.DYNAMIC
        self.body = pymunk.Body(mass, pymunk.moment_for_box(mass, (scale.x, scale.y)), body_type=body_type)
        self.body.position = pos
        self.shape = pymunk.Poly.create_box(self.body, size=scale)
        self.shape.sensor = isTrigger
        self.shape.friction = friction
        self.shape.elasticity = 0.0
        self.shape.collision_type = 2
        space.add(self.body, self.shape)

    def update(self):
        if self.hasGravity:
            self.body.apply_force_at_local_point((0, -self.mass * self.gravity), (0, 0))
        self.body.velocity *= (1 - self.drag)
        self.pos = Vec2d(self.body.position.x, self.body.position.y)
        blit_rotate_texture(self.image, (self.body.position.x, self.body.position.y), -self.body.angle*57.2958, self.scale)

#class Particle:
#    def __init__(self, pos:Vector2, vel:Vector2, color:tuple, radius:int, drag:float, hasGravity=True, gravity:float=0.5):
#        self.pos = pos
#        self.vel = vel
#        self.radius = radius
#        self.color = color
#        self.drag = drag
#        self.hasGravity = hasGravity
#        self.gravity = gravity
#    def update(self):
#        if self.vel.x > 0: # -----Drag-----
#            self.vel.x -= self.drag
#        if self.vel.x < 0:
#            self.vel.x += self.drag
#        if self.vel.y > 0 and self.hasGravity == False: #
#            self.vel.y -= self.drag
#        if self.vel.y < 0 and self.hasGravity == False:
#            self.vel.y += self.drag
#        if abs(self.vel.x) < self.drag:
#            self.vel.x = 0
#        if abs(self.vel.y) < self.drag and self.hasGravity == False:
#            self.vel.y = 0
#        if self.hasGravity:
#            self.vel.y += self.gravity
#        self.pos += self.vel
#        pygame.draw.circle(screen, self.color, self.pos+screenshake, self.radius)
#
#class ParticleSystem:
#    def __init__(self, amount:int, minVel: Vector2, maxVel: Vector2, drag:float, pos:Vector2, radius:int, color:tuple, aliveSeconds:int, hasGravity=True, gravity=0.5):
#        self.particles = np.array([])
#        self.amount = amount
#        self.shouldDie = False
#        self.time = aliveSeconds
#        random.seed()
#        for ps in range(amount):
#            self.particles = np.append(self.particles, Particle(pos, Vector2(random.randrange(minVel.x, maxVel.x), random.randrange(minVel.y, maxVel.y)), color, radius, drag, hasGravity, gravity))
#    def update(self):
#        if self.shouldDie == False:
#            for particle in self.particles:
#                particle.update()
#            self.time -= 1*dt
#        if self.time <= 0:
#            for particle in self.particles:
#                if particle.radius > 0:
#                    particle.radius -= 0.5
#                else:
#                    self.shouldDie = True
#
#class UIButton:
#    def __init__(self, img, pos:Vector2):
#        self.img = img
#        self.pos = pos
#        self.enabled = True
#    def update(self):
#        if self.enabled == True:
#            self.rect = screen.blit(self.img, self.pos.xy)
#            if self.rect.collidepoint(pygame.mouse.get_pos()):
#                if pygame.BUTTON_LEFT in pygame.mouse.get_pressed():
#                    self.onClick()
#    def onClick(self):
#        pass # Replaced in class

physics_objects = []
collision_objects = []
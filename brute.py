import random
import pygame
from pygame.math import Vector2
from pytmx import load_pygame
import math
import pymunk
from pymunk.vec2d import Vec2d
import sys
import pymunk.pygame_util
from pygame._sdl2.video import Window, Texture, Image, Renderer
from pygame import K_BACKSPACE,K_TAB,K_CLEAR,K_RETURN,K_PAUSE,K_ESCAPE,K_SPACE,K_EXCLAIM,K_QUOTEDBL,K_HASH,K_DOLLAR,K_AMPERSAND,K_QUOTE,K_LEFTPAREN,K_RIGHTPAREN,K_ASTERISK,K_PLUS,K_COMMA,K_MINUS,K_PERIOD,K_SLASH,K_0,K_1,K_2,K_3,K_4,K_5,K_6,K_7,K_8,K_9,K_COLON,K_SEMICOLON,K_LESS,K_EQUALS,K_GREATER,K_QUESTION,K_AT,K_LEFTBRACKET,K_BACKSLASH,K_RIGHTBRACKET,K_CARET,K_UNDERSCORE,K_BACKQUOTE,K_a,K_b,K_c,K_d,K_e,K_f,K_g,K_h,K_i,K_j,K_k,K_l,K_m,K_n,K_o,K_p,K_q,K_r,K_s, K_t,K_u,K_v,K_w,K_x,K_y,K_z,K_DELETE,K_KP0,K_KP1,K_KP2,K_KP3,K_KP4,K_KP5,K_KP6,K_KP7,K_KP8,K_KP9,K_KP_PERIOD,K_KP_DIVIDE,K_KP_MULTIPLY,K_KP_MINUS,K_KP_PLUS,K_KP_ENTER,K_KP_EQUALS,K_UP,K_DOWN,K_RIGHT,K_LEFT,K_INSERT,K_HOME,K_END,K_PAGEUP,K_PAGEDOWN,K_F1,K_F2,K_F3,K_F4,K_F5,K_F6,K_F7,K_F8,K_F9,K_F10,K_F11,K_F12,K_F13,K_F14,K_F15,K_NUMLOCK,K_CAPSLOCK,K_SCROLLOCK,K_RSHIFT,K_LSHIFT,K_RCTRL,K_LCTRL,K_RALT,K_LALT,K_RMETA,K_LMETA,K_LSUPER,K_RSUPER,K_MODE,K_HELP,K_PRINT,K_SYSREQ,K_BREAK,K_MENU,K_POWER,K_EURO,K_AC_BACK

renderer: Renderer
window: Window
_window_surf:pygame.Surface
fps_cap = 60
clock:pygame.time.Clock
space:pymunk.Space
cam:Vector2
screenshake:Vector2
transparent_img:Texture
_circle_surf:pygame.Surface
circle_texture:Texture

Surface = pygame.Surface
Clock = pygame.Clock
Rect = pygame.Rect
Sound = pygame.mixer.Sound

_version = "1.7.5"

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
    global _circle_surf
    global circle_texture
    pygame.init()
    window = Window(title, size)
    renderer = Renderer(window, accelerated=1)
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

    transparent_img = load_texture("data/scripts/shapes/transparent.png")
    _circle_surf = pygame.image.load("data/scripts/shapes/circle.png").convert_alpha()
    circle_texture = Texture.from_surface(renderer, _circle_surf)

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
    return dest

def blit_surface(surface:pygame.Surface, position, size=(-1, -1)):
    renderer.draw_color = (255, 255, 255)
    px, py = position
    if size == (-1, -1):
        w, h = surface.get_size()
    else:
        w, h = size
    dest = pygame.Rect(px, py, w, h)
    renderer.blit(Texture.from_surface(renderer, surface), dest)
    return dest

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
def angle_between(vector1:tuple[int, int], vector2:tuple[int, int]):
    _vec1 = Vector2(vector1)
    _vec2 = Vector2(vector2)
    dot_product = _vec1.dot(vector2)
    magnitude1 = _vec1.length()
    magnitude2 = _vec2.length()
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
    screenshake = screenshake.move_towards(Vector2(0, 0), 1)
    space.step(dt)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAUSE:
                debug_menu_enabled = not debug_menu_enabled
            on_keyboard_pressed(event.key)
        if event.type == pygame.MOUSEBUTTONDOWN:
            on_mouse_pressed(event.button)
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

def on_keyboard_pressed(key):
    pass

def on_mouse_pressed(button):
    pass

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
    def __init__(self, image:Texture, pos: tuple[int, int], rot: int, scale: tuple[int, int], isTrigger=False, kinematic=False, mass=1, drag=0.005, hasGravity=True, gravity=0.1, friction=1.0, layer='base'):
        self.image = image
        self.pos = Vec2d(pos[0], pos[1])
        self.rot = rot
        self.scale = Vec2d(scale[0], scale[1])
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
        self.body = pymunk.Body(mass, pymunk.moment_for_box(mass, (self.scale.x, self.scale.y)), body_type=body_type)
        self.body.position = pos
        self.shape = pymunk.Poly.create_box(self.body, size=self.scale)
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

class ParticleSystem:
    def __init__(self, amount:int, minVel: tuple[float, float], maxVel: tuple[float, float], drag:float, pos:tuple[int, int], radius:int, color:tuple, aliveSeconds:int, gravity=0):
        self.particles = []
        self.amount = amount
        self.shouldDie = False
        self.time = aliveSeconds
        self.gravity = gravity
        self.drag = drag
        random.seed()
        for ps in range(amount):
            self.particles.append({"x": pos[0], "y": pos[1], "vel_x": random.uniform(minVel[0], maxVel[0]), "vel_y": random.uniform(minVel[1], maxVel[1]), "radius": radius, "color": color, "texture": Texture.from_surface(renderer, colorImg(_circle_surf, (255, 255, 255), color))})
    def update(self):
        if self.shouldDie == False:
            for particle in self.particles:
                if particle["vel_x"] > 1:
                    particle["vel_x"] -= self.drag*dt
                elif particle["vel_x"] < 1:
                    particle["vel_x"] += self.drag*dt
                else:
                    particle["vel_x"] = 0
                if particle["vel_y"] > 1:
                    particle["vel_y"] -= self.drag*dt
                elif particle["vel_y"] < 1:
                    particle["vel_y"] += self.drag*dt
                else:
                    particle["vel_y"] = 0
                particle["vel_y"] += self.gravity*dt
                particle["x"] += particle["vel_x"]
                particle["y"] += particle["vel_y"]
                blit(particle["texture"], (particle["x"], particle["y"]), (particle["radius"]*2, particle["radius"]*2))
            self.time -= 1*dt
        if self.time <= 0:
            for particle in self.particles:
                if particle["radius"] > 0:
                    particle["radius"] -= 0.5
                else:
                    self.shouldDie = True

class UIButton:
    def __init__(self, img:Texture, pos:tuple[int, int]):
        self.img = img
        self.pos = pos
        self.enabled = True
    def update(self):
        if self.enabled == True:
            self.rect = blit(self.img, self.pos)
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                if pygame.BUTTON_LEFT in pygame.mouse.get_pressed():
                    self.onClick()
    def onClick(self):
        pass  # Replaced in class
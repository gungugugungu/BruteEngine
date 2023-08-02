import random
import pygame
from pygame.math import Vector2
import data.scripts.settings as settings
from pytmx import load_pygame
import numpy as np
import math
import pygame_shaders
import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pygame_util

pygame.init()
screen = pygame.surface.Surface((69, 69))
clock = pygame.time.Clock()
space = pymunk.Space(True)
space.threads = 4
space.gravity = (0, 981)
square = pygame.image.load('data/scripts/shapes/square.png').convert_alpha()
circle = pygame.image.load('data/scripts/shapes/circle.png').convert_alpha()

cCheckRes = 4
iterations = 10

debugProperties = []
debugMenuEnabled = False

dt = 0

Shader = pygame_shaders.Shader
clear = pygame_shaders.clear

def angleBetween(vector1, vector2):
    dot_product = vector1.dot(vector2)

    magnitude1 = vector1.length()
    magnitude2 = vector2.length()

    angle_radians = math.acos(dot_product / (magnitude1 * magnitude2))

    angle_degrees = math.degrees(angle_radians)

    return angle_degrees

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

def RenderText(text="Secret text", font='', textcolor=(0, 0, 0), fontsize=16, aa=True):
    return pygame.font.Font(f'data/{font}.ttf', fontsize).render(text, aa, textcolor)

def shake_screen(power:int):
    settings.screenshake = Vector2(random.randrange(-power, power), random.randrange(-power, power))

def move_towards(pos: float, targetPos: float, speed: float):
    return Vector2(pos, 0).move_towards(Vector2(targetPos), speed).x

def update():
    physics_objects.clear()
    collision_objects.clear()
    settings.screenshake = settings.screenshake.move_towards(Vector2(0, 0), 1)
    space.step(dt)
    if debugMenuEnabled:
        pygame.draw.rect(screen, (0, 0, 0), (0,0,256,(len(debugProperties)+1)*16))
        screen.blit(RenderText('fps: '+str(int(clock.get_fps())), 'font', (0, 255, 0), 16), (0, 0))
        for i, d in enumerate(debugProperties):
            screen.blit(RenderText(d, 'font', (0, 255, 0), 16), (0, (i+1)*16))
        draw_options = pymunk.pygame_util.DrawOptions(screen)
        space.debug_draw(draw_options)

def colorImg(image, color, newColor):
    newImg = image.copy()
    paxalaray = pygame.PixelArray(newImg)
    paxalaray.replace(color, newColor)
    return paxalaray.surface

class VariableStorer:
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
    def __init__(self, timeBetweenFrames:int,  frames:list):
        self.timeBetweenFrames = timeBetweenFrames
        self.frames = frames
        self.timer = Timer(timeBetweenFrames)
        self.image = self.frames[0]
    def update(self):
        self.timer.update()
        if self.timer.done:
            self.timer.time = self.timeBetweenFrames
            if self.frames.index(self.image) >= len(self.frames)-1:
                self.image = self.frames[0]
            else:
                self.image = self.frames[self.frames.index(self.image)+1]

class Tilemap:
    def __init__(self, file_path:str, scaleBy=1, max_bake_size=Vector2(10000, 10000)):
        self.path = file_path
        self.file = load_pygame(file_path)
        self.scale_by = scaleBy
        self.baked = False
        self.bakeSurface = pygame.Surface(max_bake_size.xy).convert_alpha()
        self.bakeSurface.set_colorkey((255, 0, 255))
    def bake(self, tileLayers:list, objectLayers:list):
        self.baked = True
        self.bakeSurface.fill((255, 0, 255))
        for tileLayerName in tileLayers:
            for x, y, surf in np.array(list(self.file.get_layer_by_name(tileLayerName).tiles())):
                self.bakeSurface.blit(pygame.transform.scale(surf, (surf.get_width()*self.scale_by, surf.get_height()*self.scale_by)), ((x*surf.get_width())*self.scale_by, (y*surf.get_height())*self.scale_by))
        for objectLayerName in objectLayers:
            for obj in np.array(self.file.get_layer_by_name(objectLayerName)):
                self.bakeSurface.blit(pygame.transform.rotate(pygame.transform.scale(obj.image.pygame.Surface.convert_alpha(), (obj.width*self.scale_by, obj.height*self.scale_by)), -obj.rotation), (obj.x*self.scale_by, obj.y*self.scale_by))
    def bake_delete(self):
        self.baked = False
        self.bakeSurface.fill((255, 0, 255))
    def bake_draw(self):
        if self.baked:
            screen.blit(self.bakeSurface, settings.cam+settings.screenshake)
        else:
            print('Not baked, cannot render')
    def reload(self):
        self.file = load_pygame(self.path)
    def get_obj_by_name(self, name, layer):
        for obj in self.file.get_layer_by_name(layer):
            if obj.name == name:
                return obj
    def get_obj_by_type(self, type, layer):
        for obj in self.file.get_layer_by_name(layer):
            if obj.type == type:
                return obj
    def draw_all_objects(self, layer):
        rects = []
        for obj in self.file.get_layer_by_name(layer):
            rects.append(screen.blit(pygame.transform.rotate(pygame.transform.scale(obj.image.convert_alpha(), (obj.width*self.scale_by, obj.height*self.scale_by)), -obj.rotation), ((obj.x+settings.cam.x+settings.screenshake.x)*self.scale_by, (obj.y+settings.cam.y+settings.screenshake.y)*self.scale_by)))
        return rects
    def draw_objects_to_different_screen(self, surface, layer):
        rects = []
        for obj in self.file.get_layer_by_name(layer):
            rects.append(surface.blit(pygame.transform.rotate(pygame.transform.scale(obj.image.convert_alpha(), (obj.width*self.scale_by, obj.height*self.scale_by)), -obj.rotation), ((obj.x+settings.cam.x+settings.screenshake.x)*self.scale_by, (obj.y+settings.cam.y+settings.screenshake.y)*self.scale_by)))
        return rects
    def get_all_objects(self, layer):
        retun = []
        for obj in self.file.get_layer_by_name(layer):
            retun.append(obj)
        return retun
    def draw(self, layer, offset=Vector2(0, 0)):
        colobs = []
        for x, y, surf in self.file.get_layer_by_name(layer).tiles():
            rect = screen.blit(pygame.transform.scale(surf.convert_alpha(), (surf.get_width()*self.scale_by, surf.get_height()*self.scale_by)), ((x*surf.get_width()+settings.cam.x+offset.x+settings.screenshake.x+settings.camSize.x)*self.scale_by, (y*surf.get_height()+settings.cam.y+offset.y+settings.camSize.y+settings.screenshake.y)*self.scale_by))
            colobs.append(rect)
        return colobs
    def draw_to_different_surface(self, layer, surface, offset=Vector2(0, 0)):
        colobs = []
        for x, y, surf in self.file.get_layer_by_name(layer).tiles():
            rect = surface.blit(pygame.transform.scale(surf.convert_alpha(), (surf.get_width()*self.scale_by, surf.get_height()*self.scale_by)), (x*surf.get_width()+settings.cam.x+offset.x+settings.screenshake.x-settings.camSize.x*self.scale_by, y*surf.get_height()+settings.cam.y+offset.y-settings.camSize.y+settings.screenshake.y*self.scale_by))
            colobs.append(rect)
        return colobs
    def draw_all_layers(self,offset=Vector2(0, 0)):
        colobs = []
        for layer in self.file.visible_tile_layers.tiles():
            for x, y, surf in self.file.get_layer_by_name(layer.name).tiles():
                rect = screen.blit(pygame.transform.scale(surf.convert_alpha(), (surf.get_width()+settings.camSize.x, surf.get_height()+settings.camSize.y)), (x*surf.get_width()+settings.cam.x+offset.x+settings.screenshake.x-settings.camSize.x, y*surf.get_height()+settings.cam.y+offset.y-settings.camSize.y+settings.screenshake.y))
                colobs.append(rect)
        return colobs
    def get_layer_colobjs(self, layer, offset=Vector2(0, 0)):
        colobs = []
        for x, y, surf in (self.file.get_layer_by_name(layer).tiles()):
            rect = pygame.Rect(x*32+offset.x, y*32+offset.y, surf.get_width(), surf.get_height())
            colobs.append(rect)
        return colobs

class Object:
    def __init__(self, image, pos: Vec2d, rot: int, scale: Vec2d, isTrigger=False, friction=1.0, layer='base'):
        self.image = image
        self.pos = pos
        self.rot = rot
        self.scale = scale
        self.isTrigger = isTrigger
        # Initialize pymunk body for the object (kinematic body)
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = pos
        self.shape = pymunk.Poly.create_box(self.body, size=scale)
        self.shape.sensor = isTrigger
        self.shape.friction = friction
        self.shape.collision_type = 1  # Assign a unique collision type (integer) for this object
        space.add(self.body, self.shape)  # Add the body and shape to the pymunk space

    def update(self):
        # Update the position of the object based on the pymunk body's position
        self.pos = Vec2d(self.body.position.x, self.body.position.y)
        draw_object(self.image, self.body.position, self.body.angle, self.scale)
        # The rotation and rendering code can remain the same

class PhysicsObject:
    def __init__(self, image, pos: Vec2d, rot: int, scale: Vec2d, isTrigger=False, kinematic=False, mass=1, drag=0.005, hasGravity=True, gravity=0.1, friction=1.0, layer='base'):
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
        # Initialize pymunk body for the object (dynamic body if not kinematic)
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
        self.shape.collision_type = 2  # Assign a unique collision type (integer) for this object
        space.add(self.body, self.shape)  # Add the body and shape to the pymunk space

    def update(self):
        if self.hasGravity:
            self.body.apply_force_at_local_point((0, -self.mass * self.gravity), (0, 0))
        self.body.velocity *= (1 - self.drag)  # Apply drag to velocity

        # The rest of the code dealing with collision detection and response can be removed
        # Pymunk handles collisions and responses internally based on the shapes and bodies added to the space

        # Update the position of the object based on the pymunk body's position
        self.pos = Vec2d(self.body.position.x, self.body.position.y)
        draw_object(self.image.convert_alpha(), self.body.position, self.body.angle, self.scale)
        # The rotation and rendering code can remain the same

def draw_object(image, pos, rot, scale):
    # Scale the image
    scaled_image = pygame.transform.scale(image, (int(scale.x), int(scale.y)))
    # Rotate the image
    rotated_image = pygame.transform.rotate(scaled_image, -(rot*57.2958))
    # Get the position of the top-left corner of the image
    x, y = pos.x -rotated_image.get_width() / 2, pos.y -rotated_image.get_height() / 2
    # Draw the image on the screen
    screen.blit(rotated_image, (x, y))

class Particle:
    def __init__(self, pos:Vector2, vel:Vector2, color:tuple, radius:int, drag:float, hasGravity=True, gravity:float=0.5):
        self.pos = pos
        self.vel = vel
        self.radius = radius
        self.color = color
        self.drag = drag
        self.hasGravity = hasGravity
        self.gravity = gravity
    def update(self):
        if self.vel.x > 0: # -----Drag-----
            self.vel.x -= self.drag
        if self.vel.x < 0:
            self.vel.x += self.drag
        if self.vel.y > 0 and self.hasGravity == False: #
            self.vel.y -= self.drag
        if self.vel.y < 0 and self.hasGravity == False:
            self.vel.y += self.drag
        if abs(self.vel.x) < self.drag:
            self.vel.x = 0
        if abs(self.vel.y) < self.drag and self.hasGravity == False:
            self.vel.y = 0
        if self.hasGravity:
            self.vel.y += self.gravity
        self.pos += self.vel
        pygame.draw.circle(screen, self.color, self.pos+settings.screenshake, self.radius)

class ParticleSystem:
    def __init__(self, amount:int, minVel: Vector2, maxVel: Vector2, drag:float, pos:Vector2, radius:int, color:tuple, aliveSeconds:int, hasGravity=True, gravity=0.5):
        self.particles = np.array([])
        self.amount = amount
        self.shouldDie = False
        self.time = aliveSeconds
        random.seed()
        for ps in range(amount):
            self.particles = np.append(self.particles, Particle(pos, Vector2(random.randrange(minVel.x, maxVel.x), random.randrange(minVel.y, maxVel.y)), color, radius, drag, hasGravity, gravity))
    def update(self):
        if self.shouldDie == False:
            for particle in self.particles:
                particle.update()
            self.time -= 1*dt
        if self.time <= 0:
            for particle in self.particles:
                if particle.radius > 0:
                    particle.radius -= 0.5
                else:
                    self.shouldDie = True

class UIButton:
    def __init__(self, img, pos:Vector2):
        self.img = img
        self.pos = pos
        self.enabled = True
    def update(self):
        if self.enabled == True:
            self.rect = screen.blit(self.img, self.pos.xy)
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                if pygame.BUTTON_LEFT in pygame.mouse.get_pressed():
                    self.onClick()
    def onClick(self):
        pass # Replaced in class

physics_objects = []
collision_objects = []
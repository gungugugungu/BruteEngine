import random
import pygame
from pygame.math import Vector2
import data.scripts.settings as settings
from pytmx import load_pygame
import numpy as np
import math

""""
    ----------------------------------------------------------------
    ----------------------------------------------------------------
    ----------------------------------------------------------------
    made by Gungu
    Notes:

    If you steal, I'll actually be quite sad, cause I worked a lot on this thing. 
    Around 50 hours already. :|
    ----------------------------------------------------------------
    ----------------------------------------------------------------
    ----------------------------------------------------------------
"""

screen = pygame.surface.Surface((69, 69))
clock = pygame.time.Clock()
square = pygame.image.load('data/scripts/shapes/square.png')
circle = pygame.image.load('data/scripts/shapes/circle.png')

cCheckRes = 4
iterations = 10

debugProperties = []
debugMenuEnabled = False

dt = 0

import math
import pygame

import math
import pygame

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
    if debugMenuEnabled:
        pygame.draw.rect(screen, (0, 0, 0), (0,0,256,(len(debugProperties)+1)*16))
        screen.blit(RenderText('fps: '+str(int(clock.get_fps())), 'font', (0, 255, 0), 16), (0, 0))
        for i, d in enumerate(debugProperties):
            screen.blit(RenderText(d, 'font', (0, 255, 0), 16), (0, (i+1)*16))

def colorImg(image, color, newColor):
    paxalaray = pygame.PixelArray(image)
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
    def __init__(self, image, pos: pygame.Vector2, rot: int, scale: pygame.Vector2, isTrigger=False, layer='base'):
        self.image = image
        self.pos = pos
        self.rot = rot
        self.scale = scale
        self.rect = screen.blit(pygame.transform.rotate(pygame.transform.scale(self.image, self.scale), self.rot), self.pos)
        self.isTrigger = isTrigger
    def update(self):
        self.rect = screen.blit(pygame.transform.rotate(pygame.transform.scale(self.image, self.scale+settings.camSize.xy), self.rot), self.pos+settings.cam+settings.screenshake-settings.camSize)
        if self.isTrigger == False:
            collision_objects.append(self)

class PhysicsObject:
    def __init__(self, image, pos: pygame.Vector2, rot: int, scale: pygame.Vector2, isTrigger=False, kinematic=False, mass:float=1, drag=0.005, hasGravity=True, gravity=0.1, friction=0.7, layer='base'):
        self.image:pygame.Surface = image
        self.pos = pos
        self.rot = rot
        self.scale = scale
        self.rect = screen.blit(pygame.transform.rotate(pygame.transform.scale(self.image, self.scale), self.rot), self.pos)
        self.isTrigger = isTrigger
        self.vel = pygame.Vector2(0, 0)
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
    def update(self):
        if self.hasGravity:
            self.vel.y += self.gravity
            if self.canMoveDown == False:
                self.vel = self.vel.move_towards(Vector2(0, self.vel.y), self.friction)
        if self.vel.x > 0 and self.canMoveRight == False:
            self.vel.x = 0
        if self.vel.x < 0 and self.canMoveLeft == False:
            self.vel.x = 0
        if self.vel.y < 0 and self.canMoveUp == False:
            self.vel.y = 0
        if self.vel.y > 0 and self.canMoveDown == False:
            self.vel.y = 0
        self.vel = self.vel.move_towards(Vector2(0, 0), self.drag)
        if self.vel.x != 0 or self.vel.y != 0:
            self.move(self.pos+self.vel)
        self.rect = screen.blit(pygame.transform.rotate(pygame.transform.scale(self.image, self.scale), self.rot), self.pos+settings.cam+settings.screenshake)
        physics_objects.append(self)
        if self.isTrigger == False:
            collision_objects.append(self)
        self.canMoveUp = True
        self.canMoveDown = True
        self.canMoveLeft = True
        self.canMoveRight = True
    def move(self, position):
        pobj_rects = (
            (Vector2(position.x+cCheckRes, position.y+self.rect.h-cCheckRes), Vector2(self.rect.w-cCheckRes*2, cCheckRes)),  # bottom
            (Vector2(position.x+cCheckRes, position.y), Vector2(cCheckRes, self.rect.h-cCheckRes*2)),  # top
            (Vector2(position.x, position.y+cCheckRes), Vector2(cCheckRes, self.rect.h-cCheckRes*2)),  # left
            (Vector2(position.x+self.rect.w-cCheckRes, position.y+cCheckRes), Vector2(cCheckRes, self.rect.h-cCheckRes*2)),  # right
        )
        pobj_can_move = [True, True, True, True]
        colliding_objects = tuple([cobj for cobj in collision_objects if cobj != self and any(AABB(pobj_rect[0], pobj_rect[1], Vector2(cobj.pos.x, cobj.pos.y), Vector2(cobj.scale.x, cobj.scale.y)) for pobj_rect in pobj_rects)])
        collided = False
        for cobj in colliding_objects:
            for i, pobj_rect in enumerate(pobj_rects):
                if AABB(pobj_rect[0], pobj_rect[1], Vector2(cobj.pos.x, cobj.pos.y), Vector2(cobj.scale.x, cobj.scale.y)):
                    pobj_can_move[i] = False
                    collided = True
        self.canMoveDown, self.canMoveUp, self.canMoveLeft, self.canMoveRight = pobj_can_move
        if collided:
            step = 1
            for i in range(iterations):
                new_pos = self.pos.lerp(position, step/10)
                collided = any(AABB(new_pos, self.scale, cobj.pos, cobj.scale) for cobj in colliding_objects)
                if not collided:
                    self.pos = new_pos
                    break
                step += 1
            if self.canMoveDown and position.y > self.pos.y:
                self.pos.y = self.pos.move_towards(position, abs(self.pos.y-position.y)-self.friction).y
            else:
                self.vel.y = 0
            if self.canMoveUp and position.y < self.pos.y:
                self.pos.y = self.pos.move_towards(position, abs(self.pos.y-position.y)-self.friction).y
                self.vel.y = self.vel.move_towards(Vector2(self.vel.x, 0), self.friction).y
            else:
                self.vel.y = 0
            if self.canMoveLeft and position.x < self.pos.x:
                self.pos.x = self.pos.move_towards(position, abs(self.pos.x-position.x)-self.friction).x
                self.vel.x = self.vel.move_towards(Vector2(0, self.vel.y), self.friction).x
            else:
                self.vel.x = 0
            if self.canMoveRight and position.x > self.pos.x:
                self.pos.x = self.pos.move_towards(position, abs(self.pos.x-position.x)-self.friction).x
                self.vel.x = self.vel.move_towards(Vector2(0, self.vel.y), self.friction).x
            else:
                self.vel.x = 0
            return False
        else:
            self.pos = position
            return True

def AABB(rect1pos:Vector2, rect1size:Vector2, rect2pos:Vector2, rect2size:Vector2):
    if rect1pos.x+rect1size.x<rect2pos.x or rect1pos.x>rect2pos.x+rect2size.x:
        return False
    if rect1pos.y+rect1size.y<rect2pos.y or rect1pos.y>rect2pos.y+rect2size.y:
        return False
    return True

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
    def __init__(self, amount:int, minVel: Vector2, maxVel: Vector2, drag:float, pos:Vector2, radius:int, color:tuple, aliveFrames:int, hasGravity=True, gravity=0.5):
        self.particles = np.array([])
        self.amount = amount
        self.shouldDie = False
        self.time = aliveFrames
        random.seed()
        for ps in range(amount):
            self.particles = np.append(self.particles, Particle(pos, Vector2(random.randrange(minVel.x, maxVel.x), random.randrange(minVel.y, maxVel.y)), color, radius, drag, hasGravity, gravity))
    def update(self):
        if self.shouldDie == False:
            for particle in self.particles:
                particle.update()
            self.time -= 1
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
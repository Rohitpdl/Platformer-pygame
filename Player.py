import pygame
import os
from os import listdir
from os.path import isfile, join, dirname, abspath

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    try:
        
        base_dir = dirname(abspath(__file__))
        path = join(base_dir, "assets", dir1, dir2)
        
        images = [f for f in listdir(path) if isfile(join(path, f))]

        all_sprites = {}

        for image in images:
            sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

            sprites = []
            for i in range(sprite_sheet.get_width() // width):
                surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
                rect = pygame.Rect(i * width, 0, width, height)
                surface.blit(sprite_sheet, (0, 0), rect)
                sprites.append(pygame.transform.scale2x(surface))

            if direction:
                all_sprites[image.replace(".png", "") + "_right"] = sprites
                all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
            else:
                all_sprites[image.replace(".png", "")] = sprites

        return all_sprites
    except Exception as e:
        print(f"Error loading sprites: {e}")
        fallback_sprite = pygame.Surface((width*2, height*2), pygame.SRCALPHA)
        fallback_sprite.fill((255, 165, 0))
        
        all_sprites = {}
        if direction:
            all_sprites["idle_right"] = [fallback_sprite]
            all_sprites["idle_left"] = [pygame.transform.flip(fallback_sprite, True, False)]
            all_sprites["run_right"] = [fallback_sprite]
            all_sprites["run_left"] = [pygame.transform.flip(fallback_sprite, True, False)]
            all_sprites["jump_right"] = [fallback_sprite]
            all_sprites["jump_left"] = [pygame.transform.flip(fallback_sprite, True, False)]
            all_sprites["fall_right"] = [fallback_sprite]
            all_sprites["fall_left"] = [pygame.transform.flip(fallback_sprite, True, False)]
            all_sprites["double_jump_right"] = [fallback_sprite]
            all_sprites["double_jump_left"] = [pygame.transform.flip(fallback_sprite, True, False)]
            all_sprites["hit_right"] = [fallback_sprite]
            all_sprites["hit_left"] = [pygame.transform.flip(fallback_sprite, True, False)]
        else:
            all_sprites["sprite"] = [fallback_sprite]
        
        return all_sprites

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "VirtualGuy", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width , height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0


    # def make_hit(self):
    #     self.hit = True


    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self, *args, **kwargs):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x, offset_y=0):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))
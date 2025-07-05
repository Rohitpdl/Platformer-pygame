import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer - Expanded Maze")

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5

LEVEL_WIDTH = 3000
LEVEL_HEIGHT = 2000

window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    try:
        path = join("assets", dir1, dir2)
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
    except:
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


def get_block(size, tile_x=96, tile_y=0):
    try:
        path = join("assets", "Terrain", "Terrain.png")
        image = pygame.image.load(path).convert_alpha()
        surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
        rect = pygame.Rect(tile_x, tile_y, size, size)
        surface.blit(image, (0, 0), rect)
        return pygame.transform.scale2x(surface)
    except:
        surface = pygame.Surface((size, size))
        if tile_x == 96:
            surface.fill((34, 139, 34))
        else:
            surface.fill((220, 20, 60))
        
        pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 2)
        return surface


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
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

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()
        print(self.rect.left)
        print(self.rect.bottom)

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


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x, offset_y=0):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size, 96, 0)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class FloatingBlock(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size, "floating")
        block = get_block(size, 0, 0)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


def get_background(name):
        width, height = 64, 64
        image = pygame.image.load(join("assets", "Background", name))
        _, _, width, height = image.get_rect()
        image = pygame.Surface((width, height))
        image.fill((135, 206, 235))
        
        tiles = []
        for i in range(WIDTH // width + 1):
            for j in range(HEIGHT // height + 1):
                pos = (i * width, j * height)
                tiles.append(pos)

        return tiles, image


def draw(window, background, bg_image, player, objects, offset_x, offset_y):
    window.fill((135, 206, 235))

    for tile in background:
        window.blit(bg_image, (tile[0] - offset_x, tile[1] - offset_y))

    for obj in objects:
        obj.draw(window, offset_x, offset_y)

    player.draw(window, offset_x, offset_y)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    player.move(player.x_vel, 0)
    player.update()
    
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if player.x_vel > 0:
                player.rect.right = obj.rect.left
            elif player.x_vel < 0:
                player.rect.left = obj.rect.right
            player.x_vel = 0
            break
    
    player.move(0, player.y_vel)
    player.update()
    
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if player.y_vel > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif player.y_vel < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
            break


def create_expanded_maze_level():
    block_size = 96
    
    green_blocks = [
        (0, 0),
        (96, 0),
        (192, 0),
        (288, 0),
        (384, 0),
        (480, 0),
        (576, 0),
        (672, 0),
        (768, 0),
        (864, 0),
        (960, 0),
        (1056, 0),
        (1152, 0),
        (1248, 0),
        (1344, 0),
        (1440, 0),
        (1536, 0),
        (1632, 0),
        (1728, 0),
        (1824, 0),
        (1920, 0),
        (2016, 0),
        (2112, 0),
        (2208, 0),
        (2304, 0),
        (2400, 0),
        (2496, 0),
        (2592, 0),
        (2688, 0),
        (2784, 0),
        (2880, 0),
        (0, 96),
        (384, 96),
        (1536, 96),
        (2880, 96),
        (0, 192),
        (384, 192),
        (1536, 192),
        (2880, 192),
        (0, 288),
        (288, 288),
        (384, 288),
        (672, 288),
        (768, 288),
        (864, 288),
        (960, 288),
        (1056, 288),
        (1536, 288),
        (2016, 288),
        (2112, 288),
        (2208, 288),
        (2880, 288),
        (0, 384),
        (288, 384),
        (384, 384),
        (672, 384),
        (768, 384),
        (864, 384),
        (960, 384),
        (1056, 384),
        (1536, 384),
        (2016, 384),
        (2112, 384),
        (2208, 384),
        (2880, 384),
        (0, 480),
        (1056, 480),
        (1536, 480),
        (1920, 480),
        (2016, 480),
        (2112, 480),
        (2208, 480),
        (2880, 480),
        (0, 576),
        (1056, 576),
        (1536, 576),
        (1728, 576),
        (1824, 576),
        (1920, 576),
        (2016, 576),
        (2112, 576),
        (2208, 576),
        (2880, 576),
        (0, 672),
        (288, 672),
        (384, 672),
        (480, 672),
        (576, 672),
        (768, 672),
        (1056, 672),
        (1536, 672),
        (2208, 672),
        (2880, 672),
        (0, 768),
        (768, 768),
        (1056, 768),
        (1536, 768),
        (1632, 768),
        (1728, 768),
        (1824, 768),
        (1920, 768),
        (2208, 768),
        (2880, 768),
        (0, 864),
        (768, 864),
        (1056, 864),
        (1536, 1056),
        (1632, 864),
        (1728, 864),
        (1824, 864),
        (1920, 864),
        (2208, 864),
        (2880, 864),
        (0, 960),
        (288, 960),
        (384, 960),
        (480, 960),
        (576, 960),
        (672, 960),
        (1056, 960),
        (2208, 960),
        (2304, 960),
        (2400, 960),
        (2880, 960),
        (0, 1056),
        (192, 1056),
        (288, 1056),
        (1056, 1056),
        (2208, 1056),
        (2304, 1056),
        (2400, 1056),
        (2880, 1056),
        (0, 1152),
        (96, 1152),
        (192, 1152),
        (288, 1152),
        (1056, 1152),
        (1152, 1152),
        (1248, 1152),
        (1344, 1152),
        (1440, 1152),
        (1536, 1152),
        (1632, 1152),
        (1728, 1152),
        (1824, 1152),
        (1920, 1152),
        (2016, 1152),
        (2112, 1152),
        (2208, 1152),
        (2304, 1152),
        (2400, 1152),
        (2496, 1152),
        (2784, 1152),
        (2880, 1152),
        (0, 1248),
        (96, 1248),
        (192, 1248),
        (288, 1248),
        (480, 1248),
        (576, 1248),
        (672, 1248),
        (768, 1248),
        (864, 1248),
        (960, 1248),
        (1056, 1248),
        (1152, 1248),
        (1248, 1248),
        (1344, 1248),
        (2784, 1248),
        (2880, 1248),
        (0, 1344),
        (96, 1344),
        (192, 1344),
        (288, 1344),
        (480, 1344),
        (576, 1344),
        (672, 1344),
        (768, 1344),
        (864, 1344),
        (960, 1344),
        (1056, 1344),
        (1152, 1344),
        (1248, 1344),
        (2592, 1344),
        (2688, 1344),
        (2784, 1344),
        (2880, 1344),
        (0, 1440),
        (480, 1440),
        (576, 1440),
        (672, 1440),
        (768, 1440),
        (864, 1440),
        (960, 1440),
        (1056, 1440),
        (1152, 1440),
        (1248, 1440),
        (2592, 1440),
        (2688, 1440),
        (2784, 1440),
        (2880, 1440),
        (0, 1536),
        (2592, 1536),
        (2688, 1536),
        (2784, 1536),
        (2880, 1536),
        (0, 1632),
        (2208, 1632),
        (2304, 1632),
        (2400, 1632),
        (2496, 1632),
        (2592, 1632),
        (2688, 1632),
        (2784, 1632),
        (2880, 1632),
        (0, 1728),
        (2208, 1728),
        (2304, 1728),
        (2400, 1728),
        (2496, 1728),
        (2592, 1728),
        (2688, 1728),
        (2784, 1728),
        (2880, 1728),
        (0, 1824),
        (96, 1824),
        (192, 1824),
        (288, 1824),
        (384, 1824),
        (480, 1824),
        (576, 1824),
        (672, 1824),
        (768, 1824),
        (864, 1824),
        (960, 1824),
        (1056, 1824),
        (1152, 1824),
        (1248, 1824),
        (1344, 1824),
        (1440, 1824),
        (1536, 1824),
        (1632, 1824),
        (1728, 1824),
        (1824, 1824),
        (1920, 1824),
        (2016, 1824),
        (2112, 1824),
        (2208, 1824),
        (2304, 1824),
        (2400, 1824),
        (2496, 1824),
        (2592, 1824),
        (2688, 1824),
        (2784, 1824),
        (2880, 1824)
    ]
    
    red_blocks = [
        (1152, 288),
        (1440, 288),
        (96, 384),
        (2400, 384),
        (1440, 480),
        (2688, 576),
        (1152, 672),
        (192, 768),
        (2400, 768),
        (2496, 768),
        (1344, 864),
        (2400, 1440)
    ]
    
    return green_blocks, red_blocks


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96

    player = Player(150, LEVEL_HEIGHT - block_size * 3, 50, 50)
    
    green_positions, red_positions = create_expanded_maze_level()
    
    green_blocks = [Block(x, y, block_size) for x, y in green_positions]
    
    red_blocks = [FloatingBlock(x, y, block_size) for x, y in red_positions]

    objects = [*green_blocks, *red_blocks]

    offset_x = 0
    offset_y = 0
    scroll_area_width = 250
    scroll_area_height = 200

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            player.x_vel = -PLAYER_VEL
            player.direction = "left"
        elif keys[pygame.K_RIGHT]:
            player.x_vel = PLAYER_VEL  
            player.direction = "right"
        else:
            player.x_vel = 0
            
        player.rect.x += player.x_vel
        
        for obj in objects:
            if player.rect.colliderect(obj.rect):
                if player.x_vel > 0:
                    player.rect.right = obj.rect.left
                elif player.x_vel < 0:
                    player.rect.left = obj.rect.right
                player.x_vel = 0
                break
        
        player_landed = False
        player.rect.y += player.y_vel
        
        for obj in objects:
            if player.rect.colliderect(obj.rect):
                if player.y_vel > 0:
                    player.rect.bottom = obj.rect.top
                    player.landed()
                    player_landed = True
                elif player.y_vel < 0:
                    player.rect.top = obj.rect.bottom
                    player.hit_head()
                break
        
        player.update()
        
        target_offset_x = player.rect.centerx - WIDTH // 2
        target_offset_y = player.rect.centery - HEIGHT // 2
        
        camera_speed = 0.1
        offset_x += (target_offset_x - offset_x) * camera_speed
        offset_y += (target_offset_y - offset_y) * camera_speed
        
        offset_x = max(0, min(offset_x, LEVEL_WIDTH - WIDTH))
        offset_y = max(0, min(offset_y, LEVEL_HEIGHT - HEIGHT))

        draw(window, background, bg_image, player, objects, offset_x, offset_y)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
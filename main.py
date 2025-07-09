import pygame

pygame.init()

WIDTH, HEIGHT = 1000, 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer - Expanded Maze")

from Player import Player
from level import Block, FloatingBlock, get_background, create_expanded_maze_level
from collision import handle_vertical_collision, collide

# Constants
FPS = 60
PLAYER_VEL = 5
STARTX = 150
STARTY = 1800
LEVEL_WIDTH = 3000
LEVEL_HEIGHT = 2000


def draw(window, background, bg_image, player, objects, offset_x, offset_y):
    window.fill((211, 211, 211))

    for tile in background:
        window.blit(bg_image, (tile[0] - offset_x, tile[1] - offset_y))

    for obj in objects:
        obj.draw(window, offset_x, offset_y)

    player.draw(window, offset_x, offset_y)

    pygame.display.update()


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96
    player = Player(STARTX, STARTY, 50, 50)

    green_positions, red_positions = create_expanded_maze_level()
    green_blocks = [Block(x, y, block_size) for x, y in green_positions]
    red_blocks = [FloatingBlock(x, y, block_size) for x, y in red_positions]
    objects = [*green_blocks, *red_blocks]

    offset_x = 0
    offset_y = 0

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

        player.rect.y += player.y_vel
        for obj in objects:
            if player.rect.colliderect(obj.rect):
                if player.y_vel > 0:
                    player.rect.bottom = obj.rect.top
                    player.landed()
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

import pygame

def HandleCollision(player, objects):
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

import pygame
import sys
from main import main 
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game")

FONT = pygame.font.Font("assets/Fonts/PressStart2P-Regular.ttf", 35)
TITLE_FONT = pygame.font.Font("assets/Fonts/PressStart2P-Regular.ttf", 50)
 
WHITE= (255, 255, 255)
GREEN = (85, 193, 0)
GREEN_DARK = (60, 130, 0)
RED = (207, 13, 0)
RED_DARK = (140, 0, 0)
SHADOW_COLOR = (135, 135, 135)
BLUE = (83, 47, 0)
BLACK= (0, 0, 0)

background_img = pygame.image.load("assets/Background/Graphics.png")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

class Button:
    def __init__(self, text, x, y, width, height, default_color, hover_color):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.default_color = default_color
        self.hover_color = hover_color
        self.color = self.default_color

    def draw(self, screen, mouse_pos):
        # Check hover
        if self.rect.collidepoint(mouse_pos):
            self.color = self.hover_color
        else:
            self.color = self.default_color

        # Draw shadow
        shadow_rect = self.rect.copy()
        shadow_rect.x += 6
        shadow_rect.y += 6
        pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, border_radius=12)

        # Draw button
        pygame.draw.rect(screen, self.color, self.rect, border_radius=12)

        # Draw border
        pygame.draw.rect(screen, WHITE, self.rect, width=3, border_radius=12)

        text_surf = FONT.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Create buttons
play_button = Button("Play", WIDTH // 2 - 125, HEIGHT // 2 , 250, 75, GREEN, GREEN_DARK)
quit_button = Button("Quit", WIDTH // 2 - 125, HEIGHT // 2 + 100, 250, 75, RED, RED_DARK)

def draw_text(text, font, color, surface, x, y):
    txt_obj = font.render(text, True, color)
    txt_rect = txt_obj.get_rect(center=(x, y))
    surface.blit(txt_obj, txt_rect)
    return txt_rect

def menu():
    clock = pygame.time.Clock()
    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(background_img,(0, 0))

        play_button.draw(screen, mouse_pos)
        quit_button.draw(screen, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.is_clicked(event.pos):
                    main(screen)
                if quit_button.is_clicked(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    menu()

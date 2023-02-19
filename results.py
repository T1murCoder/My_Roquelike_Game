import pygame

from menu import load_image
from menu import FONT


def results_scene(surface, real_screen, mode, kills, waves):
    game_over_image = load_image("menu_bgs/results.png")
    game_over_image = pygame.transform.scale(game_over_image, surface.get_size())

    game_over_running = True
    while game_over_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_over_running = False
        if real_screen.get_size() == (1920, 1200):
            surface.blit(pygame.transform.scale(game_over_image, (1920, 1200)), (0, 0))
        else:
            surface.blit(pygame.transform.scale(game_over_image, (1920, 1080)), (0, 0))

        mode_text = FONT.render(f"Your mode: {mode}", True, (255, 255, 255))
        kills_text = FONT.render(f"You killed: {kills} enemies", True, (255, 255, 255))
        time_text = FONT.render(f"You survived: {waves} waves", True, (255, 255, 255))

        surface.blit(mode_text, (surface.get_width() // 2 - mode_text.get_width() // 2, surface.get_height() // 2 - 50))
        surface.blit(kills_text, (surface.get_width() // 2 - mode_text.get_width() // 2, surface.get_height() // 2))
        surface.blit(time_text, (surface.get_width() // 2 - mode_text.get_width() // 2, surface.get_height() // 2 + 50))

        real_screen.blit(pygame.transform.scale(surface, real_screen.get_size()), (0, 0))

        pygame.display.flip()

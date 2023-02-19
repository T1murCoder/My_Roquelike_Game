import pygame

from menu import load_image


def win_scene(surface, real_screen):
    game_over_image = load_image("menu_bgs/win.png")
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

        real_screen.blit(pygame.transform.scale(surface, real_screen.get_size()), (0, 0))

        pygame.display.flip()

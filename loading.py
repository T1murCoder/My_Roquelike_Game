import pygame

from menu import load_image


def loading_scene(surface, real_screen):
    CLOCK = pygame.time.Clock()

    WORK = 100

    width, height = surface.get_width(), surface.get_height()

    game_logo_image = pygame.transform.scale(load_image("loading/game_logo.png"), (200, 200))
    game_name_image = load_image("loading/roquelike-game.png")

    # load background image
    loading_bg_image = load_image("loading/loading_bar_background.png")
    loading_bar_image = load_image("loading/loading_bar.png")

    # load bar image
    loading_bg_rect = loading_bg_image.get_rect(center=(width // 2, height // 2))
    loading_bar_rect = loading_bar_image.get_rect(midleft=(width // 2 - loading_bg_image.get_width() // 2 + 20,
                                                           height // 2))

    for i in range(WORK):
        surface.fill("#0d0e2e")

        loading_bar_width = i / WORK * 720

        loading_bar_image_resized = pygame.transform.scale(loading_bar_image, (int(loading_bar_width), 165))

        surface.blit(loading_bg_image, loading_bg_rect)
        surface.blit(loading_bar_image_resized, loading_bar_rect)
        surface.blit(game_logo_image, (width - 20 - game_logo_image.get_width(),
                                       height - 20 - game_logo_image.get_height()))

        surface.blit(game_name_image, (width // 2 - game_name_image.get_width() // 2,
                                       height // 2 - game_name_image.get_height() - 100))

        real_screen.blit(pygame.transform.scale(surface, real_screen.get_size()), (0, 0))

        pygame.display.flip()
        CLOCK.tick(60)

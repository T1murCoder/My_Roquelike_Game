import sys

import pygame
import os


pygame.init()
size = width, height = 1280, 720
screen = pygame.display.set_mode(size)
FONT = pygame.font.Font(None, 50)


class Menu:
    def __init__(self):
        self.option_surfaces = []
        self.functions = []
        self.current_option_index = 0

    def append_option(self, option, function):
        self.option_surfaces.append(FONT.render(option, True, (100, 255, 100)))
        self.functions.append(function)

    def switch(self, direction):
        self.current_option_index += direction
        self.current_option_index %= len(self.option_surfaces)
        if self.current_option_index < 0:
            self.current_option_index = len(self.option_surfaces) - 1

    def select(self):
        self.functions[self.current_option_index]()

    def draw(self, surface, x, y, y_padding):
        for i, option in enumerate(self.option_surfaces):
            option_rect = option.get_rect()
            option_rect.topleft = (x, y + i * y_padding)
            if i == self.current_option_index:
                pygame.draw.rect(surface, (0, 100, 0), option_rect)
            surface.blit(option, option_rect)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def menu_scene():
    # TODO: Сделать изображение для меню
    # TODO: Добавить settings (Тут должно быть разрешение экрана
    menu_running = True

    def start_game():
        nonlocal menu_running
        menu_running = False

    menu = Menu()
    menu.append_option("Play", lambda: start_game())
    menu.append_option("Quit", lambda: sys.exit(0))

    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    menu.switch(-1)
                elif event.key == pygame.K_s:
                    menu.switch(1)
                elif event.key == pygame.K_SPACE:
                    menu.select()

        screen.fill("#0d0e2e")
        menu.draw(screen, 100, 100, 50)

        pygame.display.flip()


def loading_scene():
    CLOCK = pygame.time.Clock()
    # TODO: Сделать надпись

    WORK = 100

    game_logo_image = pygame.transform.scale(load_image("loading/game_logo.png"), (200, 200))

    # load background image
    loading_bg_image = load_image("loading/loading_bar_background.png")
    loading_bg_rect = loading_bg_image.get_rect(center=(640, 360))

    # load bar image
    loading_bar_image = load_image("loading/loading_bar.png")
    loading_bar_rect = loading_bar_image.get_rect(midleft=(280, 360))

    for i in range(WORK):
        screen.fill("#0d0e2e")

        loading_bar_width = i / WORK * 720

        loading_bar_image_resized = pygame.transform.scale(loading_bar_image, (int(loading_bar_width), 165))

        screen.blit(loading_bg_image, loading_bg_rect)
        screen.blit(loading_bar_image_resized, loading_bar_rect)
        screen.blit(game_logo_image, (width - 20 - game_logo_image.get_width(),
                                      height - 20 - game_logo_image.get_height()))

        pygame.display.flip()
        CLOCK.tick(60)


def game_over_scene():
    game_over_image = load_image("menu_bgs/game_over.png")

    game_over_running = True
    while game_over_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_over_running = False
        screen.blit(game_over_image, (0, 0))
        pygame.display.flip()

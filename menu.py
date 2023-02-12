import sys

import pygame
import os


pygame.init()
size = width, height = 1280, 720
screen = pygame.display.set_mode(size)
FONT = pygame.font.Font(None, 50)


class Menu:
    def __init__(self):
        self.option_text = []
        self.functions = []
        self.current_option_index = 0

    def append_option(self, option, function):
        self.option_text.append(option)
        self.functions.append(function)

    def switch(self, direction):
        self.current_option_index += direction
        self.current_option_index %= len(self.option_text)
        if self.current_option_index < 0:
            self.current_option_index = len(self.option_text) - 1

    def select(self):
        self.functions[self.current_option_index]()

    def draw(self, surface, x, y, y_padding):
        option_surfaces = [FONT.render(option, True, (100, 255, 100)) for option in self.option_text]
        for i, option in enumerate(option_surfaces):
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
    hints_image = load_image("menu/controls_hint.png")

    menu_running = True

    current_page = "main"

    fullscreen_toggled = False
    sound_toggled = True

    def start_game():
        nonlocal menu_running
        menu_running = False

    def switch_page():
        nonlocal current_page
        if current_page == "main":
            current_page = "settings"
        else:
            current_page = "main"

    def switch_display_mode():
        nonlocal fullscreen_toggled

        if fullscreen_toggled is False:
            fullscreen_toggled = True
            menu_settings_page.option_text[0] = "Fullscreen - on"
        else:
            fullscreen_toggled = False
            menu_settings_page.option_text[0] = "Fullscreen - off"

    def switch_sound_mode():
        nonlocal sound_toggled

        if sound_toggled is False:
            sound_toggled = True
            menu_settings_page.option_text[1] = "Sound - on"
        else:
            sound_toggled = False
            menu_settings_page.option_text[1] = "Sound - off"

    menu_main_page = Menu()
    menu_main_page.append_option("Play", start_game)
    menu_main_page.append_option("Settings", switch_page)
    menu_main_page.append_option("Quit", lambda: sys.exit(0))

    menu_settings_page = Menu()
    menu_settings_page.append_option("Fullscreen - off", switch_display_mode)
    menu_settings_page.append_option("Sound - on", switch_sound_mode)
    menu_settings_page.append_option("Back", switch_page)

    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if current_page == "main":
                    if event.key == pygame.K_w:
                        menu_main_page.switch(-1)
                    elif event.key == pygame.K_s:
                        menu_main_page.switch(1)
                    elif event.key == pygame.K_SPACE:
                        menu_main_page.select()
                else:
                    if event.key == pygame.K_w:
                        menu_settings_page.switch(-1)
                    elif event.key == pygame.K_s:
                        menu_settings_page.switch(1)
                    elif event.key == pygame.K_SPACE:
                        menu_settings_page.select()

        screen.fill("#0d0e2e")
        if current_page == "main":
            menu_main_page.draw(screen, 100, 100, 50)
        else:
            menu_settings_page.draw(screen, 100, 100, 50)
            # print(f"Fullscreen - {fullscreen_toggled}, Sound - {sound_toggled}")

        screen.blit(hints_image, (50, height - 25 - hints_image.get_height()))

        pygame.display.flip()
    return {"Fullscreen_toggled": fullscreen_toggled, "Sound_toggled": sound_toggled}


def loading_scene():
    CLOCK = pygame.time.Clock()

    WORK = 100

    game_logo_image = pygame.transform.scale(load_image("loading/game_logo.png"), (200, 200))
    game_name_image = load_image("loading/roquelike-game.png")

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

        screen.blit(game_name_image, (width // 2 - game_name_image.get_width() // 2,
                                      height // 2 - game_name_image.get_height() - 100))

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

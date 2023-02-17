import sys

import pygame
import os
import json


pygame.init()
size = width, height = 1920, 1080
virtual_screen = pygame.display.set_mode(size)
FONT = pygame.font.Font(None, 50)


class Menu:
    def __init__(self, volume=50):
        self.switch_snd = pygame.mixer.Sound("data/sounds/switch_tab.wav")
        self.select_snd = pygame.mixer.Sound("data/sounds/select.wav")
        self.option_text = []
        self.functions = []
        self.hor_values = []  # hor -> horizontal
        self.current_option_index = 0
        self.volume = volume

    def append_option(self, option, function, horizontal_values=None, current_horizontal_idx=0, hor_auto_call=False):
        self.option_text.append(option)
        self.functions.append(function)
        self.hor_values.append([horizontal_values, current_horizontal_idx, hor_auto_call])

    def switch_vertical(self, direction):
        self.current_option_index += direction
        self.current_option_index %= len(self.option_text)
        if self.current_option_index < 0:
            self.current_option_index = len(self.option_text) - 1
        self.switch_snd.set_volume(self.volume / 100)
        self.switch_snd.play()

    def switch_horizontal(self, direction):

        if self.hor_values[self.current_option_index][0]:
            self.hor_values[self.current_option_index][1] += direction
            self.hor_values[self.current_option_index][1] %= len(self.hor_values[self.current_option_index][0])
            if self.hor_values[self.current_option_index][1] < 0:
                self.hor_values[self.current_option_index][1] = len(self.hor_values[self.current_option_index][0]) - 1
            current_option_array = self.hor_values[self.current_option_index]
            current_option_array_index = current_option_array[1]
            option_text = current_option_array[0][current_option_array_index]
            self.option_text[self.current_option_index] = option_text
            if current_option_array[2]:
                self.functions[self.current_option_index]()
        self.switch_snd.set_volume(self.volume / 100)
        self.switch_snd.play()

    def select(self):
        self.functions[self.current_option_index]()
        self.select_snd.set_volume(self.volume / 100)
        self.select_snd.play()

    def set_volume(self, volume):
        self.volume = volume

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


def get_size_from_json():
    with open("data/settings/settings.json") as file:
        f = file.read()
        data = json.loads(f)
        size = data["size"]
    return size


def get_sfx_volume_from_json():
    with open("data/settings/settings.json") as file:
        f = file.read()
        data = json.loads(f)
        volume = data["sfx_volume"]
    return volume


def menu_scene(surface, real_screen):
    hints_image = load_image("menu/controls_hint.png")

    def load_settings_data():
        nonlocal fullscreen_toggled, music_toggled, volume, interface_volume, sfx_volume
        with open("data/settings/settings.json") as file:
            f = file.read()
            data = json.loads(f)
            fullscreen_toggled = data["fullscreen_toggled"]
            music_toggled = data["music_toggled"]
            volume = data["music_volume"]
            interface_volume = data["interface_volume"]
            sfx_volume = data["sfx_volume"]
            if not (0 <= volume <= 100):
                volume = 100

    menu_running = True

    current_page = "main"

    fullscreen_toggled = False
    music_toggled = True
    volume = 100
    interface_volume = 100
    sfx_volume = 100
    screen_resolution = get_size_from_json()

    load_settings_data()

    if fullscreen_toggled:
        pygame.display.toggle_fullscreen()

    if not music_toggled:
        pygame.mixer.music.set_volume(0)

    fullscreen_text = "Fullscreen - off" if not fullscreen_toggled else "Fullscreen - on"

    music_text = "Music - on" if music_toggled else "Music - off"

    volume_list = [i for i in range(0, 101, 10)]

    volume_idx = volume_list.index(volume)
    volume_text = f"Music Volume -> {volume_list[volume_idx]}"

    screen_resolution_list = [[800, 600], [1280, 720], [1920, 1080], [1920, 1200]]
    screen_resolution_text = f"Screen resolution -> {screen_resolution[0]}x{screen_resolution[1]}"
    screen_resolution_text_list = [f"Screen resolution -> {elem[0]}x{elem[1]}"
                                   for elem in screen_resolution_list]
    screen_resolution_idx = screen_resolution_list.index(screen_resolution)

    interface_volume_idx = volume_list.index(interface_volume)
    interface_volume_text = f"Interface volume -> {volume_list[interface_volume_idx]}"

    sfx_volume_idx = volume_list.index(sfx_volume)
    sfx_volume_text = f"Sfx volume -> {volume_list[sfx_volume_idx]}"

    def save_settings_file():
        with open("data/settings/settings.json", "w") as file:
            option_text = menu_settings_page.option_text[2]
            volume = int(option_text[option_text.find('>') + 1:])
            dt = {
                "fullscreen_toggled": fullscreen_toggled,
                "music_toggled": music_toggled,
                "music_volume": volume,
                "interface_volume": interface_volume,
                "sfx_volume": sfx_volume,
                "size": screen_resolution
                }
            json.dump(dt, file)

    def start_game():
        nonlocal menu_running
        menu_running = False
        save_settings_file()

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
            pygame.display.toggle_fullscreen()
        else:
            fullscreen_toggled = False
            menu_settings_page.option_text[0] = "Fullscreen - off"
            pygame.display.toggle_fullscreen()

    def switch_music_mode():
        nonlocal music_toggled

        if music_toggled is False:
            music_toggled = True
            menu_settings_page.option_text[1] = "Music - on"
            set_music_volume()
        else:
            music_toggled = False
            menu_settings_page.option_text[1] = "Music - off"
            pygame.mixer.music.set_volume(0)

    def set_screen_resolution():
        nonlocal screen_resolution

        text = menu_settings_page.option_text[3].split()[3]
        screen_resolution = list(map(int, text.split("x")))

    def function_for_quit():
        """По большому счёту, это костыль, потому что я не нашёл способа
            как адекватно можно вызвать две функции в одной строке"""
        save_settings_file()
        sys.exit(0)

    def set_music_volume():
        if music_toggled:
            option_text = menu_settings_page.option_text[2]
            volume = int(option_text[option_text.find('>') + 1:])
            pygame.mixer.music.set_volume(volume / 100)

    def set_interface_volume():
        nonlocal interface_volume
        option_text = menu_settings_page.option_text[4]
        interface_volume = int(option_text[option_text.find('>') + 1:])
        menu_settings_page.set_volume(interface_volume)

    def set_sfx_volume():
        nonlocal sfx_volume
        option_text = menu_settings_page.option_text[5]
        sfx_volume = int(option_text[option_text.find('>') + 1:])

    menu_main_page = Menu(volume=interface_volume)
    menu_main_page.append_option("Play", start_game)
    menu_main_page.append_option("Settings", switch_page)
    menu_main_page.append_option("Quit", function_for_quit)

    menu_settings_page = Menu(volume=interface_volume)
    menu_settings_page.append_option(fullscreen_text, switch_display_mode)
    menu_settings_page.append_option(music_text, switch_music_mode)
    menu_settings_page.append_option(volume_text, set_music_volume,
                                     [f"Music volume -> {i}" for i in volume_list], volume_idx, True)

    menu_settings_page.append_option(screen_resolution_text, set_screen_resolution,
                                     screen_resolution_text_list, screen_resolution_idx, True)

    menu_settings_page.append_option(interface_volume_text, set_interface_volume,
                                     [f"Interface volume -> {i}" for i in volume_list],
                                     interface_volume_idx, True)

    menu_settings_page.append_option(sfx_volume_text, set_sfx_volume,
                                     [f"Sfx volume -> {i}" for i in volume_list], sfx_volume_idx, True)

    menu_settings_page.append_option("Back", switch_page)
    set_music_volume()

    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings_file()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if current_page == "main":
                    if event.key == pygame.K_w:
                        menu_main_page.switch_vertical(-1)
                    elif event.key == pygame.K_s:
                        menu_main_page.switch_vertical(1)
                    elif event.key == pygame.K_SPACE:
                        menu_main_page.select()
                else:
                    if event.key == pygame.K_w:
                        menu_settings_page.switch_vertical(-1)
                    elif event.key == pygame.K_s:
                        menu_settings_page.switch_vertical(1)
                    elif event.key == pygame.K_SPACE:
                        menu_settings_page.select()
                    elif event.key == pygame.K_d:
                        menu_settings_page.switch_horizontal(1)
                    elif event.key == pygame.K_a:
                        menu_settings_page.switch_horizontal(-1)
                if event.key == pygame.K_F11:
                    switch_display_mode()

        surface.fill("#0d0e2e")
        if current_page == "main":
            menu_main_page.draw(surface, 100, 100, 50)
        else:
            menu_settings_page.draw(surface, 100, 100, 50)
            # print(f"Fullscreen - {fullscreen_toggled}, Sound - {music_toggled}")

        surface.blit(hints_image, (50, height - 25 - hints_image.get_height()))

        real_screen.blit(pygame.transform.scale(surface, real_screen.get_size()), (0, 0))

        pygame.display.flip()


def loading_scene(surface, real_screen):
    CLOCK = pygame.time.Clock()

    WORK = 100

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


def game_over_scene(surface, real_screen):
    game_over_image = load_image("menu_bgs/game_over.png")
    game_over_image = pygame.transform.scale(game_over_image, size)

    game_over_running = True
    while game_over_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_over_running = False
        surface.blit(pygame.transform.scale(game_over_image, (1920, 1080)), (0, 0))

        real_screen.blit(pygame.transform.scale(surface, real_screen.get_size()), (0, 0))

        pygame.display.flip()

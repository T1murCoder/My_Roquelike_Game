import sys

import pygame


pygame.init()
size = width, height = 1280, 720
screen = pygame.display.set_mode(size)
FONT = pygame.font.Font(None, 50)


class Menu:
    def __init__(self):
        self.option_surfaces = []
        self.functions = []
        self.current_index = 0

    def append_option(self, option, function):
        self.option_surfaces.append(FONT.render(option, True, (100, 255, 100)))
        self.functions.append(function)

    def switch(self, direction):
        self.current_index += direction
        self.current_index %= len(self.option_surfaces)
        if self.current_index < 0:
            self.current_index = len(self.option_surfaces) - 1

    def select(self):
        self.functions[self.current_index]()

    def draw(self, surface, x, y, y_padding):
        for i, option in enumerate(self.option_surfaces):
            option_rect = option.get_rect()
            option_rect.topleft = (x, y + i * y_padding)
            if i == self.current_index:
                pygame.draw.rect(surface, (0, 100, 0), option_rect)
            surface.blit(option, option_rect)


def create_menu():
    # TODO: Сделать изображение для меню
    menu_running = True

    def start_game():
        nonlocal menu_running
        menu_running = False

    menu = Menu()
    menu.append_option("Play", lambda: start_game())
    menu.append_option("Quit", lambda: print("Quit"))

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

        screen.fill((0, 0, 0))
        menu.draw(screen, 100, 100, 50)

        pygame.display.flip()

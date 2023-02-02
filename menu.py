import pygame


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, text, func, *group):
        super().__init__(*group)
        self.image = pygame.surface.Surface(width, height)
        pygame.draw.rect(self.image, pygame.Color("grey"), (0, 0, width, height))
        font = pygame.font.Font(None, 50)
        pygame_text = font.render(text, True, (100, 255, 100))
        self.image.blit(pygame_text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.action_func = func

    def check_hit(self):
        # TODO: Сделать активацию функции при нажатии
        pass

    def update(self):
        pass


class Background(pygame.sprite.Sprite):
    def __init(self, *group):
        super().__init__(*group)


def create_menu():
    pass
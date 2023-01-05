import random

import pygame

import os
import sys

import pygame

size = width, height = 1280, 720
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Moving Game')
clock = pygame.time.Clock()


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


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.image = pygame.Surface((30, 50))
        pygame.draw.rect(self.image, pygame.Color("blue"), (0, 0, 30, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 10
        self.ready_to_shoot = True
        self.fire_cooldown = 7
        self.time_gone_from_shot = 0

    def move(self, direction):
        if direction == "right":
            self.rect = self.rect.move(self.speed, 0)
            if pygame.sprite.spritecollideany(self, borders_sprites):
                self.rect = self.rect.move(-self.speed, 0)
        elif direction == "left":
            self.rect = self.rect.move(-self.speed, 0)
            if pygame.sprite.spritecollideany(self, borders_sprites):
                self.rect = self.rect.move(self.speed, 0)
        elif direction == "up":
            self.rect = self.rect.move(0, -self.speed)
            if pygame.sprite.spritecollideany(self, borders_sprites):
                self.rect = self.rect.move(0, self.speed)
        elif direction == "down":
            self.rect = self.rect.move(0, self.speed)
            if pygame.sprite.spritecollideany(self, borders_sprites):
                self.rect = self.rect.move(0, -self.speed)

    def shoot(self, direction):
        if self.ready_to_shoot:
            bullet_x = self.rect.x
            bullet_y = self.rect.y
            Bullet(bullet_x, bullet_y, direction, [bullet_sprites, all_sprites])
            self.ready_to_shoot = False

    def update(self, *args):
        if not args:
            if not self.ready_to_shoot:
                self.time_gone_from_shot += 1
                if self.time_gone_from_shot == self.fire_cooldown:
                    self.ready_to_shoot = True
                    self.time_gone_from_shot = 0


class Enemy(pygame.sprite.Sprite):
    image = pygame.Surface((30, 50))
    pygame.draw.rect(image, pygame.Color("red"), (0, 0, 30, 50))

    def __init__(self, x, y, health, *group):
        super().__init__(*group)
        self.image = Enemy.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.health = health

    def move(self):
        pass

    def update(self, *args):
        if self.health == 0:
            self.kill()
        if pygame.sprite.spritecollideany(self, bullet_sprites):
            self.health -= 1


class Bullet(pygame.sprite.Sprite):
    image = pygame.Surface((21, 21))
    pygame.draw.circle(image, "gray", (11, 11), 10)
    image.set_colorkey(image.get_at((0, 0)))
    image = image.convert_alpha()

    def __init__(self, x, y, direction, *group):
        super().__init__(*group)
        self.image = Bullet.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 15
        self.direction = direction

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, borders_sprites):
            self.kill()
        if pygame.sprite.spritecollideany(self, enemies_sprites):
            self.kill()
        if self.direction == 'right':
            self.rect = self.rect.move(self.speed, 0)
        elif self.direction == 'left':
            self.rect = self.rect.move(-self.speed, 0)
        elif self.direction == 'up':
            self.rect = self.rect.move(0, -self.speed)
        elif self.direction == 'down':
            self.rect = self.rect.move(0, self.speed)


class Border(pygame.sprite.Sprite):
    def __init__(self, side, *group):
        super().__init__(*group)
        if side == "right" or side == "left":
            self.image = pygame.Surface((10, height))
            pygame.draw.rect(self.image, pygame.Color("purple"), (0, 0, 10, height))
            self.rect = self.image.get_rect()
            if side == "left":
                self.rect.x = 0
            else:
                self.rect.x = width - 10
            self.rect.y = 0
        elif side == "up" or side == "down":
            self.image = pygame.Surface((width, 10))
            pygame.draw.rect(self.image, pygame.Color("purple"), (0, 0, width, 10))
            self.rect = self.image.get_rect()
            self.rect.x = 0
            if side == "up":
                self.rect.y = 0
            else:
                self.rect.y = height - 10


def spawn_enemies(count):
    for i in range(count):
        enemy_x = random.randint(0, width - Enemy.image.get_rect()[2] - 10)
        enemy_y = random.randint(0, height - Enemy.image.get_rect()[3] - 10)
        enemy = Enemy(enemy_x, enemy_y, 3, [enemies_sprites, all_sprites])
        while pygame.sprite.spritecollideany(enemy, player_sprite):
            enemy.kill()
            enemy_x = random.randint(0, width - Enemy.image.get_rect()[2] - 10)
            enemy_y = random.randint(0, height - Enemy.image.get_rect()[3] - 10)
            enemy = Enemy(enemy_x, enemy_y, 3, [enemies_sprites, all_sprites])


if __name__ == '__main__':
    fps = 30

    all_sprites = pygame.sprite.Group()
    borders_sprites = pygame.sprite.Group()
    player_sprite = pygame.sprite.Group()
    bullet_sprites = pygame.sprite.Group()
    enemies_sprites = pygame.sprite.Group()

    player = Player(width // 2, height // 2, [player_sprite, all_sprites])
    Border("left", [all_sprites, borders_sprites])
    Border("right", [all_sprites, borders_sprites])
    Border("up", [all_sprites, borders_sprites])
    Border("down", [all_sprites, borders_sprites])

    spawn_enemies(5)

    running = True
    while running:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # Shooting
                if event.key == pygame.K_RIGHT:
                    player.shoot("right")
                elif event.key == pygame.K_LEFT:
                    player.shoot("left")
                elif event.key == pygame.K_UP:
                    player.shoot("up")
                elif event.key == pygame.K_DOWN:
                    player.shoot("down")

        pressed = pygame.key.get_pressed()
        # Player movement
        if pressed[pygame.K_w]:
            player.move("up")
        if pressed[pygame.K_s]:
            player.move("down")
        if pressed[pygame.K_d]:
            player.move("right")
        if pressed[pygame.K_a]:
            player.move("left")

        screen.fill(pygame.Color("black"))
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()

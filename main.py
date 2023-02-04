import random

import math

import os
import sys

import pygame
import pytmx

from menu import create_menu, Menu

size = width, height = 1280, 720
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Roquelike Game')
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


class Level:
    def __init__(self, filename):
        self.map = pytmx.load_pygame(f"data/map/{filename}")
        self.width = self.map.width
        self.height = self.map.height
        self.tile_size = self.map.tilewidth
        self.create_tile_sprites()

    def create_tile_sprites(self):
        # пришлось расположить тайлы, которые отвечают за стенки на краю карты
        walls_gids = [self.map.get_tile_gid(x, 999, 0) for x in range(9)]

        for y in range(self.height):
            for x in range(self.width):

                image = self.map.get_tile_image(x, y, 0)

                if image:
                    pos_x = x * self.tile_size
                    pos_y = y * self.tile_size

                    gid = self.map.get_tile_gid(x, y, 0)
                    if gid in walls_gids:
                        pass
                        Tile(image, pos_x, pos_y, [level_sprites, wall_sprites])
                    else:
                        Tile(image, pos_x, pos_y, level_sprites)


class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, *group):
        super().__init__(*group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Player(pygame.sprite.Sprite):
    stand_image_right = load_image("hero/hero-stand_R.png")
    stand_image_left = pygame.transform.flip(load_image("hero/hero-stand_R.png"), True, False)
    right_images = [load_image("hero/hero-walk_1_R.png"),
                    load_image("hero/hero-walk_2_R.png"),
                    load_image("hero/hero-walk_3_R.png"),
                    load_image("hero/hero-walk_4_R.png")]
    left_images = [pygame.transform.flip(elem, True, False) for elem in right_images]

    def __init__(self, x, y, *group):
        super().__init__(*group)
        # TODO: Сделать хп игроку и их снятие (+ кадры неуязвимости)
        # TODO: Графические отрисовывать хп
        self.image = Player.stand_image_right
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 10
        self.orientation = "right"
        self.phase = 0
        self.ready_to_shoot = True
        self.fire_cooldown = 7
        self.time_gone_from_shot = 0

    def move(self, direction):
        # Player movement
        if direction == "right":
            self.rect = self.rect.move(self.speed, 0)
            if pygame.sprite.spritecollideany(self, wall_sprites):
                self.rect = self.rect.move(-self.speed, 0)
            self.orientation = "right"
        elif direction == "left":
            self.rect = self.rect.move(-self.speed, 0)
            if pygame.sprite.spritecollideany(self, wall_sprites):
                self.rect = self.rect.move(self.speed, 0)
            self.orientation = "left"
        elif direction == "up":
            self.rect = self.rect.move(0, -self.speed)
            if pygame.sprite.spritecollideany(self, wall_sprites):
                self.rect = self.rect.move(0, self.speed)
        elif direction == "down":
            self.rect = self.rect.move(0, self.speed)
            if pygame.sprite.spritecollideany(self, wall_sprites):
                self.rect = self.rect.move(0, -self.speed)

    def input(self):
        pressed = pygame.key.get_pressed()
        # Player movement
        key_pressed = False
        if pressed[pygame.K_w]:
            player.move("up")
            key_pressed = True
        if pressed[pygame.K_s]:
            player.move("down")
            key_pressed = True
        if pressed[pygame.K_d]:
            player.move("right")
            key_pressed = True
        if pressed[pygame.K_a]:
            player.move("left")
            key_pressed = True
        if key_pressed:
            self.change_phase()
        if not pressed[pygame.K_w] and not pressed[pygame.K_s] and not pressed[pygame.K_d] and not pressed[pygame.K_a]:
            self.change_phase(reset=True)

    def change_phase(self, reset=False):
        if reset:
            self.phase = 0
            if self.orientation == "right":
                self.image = Player.stand_image_right
            else:
                self.image = Player.stand_image_left
            return
        if self.orientation == "right":
            self.image = Player.right_images[self.phase]
            self.phase += 1
            self.phase %= 4
        elif self.orientation == "left":
            self.image = Player.left_images[self.phase]
            self.phase += 1
            self.phase %= 4

    def shoot(self, mouse_x, mouse_y):
        if self.ready_to_shoot:
            # Spawn bullet
            bullet_x = self.rect.centerx
            bullet_y = self.rect.centery
            Bullet(bullet_x, bullet_y, mouse_x, mouse_y, [bullet_sprites, all_sprites])
            self.ready_to_shoot = False

    def update(self, *args):
        self.input()
        if not self.ready_to_shoot:
            self.time_gone_from_shot += 1
            if self.time_gone_from_shot == self.fire_cooldown:
                self.ready_to_shoot = True
                self.time_gone_from_shot = 0


class Enemy(pygame.sprite.Sprite):
    stand_image_right = load_image("enemy/enemy-stand_R.png")
    stand_image_left = pygame.transform.flip(load_image("enemy/enemy-stand_R.png"), True, False)
    right_images = [load_image("enemy/enemy-walk_1_R.png"),
                    load_image("enemy/enemy-walk_2_R.png"),
                    load_image("enemy/enemy-walk_3_R.png"),
                    load_image("enemy/enemy-walk_4_R.png")]
    left_images = [pygame.transform.flip(elem, True, False) for elem in right_images]
    # image = pygame.Surface((30, 50))
    # pygame.draw.rect(image, pygame.Color("red"), (0, 0, 30, 50))

    def __init__(self, x, y, health, *group):
        super().__init__(*group)
        self.image = Enemy.stand_image_right
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vision_range = 500
        self.speed = 5
        self.phase = 0
        self.orientation = "right"
        self.get_orientation()
        self.health = health

    def get_orientation(self):
        x_diff = player.rect.x - self.rect.x
        y_diff = player.rect.y - self.rect.y
        angle = math.atan2(y_diff, x_diff)
        x_movement = int(math.cos(angle) * self.speed)
        if x_movement > 0:
            self.orientation = "right"
        else:
            self.orientation = "left"

    def move(self):
        # Calculate the direction
        x_diff = player.rect.x - self.rect.x
        y_diff = player.rect.y - self.rect.y
        angle = math.atan2(y_diff, x_diff)
        x_movement = int(math.cos(angle) * self.speed)
        y_movement = int(math.sin(angle) * self.speed)
        self.rect = self.rect.move(x_movement, y_movement)

    def change_phase(self, reset=False):
        if reset:
            self.phase = 0
            if self.orientation == "right":
                self.image = Enemy.stand_image_right
            else:
                self.image = Enemy.stand_image_left
            return
        if self.orientation == "right":
            self.image = Enemy.right_images[self.phase]
            self.phase += 1
            self.phase %= 4
        elif self.orientation == "left":
            self.image = Enemy.left_images[self.phase]
            self.phase += 1
            self.phase %= 4

    def get_distance_to_player(self):
        x_range = abs(self.rect.centerx) - abs(player.rect.centerx)
        y_range = abs(self.rect.centery) - abs(player.rect.centery)
        distance = round((x_range ** 2 + y_range ** 2) ** 0.5)
        return distance

    def update(self, *args):
        distance = self.get_distance_to_player()
        if distance <= self.vision_range:
            self.move()
            self.get_orientation()
            self.change_phase()
        else:
            self.get_orientation()
            self.change_phase(reset=True)
        if self.health == 0:
            self.kill()
        if pygame.sprite.spritecollideany(self, bullet_sprites):
            self.health -= 1


class Bullet(pygame.sprite.Sprite):
    image = load_image("bullet/green_bullet.png")

    def __init__(self, x, y, mouse_x, mouse_y, *group):
        super().__init__(*group)
        self.image = Bullet.image
        self.image = pygame.transform.scale(self.image, (11, 21))
        self.image = pygame.transform.rotate(self.image, -90)

        # Calculate the angle to rotate image
        x_diff = mouse_x - x
        y_diff = mouse_y - y
        angle = math.degrees(math.atan2(-y_diff, x_diff))
        self.image = pygame.transform.rotate(self.image, angle)

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.spawn_x = x
        self.spawn_y = y
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y
        self.speed = 15

    def move(self):
        # Calculate the direction
        x_diff = self.mouse_x - self.spawn_x
        y_diff = self.mouse_y - self.spawn_y
        angle = math.atan2(y_diff, x_diff)
        x_movement = int(math.cos(angle) * self.speed)
        y_movement = int(math.sin(angle) * self.speed)
        self.rect = self.rect.move(x_movement, y_movement)

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, wall_sprites):
            self.kill()
        if pygame.sprite.spritecollideany(self, enemies_sprites):
            self.kill()
        self.move()


class Gun(pygame.sprite.Sprite):
    # image = pygame.surface.Surface((30, 20))
    # pygame.draw.rect(image, pygame.Color("grey"), (0, 0, 30, 20))
    # TODO: Найти нормальный спрайт
    # TODO: Расположить спрайт так чтобы пули спавнились также, но вылетали как будто из ствола
    image = load_image("guns/assault_riffle.png")

    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.image = Gun.image
        self.orig_image = Gun.image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

    def rotate(self):
        x, y = self.rect.center

        direction = pygame.mouse.get_pos() - pygame.Vector2(x, y)
        radius, angle = direction.as_polar()
        if player.orientation == "right":
            self.image = pygame.transform.rotate(self.orig_image, -angle)
        else:
            self.image = pygame.transform.flip(pygame.transform.rotate(self.orig_image, -angle), True, True)
        self.rect = self.image.get_rect(center=self.rect.center)

    def flip(self):
        if player.orientation == "right":
            self.orig_image = Gun.image
        else:
            self.orig_image = pygame.transform.flip(Gun.image, True, False)

    def set_pos(self):
        if player.orientation == "right":
            self.rect.centerx = player.rect.right
            self.rect.centery = player.rect.centery + 10
        else:
            self.rect.centerx = player.rect.left - 10
            self.rect.centery = player.rect.centery + 10

    def update(self):
        self.flip()
        self.rotate()
        self.set_pos()


# TODO: Убрать класс Border
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


class Crosshair(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = load_image("crosshair/crosshair.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = pygame.mouse.get_pos()[0]
        self.rect.centery = pygame.mouse.get_pos()[1]

    def update(self):
        self.rect.centerx, self.rect.centery = pygame.mouse.get_pos()


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


class AllSpritesGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def draw(self, surface):
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            surface.blit(sprite.image, sprite.rect.topleft)


def spawn_enemies(count):
    for i in range(count):
        enemy_x = random.randint(10, width - Enemy.stand_image_right.get_rect()[2] - 10)
        enemy_y = random.randint(10, height - Enemy.stand_image_right.get_rect()[3] - 10)
        enemy = Enemy(enemy_x, enemy_y, 3, [enemies_sprites, all_sprites])
        while pygame.sprite.spritecollideany(enemy, player_sprite):
            enemy.kill()
            enemy_x = random.randint(10, width - Enemy.stand_image_right.get_rect()[2] - 10)
            enemy_y = random.randint(10, height - Enemy.stand_image_right.get_rect()[3] - 10)
            enemy = Enemy(enemy_x, enemy_y, 3, [enemies_sprites, all_sprites])


if __name__ == '__main__':
    fps = 30
    # TODO: Сделать скорость передвижение не зависящую от fps

    pygame.mouse.set_visible(False)

    create_menu()

    game_stage = "game"

    # TODO: добавить сцены в игру
    # TODO: Добавить файл с конфигом?

    all_sprites = AllSpritesGroup()
    borders_sprites = pygame.sprite.Group()
    player_sprite = pygame.sprite.Group()
    bullet_sprites = pygame.sprite.Group()
    enemies_sprites = pygame.sprite.Group()
    crosshair_sprite = pygame.sprite.Group()
    gun_sprites = pygame.sprite.Group()

    level_sprites = pygame.sprite.Group()
    wall_sprites = pygame.sprite.Group()

    # create Camera
    camera = Camera()

    level = Level("map.tmx")

    # create Crosshair
    Crosshair(crosshair_sprite)

    # create Player
    player = Player(width // 2, height // 2, [player_sprite, all_sprites])
    Gun(player.rect.centerx, player.rect.centery - 20, [gun_sprites])

    # create Borders
    # Border("left", [all_sprites, borders_sprites])
    # Border("right", [all_sprites, borders_sprites])
    # Border("up", [all_sprites, borders_sprites])
    # Border("down", [all_sprites, borders_sprites])

    spawn_enemies(5)

    running = True
    while running:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                pass
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Shooting
                if event.button == 1:
                    player.shoot(event.pos[0], event.pos[1])

        # изменяем ракурс камеры
        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)

        for sprite in level_sprites:
            camera.apply(sprite)

        # for sprite in gun_sprites:
        #     camera.apply(sprite)

        screen.fill(pygame.Color("black"))

        level_sprites.draw(screen)

        all_sprites.update()
        all_sprites.draw(screen)

        gun_sprites.update()
        gun_sprites.draw(screen)

        crosshair_sprite.update()
        crosshair_sprite.draw(screen)

        pygame.display.flip()

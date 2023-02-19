import random

import math

import pygame
import pytmx

from menu import menu_scene, get_size_from_json, get_sfx_volume_from_json, load_image, get_difficulty_from_json, FONT
from loading import loading_scene
from game_over import game_over_scene
from win import win_scene


pygame.mixer.pre_init()
pygame.init()
size = width, height = get_size_from_json()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Roguelike-game")
pygame.display.set_icon(load_image("icon/icon.png"))
virtual_screen = pygame.surface.Surface((1920, 1080))
clock = pygame.time.Clock()


class Level:
    def __init__(self, filename):
        self.map = pytmx.load_pygame(f"data/map/{filename}")
        self.width = self.map.width
        self.height = self.map.height
        self.tile_size = self.map.tilewidth
        self.map_left_up_border = None
        self.map_right_down_border = None
        self.create_tile_sprites()

    def create_tile_sprites(self):
        # пришлось расположить тайлы, которые отвечают за стенки на краю карты
        walls_gids = [self.map.get_tile_gid(x, 999, 0) for x in range(10)]

        pos_x, pos_y = None, None

        for y in range(self.height - 1):
            for x in range(self.width):

                image = self.map.get_tile_image(x, y, 0)

                if image:
                    pos_x = x * self.tile_size
                    pos_y = y * self.tile_size

                    gid = self.map.get_tile_gid(x, y, 0)
                    if gid in walls_gids:
                        Tile(image, pos_x, pos_y, [level_sprites, wall_sprites])
                    else:
                        Tile(image, pos_x, pos_y, level_sprites)

                    if not self.map_left_up_border:
                        self.map_left_up_border = Tile(pygame.Surface((self.tile_size, self.tile_size)),
                                                       pos_x, pos_y, level_sprites)
        if pos_x:
            self.map_right_down_border = Tile(pygame.Surface((self.tile_size, self.tile_size)),
                                              pos_x, pos_y, level_sprites)


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

    heart_image = load_image("interface/heart.png")
    half_heart_image = load_image("interface/half_heart.png")
    no_heart_image = load_image("interface/no_heart.png")

    def __init__(self, x, y, *group):
        super().__init__(*group)
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
        self.max_hp = 8
        self.current_hp = 8
        self.invincibility_frames = 15
        self.current_invincibility_frame = 0
        self.ready_to_take_damage = True

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
            bullet_x = player_gun.rect.centerx
            bullet_y = player_gun.rect.centery
            Bullet(bullet_x, bullet_y, mouse_x, mouse_y, [bullet_sprites, all_sprites])
            self.ready_to_shoot = False
            gun_shot_snd.play()

    def draw_hp(self):
        heart_x = 10
        heart_y = 10
        heart_image_width = Player.heart_image.get_width()
        full_hearts = self.current_hp // 2
        max_hearts = self.max_hp // 2
        half_heart = (self.max_hp - self.current_hp) % 2
        no_hearts = max_hearts - half_heart - full_hearts
        for i in range(max_hearts):
            virtual_screen.blit(Player.no_heart_image, (heart_x, heart_y))
            heart_x += 10 + heart_image_width
        if self.current_hp > 0:
            heart_x = 10
            if full_hearts:
                for i in range(full_hearts):
                    virtual_screen.blit(Player.heart_image, (heart_x, heart_y))
                    heart_x += 10 + heart_image_width
            if half_heart:
                virtual_screen.blit(Player.half_heart_image, (heart_x, heart_y))
            if no_hearts:
                for i in range(no_hearts):
                    virtual_screen.blit(Player.no_heart_image, (heart_x, heart_y))
                    heart_x += 10 + heart_image_width

    def get_damage(self):
        if self.ready_to_take_damage:
            self.current_hp -= 1
            if self.current_hp < 0:
                self.current_hp = 0
            self.ready_to_take_damage = False
            getting_damage_snd.play()

    def get_heal(self):
        self.current_hp += 1
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp

    def update(self, *args):
        if self.current_hp == 0:
            global running, game_over
            running = False
            game_over = True
        self.input()
        self.draw_hp()
        if not self.ready_to_shoot:
            self.time_gone_from_shot += 1
            if self.time_gone_from_shot == self.fire_cooldown:
                self.ready_to_shoot = True
                self.time_gone_from_shot = 0
        if not self.ready_to_take_damage:
            self.current_invincibility_frame += 1
            if self.current_invincibility_frame == self.invincibility_frames:
                self.current_invincibility_frame = 0
                self.ready_to_take_damage = True


class Enemy(pygame.sprite.Sprite):
    stand_image_right = load_image("enemy/enemy-stand_R.png")
    stand_image_left = pygame.transform.flip(load_image("enemy/enemy-stand_R.png"), True, False)
    right_images = [load_image("enemy/enemy-walk_1_R.png"),
                    load_image("enemy/enemy-walk_2_R.png"),
                    load_image("enemy/enemy-walk_3_R.png"),
                    load_image("enemy/enemy-walk_4_R.png")]
    left_images = [pygame.transform.flip(elem, True, False) for elem in right_images]

    vision_range = 500

    def __init__(self, x, y, health, drop_chance, *group):
        super().__init__(*group)
        self.image = Enemy.stand_image_right
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vision_range = Enemy.vision_range
        self.speed = 5
        self.phase = 0
        self.orientation = "right"
        self.get_orientation()
        self.hp_drop_chance = drop_chance
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

        self.rect = self.rect.move(x_movement, 0)
        if pygame.sprite.spritecollideany(self, wall_sprites):
            self.rect = self.rect.move(-x_movement, 0)

        self.rect = self.rect.move(0, y_movement)
        if pygame.sprite.spritecollideany(self, wall_sprites):
            self.rect = self.rect.move(0, -y_movement)

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

    def check_hit_player(self):
        if pygame.sprite.spritecollideany(self, player_sprite):
            player.get_damage()

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
            global kills
            if random.choice(self.hp_drop_chance):
                Heart(self.rect.centerx, self.rect.centery, [all_sprites])
            self.kill()
            kills += 1
            enemy_death_snd.play()
        if pygame.sprite.spritecollideany(self, bullet_sprites):
            self.health -= 1
        self.check_hit_player()


class Bullet(pygame.sprite.Sprite):
    image = load_image("bullet/green_bullet.png")

    def __init__(self, x, y, mouse_x, mouse_y, *group):
        super().__init__(*group)
        self.image = Bullet.image
        self.image = pygame.transform.scale(self.image, (11, 21))
        self.image = pygame.transform.rotate(self.image, -90)

        self.speed = 20

        # Calculate the angle to rotate image and move
        x_diff = mouse_x - x
        y_diff = mouse_y - y
        angle = math.atan2(y_diff, x_diff)
        self.image = pygame.transform.rotate(self.image, -math.degrees(angle))

        self.x_movement = int(math.cos(angle) * self.speed)
        self.y_movement = int(math.sin(angle) * self.speed)

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.spawn_x = x
        self.spawn_y = y
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y

    def move(self):
        self.rect = self.rect.move(self.x_movement, self.y_movement)

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, wall_sprites):
            self.kill()
        if pygame.sprite.spritecollideany(self, enemies_sprites):
            self.kill()
        self.move()


class Heart(pygame.sprite.Sprite):
    image = load_image("interface/half_heart.png")
    image = pygame.transform.scale(image, (19, 15))

    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.image = Heart.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, player_sprite):
            if player.current_hp != player.max_hp:
                player.get_heal()
                self.kill()


class Gun(pygame.sprite.Sprite):
    image = load_image("guns/player_gun.png", (255, 255, 255))
    image = pygame.transform.flip(image, True, False)

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
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if player.orientation == "right":
            if mouse_x >= self.rect.centerx:
                self.orig_image = Gun.image
            else:
                self.orig_image = pygame.transform.flip(Gun.image, False, True)
        else:
            if mouse_x >= self.rect.centerx:
                self.orig_image = pygame.transform.flip(Gun.image, True, True)
            else:
                self.orig_image = pygame.transform.flip(Gun.image, True, False)

    def set_pos(self):
        if player.orientation == "right":
            self.rect.centerx = player.rect.centerx - 15
            self.rect.centery = player.rect.centery + 15
        else:
            self.rect.centerx = player.rect.centerx + 15
            self.rect.centery = player.rect.centery + 15

    def update(self):
        self.flip()
        self.rotate()
        self.set_pos()


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


def get_enemy_coords():
    left_x_border, up_y_border = level.map_left_up_border.rect[:2]
    right_x_border, down_y_border = level.map_right_down_border.rect[:2]
    return left_x_border, up_y_border, right_x_border, down_y_border


def spawn_enemies(count, hp_drop_chance):
    for i in range(count):
        border_min_x, border_min_y, border_max_x, border_max_y = get_enemy_coords()

        player_x, player_y = player.rect[:2]

        min_enemy_x = player_x - Enemy.vision_range
        max_enemy_x = player_x + player.image.get_width() + Enemy.vision_range

        min_enemy_y = player_y - Enemy.vision_range
        max_enemy_y = player_y + player.image.get_height() + Enemy.vision_range

        enemy_x = random.randint(min_enemy_x, max_enemy_x)
        enemy_y = random.randint(min_enemy_y, max_enemy_y)

        enemy = Enemy(enemy_x, enemy_y, 3, hp_drop_chance, [enemies_sprites, all_sprites])
        while pygame.sprite.spritecollideany(enemy, player_sprite)\
                or pygame.sprite.spritecollideany(enemy, wall_sprites)\
                or not border_min_x < enemy_x < border_max_x\
                or not border_min_y < enemy_y < border_max_y:
            enemy.kill()
            enemy_x = random.randint(min_enemy_x, max_enemy_x)
            enemy_y = random.randint(min_enemy_y, max_enemy_y)
            enemy = Enemy(enemy_x, enemy_y, 3, hp_drop_chance, [enemies_sprites, all_sprites])


def draw_kills(surface, real_screen):
    width, height = real_screen.get_size()
    text = FONT.render(f"Kills: {kills}", True, (255, 255, 255))
    font_width, font_height = text.get_size()
    surface.blit(text, (width - font_width - 10, font_height - 30))


def time_bar(surface, time):
    global current_time

    if current_time > 0:
        TIME = time
        loading_bg_image = pygame.transform.scale(load_image("loading/loading_bar_background.png"), (width // 2, 60))
        loading_bar_image = load_image("loading/loading_bar.png")

        loading_bg_pos = 40
        loading_bar_height = 55

        loading_bg_rect = loading_bg_image.get_rect(center=(width // 2, loading_bg_pos))
        loading_bar_rect = loading_bar_image.get_rect(midleft=(width // 2 - loading_bg_image.get_width() // 2 + 15,
                                                               loading_bg_pos + loading_bar_height))

        i = current_time

        loading_bar_width = i / TIME * (loading_bg_image.get_width() - 25)
        loading_bar_image_resized = pygame.transform.scale(loading_bar_image,
                                                           (int(loading_bar_width), loading_bar_height))

        surface.blit(loading_bg_image, loading_bg_rect)
        surface.blit(loading_bar_image_resized, loading_bar_rect)

        current_time -= 1
        if current_time == 0:
            global running, win
            running = False
            win = True


if __name__ == '__main__':
    fps = 30

    kills = 0

    pygame.mouse.set_visible(False)

    pygame.mixer.music.load("data/sounds/game_soundtrack.mp3")
    pygame.mixer.music.play(-1)

    loading_scene(virtual_screen, screen)
    menu_scene(virtual_screen, screen)

    sfx_volume = get_sfx_volume_from_json() / 100

    difficulty = get_difficulty_from_json()

    endless_flag = False

    if difficulty == "Easy":
        time = 60
        interval = 30
        enemies_count_spawn = 5
        hp_drop_chance = [0, 0, 0, 1]
    elif difficulty == "Medium":
        time = 180
        interval = 20
        enemies_count_spawn = 7
        hp_drop_chance = [0, 0, 0, 0, 1]
    elif difficulty == "Hard":
        time = 300
        interval = 15
        enemies_count_spawn = 9
        hp_drop_chance = [0, 0, 0, 0, 0, 1]
    elif difficulty == "Insane":
        time = -1
        interval = 15
        enemies_count_spawn = 11
        endless_flag = True
        hp_drop_chance = [0, 0, 0, 0, 0, 0, 0, 0, 1]
    else:
        time = -1
        interval = 25
        enemies_count_spawn = 6
        endless_flag = True
        hp_drop_chance = [0, 0, 0, 1]

    TIME = time * fps

    enemy_spawn_timer = interval * fps
    current_spawn_timer = 0
    ready_to_spawn = True

    gun_shot_snd = pygame.mixer.Sound("data/sounds/gun_shot.mp3")
    getting_damage_snd = pygame.mixer.Sound("data/sounds/getting_damage.wav")
    enemy_death_snd = pygame.mixer.Sound("data/sounds/enemy_death.mp3")

    gun_shot_snd.set_volume(sfx_volume)
    getting_damage_snd.set_volume(sfx_volume)
    enemy_death_snd.set_volume(sfx_volume)

    all_sprites = AllSpritesGroup()
    borders_sprites = pygame.sprite.Group()
    player_sprite = pygame.sprite.Group()
    bullet_sprites = pygame.sprite.Group()
    enemies_sprites = pygame.sprite.Group()
    crosshair_sprite = pygame.sprite.Group()
    gun_sprites = pygame.sprite.Group()

    level_sprites = pygame.sprite.Group()
    wall_sprites = pygame.sprite.Group()

    interface_sprites = pygame.sprite.Group()

    current_time = TIME

    # create Camera
    camera = Camera()

    level = Level("arena_map.tmx")

    # create Crosshair
    Crosshair(crosshair_sprite)

    # create Player
    player = Player(width // 2, height // 2, [player_sprite, all_sprites])
    player_gun = Gun(player.rect.centerx, player.rect.centery - 20, [gun_sprites])

    game_over = False
    win = False

    running = True
    while running:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
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

        if ready_to_spawn:
            spawn_enemies(enemies_count_spawn, hp_drop_chance)
            ready_to_spawn = False
        else:
            current_spawn_timer += 1
            if current_spawn_timer == enemy_spawn_timer:
                ready_to_spawn = True

        virtual_screen.fill(pygame.Color("black"))

        level_sprites.draw(virtual_screen)

        all_sprites.update()
        all_sprites.draw(virtual_screen)

        gun_sprites.update()
        gun_sprites.draw(virtual_screen)

        if not endless_flag:
            time_bar(virtual_screen, TIME)

        draw_kills(virtual_screen, screen)

        crosshair_sprite.update()
        crosshair_sprite.draw(virtual_screen)

        if screen.get_size() == (1920, 1200):
            virtual_screen = pygame.transform.scale(virtual_screen, (1920, 1200))
        screen.blit(virtual_screen, (0, 0))

        pygame.display.flip()

    if win:
        win_scene(virtual_screen, screen)
    elif game_over:
        game_over_scene(virtual_screen, screen)

    pygame.quit()

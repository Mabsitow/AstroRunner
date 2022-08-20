import pygame
import math
from sys import exit
from random import randint, choice

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 384
FPS = 60

# Init PyGame
pygame.init()

# Set the window title
pygame.display.set_caption('AstroRunner')

# Create the window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set the game clock
clock = pygame.time.Clock()

# Set the mixer
pygame.mixer.pre_init(44100, -16, 2, 512)

# Define some global variables
game_active = False
start_time = 0
score = 0
level = 0
enemy_spawn_time = 2000
background_scroll = 1
player_speed = 0.1
enemy_speed = 0.1
player_hitted = 0
player_invulnerable = 0

class Background(pygame.sprite.Sprite):
    def __init__(self, background):
        super().__init__()

        if background == 'one':
            self.texture = pygame.image.load('assets/textures/backgrounds/background_1.png').convert_alpha()
            self.texture_width = self.texture.get_width()
            self.tiles = math.ceil(SCREEN_WIDTH / self.texture_width) + 1
        elif background == 'two':
            self.texture = pygame.image.load('assets/textures/backgrounds/background_2.png').convert_alpha()
            self.texture_width = self.texture.get_width()
            self.tiles = math.ceil(SCREEN_WIDTH / self.texture_width) + 1
        elif background == 'three':
            self.texture = pygame.image.load('assets/textures/backgrounds/background_3.png').convert_alpha()
            self.texture_width = self.texture.get_width()
            self.tiles = math.ceil(SCREEN_WIDTH / self.texture_width) + 1

        self.scroll = 0
        self.image = self.texture
        self.rect = self.image.get_rect()
        
    def update(self):
        self.animation_state()

    def animation_state(self):
        for i in range(0, self.tiles):
            screen.blit(self.texture, (i * self.texture_width + self.scroll, 0))
            self.rect.x = i * self.texture_width + self.scroll

        self.scroll -= background_scroll
        if abs(self.scroll) > self.texture_width: self.scroll = 0

class Floor(pygame.sprite.Sprite):
    def __init__(self, floor):
        super().__init__()

        if floor == 'one':
            texture = pygame.image.load('assets/textures/backgrounds/floor_1.png').convert_alpha()
        elif floor == 'two':
            texture = pygame.image.load('assets/textures/backgrounds/floor_2.png').convert_alpha()
        elif floor == 'three':
            texture = pygame.image.load('assets/textures/backgrounds/floor_3.png').convert_alpha()

        self.image = texture
        self.rect = self.image.get_rect(topleft = (0, 279))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        texture_walking_1 = pygame.image.load('assets/textures/player/player_walking_1.png').convert_alpha()
        texture_walking_2 = pygame.image.load('assets/textures/player/player_walking_2.png').convert_alpha()
        self.player_walk = [texture_walking_1, texture_walking_2]
        texture_damaged_1 = pygame.image.load('assets/textures/player/texture_damaged_1.png').convert_alpha()
        texture_damaged_2 = pygame.image.load('assets/textures/player/texture_damaged_2.png').convert_alpha()
        self.player_damaged = [texture_walking_1, texture_damaged_1, texture_walking_2, texture_damaged_2]
        self.player_index = 0
        self.player_jump = pygame.image.load('assets/textures/player/player_jump.png').convert_alpha()
        self.jump_damaged = pygame.image.load('assets/textures/player/damaged_jump.png').convert_alpha()
        self.jump_damaged = [self.player_jump, self.jump_damaged]

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(bottomleft = (40, 279))
        self.gravity = 0
        self.jump_sound = pygame.mixer.Sound('assets/sounds/jump.wav')
        self.jump_sound.set_volume(0.1)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.rect.bottom >= 279:
            self.gravity = -20
            self.jump_sound.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 279:
            self.rect.bottom = 279

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()

    def animation_state(self):
        global player_invulnerable

        if self.rect.bottom < 279:
            if player_invulnerable <= 0:
                self.image = self.player_jump
            else:
                self.player_index += 0.3
                if self.player_index >= len(self.jump_damaged): self.player_index = 0
                self.image = self.jump_damaged[int(self.player_index)]
        else:
            if player_invulnerable <= 0:
                self.player_index += player_speed
                if self.player_index >= len(self.player_walk): self.player_index = 0
                self.image = self.player_walk[int(self.player_index)]
            else:
                self.player_index += 0.3
                if self.player_index >= len(self.player_damaged): self.player_index = 0
                self.image = self.player_damaged[int(self.player_index)]

class Enemy(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()

        if type == 'slime':
            slime_1 = pygame.image.load('assets/textures/enemies/slime/slime_1.png').convert_alpha()
            slime_2 = pygame.image.load('assets/textures/enemies/slime/slime_2.png').convert_alpha()
            self.frames = [slime_1, slime_2]
            x_pos = randint(1024, 1512)
            y_pos = 279
        elif type == 'snail':
            snail_1 = pygame.image.load('assets/textures/enemies/snail/snail_1.png').convert_alpha()
            snail_2 = pygame.image.load('assets/textures/enemies/snail/snail_2.png').convert_alpha()
            self.frames = [snail_1, snail_2]
            x_pos = randint(1024, 1512)
            y_pos = 279
        elif type == 'fly':
            fly_1 = pygame.image.load('assets/textures/enemies/fly/fly_1.png').convert_alpha()
            fly_2 = pygame.image.load('assets/textures/enemies/fly/fly_2.png').convert_alpha()
            self.frames = [fly_1, fly_2]
            x_pos = randint(1024, 1512)
            y_pos = randint(80, 200)

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(bottomleft = (x_pos, y_pos))

    def animation_state(self):
        self.animation_index += enemy_speed
        if self.animation_index >= len(self.frames): self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        self.rect.x -= 6
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()

class Lifes(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        life_3 = pygame.image.load('assets/textures/objects/life_3.png').convert_alpha()
        life_2 = pygame.image.load('assets/textures/objects/life_2.png').convert_alpha()
        life_1 = pygame.image.load('assets/textures/objects/life_1.png').convert_alpha()
        self.frames = [life_3, life_2, life_1]
        self.lifes_index = 0
        self.image = self.frames[self.lifes_index]
        image_width = int(life_3.get_width())
        self.rect = self.image.get_rect(topleft = (1024 - image_width - 20, 10))

    def update(self):
        self.hitted()

    def hitted(self):
        global player_hitted

        if player_hitted == 1:
            self.lifes_index = 1
        elif player_hitted == 2:
            self.lifes_index = 2
        else:
            self.lifes_index = 0

        self.image = self.frames[self.lifes_index]

hit_sound = pygame.mixer.Sound('assets/sounds/hit.wav')
hit_sound.set_volume(1)

# Functions
def display_score():
    current_time = int(pygame.time.get_ticks() / 1000) - start_time
    score = pygame.font.Font(Score.font_type, Score.size)
    score_texture = score.render(f'Score: {current_time}', False, 'White' if level > 1 else 'Black')
    score_rectangle = score_texture.get_rect(center = (512, 20))
    screen.blit(score_texture, score_rectangle)

    return current_time

def display_text(text, position_y, color, position_x = 512):
    score = pygame.font.Font(Score.font_type, Score.size)
    score_texture = score.render(f'{text}', False, color)
    score_rectangle = score_texture.get_rect(center = (position_x, position_y))
    screen.blit(score_texture, score_rectangle)

def collision_sprite():
    global player_hitted, player_invulnerable, hit_sound

    if pygame.sprite.spritecollide(player.sprite, enemy, False):
        while player_invulnerable <= 0:
            player_hitted += 1
            hit_sound.play()

            if player_hitted > 0:
                if player_hitted == 3:
                    enemy.empty()
                    return False
                else:
                    player_invulnerable = 90

        return True
    else:
        return True

music_run = 0

def ending_music():
    pygame.mixer.music.pause()
    pygame.mixer.music.unload()
    pygame.mixer.music.load('assets/music/end.wav')
    pygame.mixer.music.play()

# Set starting music
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.load('assets/music/title.wav')
pygame.mixer.music.play(-1)

# Intro & Outro
player_standing_texture = pygame.image.load('assets/textures/player/player_over.png').convert_alpha()
player_standing_rectangle = player_standing_texture.get_rect(center = (512, 160))

# Group to contain a single sprite
player = pygame.sprite.GroupSingle()
player.add(Player())

lifes = pygame.sprite.GroupSingle()
lifes.add(Lifes())

background = pygame.sprite.GroupSingle()
floor = pygame.sprite.GroupSingle()

floor.add(Floor('one'))
background.add(Background('one'))

# Group to contain multiple sprites
enemy = pygame.sprite.Group()

class Score:
    size = 30
    font_type = 'assets/font/Silkscreen-Regular.ttf'

# Timers
enemies_timer = pygame.USEREVENT + 1
pygame.time.set_timer(enemies_timer, enemy_spawn_time)

# Running loop
while True:
    # Events
    for event in pygame.event.get():
        # If we press the X to close the window
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # If the state of the game is active
        if game_active:
            # If the enemy timer is running
            if event.type == enemies_timer:
                enemy.add(Enemy(choice(['snail', 'snail', 'snail', 'slime', 'slime', 'fly'])))
        else:
            # Reset the game to start again
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                game_active = True
                start_time = int(pygame.time.get_ticks() / 1000)
                player_hitted = 0

                if music_run == 1:
                    music_run = 0

                if score <= 20:
                    level = 0
                    floor.add(Floor('one'))
                    background.add(Background('one'))
                    background_scroll = 1
                    player_speed = 0.1
                    enemy_speed = 0.1
                    pygame.mixer.music.load('assets/music/level_one.wav')
                    pygame.mixer.music.play(-1)
                elif score > 20 and score <= 50:
                    level = 1
                    floor.add(Floor('two'))
                    background.add(Background('two'))
                    enemy_spawn_time = 1600
                    background_scroll = 3
                    player_speed = 0.17
                    enemy_speed = 0.13
                    pygame.mixer.music.load('assets/music/level_two.wav')
                    pygame.mixer.music.play(-1)
                elif score > 50:
                    level = 2
                    floor.add(Floor('three'))
                    background.add(Background('three'))
                    enemy_spawn_time = 1200
                    background_scroll = 5
                    player_speed = 0.3
                    enemy_speed = 0.17
                    pygame.mixer.music.load('assets/music/level_three.wav')
                    pygame.mixer.music.play(-1)

    # If our game is running
    if game_active:
        # Background
        background.update()

        # Floor texture
        floor.draw(screen)

        # Display score
        score = display_score()

        # Player
        player.draw(screen) # draw sprites
        player.update() # update sprites

        # Lifes
        lifes.draw(screen)
        lifes.update()

        # Invulnerability
        if player_invulnerable > 0:
            player_invulnerable -= 1
        elif player_invulnerable <= 0: 
            player_invulnerable = 0

        # Enemies
        enemy.draw(screen) # draw enemies
        enemy.update() # update enemies

        # Collision
        game_active = collision_sprite()
    else:
        screen.fill('Black')
        screen.blit(player_standing_texture, player_standing_rectangle)

        if score > 0:
            # Game over screen
            if music_run == 0:
                ending_music()
                music_run = 1

            display_text('game over', 20, 'White')
            display_text(f'your score: {score}', 75, 'White')
            display_text('press arrow up to restart', 260, 'White')
        else:
            # Start screen
            display_text('AstroRunner', 80, 'White')
            display_text('press arrow up to start', 260, 'White')

    pygame.display.update()
    clock.tick(FPS)
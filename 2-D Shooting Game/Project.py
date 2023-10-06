import pygame
import os
import random
import csv
import time

pygame.init()



SCREEN_WIDTH = 1000
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Gally\'s Gulag')

#FPS Lock
clock = pygame.time.Clock()
FPS = 60


#Game Variables
GRAVITY = 0.75
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21

#Player action variables
move_left = False
move_right = False
shoot = False

# Loading Images

#Background image
background_img = pygame.image.load('img/cityskyline.png').convert_alpha()
#Pieces of the map
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
# Bullet
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()

#Color Variables
BG = (178, 149, 255)
GREEN = (0, 255, 0)

def draw_bg():
    screen.fill(BG)
    screen.blit(background_img, (-300,-200))

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = False
        self.update_time = pygame.time.get_ticks()
        
        # Load all player animation images
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            #Reset list of images
            temp_list = []
            #counting number of files in folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), img.get_height() * scale))
                temp_list.append(img) 
            self.animation_list.append(temp_list)
 
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # Shooting Cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, move_left, move_right):
        #Reset Variables
        dx = 0
        dy = 0


        # Assign variables for left and right
        if move_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if move_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True
        
        # Appy Gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # Collision with tiles
        for tile in world.obstacle_list:
            #check for collision in x value
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            #check for collision in y value
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #make sure user is jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top 
                #check if user is falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom 


        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0


        #update player position
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
            if self.shoot_cooldown == 0:
                self.shoot_cooldown = 20
                bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
                bullet_group.add(bullet)


    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)#0: idle
                self.idling = True
                self.idling_counter = 50
			#check if the ai in near the player
            if self.vision.colliderect(player.rect):
                #stop running and face the player
                self.update_action(0)#0: idle
                #shoot
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)#1: run
                    self.move_counter += 1
                    #update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        

    def update_animation(self):
        # Timer
        ANIMATION_COOLDOWN = 100
        # update image
        self.image = self.animation_list[self.action][self.frame_index]
        # check afk time
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if animation is over, reset index to loop
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        #check if new action is different from previous one
        if new_action != self.action:
            self.action = new_action
            #ensure animation starts over when I switch action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        #iterate through each value in csv file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        pass
                    elif tile >= 11 and tile <= 14:
                        pass
                    elif tile == 15:
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.75, 5)
                    elif tile == 16:
                        enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.75, 3)
                        enemy_group.add(enemy)
        return

    def draw(self):
        for tile in self.obstacle_list:
            screen.blit(tile[0], tile[1])


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
    
    def update(self):
        #moving the bullet
        self.rect.x += (self.direction * self.speed)
        #check if bullet is off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        #check for collision with ground
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #check bullet collision with player
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    print(enemy.health)
                    self.kill()


#create sprite groups
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()


player = Soldier('player', 50, 600, 1.75, 5)



enemy = Soldier('enemy', 700, 600, 1.75, 2)
enemy2 = Soldier('enemy', 800, 600, 1.75, 2)
enemy_group.add(enemy)
enemy_group.add(enemy2)

#Load in the level
level_data = []
for row in range(ROWS):
    r = [-1] * COLS
    level_data.append(r)
with open('level1_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            level_data[x][y] = int(tile)
world = World()
world.process_data(level_data)



running = True
while running:


    #update background
    draw_bg()
    #draw the level
    world.draw()

    clock.tick(FPS)

    player.update()
    player.draw()

    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()

    #update and draw groups
    bullet_group.update() 
    bullet_group.draw(screen)
    
    #update player action
    if player.alive:
        if shoot:
            player.shoot()
        if player.in_air:
            player.update_action(2) # Jump
        elif move_left or move_right:
            player.update_action(1) # Running
        else:
            player.update_action(0) # Idle
        player.move(move_left, move_right)



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #Player Movement
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                move_left = True
            if event.key == pygame.K_d:
                move_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                running = False

        #Player Stop Movement
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                move_left = False
            if event.key == pygame.K_d:
                move_right = False
            if event.key == pygame.K_SPACE:
                shoot = False    



    pygame.display.update()

pygame.quit()
import os, random, pygame, time

pygame.init()
pygame.font.init()

# Font and Colors
main_font = pygame.font.SysFont('comicsans', 40)
WHITE = (240, 240, 240)
BLACK = (20, 20, 20)

# Getting image directory
asset_dir = os.path.join(os.getcwd(), 'assets')

# Setting up window dimensions
WIDTH, HEIGHT = 500, 650
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Invaders')



# Ships
RED_SPACE_SHIP = pygame.image.load(os.path.join(asset_dir, 'pixel_ship_red_small.png'))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join(asset_dir, 'pixel_ship_green_small.png'))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join(asset_dir, 'pixel_ship_blue_small.png'))

# Player Ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join(asset_dir, 'pixel_ship_yellow.png'))

# Lazers
RED_LASER = pygame.image.load(os.path.join(asset_dir, 'pixel_laser_red.png'))
BLUE_LASER = pygame.image.load(os.path.join(asset_dir, 'pixel_laser_blue.png'))
GREEN_LASER = pygame.image.load(os.path.join(asset_dir, 'pixel_laser_green.png'))
YELLOW_LASER = pygame.image.load(os.path.join(asset_dir, 'pixel_laser_yellow.png'))

# Background
BG = pygame.image.load(os.path.join(asset_dir, 'background-black.png'))
BG = pygame.transform.scale(BG, (WIDTH, HEIGHT))


def collide(obj1, obj2):
    offset_X = obj2.x - obj1.x
    offset_Y = obj2.y - obj1.y
    
    return obj1.mask.overlap(obj2.mask, (offset_X, offset_Y)) != None



class Ship(object):
    
    COOLDOWN = 30
    
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = list()
        self.cool_down_counter = 0


    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)


    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
    
        
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
        
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            #print(f'Player laser: {len(self.lasers)}')
            self.lasers.append(laser)
            self.cool_down_counter = 1
        
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    
    COOLDOWN = 30
    
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)


    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (240, 50, 50), (self.x, self.y + self.get_height() + 5,
                                                 self.get_width(), 5))
        pygame.draw.rect(window, (50, 240, 50), (self.x, self.y + self.get_height() + 5, 
                                                 self.get_width() * (self.health / self.max_health), 5))


class Enemy(Ship):
    
    COLOR_MAP = {'red': (RED_SPACE_SHIP, RED_LASER),
                 'green': (GREEN_SPACE_SHIP, GREEN_LASER),
                 'blue': (BLUE_SPACE_SHIP, BLUE_LASER)}
    
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    
    def move(self, vel):
        self.y += vel


class Laser():
    
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        
    def draw(self, win):
        win.blit(self.img, (self.x, self.y))
        
    def move(self, vel):
        self.y += player_vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)
    
    def collision(self, obj):
        return collide(self, obj)
    

def main():
    
    FPS = 60 
    clock = pygame.time.Clock()
    run = True
    lives = 5
    level = 0
    player_vel = 5
    player_health = 100
    lost = False
    lost_count = 0
    laser_vel = 5
    
    # Enemy Stats
    enemies = list()
    level = 0
    wave_lenght = 5
    enemy_vel = 1
    
    player = Player(250, 300)
    
    def redraw_window():
        win.blit(BG, (0, 0))
        level_label = main_font.render(f'Level: {level}', 1, WHITE)
        lives_label = main_font.render(f'Lives: {lives}', 1, WHITE)
        
        win.blit(level_label, (10, 10))
        win.blit(lives_label, (WIDTH - lives_label.get_width() - 10, 10))
        
        for enemy in enemies:
            enemy.draw(win)        
        
        player.draw(win)
        
        if lost:
            lost_text = main_font.render('You\'ve Lost !', 1, WHITE)
            win.blit(lost_text, ((WIDTH - lost_text.get_width()) // 2, HEIGHT // 2))
            
        
        pygame.display.update()
    
    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        redraw_window()
        
        
        if lives <= 0 or player.health <= 0:
            lost = True
            
        if lost:
            lost_count += 1
            if lost_count < FPS * 3:
                continue
            else:
                run = False
        
        
        if len(enemies) == 0:
            level += 1
            if Player.COOLDOWN > 15:
                Player.COOLDOWN -= (level - 1) * 5
            wave_lenght += 2
            
            if enemy_vel <= 3:
                enemy_vel += 1
            
            for _ in range(wave_lenght):
                enemies.append(Enemy(random.randrange(50, WIDTH - 100), 
                                     random.randrange(-1500, -100), 
                                     random.choice(['red', 'green', 'blue'])))
                
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP] and player.y - player_vel >= 0:
            player.y -= player_vel
        
        if keys[pygame.K_DOWN] and player.y + player_vel + 15 <= HEIGHT - player.get_height():
            player.y += player_vel
            
        if keys[pygame.K_RIGHT] and player.x + player_vel <= WIDTH - player.get_width():
            player.x += player_vel
            
        if keys[pygame.K_LEFT] and player.x - player_vel >= 0:
            player.x -= player_vel
            
        if keys[pygame.K_SPACE]:
            player.shoot()
            
        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            
            if random.randrange(0, 2 * FPS) == 1:
                enemy.shoot()
            
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() >= HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        
        player.move_lasers(-laser_vel, enemies)
        
    pygame.quit()

main()

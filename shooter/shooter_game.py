from pygame import *
from random import randint
from time import time as timer


score = 0  # сбито ufo
lost = 0  # пропущено ufo
goal = 15  # кол-во сбитых ufo, чтобы win
max_lost = 5  # кол-во пропущенных ufo, чтобы lose
life = 3  # кол-во очков здоровья


class GameSprite(sprite.Sprite):
    """Standard class """
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        # конструктор class
        super().__init__()
        # all sprites - this images
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        # all sprites - this прямоугольники rect
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        # draw person
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    """Class-наследник with make main person"""
    def move(self):
        """Moving person"""
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < win_width - 70:
            self.rect.x += self.speed

    def fire(self):
        """Shoot"""
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 30, 60, -15)
        bullets.add(bullet)


class Enemy(GameSprite):
    """Class-наследник with make main enemy"""
    def update(self):
        """Auto-Moving monsters"""
        self.rect.y += self.speed
        global lost
        # исчезает if go with края screen
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width-80)
            self.rect.y = 0
            lost += 1


class Asteroid(GameSprite):
    """Class-наследник with make main enemy"""
    def update(self):
        """Auto-Moving monsters"""
        self.rect.y += self.speed
        # исчезает if go with края screen
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width-80)
            self.rect.y = 0


class Bullet(GameSprite):
    """Class-наследник with make main Bullets"""
    def update(self):
        """Auto-Moving down bullets"""
        self.rect.y += self.speed
        # исчезает if go with края screen
        if self.rect.y < 0:
            self.kill()


# connect music
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

# text
font.init()
font1 = font.SysFont('fontname', 185)
font2 = font.SysFont('fontname', 56)

win = font1.render('WINNER', True, (255, 255, 255))
lose = font1.render('LOSE', True, (255, 0, 0 ))

# images
img_back = 'galaxy.jpeg'
img_rocket = 'rocket.png'
img_enemy = 'ufo2.png'
img_bullet = 'bullet.png'
img_asteroid = 'asteroid.png'

# game window
win_width = 1920
win_height = 1020
window = display.set_mode((win_width, win_height))
display.set_caption('GalaxyShoot')
# background game window
background = transform.scale(image.load(img_back), (1920, 1020))

# make sprites
rocket = Player(img_rocket, 5, win_height-100, 100, 120, 10)
# ufo
monsters = sprite.Group()
for i in range(5):
    monster = Enemy(img_enemy, randint(80, win_width-80), -40, 130, 130, randint(1, 3))
    monsters.add(monster)

# bullets
bullets = sprite.Group()

# asteroids
asteroids = sprite.Group()
for i in range(3):
    asteroid = Asteroid(img_asteroid, randint(30, win_width - 40), -40, 80, 50, randint(1, 5))
    asteroids.add(asteroid)

# game cycle
game = True
finish = False
clock = time.Clock()
FPS = 74

reload_time = False  # флаг, отвечающий за перезарядку
num_fire = 0  # счётчик выстрелов
while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        # событие нажатия кнопки на пробел - спрайт стреляет
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                # проверяем сколько сделано выстрелов и не идёт ли перезарядка
                if num_fire < 5 and reload_time == False:
                    num_fire += 1
                    fire_sound.play()
                    rocket.fire()
                if num_fire >= 5 and reload_time == False:
                    # if player does 5 выстрелов, засекаем time and ставим флаг
                    last_time = timer()
                    reload_time = True

    if not finish:
        # draw background
        window.blit(background, (0, 0))

        # write text on screen
        text = font2.render('Score: ' + str(score), 1, (255, 255, 255))
        window.blit(text, (10, 20))

        text_lose = font2.render('Skipped: ' + str(lost), 1, (255, 255, 255))
        window.blit(text_lose, (10, 60))

        # draw sprites game
        rocket.move()
        rocket.reset()

        monsters.update()
        monsters.draw(window)

        bullets.update()
        bullets.draw(window)

        asteroids.update()
        asteroids.draw(window)

        # проверка перезарядки
        if reload_time:
            now_time = timer()
            if now_time - last_time < 3:
                # if перезарядка не кончилась, выводим info о ней
                reload = font2.render('Recharge, wait...', 1, 'red')
                window.blit(reload, (850, 500))
            else:
                # if 3 sec прошло, обнуляем счётчик bullets and снимаем флаг recharge
                num_fire = 0
                reload_time = False

        # обработка столкновения bullet and monster
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            score += 1
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 130, 130, randint(1, 3))
            monsters.add(monster)

        # if rocket коснулся врага, уменьшаем очки здоровья
        if sprite.spritecollide(rocket, monsters, False) or sprite.spritecollide(rocket, asteroids, False):
            sprite.spritecollide(rocket, monsters, True)
            sprite.spritecollide(rocket, asteroids, True)
            life -= 1

        # lose - пропустили слишком много ufo, or потеряли все очки здоровья
        if lost >= max_lost or life == 0:
            # lose, ставим background and отключаем управление sprites
            finish = True
            window.blit(lose, (820, 400))

        # win - score набрано достаточно
        if score >= goal:
            finish = True
            window.blit(win, (740, 400))

        # draw text with кол-во life
        if life == 3:
            life_color = 'chartreuse'
        if life == 2:
            life_color = 'gold'
        if life == 1:
            life_color = 'firebrick'

        text_life = font1.render(str(life), 1, life_color)
        window.blit(text_life, (1800, 10))

        display.update()
    clock.tick(FPS)
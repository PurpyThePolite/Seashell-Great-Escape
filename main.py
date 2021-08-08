import os
import random
import pygame 
import sys

from pygame.constants import KEYDOWN, K_ESCAPE
from pygame import mixer 

#initialization
pygame.init()
pygame.font.init()
pygame.mixer.init()

FPS = 60
clock = pygame.time.Clock()

WIDTH, HEIGHT = 750, 800    
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Seashell Great Escape")

# Trash images
trash1 = pygame.image.load(os.path.join("images", "trash1.png"))
trash2 = pygame.image.load(os.path.join("images", "trash2.png"))
trash3 = pygame.image.load(os.path.join("images", "trash3.png"))

# Player 
clam = pygame.image.load(os.path.join("images", "clam.png"))
clam2 = pygame.image.load(os.path.join("images", "clam2.png"))
pygame.display.set_icon(clam)

# Bubbles
bubbles = pygame.image.load(os.path.join("images", "bubbles.png"))

# Backgrounds
BG = pygame.transform.scale(pygame.image.load(os.path.join("images", "background3.png")), (WIDTH, HEIGHT))
MENU = pygame.transform.scale(pygame.image.load(os.path.join("images", "menu.png")), (WIDTH, HEIGHT))

# Buttons
START = pygame.image.load(os.path.join("images", "start.png"))
CREDITS = pygame.image.load(os.path.join("images", "credits.png"))
START1 = pygame.image.load(os.path.join("images", "start1.png"))
CREDITS1 = pygame.image.load(os.path.join("images", "credits1.png"))

# 쏘는 버블 
class Bubbles:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        #나중에 충돌을 감지하기 위해 죄다 mask를 만들어주었다.. 

    def draw(self, window):
        window.blit(self.img, (self.x + 20, self.y - 80))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

#조개 
class Player:
    #너무 자주쏘지 못하게 쿨다운 변수를 설정했다. 
    COOLDOWN = 15

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.cool_down_counter = 0
        self.clam_img = clam
        self.bubbles_img = bubbles
        self.bubbles = []
        self.mask = pygame.mask.from_surface(self.clam_img)
        self.max_health = health

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            bubbles = Bubbles(self.x, self.y, self.bubbles_img)
            self.bubbles.append(bubbles)
            self.cool_down_counter = 1

    #나중에 이미지 좀 더 유연하게 쓸 수 있게 잴 수 있는 함수 넣기 
    def get_width(self):
        return self.clam_img.get_width()

    def get_height(self):
        return self.clam_img.get_height()
    
    #objs는 enemies이다. 즉 쓰레기와 버블이 충돌하면 둘 다 없어짐
    def move_bubbles(self, vel, objs):
        self.cooldown()
        for bubbles in self.bubbles:
            bubbles.move(vel)
            if bubbles.off_screen(HEIGHT):
                self.bubbles.remove(bubbles)
            else:
                for obj in objs:
                    if bubbles.collision(obj):
                        objs.remove(obj)
                        if bubbles in self.bubbles:
                            self.bubbles.remove(bubbles)

    #데미지바와 버블이 플레이어를 졸졸 쫓아다니면서 그려진다. 
    def draw(self, window):
        window.blit(self.clam_img, (self.x, self.y))
        for bubbles in self.bubbles:
            bubbles.draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.clam_img.get_height() + 10, self.clam_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.clam_img.get_height() + 10, self.clam_img.get_width() * (self.health/self.max_health), 10))

#쓰레기 
class Enemy:
    def __init__(self, x, y,trash, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.trash_img = self.TRASH_MAP[trash]
        self.mask = pygame.mask.from_surface(self.trash_img)

    TRASH_MAP = {
                "trash1": (trash1),
                "trash2": (trash2),
                "trash3": (trash3)
                }

    def draw(self, window):
        window.blit(self.trash_img, (self.x, self.y))

    def get_width(self):
        return self.trash_img.get_width()

    def get_height(self):
        return self.trash_img.get_height()

    def move(self, vel):
        self.y += vel

# 이 함수는 masks가 주어진 offset와 충돌한다면 True를 리턴하게 돼있음 
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

#게임 자체
def main():
    run = True 
    level = 0
    lives = 100
    main_font = pygame.font.Font(os.path.join("images","DungGeunMo.ttf"),40)
    win_font = pygame.font.Font(os.path.join("images","DungGeunMo.ttf"),90)
    lost_font = pygame.font.Font(os.path.join("images","DungGeunMo.ttf"),30)

    enemies = []
    wave_length = 10
    enemy_vel = 1
    
    player_vel = 6
    bubbles_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    win = False

    #지거나 이겼을때의 화면을 얼마나 길게 보여줄지 조절하는 변수
    lost_count = 0
    win_count = 0 

    def redraw_window():
        WIN.blit(BG, (0,0))

        lives_label = main_font.render(f"바다의 인내심: {lives}%", 1, (255,255,255))
        level_label = main_font.render(f"레벨: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("GAME OVER! 메인 화면으로 3초 안에 돌아갑니다..", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH - lost_label.get_width() - 15, 375))

        if win:
            win_label = win_font.render("Y O U  W O N !", 1, (255,255,255))
            WIN.blit(win_label, ((WIDTH - win_label.get_width())/2, (HEIGHT - win_label.get_height())/2))

        pygame.display.update()

    while run:
        
        clock.tick(FPS)
        redraw_window()

        #만약에 지면 lost 카운트가 올라간다. 
        #4초 이상 화면 유지가 안되고 메인 화면으로 돌아간다.
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count >= FPS * 4:
                run = False
                main_menu()
            else:
                continue

        #만약에 이기면 win 카운트가 올라간다. 
        #4초 이상 화면 유지가 안되고 이기면 나오는 화면이 뜬다.
        if level == 4:
            win = True 
            win_count += 1

        if win: 
            if win_count >= FPS*4: 
                run = False
                win_screen()
            else:
                continue
                
        #적이 더 이상 없을 때, 즉 레벨 업 
        if len(enemies) == 0:
            player.health = 100
            level += 1
            wave_length += 10
            enemy_vel += 1
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["trash2", "trash3", "trash1"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                run = False
                main_menu()

        #플레이어의 방향 조절이다. 
        #화면 밖으로 튀어나가면 안되니까 조절해놓음 
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
 
            #충돌하거나 놓치거나 
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 5
                enemies.remove(enemy)

        #처음에 변수 설정을 양수로 해놔서 음수로 해놔야 버블이 제대로 나간다
        player.move_bubbles(-bubbles_vel, enemies)

#긴 문단을 자동으로 예쁘게 화면에 맞춰 써주는 함수이다. 
def paragraphs(text, x, y, size):
    words = text.split()

    screen = WIN
    width = 700
    color = (0,0,0)
    font = pygame.font.Font(os.path.join("images","DungGeunMo.ttf"),size)

    lines = []

#내가 설정한 가로크기보다 벗어나면 다음 줄로 넘긴다. 
#또 내가 / 로 문장을 구분하면 다음 줄로 넘긴다.
    while len(words) > 0:
        line_words = []
        while len(words) > 0 :
            line_words.append(words.pop(0))
            if line_words[len(line_words)-1] == "/":
                del line_words[len(line_words)-1]
                break
            fw, fh = font.size(' '.join(line_words + words[:1]))
            if fw > width:
                break

        line = ' '.join(line_words)
        lines.append(line)

    y_offset = 0
    for line in lines:
        fw, fh = font.size(line)

        # (tx, ty)는 폰트 surface의 왼쪽 상단이다. 
        tx = x - fw / 2
        ty = y + y_offset

        font_surface = font.render(line, True, color)
        screen.blit(font_surface, (tx, ty))

        y_offset += fh

#게임 크레딧 
def credits():
    
    text = """~ C R E D I T S ~ / . / 
        브금 : / 동방프로젝트 - 폐옥 럴러바이 (편집) 
        / 동방프로젝트 - 하르트만의 요괴소녀 / . / 이미지 : / 
        대해원과 와다노하라 - 배경 (편집) / 나머지는 송가현이 그림 / . / 
        고마운 분들 : / 나의 인내심 / 나의 구글링 실력  """
    text2 = "copyrights to 심리학부 2020130404 송가현 all rights reserved. / 비영리적인 목적으로 2021 kucc 새싹 코딩대회를 위해 만들었습니다. "

    run = True
    while run:
        WIN.blit(MENU,(0,0))
        s = pygame.Surface((750, 450))
        s.set_alpha(128)
        s.fill((255,255,255))
        WIN.blit(s,(0,200))

        paragraphs(text, 375, 230, 25)
        paragraphs(text2, 280 , 600, 15)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                main_menu()

#게임 방법 
def tutorial():
    mixer.music.load(os.path.join("images", "BGM.mp3"))
    pygame.mixer.music.play(-1)
    text = """
        ~게임 방법 설명~ / . /  / 
        조작키: A, W, S, D / 
        스페이스바를 누르면 조개가 버블을 쏩니다. /
        쓰레기를 놓칠 때마다 바다의 인내심이 –5 감소합니다! /
        생명은 레벨이 올라가면 리필됩니다. / . /  / WISH YOU LUCK!  / """

    run = True
    while run:
        
        WIN.blit(BG,(0,0))
        s = pygame.Surface((750, 400))
        s.set_alpha(128)
        s.fill((255,255,255))
        WIN.blit(s,(0,200))
        paragraphs(text, 375, 230, 30)
        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                main()

#게임 이기면 나오는 화면 
def win_screen():

    text = """승리하셨습니다! / . / 조개가 지금까지 같이 해와 준 것에 대해 감사함을 표합니다. / . / 이제 조개는 지상으로 올라가서 좀 더 맑은 공기를 누릴 수 있게 되었습니다. / . /
    조개에게 행복한 미래를 빌어 주세요. / . / 조개야 안녕! """

    run = True
    while run:
        
        WIN.blit(MENU,(0,0))
        s = pygame.Surface((750, 600))
        s.set_alpha(128)
        s.fill((255,255,255))
        WIN.blit(s,(0,100))
        WIN.blit(clam2,((WIDTH - clam2.get_width())/2, 150))

        paragraphs(text, 375, 300, 30)
        paragraphs("esc 버튼을 누르면 크레딧 화면으로 넘어갑니다..", 570, 670, 15)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                credits()

#게임 시작할 때 스크린 
def main_menu():
    mixer.music.load(os.path.join("images", "MENU_BGM.mp3"))
    pygame.mixer.music.play(-1)
    title_font = pygame.font.Font(os.path.join("images","DungGeunMo.ttf"),70)
    eng_font = pygame.font.Font(os.path.join("images","fontstuck.ttf"),15)
    run = True
  
    while run:
        clock.tick(FPS)
        WIN.blit(MENU, (0,0))
        
        mx, my = pygame.mouse.get_pos()

        title_label = title_font.render("조개의 바다 대탈출", 1, (255,255,255))
        eng_label= eng_font.render("The great escape of the little seashell", 1, (255,255,255))
        WIN.blit(eng_label, ((WIDTH - eng_label.get_width())/2, 620))
        WIN.blit(title_label, ((WIDTH - title_label.get_width())/2, 650))

        start_button = pygame.Rect(180, 500, 180, 70)
        credits_button = pygame.Rect(390, 500, 180, 70)
        WIN.blit(START1, start_button)
        WIN.blit(CREDITS1, credits_button)

        text = """이미 오염물질로 가득 차버린 심해 밑바닥. / 그 곳에는 이 곳에서의 탈출을 꿈꾸는 작은 조개가 있다. / 
    조개를 도와 쓰레기들을 무찌르고 지상으로 탈출하자!"""
        paragraphs(text, 375, 115, 25)

        if start_button.collidepoint((mx,my)):
            WIN.blit(START, start_button)
        if credits_button.collidepoint((mx,my)):
            WIN.blit(CREDITS, credits_button)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                run = False
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint((mx,my)):
                    tutorial()
                if credits_button.collidepoint((mx,my)):
                    credits()
               
    pygame.quit()
    sys.exit()

main_menu()
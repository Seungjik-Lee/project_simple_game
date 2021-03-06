'''
[조건]
1. 캐릭터는 화면 아래 위치, 좌우로만 이동 가능
2. 스페이스를 누르면 무기를 쏘아 올림 (여러번 발사 가능)
3. 큰 공 1개가 나타나서 바운스
4. 무기에 닿으면 공은 작은 크기 2개로 분할, 가장 작은 크기의 공은 사라짐
5. 모든 공을 없애면 게임 종료 (성공)
6. 캐릭터는 공에 닿으면 게임 종료 (실패)
7. 시간 제한 99초 초과시 게임 종료 (실패)
8. FPS는 30으로 고정 (필요시 speed값을 조정)

[게임 이미지]
1. 배경 : 640 * 480 (가로 세로) - background.png
2. 무대 : 60 * 50 - stage.png
3. 캐릭터 : 60 * 33 - character.png
4. 무기 : 20 * 430 - weapon.png
5. 공 : 160 * 160, 80 * 80, 40 * 40, 20 * 20 - balloon1.png ~ balloon4.png
'''
import pygame
import os

pygame.init() #초기화 (반드시 필요)

#---------------------------------------화면 크기 설정
screen_width = 640 #가로 크기
screen_height = 480 #세로 크기
screen = pygame.display.set_mode((screen_width, screen_height))

#---------------------------------------화면 타이틀 설정
pygame.display.set_caption("SJ Pang") #게임 이름

#---------------------------------------FPS
clock = pygame.time.Clock()

# 1. 사용자 게임 초기화 (배경화면, 게임 이미지, 좌표, 속도, 폰트 등)
current_path = os.path.dirname(__file__) #현재 파일의 위치를 반환
image_path = os.path.join(current_path, "images") #images 폴더 위치 반환

#---------------------------------------배경이미지 불러오기
background = pygame.image.load(os.path.join(image_path, "background.png"))

#---------------------------------------스테이지 불러오기
stage = pygame.image.load(os.path.join(image_path, "stage.png"))
stage_size = stage.get_rect().size
stage_height = stage_size[1] #스테이지의 높이 위에 캐릭터를 두기 위해 사용

#---------------------------------------스프라이트(캐릭터) 불러오기
character = pygame.image.load(os.path.join(image_path, "character.png"))
character_size = character.get_rect().size #이미지의 크기를 구해옴
character_width = character_size[0] #캐릭터의 가로 크기
character_height = character_size[1] #캐릭터의 세로 크기
character_x_pos = (screen_width / 2) - (character_width / 2) #화면 가로의 절반 크기에 해당하는 곳에 위치(가로위치)
character_y_pos = screen_height - character_height- stage_height #화면 세로 크기 가장 아래에 해당하는 곳에 위치(세로위치)

#---------------------------------------이동할 좌표
character_to_x = 0

#---------------------------------------캐릭터 이동 속도
character_speed = 0.6

#---------------------------------------무기 불러오기
weapon = pygame.image.load(os.path.join(image_path, "weapon.png"))
weapon_size = weapon.get_rect().size
weapon_width = weapon_size[0]
weapons = [] #한번에 여러 발 발사 가능
weapon_speed = 10 #무기 이동 속도

#---------------------------------------공 만들기
ball_images = [
    pygame.image.load(os.path.join(image_path, "balloon1.png")), 
    pygame.image.load(os.path.join(image_path, "balloon2.png")), 
    pygame.image.load(os.path.join(image_path, "balloon3.png")), 
    pygame.image.load(os.path.join(image_path, "balloon4.png"))]

#---------------------------------------공 크기에 따른 최초 스피드
ball_speed_y = [-18, -15, -12, -9] #index 0, 1, 2, 3 에 해당하는 값

#---------------------------------------최초 발생하는 큰 공 추가
balls = []
balls.append({
    "pos_x" : 50, #공의 x좌표
    "pos_y" : 50, #공의 y좌표
    "img_idx" : 0, #공의 이미지 인덱스
    "to_x" : 3, #공의 x축 이동방향,-3이면 왼쪽, +3이면 오른쪽
    "to_y" : -6, #공의 y축 이동방향,
    "init_spd_y" : ball_speed_y[0]}) #y 최초 속도

#---------------------------------------사라질 무기, 공 정보 저장 변수
weapon_to_remove = -1
ball_to_remove = -1

#---------------------------------------폰트 정의
game_font = pygame.font.Font(None, 40) #폰트 객체 생성(폰트, 크기)

#---------------------------------------총 시간
total_time = 99

#---------------------------------------시간 계산
start_ticks = pygame.time.get_ticks() #시작tick을 받아옴

#---------------------------------------이벤트 루프
running = True #게임이 진행중인가?
while running:
    dt = clock.tick(30) #게임화면의 초당 프레임 수를 설정

    # 2. 이벤트 처리 (키보드, 마우스 등)

    for event in pygame.event.get(): #어떤 이벤트가 발생하였는가?
        if event.type == pygame.QUIT: #창이 닫히는 이벤트가 발생하였는가?
            running = False #게임이 진행중이 아님

        if event.type == pygame.KEYDOWN: #키가 눌러졌는지 확인
            if event.key == pygame.K_LEFT: #캐릭터를 왼쪽으로
                character_to_x -= character_speed 
            elif event.key == pygame.K_RIGHT: #캐릭터를 오른쪽으로
                character_to_x += character_speed
            elif event.key == pygame.K_SPACE:
                weapon_x_pos = character_x_pos + (character_width / 2) - (weapon_width / 2)
                weapon_y_pos = character_y_pos
                weapons.append([weapon_x_pos, weapon_y_pos])

        if event.type == pygame.KEYUP: #방향키를 떼면 멈춤
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                character_to_x = 0

    # 3. 게임 캐릭터 위치 정의

    character_x_pos += character_to_x * dt #-면 왼쪽 +면 오른쪽

#----------------------------------------가로 경계값 처리
    if character_x_pos < 0:
        character_x_pos = 0
    elif character_x_pos > screen_width - character_width:
        character_x_pos = screen_width - character_width

#----------------------------------------무기 위치 조정
    weapons =  [ [w[0], w[1] - weapon_speed] for w in weapons]

#----------------------------------------천장에 닿은 무기 없애기
    weapons = [[w[0], w[1]] for w in weapons if w[1] > 0]

#----------------------------------------공 위치 정의
    for ball_idx, ball_val in enumerate(balls):
        ball_pos_x = ball_val["pos_x"]
        ball_pos_y = ball_val["pos_y"]
        ball_img_idx = ball_val["img_idx"]

        ball_size = ball_images[ball_img_idx].get_rect().size
        ball_width = ball_size[0]
        ball_height = ball_size[1]
#----------------------------------------가로벽에 닿았을 때 공 이동 위치 변경 (튕겨 나오는 효과)
        if ball_pos_x < 0 or ball_pos_x> screen_width - ball_width:
            ball_val["to_x"]= ball_val["to_x"] * -1

#----------------------------------------세로 위치, 스테이지에 튕겨서 올라가는 처리
        if ball_pos_y >= screen_height- stage_height - ball_height:
            ball_val["to_y"] = ball_val["init_spd_y"]
        else: #그 외의 모든 경우에는 속도를 증가
            ball_val["to_y"] += 0.5

        ball_val["pos_x"] += ball_val["to_x"]
        ball_val["pos_y"] += ball_val["to_y"]

# 4. 충돌 처리

#----------------------------------------충돌 처리를 위한 캐릭터 rect 정보 업데이트
    character_rect = character.get_rect()
    character_rect.left = character_x_pos
    character_rect.top = character_y_pos

    for ball_idx, ball_val in enumerate(balls):
        ball_pos_x = ball_val["pos_x"]
        ball_pos_y = ball_val["pos_y"]
        ball_img_idx = ball_val["img_idx"]

        ball_rect = ball_images[ball_img_idx].get_rect() #공 rect 정보 업데이트
        ball_rect.left = ball_pos_x
        ball_rect.top = ball_pos_y

#----------------------------------------공과 캐릭터 충돌 처리
        if character_rect.colliderect(ball_rect):
            running = False
            break

#----------------------------------------공과 무기의 충돌 처리
        for weapon_idx, weapon_val in enumerate(weapons):
            weapon_pos_x = weapon_val[0]
            weapon_pos_y = weapon_val[1]

#----------------------------------------무기 rect 정보 업데이트
            weapon_rect = weapon.get_rect()
            weapon_rect.left = weapon_pos_x
            weapon_rect.top = weapon_pos_y

#----------------------------------------충돌 체크
            if weapon_rect.colliderect(ball_rect):
               weapon_to_remove = weapon_idx #해당 무기 없애기 위한 값 설정
               ball_to_remove = ball_idx #해당 공 없애기 위한 값 설정
               break

#-----------------------------------------충돌된 공 or 무기 없애기
    if ball_to_remove > -1:
        del balls[ball_to_remove]
        ball_to_remove = -1

    if weapon_to_remove > -1:
        del weapons[weapon_to_remove]
        weapon_to_remove= -1

# 5. 화면에 그리기

#----------------------------------------배경 그리기
    screen.blit(background, (0, 0))

#----------------------------------------무기 그리기
    for weapon_x_pos, weapon_y_pos in weapons:
        screen.blit(weapon, (weapon_x_pos, weapon_y_pos))

#----------------------------------------
    for idx, val in enumerate(balls):
        ball_pos_x = val["pos_x"]
        ball_pos_y = val["pos_y"]
        ball_img_idx = val["img_idx"]
        screen.blit(ball_images[ball_img_idx], (ball_pos_x, ball_pos_y))

#----------------------------------------스테이지 그리기
    screen.blit(stage, (0, screen_height - stage_height))

#----------------------------------------캐릭터 그리기
    screen.blit(character, (character_x_pos, character_y_pos))

#----------------------------------------타이머 집어 넣기, 경과 시간 계산
    elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000 #경과시간(ms)을 1000으로 나눠서 초(s) 단위로 표시
    timer = game_font.render(str(int(total_time - elapsed_time)), True, (255, 255, 255)) #출력할 글자, True, 글자 색상

#----------------------------------------타이머 그리기
    screen.blit(timer, (10, 10))

#----------------------------------------시간이 0 이하면 게임 종료
    if total_time - elapsed_time <= 0:
        print("타임 아웃")
        running = False

#----------------------------------------게임화면 다시 그리기
    pygame.display.update()

#----------------------------------------잠시 대기
pygame.time.delay(1000) #1초 정도 대기(ms)

#----------------------------------------pygame 종료
pygame.quit() 
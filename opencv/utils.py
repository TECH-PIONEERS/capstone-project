import numpy as np
import cv2
import threading
import pygame
import time
import math
import const

# 경고음이 울리고 있는지 여부를 나타내는 변수
global is_beeping
is_beeping = False

# 원이 범위를 벗어나면 경고 문구 출력하는 함수
def ballOutOfRangeAlert(x, y, radius, SCREEN_WIDTH, SCREEN_HEIGHT):
    global is_beeping, isBallOutOfRange
    if x > SCREEN_WIDTH or y > SCREEN_HEIGHT:
        print("Circle x is going out of screen boundary!")
        return True
    return False

def test_head_align(output1):     
    # 우선 순위에 따라 시리얼 프로세스 수정해야하는데 그건 이 함수 다 만들고 수정하자
    # TTS 및 비프음 체크

    # 생각 해야할 케이스: x 좌표값 460 부근에서 토우쪽 led 위치가 뒤집히는 상황 
    #                   (1, 2번 영역에서는 head_x - tou_x가 음수 값이고 3, 4 5번 영역에서는 head_x - tou_x가 양수 값)
    # 생각 해야할 케이스: IR 카메라 외곽에서, 정렬된 상황 자체에서 중앙보다 더 벌어져 있다.
    #                   영역 나누어서 처리하는 것이 필요


    #print("output1[1]: " , output1[1], "output1[3]: ", output1[3])

    head_x = 0
    head_y = 0
    tou_x = 0
    tou_y = 0

    # 헤드와 토우의 x, y값 구별: y가 더 큰 값이 토우 쪽 LED
    if output1[1] > output1[3]:
        tou_x = output1[0]
        tou_y = output1[1]
        head_x = output1[2]
        head_y = output1[3]
    else:
        head_x = output1[0]
        head_y = output1[1]
        tou_x = output1[2]
        tou_y = output1[3]
    
    #print("head: ", head_x, "tou: ", tou_x) 
    
    # default_distance 값을 영역에 따라 적절하게 구성하여, 정렬된 상황에서 head_x - tou_x가 거의 0이 되도록 맞추기
    # 그 후 threshold 값은 영역에 모두 동일하게 적용하여  
    #            head_x - tou_x의 결과를 양수 / 음수값으로 구분하여 정렬되지 않은 상황의 왼쪽/오른쪽 기울기 판별

    calibration = 0

    # x 좌표로 범위 구분 및 매핑
    if head_x < 340:
        print("1")
        calibration = 60
    elif head_x > 340 and head_x < 470:
        print("2 left of center")
        calibration = 40
    elif head_x > 470 and head_x < 560:
        print("3 right of center")
        calibration = -20
    elif head_x > 560 and head_x < 590:
        print("4")
        calibration = -40
    else: 
        print("5")
        calibration= -60

    distance = head_x - tou_x + calibration

    # 정렬 및 기울어짐 판별
    if distance > -20 and distance < 20:
        print("align")
        return const.default
    elif distance < -20:
        print("왼쪽으로 기울어짐")
        return const.head_align
    elif distance > 20:
        print("오른쪽으로 기울어짐")
        return const.head_align



def generate_alert_beep():
    global is_beeping
    if not is_beeping:
        pygame.init()
        pygame.mixer.init()
        is_beeping = True
   
        # generate_long_beep(alert=True)
        beep_sound = pygame.mixer.Sound("sound/long_beep.wav")
        beep_sound.play()
        time.sleep(3)

        is_beeping = False

def generate_high_4_beep():
    global is_beeping
    if not is_beeping:
        is_beeping = True 
        pygame.init()
        pygame.mixer.init()
        beep_sound = pygame.mixer.Sound("sound/high_4_beep.wav")
        beep_sound.play()
        time.sleep(3)
        is_beeping = False

def generate_high_3_beep():
    global is_beeping
    if not is_beeping:
        is_beeping = True 
        pygame.init()
        pygame.mixer.init()
        beep_sound = pygame.mixer.Sound("sound/high_3_beep.wav")
        beep_sound.play()
        time.sleep(3)
        is_beeping = False

def generate_high_2_beep():
    global is_beeping
    if not is_beeping:
        is_beeping = True 
        pygame.init()
        pygame.mixer.init()
        beep_sound = pygame.mixer.Sound("sound/high_2_beep.wav")
        beep_sound.play()
        time.sleep(3)
        is_beeping = False

def generate_high_1_beep():
    global is_beeping
    if not is_beeping:
        is_beeping = True 
        pygame.init()
        pygame.mixer.init()
        beep_sound = pygame.mixer.Sound("sound/high_1_beep.wav")
        beep_sound.play()
        time.sleep(3)
        is_beeping = False

def generate_mid_beep():
    global is_beeping
    if not is_beeping:
        is_beeping = True 
        pygame.init()
        pygame.mixer.init()
        beep_sound = pygame.mixer.Sound("sound/mid_beep.wav")
        beep_sound.play()
        time.sleep(3)
        is_beeping = False

def generate_long_beep():
    global is_beeping
    if not is_beeping:
        is_beeping = True   
        pygame.init()
        pygame.mixer.init()
        beep_sound = pygame.mixer.Sound("sound/long_beep.wav")
        beep_sound.play()
        time.sleep(1)
        is_beeping = False

def generate_high_beep():
    global is_beeping
    if not is_beeping:
        is_beeping = True 
        pygame.init()
        pygame.mixer.init()
        beep_sound = pygame.mixer.Sound("sound/high_beep.wav")
        beep_sound.play()
        time.sleep(3)
        is_beeping = False

def generate_low_beep():
    global is_beeping
    if not is_beeping:
        is_beeping = True 
        pygame.init()
        pygame.mixer.init()
        beep_sound = pygame.mixer.Sound("sound/low_beep.wav")
        beep_sound.play()
        time.sleep(1)
        is_beeping = False

def camera_calibration(image):
    # 카메라 보정 함수 
    # image는 picam2.capture_array()로 받아온 frame
    
    # 최종 버전: v6
    fx = 326.819
    fy = 329.259
    cx = 321.455
    cy = 198.692
    k1 = -0.298901
    k2 = 0.072073
    p1 = 0.001761
    p2 = -0.000953

    # 카메라 매트릭스와 왜곡 계수 정의
    mtx = np.array([[fx, 0, cx],
                    [0, fy, cy],
                    [0, 0, 1]])
    dist = np.array([[k1, k2, p1, p2]])

    # 입력 이미지의 크기 가져오기
    h, w = image.shape[:2]

    # 최적의 새 카메라 매트릭스 계산
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    # 이미지를 새 카메라 매트릭스에 맞게 왜곡 보정
    dst = cv2.undistort(image, mtx, dist, None, newcameramtx)

    # ROI(관심 영역) 추출
    x, y, w, h = roi
    dst = dst[y:y+h, x:x+w]

    return dst

def pixel_to_cm(height):
    print(200/height) #단위(mm)
    return 200/height

def find_foot(a1, b1, a2, b2, a3, b3):
    # a1, b1 / a2, b2는 헤드 ir센서의 좌표
    # a3, b3는 홀의 좌표
     
    # 직선 l의 기울기 계산
    if a2 - a1 != 0:
        m = (b2 - b1) / (a2 - a1)
    else:
        m = float('inf')  # Handle vertical lines

    # Calculate perpendicular slope
    if m != 0:
        m_perpendicular = -1 / m
    else:
        m_perpendicular = float('inf')  # Handle vertical lines

    # 수선의 발 계산
    x_foot = (a3 + m * b3 - m * b1 + m * a1) / (m + 1/m)
    y_foot = b3 + m_perpendicular * (x_foot - a3)

    return x_foot, y_foot
# x_foot, y_foot이 헤드 범위 밖이라면 정렬x로 판단

# 좌표 예시
# a1, b1 = 1, 2
# a2, b2 = 4, 5
# a3, b3 = 3, 3

# x_foot, y_foot = find_foot(a1, b1, a2, b2, a3, b3)
# print("Foot coordinates:", (x_foot, y_foot))

def goal(goal_y,y):
    # if 공의 y좌표가 40 ~ 80 사이면 골이라고 판단
    if(y >= (goal_y-10) and y < (goal_y+10)):
        # print("goal")
        return Trueif
    else:
        # print("miss")
        return False

def 골과공정렬(goal_y, y):
    if(y >= (goal_y-8) and y <= (goal_y+8)):
        return True
    elif y < (goal_y-8):
        return 2
    elif y > (goal_y+8):
        return 3

def is_valid_string(input_string):
    before = ''
    num = ''
    arr = []
    if (len(input_string) > 0 and input_string[0] == ',') or len(input_string) == 0: return False, arr
    
    for char in input_string:
        if not (char.isdigit() or char == ','):
            return False, arr
        if before == ',' and char == ',':
            return False, arr
        if char.isdigit():
            num += char
        elif char == ',':
            num = int(float(num))
            if num == 1023 and len(arr) == 0:
                return False, []
            if num < 1023: arr.append(num)
            num = ''
        before = char
    if before != ',':
        # return True
        return True, arr
    else: return False, arr

def return_ball_direction_change(previous_pos, current_pos, threshold=30):
    if abs(current_pos - previous_pos) >= threshold:
        if previous_pos < current_pos:
            return 'bottom'
        elif previous_pos > current_pos:
            return 'up'

def get_ball_head_distance(ball_pos, head_pos, cm):
    print(f'1cm {cm}')
    가로거리차이 = (abs(ball_pos[0]-head_pos) * cm / 10)
    print(f'헤드와 공의 거리 차이는 {가로거리차이}cm입니다 헤드와 공의 거리 차이는 {abs(ball_pos[0]-head_pos)} pixel')
    return 

import numpy as np
import cv2
import threading
import pygame
import time
import math
import const
import pyttsx3
from espeak import espeak

# 경고음이 울리고 있는지 여부를 나타내는 변수
global is_beeping
is_beeping = False

start_x = 8
start_y = 101
end_x = 600
end_y = 174
goal_x = 572

def test_head_align(output1):     
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

    if head_x < 263:
        tou_x = tou_x *  0.75
    elif head_x >= 263 and head_x < 298:
        tou_x = tou_x * 0.74
    elif head_x >= 298 and head_x < 368:
        tou_x = tou_x * 0.785
    elif head_x >= 368 and head_x < 438:
        tou_x = tou_x * 0.84
    elif head_x >= 438 and head_x < 508:
        tou_x = tou_x * 0.88
    elif head_x >= 508 and head_x < 578:
        tou_x = tou_x * 0.925
    elif head_x >= 578 and head_x < 648:
        tou_x = tou_x * 0.939
    elif head_x >= 648 and head_x < 718:
        tou_x = tou_x * 0.957
    elif head_x >= 718 and head_x < 788:
        tou_x = tou_x * 0.98
    elif head_x >= 788 and head_x < 858:
        tou_x = tou_x * 1.005
    elif head_x >= 858 and head_x < 928:
        tou_x = tou_x * 1.01
    elif head_x >= 928 and head_x < 968:
        tou_x = tou_x * 1.016
    else:
        tou_x = tou_x * 1.016

    distance = head_x - int(tou_x)

    # print("head : ", head_x, "tou: ", tou_x, "distance : ", distance)

    # 정렬 및 기울어짐 판별
    if distance >= -20 and distance <= 20:
        return const.default
    elif distance < -20: #CW (7.1 ~ 7.3)
        #print("CW")
        if distance < -50:
            return 7.3
        elif distance < -100:
            return 7.2
        else:
            return 7.1
        #return const.head_align
    elif distance > 20: #CCW (7.4 ~ 7.6)
        #print("CCW")
        if distance > 50:
            return 7.6
        elif distance > 100:
            return 7.5
        else:
            return 7.4
        #return const.head_align

def generate_beep(case):
    global is_beeping
    if not is_beeping:
        is_beeping = True 
        pygame.init()
        pygame.mixer.init()
        match case:
            case 1:
                beep_sound = pygame.mixer.Sound("sound/high_4_beep.wav")
            case 2:
                beep_sound = pygame.mixer.Sound("sound/high_3_beep.wav")
            case 3:
                beep_sound = pygame.mixer.Sound("sound/high_2_beep.wav")
            case 4:
                beep_sound = pygame.mixer.Sound("sound/high_1_beep.wav")
            case 5:
                beep_sound = pygame.mixer.Sound("sound/mid_beep.wav")
            case 6:
                beep_sound = pygame.mixer.Sound("sound/long_beep.wav")
            case 8:
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

def pixel_to_mm():
    height = end_y-start_y
    return 270/height

mm = int(pixel_to_mm())

def goal(x, y):
    goal_y = 36
    goal_x = 578
    # if 공의 y좌표가 40 ~ 80 사이면 골이라고 판단
    if(y >= (goal_y-10) and y < (goal_y+10)) and (x >= (goal_x-6) and x < (goal_x+6)):
        # print("goal")
        return True
    else:
        # print("miss")
        return False

def is_align_x(x):
    leftmost, rightmost = 97, 12
    if x > leftmost:
        return 2
    elif x < rightmost:
        return 3
    else: # x align success
        return True

def is_align(y, offset):
    goal_y = 36
    if(y >= (goal_y-offset) and y <= (goal_y+offset)):
        return True
    elif y < (goal_y-offset):
        return 2
    elif y > (goal_y+offset):
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

def return_ball_direction(previous_pos, current_pos, threshold=30):
    if abs(current_pos - previous_pos) >= threshold:
        if previous_pos < current_pos:
            return 'down'
        elif previous_pos > current_pos:
            return 'up'
    else:
        return 'straight'

def get_distance_AB(A, B):
    dist = (abs(A-B) * mm / 10)
    return dist

def euclidean_distance(x1, y1, x2, y2):
    return (math.sqrt((x2 - x1)**2 + (y2 - y1)**2) * mm / 10)

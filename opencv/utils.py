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


# 원이 범위를 벗어나면 경고 문구 출력하는 함수
def ballOutOfRangeAlert(x, radius, SCREEN_WIDTH, SCREEN_HEIGHT):
    if x - r < (SCREEN_WIDTH // 5) * 2: # 카메라쪽
        print("Circle x is going out of screen boundary!")
        return True
    elif x + r > (SCREEN_WIDTH // 5) * 3: # 바깥쪽
        print("Circle x is going out of screen boundary!")
        return True    
    else:
        return False

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
    elif head_x >= 263 and head_x < 298: #done
        tou_x = tou_x * 0.75
    elif head_x >= 298 and head_x < 333: #done
        tou_x = tou_x * 0.8
    elif head_x >= 333 and head_x < 368: #done
        tou_x = tou_x * 0.82
    elif head_x >= 368 and head_x < 403: #done
        tou_x = tou_x * 0.852
    elif head_x >= 403 and head_x < 438: #done
        tou_x = tou_x * 0.888
    elif head_x >= 438 and head_x < 473: #done
        tou_x = tou_x * 0.86
    elif head_x >= 473 and head_x < 508: #done
        tou_x = tou_x * 0.87
    elif head_x >= 508 and head_x < 543: #done
        tou_x = tou_x * 0.9
    elif head_x >= 543 and head_x < 578: #done
        tou_x = tou_x * 0.93
    elif head_x >= 578 and head_x < 613: #done
        tou_x = tou_x * 0.93
    elif head_x >= 613 and head_x < 648: #done
        tou_x = tou_x * 0.95
    elif head_x >= 648 and head_x < 683: #done
        tou_x = tou_x * 0.95
    elif head_x >= 683 and head_x < 718: #done
        tou_x = tou_x * 0.95
    elif head_x >= 718 and head_x < 753: #done
        tou_x = tou_x * 0.965
    elif head_x >= 753 and head_x < 788: #done
        tou_x = tou_x * 0.969
    elif head_x >= 788 and head_x < 823: #done
        tou_x = tou_x * 0.98
    elif head_x >= 823 and head_x < 858: #done
        tou_x = tou_x * 0.987
    elif head_x >= 858 and head_x < 893: #done
        tou_x = tou_x * 0.987
    elif head_x >= 893 and head_x < 928: #done
        tou_x = tou_x * 0.995
    elif head_x >= 928 and head_x < 968: #done
        tou_x = tou_x * 1.03
    else:
        tou_x = tou_x * 1.04

    distance = head_x - int(tou_x)

    #print("head : ", head_x, "tou: ", tou_x, "distance : ", distance)

    # 정렬 및 기울어짐 판별
    if distance > -30 and distance < 30:
        return const.default
    elif distance < -30:
        print("CW")
        return const.head_align
    elif distance > 30:
        print("CCW")
        return const.head_align
    else:
        return const.head_align

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

def pixel_to_mm(height):
    return 270/height

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

def is_align2(y,ball_y, offset):
    if(y >= (ball_y-offset) and y <= (ball_y+offset)):
        return True
    elif y < (ball_y-offset):
        return 2
    elif y > (ball_y+offset):
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

mm = int(pixel_to_mm(end_y-start_y))

def get_distance_AB(A, B):
    dist = (abs(A-B) * mm / 10)
    return dist

def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

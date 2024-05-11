# 공 외곽선이 화면의 1/3 벗어났을 경우 경고 문구 출력하는 코드

from picamera2 import Picamera2
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import utils 
import threading 
import serial
import cv2
import numpy as np
import time

lf = b'\n'  # Linefeed in ASCII
myString = None
myString1 = None

myPort = serial.Serial('/dev/ttyUSB0', 19200)
myPort1 = serial.Serial('/dev/ttyUSB1', 19200)
time.sleep(2) 

def is_valid_string(input_string):
    if input_string[0] == ',': return False
    for char in input_string:
        if not (char.isdigit() or char == ','):
            return False
    return True

def setup():
    # Clear serial buffer
    myPort.reset_input_buffer()
    myPort1.reset_input_buffer()

def ir_data():
    global myString, myString1
    while True:
        myString = myPort.readline().decode().rstrip()
        myString1 = myPort1.readline().decode().rstrip()
        
        if myString or myString1:
            if is_valid_string(myString) and is_valid_string(myString1):
                # print(myString)
                # print(myString1)
                output = list(map(float, myString.split(',')))
                output1 = list(map(float, myString1.split(',')))
                output = list(map(int, output))
                output1 = list(map(int, output1))
                print(f"output 0 : {output}")
                print(f"output 1 : {output1}")

flag = 0
start_x, start_y, end_x, end_y, goal_x, goal_y = 0, 0, 0, 0, 0, 0
previous_frame = None

# 원이 범위를 벗어나면 경고 문구 출력하는 함수
def ballOutOfRangeAlert(circles, SCREEN_WIDTH):
    # 경계 범위 설정
    BOUNDARY_X = SCREEN_WIDTH // 3 # 화면 너비의 1/3
    for (x, y, r) in circles:
        if x - r < BOUNDARY_X:
            print("Circle is going out of screen boundary!")
            if not utils.is_beeping:
                beep_thread = threading.Thread(target=utils.generate_alert_beep)
                beep_thread.start()
                print("Running alert beep")
            if not utils.isBallOutOfRange:
                utils.isBallOutOfRange = True
        elif utils.isBallOutOfRange is True:
            utils.isBallOutOfRange = False


def 골과공정렬(y):
    if(y >= (goal_y-5) and y < (goal_y+5)):
        print("골 과 공 정렬")
        return True
    else:
        print("골 과 공 정렬되지않음")
        return False

# 공 x좌표가 107보다 작을 때 골이라고 판단하는 함수
def goal(y):
    # if 공의 y좌표가 40 ~ 80 사이면 골이라고 판단
    if(y >= (goal_y-10) and y < (goal_y+10)):
        print("goal")
        return True
    else:
        print("miss")
        return False

def get_xy(event, x, y):
    if event == cv2.EVENT_LBUTTONUP:
        print(x,y)

def get_position(event, x, y, flags, params):
    global start_x 
    global start_y 
    global end_x 
    global end_y 
    global flag
    global goal_x
    global goal_y
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Clicked at (x={}, y={})".format(x, y))
        if flag == 0:
            start_x = x
            start_y = y
            flag = 1
        elif flag == 1:
            end_x = x
            end_y = y
            flag = 2  # flag를 2로 설정하여 crop할 좌표를 모두 선택한 상태로 변경
            utils.pixel_to_cm(end_y-start_y)
            # cv2.destroyWindow('cap')  # 마우스 클릭 이벤트를 위한 창 닫기
        elif flag == 2:
            goal_x = x
            goal_y = y
            flag = 3
    return 
golfball_size = 3

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())

# 노랑색을 검출하기 위한 상한값, 하한값 경계 정의
colorLower = (0, 138, 138)  
colorUpper = (150, 250, 250) 

pts = deque(maxlen=args["buffer"])
picam2 = Picamera2()
picam2.video_configuration.controls.FrameRate = 60.0
picam2.preview_configuration.main.size=(640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.start()

while True:
    cap = picam2.capture_array()

    if cap is None:
            print('no frame')
            cap = previous_frame  # 이전 프레임을 사용
    else:
        previous_frame = cap

    # cap = utils.camera_calibration(cap)
    # 프레임 크기 조정, 블러 처리, HSV 색 공간으로 변환
    cv2.namedWindow('cap')
    cv2.setMouseCallback('cap', get_position)
    
    myString = myPort.readline().decode("latin-1").rstrip()
    myString1 = myPort1.readline().decode("latin-1").rstrip()
        
    if myString or myString1:
        if is_valid_string(myString) and is_valid_string(myString1):
            print(myString)
            print(myString1)
            output = list(map(float, myString.split(',')))
            output1 = list(map(float, myString1.split(',')))
            output = list(map(int, output))
            output1 = list(map(int, output1))
    
    if flag == 3:
        frame = cap[start_y:end_y, start_x:end_x]
        # cv2.setMouseCallback('Frame', get_xy)
        SCREEN_WIDTH = end_x - start_x
        if(len(output1) > 0):
            print(utils.scale_value(output1[0]))
            cv2.circle(frame,(utils.scale_value(output1[0]), (end_y-start_y)//2 ), 5, (255,0,0), -1)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
        mask = cv2.inRange(hsv, colorLower, colorUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # Canny Edge Detection을 사용하여 에지 검출
        edges = cv2.Canny(mask, 30, 150)

        cnts = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            if M["m00"] == 0 : M["m00"] = 1
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                # 원 중심 좌표와 반지름을 이용하여 중심 계산
            if radius > golfball_size:
                cv2.circle(frame, (int(x), int(y)), int(radius),
                    (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                if x <= goal_y + 30:
                    goal(y)
                    골과공정렬(y)
            print(center)
            # 원의 외곽선이 지정된 범위를 벗어나면 경고 문구를 출력
            # ballOutOfRangeAlert(circles, SCREEN_WIDTH)

            pts.appendleft(center)

        # 프레임 보여주기
        cv2.imshow("Frame", frame)
    else:
        cv2.imshow('cap', cap)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

setup()
cv2.destroyAllWindows()

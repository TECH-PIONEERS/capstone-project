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

flag = 0
start_x, start_y, end_x, end_y = 0, 0, 0, 0
previous_frame = None

# 원의 외곽선이 범위를 벗어나면 경고 문구 출력하는 함수
def check_circles_out_of_screen(circles, SCREEN_WIDTH):
    # 경계 범위 설정
    BOUNDARY_X = SCREEN_WIDTH // 3 # 화면 너비의 1/3
    for (x, y, r) in circles:
        if x - r < BOUNDARY_X:
            print("Circle is going out of screen boundary!")
            beep_thread = threading.Thread(target=utils.generate_alert_beep)
            beep_thread.start()
            print("Running high beep")

def get_xy(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONUP:
        print(x,y)

def get_position(event, x, y, flags, params):
    global start_x 
    global start_y 
    global end_x 
    global end_y 
    global flag
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
    return 

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())

# 노랑색을 검출하기 위한 상한값, 하한값 경계 정의
colorLower = (0, 138, 138)  
colorUpper = (40, 255, 255) 
 
pts = deque(maxlen=args["buffer"])
    
picam2 = Picamera2()
picam2.preview_configuration.main.size=(640, 400)
picam2.preview_configuration.main.format = "RGB888"
picam2.start()

while True:
    cap = picam2.capture_array()

    # 프레임을 잡지 못하면 비디오 종료
    if cap is None:
        print('no frame')
        cap = previous_frame  # 이전 프레임을 사용
    else:
        previous_frame = cap

    cap = utils.camera_calibration(cap)

    # 프레임 크기 조정, 블러 처리, HSV 색 공간으로 변환
    cv2.namedWindow('cap')
    cv2.setMouseCallback('cap', get_position)
    
    if flag == 2:
        frame = cap[start_y:end_y, start_x:end_x]
        # cv2.setMouseCallback('Frame', get_xy)

        SCREEN_WIDTH = end_x - start_x
        
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
        mask = cv2.inRange(hsv, colorLower, colorUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # Canny Edge Detection을 사용하여 에지 검출
        edges = cv2.Canny(mask, 50, 150)

        # # Hough 변환을 사용하여 원 검출
        circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                                param1=70, param2=30, minRadius=5, maxRadius=300)


        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

                # 원 중심 좌표와 반지름을 이용하여 중심 계산
                center = (x, y)
                print(center)
                pts.appendleft(center)
            
            # 원의 외곽선이 지정된 범위를 벗어나면 경고 문구를 출력
            check_circles_out_of_screen(circles, SCREEN_WIDTH)

        # # 이전 중심과 현재 중심을 연결하는 선을 그림
        for i in range(1, len(pts)):
            if pts[i - 1] is None or pts[i] is None:
                continue
            thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
            cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

        # 프레임 보여주기
        cv2.imshow("Frame", frame)
    else:
        cv2.imshow('cap', cap)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cv2.destroyAllWindows()

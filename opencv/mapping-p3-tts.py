from multiprocessing import Process, Pipe
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
import utilsp3

lf = b'\n'  # Linefeed in ASCII
myString = None
myString1 = None
golfball_size = 3
flag = 0
start_x, start_y, end_x, end_y, goal_x, goal_y = 0, 0, 0, 0, 0, 0
previous_frame = None
colorLower = (0, 138, 138)  
colorUpper = (150, 250, 250) 

# tts_process는 global flag에 따라 비프음 및 TTS 출력하는 프로세스
# 출력을 위한 프로세스는 상황마다 시작되고 종료된다.
def tts_process():
    while True:
        if utilsp3.is_beeping is False:
            if utilsp3.isBallOutOfRange is True: # 원이 범위를 벗어나면 경고음 출력
                beep_process = Process(target=utilsp3.generate_alert_beep)
                beep_process.start() # 시작
                print("Running alert beep")
                beep_process.join() # 종료


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

def stream_opencv(conn):
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video",
        help="path to the (optional) video file")
    ap.add_argument("-b", "--buffer", type=int, default=64,
        help="max buffer size")
    args = vars(ap.parse_args())

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

        cv2.namedWindow('cap')
        cv2.setMouseCallback('cap', get_position)

        if flag == 3:
            frame = cap[start_y:end_y, start_x:end_x]
            SCREEN_WIDTH = end_x - start_x

            if conn.poll():
                res = conn.recv()
                output = res[0]
                output1 = res[1]
                print(f'{output} {output1}')
                if(len(output1) > 0):
                    cv2.circle(frame,(output1[0]//4+100, (end_y-start_y)//2 ), 5, (255,0,255), -1)
                if(len(output) > 1):
                    cv2.circle(frame,((end_x-start_x)//2, SCREEN_HEIGHT-(output[0])//4 ), 5, (255,255,255), -1)
                if(len(output) > 3):
                    cv2.circle(frame,((end_x-start_x)//2, SCREEN_HEIGHT-(output[2])//4 ), 5, (255,0,0), -1)
                    
            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        
            mask = cv2.inRange(hsv, colorLower, colorUpper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            edges = cv2.Canny(mask, 30, 150)
            cnts = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            if len(cnts) > 0:
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c) # 원의 중심의 x, y
                M = cv2.moments(c)
                if M["m00"] == 0 : M["m00"] = 1
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                print(center)
                    # 원 중심 좌표와 반지름을 이용하여 중심 계산
                if radius > golfball_size:
                    cv2.circle(frame, (int(x), int(y)), int(radius),
                        (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
                    if x <= goal_y + 30:
                        utils.goal(goal_y,y)
                utilsp3.ballOutOfRangeAlert((x, radius), SCREEN_WIDTH) # 공이 범위 벗어났을 시 경고 알림
                pts.appendleft(center)
            cv2.imshow("Frame", frame)
        else:
            cv2.imshow('cap', cap)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
    cv2.destroyAllWindows()

def get_serial(conn):
    # myPort = serial.Serial('/dev/ttyUSB1', 2400,timeout=0.2)
    # myPort1 = serial.Serial('/dev/ttyUSB0', 2400, timeout=0.2)
    myPort = serial.Serial('/dev/ttyUSB1', 9600,timeout=0.1)
    myPort1 = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.1)
    time.sleep(0.5) 
    myPort.reset_input_buffer()
    myPort1.reset_input_buffer()
    previous_output, previous_output1 = [], []
    while True:
        myString = myPort.readline().decode("latin-1").rstrip()
        myString1 = myPort1.readline().decode("latin-1").rstrip()
        if myString or myString1:
            # if utils.is_valid_string(myString) and utils.is_valid_string(myString1):
            #     output = list(map(int, list(map(float, myString.split(',')))))
            #     output1 = list(map(int, list(map(float, myString1.split(',')))))
            o1_bool, output = utils.is_valid_string(myString)
            o2_bool, output1 = utils.is_valid_string(myString1)
            if o1_bool or o2_bool:
                conn.send([output, output1])
                previous_output, previous_output1 = output, output1
        
        else:
            conn.send([previous_output, previous_output1])


if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p1 = Process(target=stream_opencv, args=(parent_conn,))
    p2 = Process(target=get_serial, args=(child_conn,))
    p2.start()
    p1.start()
    p1.join()
    p2.join()

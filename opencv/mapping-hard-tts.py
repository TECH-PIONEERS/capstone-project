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

lf = b'\n'  # Linefeed in ASCII
myString = None
myString1 = None
golfball_size = 3
flag = 0
start_x, start_y, end_x, end_y, goal_x, goal_y = 0, 0, 0, 0, 0, 0
previous_frame = None
# colorLower = (0, 138, 138) # tuning required! 
colorLower = (5, 152, 152) 
colorUpper = (150, 250, 250) 
# colorLower = ( 0, 0, 200) # setting for red
# colorUpper = ( 60, 10, 255) # GBR
previous_pos = [-999, -999]
previous_direction = ''

global tts_flag
tts_flag = 000

# tts_process는 global flag에 따라 비프음 및 TTS 출력하는 프로세스
def tts_process():
    global tts_flag

    while True:
        if utils.is_beeping is False:
<<<<<<< HEAD
            print(utils.tts_flag)
            if utils.tts_flag == 999: #퍼터 값이 없을 경우
=======
            if tts_flag == 999: #퍼터 값이 없을 경우
>>>>>>> 8a332a53d52a724356bbeb8602f3d0c7af876e0b
                print("Running alert beep")
                beep_thread = threading.Thread(target=utils.generate_alert_beep)
                beep_thread.start()
                beep_thread.join()

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
    global previous_direction
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

        cap = utils.camera_calibration(cap)
        cv2.namedWindow('cap')
        cv2.setMouseCallback('cap', get_position)

        if flag == 3:
            frame = cap[start_y:end_y, start_x:end_x]
            SCREEN_WIDTH = end_x - start_x
            SCREEN_HEIGHT = end_y - start_y

            if conn.poll():
                res = conn.recv()
                output = res[0]
                output1 = res[1]
                # print(f'{output} {output1}')
                if(len(output1) > 0):
                    # print(output1[0]//4 -80)
                    if output1[0]//4 -80 <= -80:
                        continue
                    elif output1[0]//4 -80 <= 15:
                        calibration = 0.43
                    elif output1[0]//4 -80 <= 60:
                        calibration = 0.42
                    else: 
                        calibration = 0.41
                    if(len(output) > 1):
                        cv2.circle(frame,( int(output1[0]//4 * calibration), int((output[0])//4 * 0.4)), 5, (0,0,255), -1)
                    if(len(output) > 3):
                        cv2.circle(frame,( int(output1[0]//4 * calibration), int((output[2])//4 * 0.4)), 5, (255,0,255), -1)
                    
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
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                if M["m00"] == 0 : M["m00"] = 1
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                
                if previous_pos[0] == -999 or previous_pos[1] == -999 : 
                    previous_pos[0] = center[0]
                    previous_pos[1] = center[1]
                else:
                    if previous_direction == '':
                        previous_direction = utils.return_ball_direction_change(previous_pos[1], center[1])
                    else:
                        current_direction = utils.return_ball_direction_change(previous_pos[1], center[1])
                        if previous_direction != current_direction:
                            print('방향 바뀜')
                    current_direction = previous_direction
                    previous_pos[0] = center[0]
                    previous_pos[1] = center[1]
                    
                    
                    # 원 중심 좌표와 반지름을 이용하여 중심 계산
                if radius > golfball_size:
                    cv2.circle(frame, (int(x), int(y)), int(radius),
                        (255, 0, 0), 2)
                    cv2.circle(frame, center, 2, (255, 0, 0), -1)
                    if x <= goal_y + 30:
                        utils.goal(goal_y,y)

                pts.appendleft(center)
            cv2.imshow("Frame", frame)
        else:
            cv2.imshow('cap', cap)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
    cv2.destroyAllWindows()

def get_serial(conn):
    global tts_flag

    myPort = serial.Serial('/dev/ttyUSB0', 9600,timeout=0.1)
    myPort1 = serial.Serial('/dev/ttyUSB1', 9600, timeout=0.1)
    time.sleep(0.5) 
    myPort.reset_input_buffer()
    myPort1.reset_input_buffer()
    while True:
        myString = myPort.readline().decode("latin-1").rstrip()
        myString1 = myPort1.readline().decode("latin-1").rstrip()
        if myString or myString1:
            o1_bool, output = utils.is_valid_string(myString)
            o2_bool, output1 = utils.is_valid_string(myString1)
            print(output, output1)
            if o1_bool or o2_bool:
                utils.tts_flag = 0
                # print('chabge utils tts flag 0')
                conn.send([output, output1])
    
            elif len(output) == 0 and len(output1) == 0:
                print('chabge utils tts flag 999')
                utils.tts_flag = 999
    
if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p1 = Process(target=stream_opencv, args=(parent_conn,))
    p2 = Process(target=get_serial, args=(child_conn,))
    p3 = Process(target=tts_process)
    p2.start()
    p1.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()

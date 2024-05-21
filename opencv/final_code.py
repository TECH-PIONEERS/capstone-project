from multiprocessing import Process, Pipe, Manager
from picamera2 import Picamera2
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import utils 
import const
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

# yello
# colorLower = (5, 152, 152) 
# colorUpper = (150, 250, 250) 

# red
colorLower = ( 130, 210, 190) # setting for red
colorUpper = ( 185, 255, 255) # BGR

previous_direction = ''
cm = ''

def get_position(event, x, y, flags, params):
    global start_x 
    global start_y 
    global end_x 
    global end_y 
    global flag
    global goal_x
    global goal_y
    global cm
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Clicked at (x={}, y={})".format(x, y))
        if flag == 0:
            # start_x = x
            start_x = 8
            start_y = 101
            flag = 1
        elif flag == 1:
            end_x = 600
            end_y = 174
            flag = 2  # flag를 2로 설정하여 crop할 좌표를 모두 선택한 상태로 변경
            cm = int(utils.pixel_to_cm(end_y-start_y))
            # cv2.destroyWindow('cap')  # 마우스 클릭 이벤트를 위한 창 닫기
        elif flag == 2:
            goal_x = x
            goal_y = y
            flag = 3
    return 

def tts_process(tts_flag):
    import utils
    while True:
        if utils.is_beeping == True: return
        if tts_flag.value == const.ball_missing:
            print("no ball")
            beep_thread = threading.Thread(target=utils.generate_high_beep)
            beep_thread.start()
            beep_thread.join()
        elif tts_flag.value == const.ball_align_bottom:
            print("골 과 공 정렬되지않음 bottom")
            beep_thread = threading.Thread(target=utils.generate_low_beep)
            beep_thread.start()
            beep_thread.join()
        elif tts_flag.value == const.ball_align_up:
            print("골 과 공 정렬되지않음 up")
            beep_thread = threading.Thread(target=utils.generate_long_beep)
            beep_thread.start()
            beep_thread.join()    
        elif tts_flag.value == const.head_missing: #퍼터 값이 없을 경우
            print("no head")
            beep_thread = threading.Thread(target=utils.generate_alert_beep)
            beep_thread.start()
            beep_thread.join()
        elif tts_flag.value == const.head_align: #퍼터 값이 없을 경우
            print("no head align")
            beep_thread = threading.Thread(target=utils.generate_high_beep)
            beep_thread.start()
            beep_thread.join()

def stream_opencv(conn, ball_position, tts_flag, isMoving):
    global previous_direction
    global goal_y
    global flag
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
            # frame = cap[start_y:end_y, start_x:end_x]
            frame = cap[start_y:end_y, start_x:end_x]
            SCREEN_WIDTH = end_x - start_x
            SCREEN_HEIGHT = end_y - start_y

            if conn.poll():
                res = conn.recv()
                output = res[0]
                output1 = res[1]
                if(len(output1) > 0):
                    if output1[0]//4 -80 <= -80:
                        continue
                    elif output1[0]//4 -80 <= 15:
                        calibration = 0.285
                    elif output1[0]//4 -80 <= 70:
                        calibration = 0.325
                    elif output1[0]//4 -80 <= 90:
                        calibration = 0.34
                    elif output1[0]//4 -80 <= 150:
                        calibration = 0.36
                    else: 
                        calibration = 0.38
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
                ballout = utils.ballOutOfRangeAlert(center[0], center[1], radius, SCREEN_WIDTH, SCREEN_HEIGHT)
                
                if tts_flag.value == const.ball_missing: 
                    tts_flag.value = const.default
                if (utils.골과공정렬(goal_y - start_y, center[1]) == 2 or utils.골과공정렬(goal_y - start_y, center[1]) == 3) and tts_flag.value >= const.ball_align_up:
                    if utils.골과공정렬(goal_y - start_y, center[1]) == 2:
                        tts_flag.value = const.ball_align_up
                    elif utils.골과공정렬(goal_y - start_y, center[1]) == 3:
                        tts_flag.value = const.ball_align_bottom
                elif utils.골과공정렬(goal_y - start_y, center[1]) and tts_flag.value != const.default: tts_flag.value = const.default                 
                
                if ball_position[0] == -999 or ball_position[1] == -999 : 
                    ball_position[0] = center[0]
                    ball_position[1] = center[1] 
                else:
                    if previous_direction == '':
                        previous_direction = utils.return_ball_direction_change(ball_position[1], center[1])
                    else:
                        current_direction = utils.return_ball_direction_change(ball_position[1], center[1])
                        if previous_direction != current_direction:
                            print('방향 바뀜')
                    current_direction = previous_direction
                    ball_position[0] = center[0]
                    ball_position[1] = center[1]
                    # 원 중심 좌표와 반지름을 이용하여 중심 계산
                if radius > golfball_size:
                    cv2.circle(frame, (int(x), int(y)), int(radius),
                        (255, 0, 0), 2)
                    cv2.circle(frame, center, 2, (255, 0, 0), -1)
                    if x <= goal_y + 30:
                        utils.goal(goal_y,y)

                pts.appendleft(center)
            else:
                tts_flag.value = const.ball_missing
            cv2.imshow("Frame", frame)
        else:
            cv2.imshow('cap', cap)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
          break
        if key == ord("w") and center and cm != '' and not isMoving.value:
          utils.get_ball_head_distance(center, int(output1[0]//4 * calibration), cm)
    cv2.destroyAllWindows()

def get_serial(conn, tts_flag):
    myPort = serial.Serial('/dev/ttyUSB1', 9600,timeout=0.1)
    myPort1 = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.1)
    time.sleep(0.5) 
    myPort.reset_input_buffer()
    myPort1.reset_input_buffer()
    while True:
        myString = myPort.readline().decode("latin-1").rstrip()
        myString1 = myPort1.readline().decode("latin-1").rstrip()
        if myString or myString1:
            o1_bool, output = utils.is_valid_string(myString)
            o2_bool, output1 = utils.is_valid_string(myString1)
            if o1_bool or o2_bool:
                if tts_flag.value == const.head_missing:
                    tts_flag.value = const.default
                if len(output) < 3 and tts_flag.value > const.head_align:
                    tts_flag.value = const.head_align
                elif len(output) >= 3 and tts_flag.value == const.head_align:
                    tts_flag.value = const.default
                conn.send([output, output1])
            else:
                if tts_flag.value > const.head_missing:
                    tts_flag.value = const.head_missing        

BALL_MOVEMENT_THRESHOLD = 10
def check_movement(ball_pos, isMoving):
    while True:
        initial_x = ball_pos[0]
        initial_y = ball_pos[1]
        # print(f'initial value {initial_x} {initial_y}')
        time.sleep(1)  # 2초 대기
        current_x = ball_pos[0]
        current_y = ball_pos[1]
        # print(f'current value {current_x} {current_y}')

        if abs(current_x - initial_x) <= BALL_MOVEMENT_THRESHOLD and abs(current_y - initial_y) <= BALL_MOVEMENT_THRESHOLD:
            isMoving.value = False
        else:
            isMoving.value = True

if __name__ == '__main__':
    import const
    with Manager() as manager:
        parent_conn, child_conn = Pipe()
        ball_position = manager.list()
        tts_flag = manager.Namespace()
        tts_flag.value = const.default
        isMoving = manager.Namespace()
        isMoving.value = True

        ball_position.append(-999)
        ball_position.append(-999)

        p1 = Process(target=stream_opencv, args=(parent_conn, ball_position, tts_flag, isMoving))
        p2 = Process(target=get_serial, args=(child_conn,tts_flag))
        p3 = Process(target=check_movement,args=(ball_position,isMoving))
        p4 = Process(target=tts_process, args=(tts_flag, ))

        p1.start()
        p2.start()
        p3.start()
        p4.start()

        p1.join()
        p2.join()
        p3.join()
        p4.join()

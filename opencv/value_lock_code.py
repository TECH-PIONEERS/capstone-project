from multiprocessing import Process, Pipe, Manager, Value, Lock
from picamera2 import Picamera2
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
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

glo_output = []
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

def tts_process(tts_flag, tts_lock, dist, dist_lock):
    # 함수 안에서 라이브러리 import, utils 함수 및 변수 안 쓰도록
    import utils
    import time
    import pygame
    import pyttsx3
    from espeak import espeak

    #is_beeping = False
    current_dist = 0
    pygame.init()
    pygame.mixer.init()
    engine = pyttsx3.init('espeak')

    while True:
        tts_lock.acquire() # 선점 방지 Lock
        current_flag = tts_flag.value
        tts_lock.release() # 선점 해지

        dist_lock.acquire() # 선점 방지 Lock
        current_dist = dist.value
        dist_lock.release()

        if current_flag == const.ball_missing:
            print("ball missing")
            beep_sound = pygame.mixer.Sound("sound/high_beep.wav")
            beep_sound.play()
            time.sleep(3)
        elif current_flag == const.ball_align_bottom:
            print("ball bottom")
            engine.say("Down") #TTS
            engine.runAndWait()
        elif current_flag == const.ball_align_up:
            print("ball up")
            engine.say("Up") #TTS
            engine.runAndWait() 
        elif current_flag == const.head_missing: #퍼터 값이 없을 경우
            print("head missing")
            beep_sound = pygame.mixer.Sound("sound/long_beep.wav")
            beep_sound.play()
            time.sleep(3)
        elif current_flag == const.head_align: #정렬 되지 않은 경우
            print("no head align")
            beep_sound = pygame.mixer.Sound("sound/low_beep.wav")
            beep_sound.play()
            time.sleep(3)
        elif current_flag == const.head_center_down:
             print("head down")
             engine.say("head Down") #TTS
             engine.runAndWait()
        elif current_flag == const.head_center_up:
             print("head up")            
             engine.say("Head Up") #TTS
             engine.runAndWait()
        elif current_dist > 0:
             print(f"dist {current_dist}")
             engine.say(str(int(current_dist))) #TTS
             engine.runAndWait()

def stream_opencv(conn, ball_position, tts_flag, isMoving, align_success, dist, tts_lock, dist_lock):
    global previous_direction
    global goal_y
    global flag
    global glo_output
    new_ouput = []
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

                if len(output1) > 3:
                    if output1[1] > output1[3]:
                        new_ouput = [output1[2], output1[3], output1[0], output1[1]]
                elif (len(output1) > 1):
                    new_ouput = output1
                else:
                    new_ouput = []

                glo_output = new_ouput
                
                if len(new_ouput) > 1:
                    if output1[0]//4 -80 <= -80:
                        continue
                    elif output1[0]//4 -80 <= 15:
                        calibration = 0.285
                    elif output1[0]//4 -80 <= 70:
                        calibration = 0.31
                    elif output1[0]//4 -80 <= 90:
                        calibration = 0.34
                    elif output1[0]//4 -80 <= 150:
                        calibration = 0.36
                    else: 
                        calibration = 0.38
                    if(len(output) > 1):
                        cv2.circle(frame,( int(output1[0]//4 * calibration), int((output[0])//4 * 0.42)), 5, (0,0,255), -1)
                    if(len(output) > 3):
                        cv2.circle(frame,( int(output1[0]//4 * calibration), int((output[2])//4 * 0.42)), 5, (255,0,255), -1)
                        # if (utils.골과공정렬(goal_y - start_y, (int((output[0])//4 * 0.42)+int((output[2])//4 * 0.42))//2) == 2 or utils.골과공정렬(goal_y - start_y, (int((output[0])//4 * 0.42)+int((output[1])//4 * 0.42))//2) == 3) and tts_flag.value >= const.head_center_down:
                        #     if utils.골과공정렬(goal_y - start_y, (int((output[0])//4 * 0.42)+int((output[2])//4 * 0.42))//2) == 2:
                        #         lock.acquire() # 선점 방지 Lock   
                        #         tts_flag.value = const.head_center_up
                        #         lock.release() # 선점 해지
                        #     elif utils.골과공정렬(goal_y - start_y, (int((output[0])//4 * 0.42)+int((output[2])//4 * 0.42))//2) == 3:
                        #         lock.acquire() # 선점 방지 Lock
                        #         tts_flag.value = const.head_center_down
                        #         lock.release() # 선점 해지
                        # elif utils.골과공정렬(goal_y - start_y,(int((output[0])//4 * 0.42)+int((output[2])//4 * 0.42))//2) and tts_flag.value != const.default:    
                        # lock.acquire() # 선점 방지 Lock
                        # tts_flag.value = const.default
                        # lock.release() # 선점 해지  

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
                
                if tts_flag.value == const.ball_missing: 
                    tts_lock.acquire() # 선점 방지 Lock
                    tts_flag.value = const.default
                    tts_lock.release() # 선점 해지
                if (utils.골과공정렬(goal_y - start_y, center[1]) == 2 or utils.골과공정렬(goal_y - start_y, center[1]) == 3) and tts_flag.value >= const.ball_align_up:
                    if utils.골과공정렬(goal_y - start_y, center[1]) == 2:
                        tts_lock.acquire() # 선점 방지 Lock
                        tts_flag.value = const.ball_align_up
                        tts_lock.release() # 선점 해지
                    elif utils.골과공정렬(goal_y - start_y, center[1]) == 3:
                        tts_lock.acquire() # 선점 방지 Lock
                        tts_flag.value = const.ball_align_bottom
                        tts_lock.release() # 선점 해지
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
                tts_lock.acquire() # 선점 방지 Lock
                tts_flag.value = const.ball_missing
                tts_lock.release() # 선점 해지
            
            if align_success.value == const.align_default and center and not isMoving.value:
                if len(glo_output) <= 0:
                    continue
                dist_lock.acquire()
                dist.value = utils.get_ball_head_distance(center, int(glo_output[0]//4 * calibration), cm)   
                dist_lock.release()
                align_success.value = -1
        
            cv2.imshow("Frame", frame)
        else:
            cv2.imshow('cap', cap)
        #print(f'tts_flag {tts_flag.value}')
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
          break

    cv2.destroyAllWindows()

def get_serial(conn, tts_flag,align_success, tts_lock):
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
                    tts_lock.acquire() # 선점 방지 Lock
                    tts_flag.value = const.default
                    tts_lock.release() # 선점 해지
                    
                if len(output1) < 3 and tts_flag.value > const.head_align:
                    tts_lock.acquire() # 선점 방지 Lock
                    tts_flag.value = const.head_align
                    tts_lock.release() # 선점 해지
                elif len(output1) == 4 and tts_flag.value >= const.head_align:
                    tts_lock.acquire() # 선점 방지 Lock
                    tts_flag.value = utils.test_head_align(output1)
                    tts_lock.release() # 선점 해지

                    if tts_flag.value == const.default:
                        align_success.value = const.align_default
                conn.send([output, output1])
            else:
                if tts_flag.value > const.head_missing:
                    tts_lock.acquire() # 선점 방지 Lock
                    tts_flag.value = const.head_missing    
                    tts_lock.release() # 선점 해지    

BALL_MOVEMENT_THRESHOLD = 10
def check_movement(ball_pos, isMoving):
    while True:
        initial_x = ball_pos[0]
        initial_y = ball_pos[1]
        time.sleep(1)  # 2초 대기
        current_x = ball_pos[0]
        current_y = ball_pos[1]

        if abs(current_x - initial_x) <= BALL_MOVEMENT_THRESHOLD and abs(current_y - initial_y) <= BALL_MOVEMENT_THRESHOLD:
            isMoving.value = False
        else:
            isMoving.value = True

if __name__ == '__main__':
    import const
    with Manager() as manager:
        tts_lock                = Lock()
        dist_lock               = Lock()

        parent_conn, child_conn = Pipe()
        ball_position           = manager.list()
        align_success           = manager.Namespace()
        align_success.value     = -1
        #dist                    = manager.Namespace()
        #dist.value              = const.dist_default
        dist                    = Value('f', const.dist_default, lock=False)
        tts_flag                = Value('i', const.default, lock=False)
        isMoving                = manager.Namespace()
        isMoving.value          = True

        ball_position.append(-999)
        ball_position.append(-999)

        p1 = Process(target=stream_opencv, args=(parent_conn, ball_position, tts_flag, isMoving, align_success, dist, tts_lock, dist_lock))
        p2 = Process(target=get_serial, args=(child_conn,tts_flag, align_success, tts_lock, ))
        p3 = Process(target=check_movement,args=(ball_position,isMoving, ))
        p4 = Process(target=tts_process, args=(tts_flag, tts_lock, dist, dist_lock ))

        p1.start()
        p2.start()
        p3.start()
        p4.start()

        p1.join()
        p2.join()
        p3.join()
        p4.join()

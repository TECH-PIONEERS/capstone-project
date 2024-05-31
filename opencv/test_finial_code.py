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
previous_frame = None

glo_output = []

# red
colorLower = (130, 210, 190) # setting for red
colorUpper = (185, 255, 255) # BGR

previous_direction = ''

start_x = 8
start_y = 101
end_x = 600
end_y = 174
goal_x = 572

def tts_process(tts_flag, dist):
    # 함수 안에서 라이브러리 import, utils 함수 및 변수 안 쓰도록
    import utils
    import time
    import pygame
    import pyttsx3
    from espeak import espeak

    #is_beeping = False
    #current_dist = 0
    pygame.init()
    pygame.mixer.init()
    engine = pyttsx3.init('espeak')


    while True:
        #tts_lock.acquire() # 선점 방지 Lock
        current_flag = tts_flag.value
        #print(current_flag)
        #tts_lock.release() # 선점 해지

        #dist_lock.acquire() # 선점 방지 Lock
        current_dist = dist.value
        #dist_lock.release()

        if current_flag == const.ball_missing:
            print("ball missing")
            beep_sound = pygame.mixer.Sound("opencv/sound/high_1_beep.wav")
            beep_sound.play()
            time.sleep(3)
            current_dist = 0
        elif current_flag == const.ball_align_bottom:
            print("ball bottom")
            voices = engine.getProperty('voices')
            volume = engine.getProperty('volume')

            # engine.setProperty(voices, voice-)
            engine.setProperty(voices, volume+0.5)

            engine.say("Down") #TTS
            engine.runAndWait()
            current_dist = 0
        elif current_flag == const.ball_align_up:
            print("ball up")
            engine.say("Up") #TTS
            engine.runAndWait()
            current_dist = 0 
        elif current_flag == const.head_missing: #퍼터 값이 없을 경우
            print("head missing")
            beep_sound = pygame.mixer.Sound("opencv/sound/half_version/mid_beep_half.mp3")
            beep_sound.play()
            time.sleep(3)
            current_dist = 0
        elif current_flag == const.head_align: #정렬 되지 않은 경우
            print("no head align")
            beep_sound = pygame.mixer.Sound("opencv/sound/half_version/low_beep_half.mp3")
            beep_sound.play()
            time.sleep(3)
            current_dist = 0
        elif current_flag == const.head_center_down:
            print("head down")
            engine.say("head Down") #TTS
            engine.runAndWait()
            current_dist = 0
        elif current_flag == const.head_center_up:
            print("head up")            
            engine.say("Head Up") #TTS
            engine.runAndWait()
            current_dist = 0
        elif current_dist > 0:
            print(f"dist {current_dist}")
            engine.say(str(int(current_dist))) #TTS
            engine.runAndWait()

def stream_opencv(conn, ball_position, tts_flag, isMoving, align_success, dist, shot_flag):
    global previous_direction
    global flag
    global glo_output
    new_output = []
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

        frame = cap[start_y:end_y, start_x:end_x]
        SCREEN_WIDTH = end_x - start_x
        SCREEN_HEIGHT = end_y - start_y

        if conn.poll():
            res = conn.recv()
            output = res[0]
            output1 = res[1]
            #fix
            if len(output1) > 3:
                if output1[1] > output1[3]:
                    new_output = [output1[2], output1[3], output1[0], output1[1]]
                else:
                    new_output = output1
            else:
                new_output = output1
            glo_output = new_output
            # print(f"ouput : {output}")
            #fix first time new_output = []
            # print(f"ouput1 : {new_output}")
            if len(new_output) > 1:
                if new_output[0]//4 -80 <= -80:
                    continue
                elif new_output[0]//4 -80 <= 15:
                    calibration_x = 0.285
                elif new_output[0]//4 -80 <= 70:
                    calibration_x = 0.31
                elif new_output[0]//4 -80 <= 90:
                    calibration_x = 0.34
                elif new_output[0]//4 -80 <= 150:
                    calibration_x = 0.36
                else: 
                    calibration_x = 0.39
                output1_cali_x = int(new_output[0]//4 * calibration_x)
                if(len(output) > 3):
                    calibration_y = 0.29
                    diff_y = abs(output[0]-output[2])
                    print(f"diff {diff_y} {36}")
                    diff_limit = 110
                    if diff_y < diff_limit:
                        offset = abs(diff_limit-diff_y)//9
                    else:
                        offset = 0
                    output_cali_y1 = int((output[0])//4 * calibration_y - offset)
                    output_cali_y2 = int((output[2])//4 * calibration_y + offset)
                    cv2.circle(frame,(output1_cali_x, output_cali_y1), 5, (0,0,255), -1)
                    cv2.circle(frame,(output1_cali_x, output_cali_y2), 5, (255,0,0), -1)
                    
                    if shot_flag.value == False :
                        #헤드 정렬 - 위치 판단
                        is_head_align = utils.is_align((output_cali_y1+output_cali_y2)//2,2)
                        if ( is_head_align == 2 or is_head_align == 3) and tts_flag.value >= const.head_center_up:
                            if is_head_align == 2:
                                tts_flag.value = const.head_center_up
                            elif is_head_align == 3:
                                tts_flag.value = const.head_center_down
                        elif is_head_align and (tts_flag.value == const.head_center_up or tts_flag.value == const.head_center_down):
                            tts_flag.value = 1002

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
            
            # ball boundary

            if shot_flag.value == False:
                is_ball_in = utils.is_align_x(center[0]) 
                if is_ball_in == 2 or is_ball_in == 3:
                    tts_flag.value == const.ball_missing
                elif (is_ball_in != 2 and is_ball_in != 3) and tts_flag.value == const.ball_missing:
                    tts_flag.value = const.default
                
                # 공 정렬 판단
                if isMoving.value == False:
                    is_ball_aling = utils.is_align(center[1])
                    if (is_ball_aling == 2 or is_ball_aling == 3) and tts_flag.value >= const.ball_align_bottom:
                        if is_ball_aling == 2:
                            tts_flag.value = const.ball_align_up
                        elif is_ball_aling == 3:
                            tts_flag.value = const.ball_align_bottom
                    elif (is_ball_aling) and (tts_flag.value == const.ball_align_bottom or tts_flag.value == const.ball_align_up): 
                        tts_flag.value = 1003                 
                
                # OK
                if len(new_output) == 4 and tts_flag.value >= const.head_align:
                        tts_flag.value = utils.test_head_align(output1)
            else: # ball_shot
                print(f"ball shot true")
                if isMoving.value == False :
                    #det goal
                    if utils.goal(center[0], center[1]):
                        tts_flag.value = const.game_win
                        print("game_win")
                    else:
                        tts_flag.value = const.game_lose
                        print("game_lose")


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
            pts.appendleft(center) 
            # print(f"get_ball_dist : {(pts[0][0], pts[0][1], cm)}")
            # for i in range(1, len(pts)):
            #     if pts[i-1] is None or pts[i] is None:
            #         continue

                # thickness = int(np.sqrt(args["buffer"] / float(i+1))*2.5)
                # cv2.line(frame, pts[i-1], pts[i], (255,255,255), thickness)

        else:
            tts_flag.value = const.ball_missing

        #fix
        if align_success.value == const.align_default and center and not isMoving.value:
            if len(glo_output) <= 0:
                continue
            dist.value = utils.get_distance_AB(center[0], int(glo_output[0]//4 * calibration), cm)
            align_success.value = -1
    
        cv2.imshow('cap', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cv2.destroyAllWindows()

def get_serial(conn, tts_flag,align_success, shot_flag):
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
            if o1_bool or o2_bool:
                if shot_flag.value == False:
                    if tts_flag.value == const.head_missing:
                        tts_flag.value = 1001
                    if len(output1) < 3 and tts_flag.value > const.head_align:
                        tts_flag.value = const.head_align
                # elif len(output1) == 4 and tts_flag.value >= const.head_align:
                #     tts_flag.value = utils.test_head_align(output1)
                #     if tts_flag.value == const.default:
                #         align_success.value = const.align_default
                conn.send([output, output1])
            else:
                if tts_flag.value > const.head_missing:
                    tts_flag.value = const.head_missing  

BALL_MOVEMENT_THRESHOLD = 10
def check_movement(tts_flag, ball_pos, isMoving, shot_flag):
    while True:
        initial_x = ball_pos[0]
        initial_y = ball_pos[1]
        time.sleep(0.3) 
        current_x = ball_pos[0]
        current_y = ball_pos[1]

        if abs(current_x - initial_x) <= BALL_MOVEMENT_THRESHOLD and abs(current_y - initial_y) <= BALL_MOVEMENT_THRESHOLD:
            isMoving.value = False
        else:
            if current_x > const.boundary1 and (tts_flag.value == const.head_missing or tts_flag.value == const.head_center_down or tts_flag.value == const.head_center_up or tts_flag.value == const.head_align):
                shot_flag.value = True
                print("ball_shot")

            isMoving.value = True

if __name__ == '__main__':
    import const
    with Manager() as manager:
        parent_conn, child_conn = Pipe()
        ball_position = manager.list()
        align_success = manager.Namespace()
        align_success.value = -1
        dist = manager.Namespace()
        dist.value = const.dist_default
        tts_flag = manager.Namespace()
        tts_flag.value = const.default
        shot_flag = manager.Namespace()
        shot_flag.value = False
        isMoving = manager.Namespace()
        isMoving.value = True

        ball_position.append(-999)
        ball_position.append(-999)

        p1 = Process(target=stream_opencv, args=(parent_conn,ball_position,tts_flag,isMoving,align_success,dist, shot_flag, ))
        p2 = Process(target=get_serial, args=(child_conn,tts_flag, align_success,shot_flag, ))
        p3 = Process(target=check_movement,args=(tts_flag, ball_position,isMoving,shot_flag, ))
        p4 = Process(target=tts_process, args=(tts_flag,dist, ))

        p1.start()
        p2.start()
        p3.start()
        p4.start()

        p1.join()
        p2.join()
        p3.join()
        p4.join()

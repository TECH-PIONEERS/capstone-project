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

# red
colorLower = (130, 210, 190) # setting for red
colorUpper = (185, 255, 255) # BGR

previous_direction = ''

start_x = utils.start_x
start_y = utils.start_y
end_x = utils.end_x
end_y = utils.end_y
goal_x = utils.goal_x

def tts_process(tts_flag, dist, head_align_flag, shot_flag, ball_align_flag, align_success, isMovingTime, is_direction_changed_flag):
    import utils
    import time
    import pygame
    import pyttsx3
    from espeak import espeak

    pygame.init()
    pygame.mixer.init()
    engine = pyttsx3.init('espeak')
    while True:
        current_flag = int(tts_flag.value)
        float_flag = tts_flag.value
        if current_flag == const.ball_missing:
            # print("ball missing")
            beep_sound = pygame.mixer.Sound("opencv/sound/high_1_beep.wav")
            beep_sound.play()
            time.sleep(2)
            head_align_flag.value = False
        if shot_flag.value == False and isMovingTime[1] == False:
            if current_flag == const.ball_align_bottom:
                # print("ball bottom")
                engine.say("Down") #TTS
                engine.runAndWait()
                head_align_flag.value = False
            elif current_flag == const.ball_align_up:
                # print("ball up")
                engine.say("Up") #TTS
                engine.runAndWait()
                head_align_flag.value = False
            elif current_flag == const.head_missing: #퍼터 값이 없을 경우
                # print("head missing")
                beep_sound = pygame.mixer.Sound("opencv/sound/half_version/mid_beep_half.mp3")
                beep_sound.play()
                time.sleep(2)
                head_align_flag.value = False
            elif current_flag == const.head_align: #정렬 되지 않은 경우
                # 7.1 ~ 7.4: CW, 7.5 ~ 7.7: CCW
                if float_flag >= 7.1 and float_flag <= 7.3:
                    sleep_time = (float_flag - 7) * 6 # 7.1(0.6초), 7.2(1.2초), 7.3(1.8초)
                    beep_sound = pygame.mixer.Sound("opencv/sound/half_version/low_beep_half.mp3")
                    beep_sound.play()
                    time.sleep(sleep_time)
                elif float_flag >= 7.4 and float_flag <= 7.6:
                    sleep_time = (float_flag - 7.3) * 6 # 7.4(0.6초), 7.5(1.2초), 7.6(1.8초)
                    beep_sound = pygame.mixer.Sound("opencv/sound/half_version/high_1_beep_half.mp3")
                    beep_sound.play()
                    time.sleep(sleep_time)
                head_align_flag.value = False
            elif current_flag == const.head_center_down:
                # print("head down")
                beep_sound = pygame.mixer.Sound("opencv/sound/down.mp3")
                beep_sound.play()
                time.sleep(1)
                head_align_flag.value = False
            elif current_flag == const.head_center_up:
                # print("head up")            
                beep_sound = pygame.mixer.Sound("opencv/sound/up.mp3")
                beep_sound.play()
                time.sleep(1)
                head_align_flag.value = False
            elif current_flag == const.head_align_success:
                # print(f"dist {dist}")
                engine.say(str(int(dist[0]))) #TTS 공과 골 사이의 거리
                engine.runAndWait()
                engine.say(str(int(dist[1]))) #TTS 공과 헤드 사이의 거리
                engine.runAndWait()
                tts_flag.value = 1004
                head_align_flag.value = True
        else:
            if is_direction_changed_flag.value == True:
                engine.say(f"ball hit the wall")
                engine.runAndWait()
            elif current_flag == const.game_lose:
                print("lose")
                beep_sound = pygame.mixer.Sound("opencv/sound/lose.mp3")
                beep_sound.play()
                time.sleep(2)
                engine.say(f"{dist[3]}") #TTS 공과 골 사이의 거리
                engine.runAndWait()
                engine.say(f"{str(int(dist[4]))}") #TTS 공과 골 사이의 거리
                engine.runAndWait()
            elif current_flag == const.game_win:
                beep_sound = pygame.mixer.Sound("opencv/sound/nice-shot.mp3")
                beep_sound.play()
            else:
                continue

            time.sleep(5)
            align_success.value = False
            head_align_flag.value = False
            ball_align_flag.value = False
            tts_flag.value = const.default
            shot_flag.value = False
            isMovingTime[0] = 0
            isMovingTime[1] = False
            is_direction_changed_flag.value = False
            dist[0], dist[1], dist[3], dist[4] = 0,0,0,0
    

def stream_opencv(conn, ball_position, tts_flag, isMoving, align_success, dist, shot_flag, prev_ball_position, head_align_flag, ball_align_flag, isMovingTime, is_direction_changed_flag):
    global previous_direction
    global flag
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
            if len(output1) > 3:
                if output1[1] > output1[3]:
                    new_output = [output1[2], output1[3], output1[0], output1[1]]
                else:
                    new_output = output1
            else:
                new_output = output1

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
                    diff_limit = 100
                    if diff_y < diff_limit:
                        offset = abs(diff_limit-diff_y)
                    else:
                        offset = 0
                    output_cali_y1 = (output[0] / 4) * calibration_y - offset - 0.5
                    output_cali_y2 = (output[2] / 4) * calibration_y + offset - 0.5
                    # print(output_cali_y1, output_cali_y2)
                    cv2.circle(frame,(output1_cali_x, int(output_cali_y1)), 5, (0,0,255), -1)
                    cv2.circle(frame,(output1_cali_x, int(output_cali_y2)), 5, (255,0,0), -1)
                    if shot_flag.value == False :
                        #헤드 정렬 - 위치 판단
                        is_head_align = utils.is_align((output_cali_y1+output_cali_y2)//2,1)
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
            # print(f"center : {center}")
            
            # ball boundary
            if shot_flag.value == False:
                is_ball_in = utils.is_align_x(center[0]) 
                if is_ball_in == 2 or is_ball_in == 3:
                    tts_flag.value = const.ball_missing
                elif (is_ball_in != 2 and is_ball_in != 3) and tts_flag.value == const.ball_missing:
                    tts_flag.value = 1003
                
                # 공 정렬 판단
                if isMoving.value == False:
                    is_ball_aling = utils.is_align(center[1],5)
                    if (is_ball_aling == 2 or is_ball_aling == 3) and tts_flag.value >= const.ball_align_bottom:
                        if is_ball_aling == 2:
                            tts_flag.value = const.ball_align_up
                        elif is_ball_aling == 3:
                            tts_flag.value = const.ball_align_bottom
                        ball_align_flag.value = False
                    elif ball_align_flag.value == False and (is_ball_in != 2 and is_ball_in !=3): 
                        prev_ball_position[0] = center[0]
                        prev_ball_position[1] = center[1]
                        align_success.value = True
                        ball_align_flag.value = True
                        tts_flag.value = const.default                 
                
                # 헤드 정렬 판단
                if len(new_output) == 4 and tts_flag.value >= const.head_align:
                    tts_flag.value = utils.test_head_align(output1)
                    if tts_flag.value >= const.default and head_align_flag.value == False:
                        # tts_flag 값 변경
                        tts_flag.value = const.head_align_success
                        # 공과 골 사이 거리
                        dist[0] = utils.get_distance_AB(center[0],goal_x) + 2
                        # # 공과 헤드 사이 거리
                        dist[1] = utils.get_distance_AB(center[0],output1_cali_x)

            else: # ball_shot
                # print(f"ball shot true tts_flag {tts_flag.value}")
                if isMoving.value == False:
                    now = time.time()
                    if isMovingTime[1] == True:
                        timer = now - isMovingTime[0]
                        if timer >= 3:
                            #det goal
                            if utils.goal(center[0], center[1]):
                                tts_flag.value = const.game_win
                            else:
                                tts_flag.value = const.game_lose
                                # 공의 방향 공의 이동거리
                                #shot_direction = utils.return_ball_direction(prev_ball_position[1], center[1])
                                shot_direction = utils.temp_return_ball_direction(prev_ball_position[0], prev_ball_position[1], center[0], center[1], previous_direction)
                                dist[3] = shot_direction
                                shot_dist = utils.euclidean_distance(prev_ball_position[0],prev_ball_position[1],center[0],center[1])
                                dist[4] = shot_dist

            if ball_position[0] == -999 or ball_position[1] == -999 : 
                ball_position[0] = center[0]
                ball_position[1] = center[1] 
            else:
                if previous_direction == '':
                    #previous_direction = utils.return_ball_direction(ball_position[1], center[1])
                    previous_direction = utils.temp_return_ball_direction(ball_position[0], ball_position[1], center[0], center[1], previous_direction)
                else:
                    #current_direction = utils.return_ball_direction(ball_position[1], center[1])
                    current_direction = utils.temp_return_ball_direction(ball_position[0], ball_position[1], center[0], center[1], previous_direction, 2.5)
                    if previous_direction != current_direction and is_ball_in == 2 and align_success.value == True:
                        print('방향 바뀜')
                        is_direction_changed_flag.value = True
                current_direction = previous_direction
                ball_position[0] = center[0]
                ball_position[1] = center[1]
                # 원 중심 좌표와 반지름을 이용하여 중심 계산
            if radius > golfball_size:
                cv2.circle(frame, (int(x), int(y)), int(radius),
                    (255, 0, 0), 2)
                cv2.circle(frame, center, 2, (255, 0, 0), -1)
            pts.appendleft(center) 
        else:
            if shot_flag.value == False:
                tts_flag.value = const.ball_missing
            else:
                tts_flag.value = const.game_lose
                print("out of range")

        cv2.imshow('cap', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cv2.destroyAllWindows()

def get_serial(conn, tts_flag,align_success, shot_flag):
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
                if shot_flag.value == False:
                    if tts_flag.value == const.head_missing:
                        tts_flag.value = 1001
                    if len(output1) < 3 and tts_flag.value > const.head_align:
                        tts_flag.value = const.head_align
                conn.send([output, output1])
            else:
                if tts_flag.value > const.head_missing and shot_flag.value == False:
                    tts_flag.value = const.head_missing  

BALL_MOVEMENT_THRESHOLD = 10
def check_movement(tts_flag, ball_pos, isMoving, shot_flag, align_success, isMovingTime):
    while True:
        initial_x = ball_pos[0]
        initial_y = ball_pos[1]
        time.sleep(0.3) 
        current_x = ball_pos[0]
        current_y = ball_pos[1]

        threshold = 10
        not_move = abs(current_x - initial_x) <= BALL_MOVEMENT_THRESHOLD and abs(current_y - initial_y) <= BALL_MOVEMENT_THRESHOLD
        is_ball_out = utils.is_align_x(ball_pos[0])
        if not_move:
            if isMoving.value == True and is_ball_out == 2:
                # isMoving = true => false가 된 순간  
                # 이를 align공 거리와 현재 공 측정 이때 pixel 값이 threshold 값보다 크면 shot.value = true
                print(f"{align_success.value} {abs(current_x-prev_ball_position[0]) >= threshold}")
                if abs(current_x-prev_ball_position[0]) >= threshold and align_success.value == True:
                    if shot_flag.value == False:
                        shot_flag.value = True
                        if isMovingTime[1] == False:
                            isMovingTime[0] = time.time()
                            isMovingTime[1] = True
            isMoving.value = False
        else:
            isMoving.value = True
        # print(f"shot_Flag {shot_flag.value} notmove {not_move} isMoving {isMoving.value}")
        

if __name__ == '__main__':
    import const
    with Manager() as manager:
        parent_conn, child_conn = Pipe()
        ball_position = manager.list()
        prev_ball_position = manager.list()
        align_success = manager.Namespace()
        align_success.value = False
        dist = manager.list()
        tts_flag = manager.Namespace()
        tts_flag.value = const.default
        shot_flag = manager.Namespace()
        shot_flag.value = False
        isMoving = manager.Namespace()
        isMoving.value = True
        head_align_flag = manager.Namespace()
        head_align_flag.value = False
        ball_align_flag = manager.Namespace()
        ball_align_flag.value = False
        isMovingTime = manager.list() #[time, boolean]
        isMovingTime.append(0)
        isMovingTime.append(False)
        is_direction_changed_flag = manager.Namespace()
        is_direction_changed_flag.value = False


        ball_position.append(-999)
        ball_position.append(-999)
        prev_ball_position.append(-999)
        prev_ball_position.append(-999)
        dist.append(0)
        dist.append(0)
        dist.append(0)
        dist.append(0)

        p1 = Process(target=stream_opencv, args=(parent_conn,ball_position,tts_flag,isMoving,align_success,dist, shot_flag,prev_ball_position,head_align_flag, ball_align_flag, isMovingTime, is_direction_changed_flag))
        p2 = Process(target=get_serial, args=(child_conn,tts_flag, align_success,shot_flag, ))
        p3 = Process(target=check_movement,args=(tts_flag, ball_position,isMoving,shot_flag, align_success, isMovingTime ))
        p4 = Process(target=tts_process, args=(tts_flag,dist,head_align_flag, shot_flag,  ball_align_flag, align_success, isMovingTime, is_direction_changed_flag))

        p1.start()
        p2.start()
        p3.start()
        p4.start()

        p1.join()
        p2.join()
        p3.join()
        p4.join()

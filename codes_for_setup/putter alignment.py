import numpy as np
import time
import const
from multiprocessing import Process, Pipe, Manager, Value, Lock
import serial


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
            o1_bool, output = is_valid_string(myString)
            o2_bool, output1 = is_valid_string(myString1)
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
                    tts_flag.value = test_head_align(output1)
                    tts_lock.release() # 선점 해지

                    if tts_flag.value == const.default:
                        align_success.value = const.align_default
                conn.send([output, output1])
            else:
                if tts_flag.value > const.head_missing:
                    tts_lock.acquire() # 선점 방지 Lock
                    tts_flag.value = const.head_missing    
                    tts_lock.release() # 선점 해지    


if __name__ == '__main__':
    import const
    with Manager() as manager:
        tts_lock                = Lock()

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

        p2 = Process(target=get_serial, args=(child_conn,tts_flag, align_success, tts_lock, ))

        p2.start()

        p2.join()

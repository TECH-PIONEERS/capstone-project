from collections import deque
from imutils.video import VideoStream
from picamera2 import Picamera2
import numpy as np
import argparse
import cv2
import imutils
import time

# 인자 파서 설정
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())

# Deque 초기화
pts = deque(maxlen=args["buffer"])

picam2 = Picamera2()
picam2.video_configuration.controls.FrameRate = 60.0
picam2.preview_configuration.main.size=(640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.start()

time.sleep(2.0)

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

    # 프레임을 그레이스케일로 변환
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

     # 검은색의 HSV 범위 정의
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 30])  # 이 범위는 필요에 따라 조정

    # 검은색 영역 마스크 생성
    mask = cv2.inRange(hsv, lower_black, upper_black)


    # 가우시안 블러 적용 (노이즈 제거)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Canny Edge Detection 적용
    edges = cv2.Canny(blurred, 50, 150)

    # 결과 프레임 보여주기
    cv2.imshow("Original Frame", frame)
    cv2.imshow("Edges", edges)
    
    # 'q' 키를 누르면 종료
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# 모든 창 닫기
cv2.destroyAllWindows()


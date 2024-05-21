from collections import deque
from imutils.video import VideoStream
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

# 비디오 스트림 시작
vs = cv2.VideoCapture(0)

time.sleep(2.0)

while True:
    # 프레임 읽기
    ret, frame = vs.read()

    # 프레임을 잡지 못하면 비디오 종료
    if not ret:
        print('No frame captured, exiting...')
        break

    # 프레임을 그레이스케일로 변환
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

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
vs.release()

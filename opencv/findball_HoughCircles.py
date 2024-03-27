'''
원 검출위한 HoughCircles 추가
HoughCircles 파라미터 값 수정 필요
'''
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

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
    
vs = cv2.VideoCapture(0)

# 카메라나 비디오 파일을 시작하기 위한 중단 시간 부여
time.sleep(2.0)

while True:
    # 현재 프레임 잡기
    _, frame = vs.read()

    # 프레임을 잡지 못하면 비디오 종료
    if frame is None:
        break

    # 프레임 크기 조정, 블러 처리, HSV 색 공간으로 변환
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    # 노랑색에 대한 마스크 생성 후, 마스크 내의 deliations과 erotions를 제겅
    mask = cv2.inRange(hsv, colorLower, colorUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # Canny Edge Detection을 사용하여 에지 검출
    edges = cv2.Canny(mask, 50, 150)

    # Hough 변환을 사용하여 원 검출
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                               param1=70, param2=30, minRadius=5, maxRadius=300)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

            # 원 중심 좌표와 반지름을 이용하여 중심 계산
            center = (x, y)
            pts.appendleft(center)

    # 이전 중심과 현재 중심을 연결하는 선을 그림
    for i in range(1, len(pts)):
        if pts[i - 1] is None or pts[i] is None:
            continue
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # 프레임 보여주기
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # 'q'키를 눌러 while문 종료
    if key == ord("q"):
        break

# 모든 윈도우 종료
cv2.destroyAllWindows()

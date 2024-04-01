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

    # VideoCapture, VideoStream 프레임 조정
    # frame = frame[1] if args.get("video", False) else frame

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

    # 마스크 내의 윤곽선 찾기 및 현재 (x, y) 초기화
    cnts = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    # 하나의 윤곽선이 발견된 경우
    if len(cnts) > 0:
        # 마스크 내에서 가장 큰 윤곽선 찾은 후, 최소 경계 원 및 중심 계산
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        #if M["m00"] == 0 : break
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        if radius > 10:
            cv2.circle(frame, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            print(center)
            
    pts.appendleft(center)

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
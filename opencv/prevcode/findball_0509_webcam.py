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

# ������� �����ϱ� ���� ���Ѱ�, ���Ѱ� ��� ����
colorLower = (0, 138, 138)  
colorUpper = (40, 255, 255) 
 
pts = deque(maxlen=args["buffer"])
    
vs = cv2.VideoCapture('http://192.168.105.190:4747/video')

# ī�޶� ���� ������ �����ϱ� ���� �ߴ� �ð� �ο�
time.sleep(2.0)

golfball_size = 10

while True:
    # ���� ������ ���
    _, frame = vs.read()

    # VideoCapture, VideoStream ������ ����
    # frame = frame[1] if args.get("video", False) else frame

    # �������� ���� ���ϸ� ���� ����
    if frame is None:
        break

    # ������ ũ�� ����, ���� ó��, HSV �� �������� ��ȯ
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    # ������� ���� ����ũ ���� ��, ����ũ ���� deliations�� erotions�� ����
    mask = cv2.inRange(hsv, colorLower, colorUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # Canny Edge Detection�� ����Ͽ� ���� ����
    edges = cv2.Canny(mask, 50, 150)

    # ����ũ ���� ������ ã�� �� ���� (x, y) �ʱ�ȭ
    cnts = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    # �ϳ��� �������� �߰ߵ� ���
    if len(cnts) > 0:
        # ����ũ ������ ���� ū ������ ã�� ��, �ּ� ��� �� �� �߽� ���
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        if M["m00"] == 0 : M["m00"] = 1
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        if radius > golfball_size:
            cv2.circle(frame, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            print(center)
            
    pts.appendleft(center)

    # ������ �����ֱ�
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # 'q'Ű�� ���� while�� ����
    if key == ord("q"):
        break

# ��� ������ ����
cv2.destroyAllWindows()
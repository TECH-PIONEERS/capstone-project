import cv2
import numpy as np
from picamera2 import Picamera2

#picamera2 객체 생성 및 설정
picam2 = Picamera2()
picam2.video_configuration.controls.FrameRate = 60.0
picam2.preview_configuration.main.size=(640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.start()

# 색상 설정하는곳 BGR임에 유의할것
lower_bgr = np.array([150, 250, 250])
upper_bgr = np.array([180, 255, 255])


while True:
    #카메라에서 프레임 캡처
    frame = picam2.capture_array()


    # BGR이미지를 HSV로 전환
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #마스크 생성 (색상 내 영역 검출)
    mask = cv2.inRange(hsv_frame, lower_bgr, upper_bgr)

    # 원본 이미지와 비트 연산 합성
    # result = cv2.bitwise_and(frame, frame, mask=mask)

    # 결과 이미지 출력
    cv2.imshow('Frame', frame)
    cv2.imshow('Mask', mask)
    # cv2.imshow('Result', result)

    # 'q' 키를 누르면 루프 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

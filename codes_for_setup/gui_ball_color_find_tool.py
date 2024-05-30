import cv2
import numpy as np
from picamera2 import Picamera2

# Picamera2 객체 초기화 및 설정
picam2 = Picamera2()
picam2.video_configuration.controls.FrameRate = 60.0
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.start()

# 트랙바 위치를 가져오는 함수
def get_trackbar_values():
    lower_r = cv2.getTrackbarPos('Lower R', 'Trackbars')
    lower_g = cv2.getTrackbarPos('Lower G', 'Trackbars')
    lower_b = cv2.getTrackbarPos('Lower B', 'Trackbars')
    upper_r = cv2.getTrackbarPos('Upper R', 'Trackbars')
    upper_g = cv2.getTrackbarPos('Upper G', 'Trackbars')
    upper_b = cv2.getTrackbarPos('Upper B', 'Trackbars')
    return (lower_r, lower_g, lower_b, upper_r, upper_g, upper_b)

# 트랙바를 위한 윈도우 생성
cv2.namedWindow('Trackbars')

# 하위 RGB 값을 위한 트랙바 생성
cv2.createTrackbar('Lower R', 'Trackbars', 0, 255, lambda x: None)
cv2.createTrackbar('Lower G', 'Trackbars', 0, 255, lambda x: None)
cv2.createTrackbar('Lower B', 'Trackbars', 0, 255, lambda x: None)

# 상위 RGB 값을 위한 트랙바 생성
cv2.createTrackbar('Upper R', 'Trackbars', 255, 255, lambda x: None)
cv2.createTrackbar('Upper G', 'Trackbars', 255, 255, lambda x: None)
cv2.createTrackbar('Upper B', 'Trackbars', 255, 255, lambda x: None)

while True:
    # 카메라에서 프레임 캡처
    frame = picam2.capture_array()

    # 트랙바의 현재 위치 가져오기
    lower_r, lower_g, lower_b, upper_r, upper_g, upper_b = get_trackbar_values()
    lower_rgb = np.array([lower_b, lower_g, lower_r])
    upper_rgb = np.array([upper_b, upper_g, upper_r])

    # 지정된 RGB 범위에 대한 마스크 생성
    mask = cv2.inRange(frame, lower_rgb, upper_rgb)

    # 마스크를 프레임에 적용
    #result = cv2.bitwise_and(frame, frame, mask=mask)

    # 원본 프레임, 마스크 및 결과를 화면에 표시
    cv2.imshow('Frame', frame)
    cv2.imshow('Mask', mask)
    #cv2.imshow('Result', result)

    # 'q' 키를 누르면 루프 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 자원 해제
picam2.stop()
cv2.destroyAllWindows()

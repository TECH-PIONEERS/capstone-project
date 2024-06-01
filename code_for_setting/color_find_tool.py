import cv2
import numpy as np
from picamera2 import Picamera2


def camera_calibration(image):
    # 카메라 보정 함수 
    # image는 picam2.capture_array()로 받아온 frame
    
    # 최종 버전: v6
    fx = 326.819
    fy = 329.259
    cx = 321.455
    cy = 198.692
    k1 = -0.298901
    k2 = 0.072073
    p1 = 0.001761
    p2 = -0.000953

    # 카메라 매트릭스와 왜곡 계수 정의
    mtx = np.array([[fx, 0, cx],
                    [0, fy, cy],
                    [0, 0, 1]])
    dist = np.array([[k1, k2, p1, p2]])

    # 입력 이미지의 크기 가져오기
    h, w = image.shape[:2]

    # 최적의 새 카메라 매트릭스 계산
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    # 이미지를 새 카메라 매트릭스에 맞게 왜곡 보정
    dst = cv2.undistort(image, mtx, dist, None, newcameramtx)

    # ROI(관심 영역) 추출
    x, y, w, h = roi
    dst = dst[y:y+h, x:x+w]

    return dst




#picamera2 객체 생성 및 설정
picam2 = Picamera2()
picam2.video_configuration.controls.FrameRate = 60.0
picam2.preview_configuration.main.size=(640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.start()

# 색상 설정하는곳 BGR임에 유의할것
lower_bgr = np.array([90, 190, 190])
upper_bgr = np.array([180, 255, 255])


while True:
    #카메라에서 프레임 캡처
    frame = picam2.capture_array()
    frame = camera_calibration(frame)


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

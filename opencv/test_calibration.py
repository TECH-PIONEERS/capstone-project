import cv2
import numpy as np
from picamera2 import Picamera2

def camera_calibration(image):
    # v2
    fx = 335.827093
    fy = 335.827093
    cx = 300.000000
    cy = 200.000000
    k1 = -0.354948
    k2 = 0.102152
    p1 = -0.041716
    p2 = -0.002760

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


def main():
    picam2 = Picamera2()
    picam2.preview_configuration.main.size=(600,400)
    picam2.preview_configuration.main.format="RGB888"
    picam2.start()

    while True:
        frame = picam2.capture_array()

        cali_result = camera_calibration(frame)
        
        # 프레임 출력
        cv2.imshow("Webcam", frame)
        cv2.imshow("cali", cali_result)
        
        # 'q' 키를 누르면 루프 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # VideoCapture 객체와 윈도우 종료
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

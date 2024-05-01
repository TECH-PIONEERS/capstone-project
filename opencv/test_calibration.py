import cv2
import numpy as np
from picamera2 import Picamera2

def camera_calibration(image):

    # 카메라 매트릭스와 왜곡 계수 정의
    mtx = np.array([[1223.742488, 0, 941.000000],
                    [0, 1223.742488, 710.000000],
                    [0, 0, 1]])
    dist = np.array([[-0.410419, 0.150130, 0.014093, -0.001272]])

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

        frame = camera_calibration(frame)
        
        # 프레임 출력
        cv2.imshow("Webcam", frame)
        
        # 'q' 키를 누르면 루프 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # VideoCapture 객체와 윈도우 종료
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

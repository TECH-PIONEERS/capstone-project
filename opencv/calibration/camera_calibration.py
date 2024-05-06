import numpy as np
import cv2

def camera_calibration(image_path):
    # 이미지 읽기
    image = cv2.imread(image_path)

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

result_image = camera_calibration("cali_test.png")
cv2.imshow("Calibrated Image", result_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

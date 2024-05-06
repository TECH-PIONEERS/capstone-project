import cv2
import numpy as np

# 노랑색을 검출하기 위한 상한값, 하한값 경계 정의
#colorLower = (60, 246, 230)  
#colorUpper = (120, 213, 187) 

colorLower = (0, 138, 138)  
colorUpper = (50, 255, 255) 

# 이미지 로드
image = cv2.imread('302_ball_1.png')

# HSV로 변환
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 노란색 범위에 해당하는 마스크 생성
mask = cv2.inRange(hsv, colorLower, colorUpper)

# 마스크를 이용하여 색상 부분 추출
color_region = cv2.bitwise_and(image, image, mask=mask)

# 그레이스케일 변환
gray = cv2.cvtColor(color_region, cv2.COLOR_BGR2GRAY)

cv2.imshow("Circles", gray)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 가우시안 블러 적용 (노이즈 제거)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# 허프 변환을 사용하여 원 검출
circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                            param1=50, param2=30, minRadius=1, maxRadius=10)

# 원이 검출되었는지 확인
if circles is not None:
    # 원이 검출되었다면 (반지름, x좌표, y좌표) 형태로 변환하여 반지름의 크기순으로 정렬
    circles = np.round(circles[0, :]).astype("int")
    circles = sorted(circles, key=lambda x: x[2])  # 원의 반지름을 기준으로 정렬

    # 검출된 원을 원본 이미지에 그리기
    for (x, y, r) in circles:
        cv2.circle(image, (x, y), r, (0, 255, 0), 4)  # 원 그리기
        cv2.rectangle(image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)  # 원의 중심 그리기

    # 결과 이미지 출력
    cv2.imshow("Circles", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("원을 찾을 수 없습니다.")
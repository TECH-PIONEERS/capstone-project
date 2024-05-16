from picamera2 import Picamera2
import cv2 
import numpy as np 

def get_RBG_in_image(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONUP:
        print("마우스가 눌린 위치의 BGR값은 : {}".format(param['image'][y,x,:]))

    if event == cv2.EVENT_RBUTTONUP:
        print('마우스오른쪽 버튼이 눌린위치와 비슷한 색상을 가진 픽셀만 뽑기')
        threshold = 20
        value = param['image'][y,x,:]
        mask = cv2.inRange(param['imaqe'],value - threshold, value + threshold )
        range_image = cv2.bitwise_and(param['image'], param['image'], mask=mask)
        cv2.imshow("range_image",range_image)
    return 

def main():
    picam2 = Picamera2()
    picam2.preview_configuration.main.size=(640,480)
    picam2.preview_configuration.main.format="RGB888"
    picam2.start()

    while True:
        frame = picam2.capture_array()

        param = {
            'image' : frame
        }
        cv2.imshow('image', frame)
        cv2.setMouseCallback('image', get_RBG_in_image, param)
        cv2.waitKey(0)

        # 프레임 출력
        cv2.imshow("cali", frame)
        
        # 'q' 키를 누르면 루프 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # VideoCapture 객체와 윈도우 종료
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
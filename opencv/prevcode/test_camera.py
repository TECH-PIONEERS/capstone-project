import cv2
from picamera2 import Picamera2

def main():
    picam2 = Picamera2()
    picam2.preview_configuration.main.size=(600,400)
    picam2.preview_configuration.main.format="RGB888"
    picam2.start()

    while True:
        frame = picam2.capture_array()
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

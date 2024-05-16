import cv2
from picamera2 import Picamera2

def main():
    picam2 = Picamera2()
    picam2.preview_configuration.main.size=(640,480)
    picam2.preview_configuration.main.format="RGB888"
    picam2.start()
    i=0
    while True:
        frame = picam2.capture_array()        

        cv2.imshow("Webcam", frame)

        # ??? ?? ?? ??? ??
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.waitKey(1) & 0xFF == ord('c'):  # 'c' ?? ?? ? ?? ??
            capture_image(frame, i)
            i+=1

    picam2.stop()  # picamera2? release() ???? ???? ??? ??
    cv2.destroyAllWindows()

def capture_image(frame,i):
    image_name = f"image3/zmg{i+1}.jpg"
    cv2.imwrite(image_name, frame)
    print(f"capture {i+1}")

if __name__ == "__main__":
    main()

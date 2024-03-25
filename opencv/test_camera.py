import cv2

def main():
    # 로지텍 웹캠에 대한 VideoCapture 객체 생성
    cap = cv2.VideoCapture(0)  # 0은 기본 웹캠을 나타냅니다. 다른 웹캠을 사용하려면 해당 번호를 변경하세요.

    # VideoCapture 객체가 올바르게 열렸는지 확인
    if not cap.isOpened():
        print("웹캠이 열리지 않았습니다. 확인 후 다시 시도하세요.")
        return

    # 영상 출력 루프
    while True:
        # 프레임 읽기
        ret, frame = cap.read()

        # 프레임 읽기가 실패하면 루프 종료
        if not ret:
            print("프레임을 읽을 수 없습니다.")
            break

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

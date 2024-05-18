import cv2
import numpy as np

# 전역 변수를 사용하여 클릭한 좌표 저장
ir_points = []
pi_points = []

def click_event_ir(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        ir_points.append((x, y))
        cv2.circle(ir_frame_display, (x, y), 5, (255, 0, 0), -1)
        cv2.imshow('IR Video', ir_frame_display)

def click_event_pi(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pi_points.append((x, y))
        cv2.circle(pi_frame_display, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow('PiCamera Video', pi_frame_display)

def find_corresponding_points():
    ir_pts = np.array(ir_points, dtype=np.float32)
    pi_pts = np.array(pi_points, dtype=np.float32)
    return ir_pts, pi_pts

def compute_homography(ir_points, pi_points):
    H, mask = cv2.findHomography(ir_points, pi_points, cv2.RANSAC, 5.0)
    return H

def map_ir_to_pi(ir_frame, H):
    pi_frame = cv2.warpPerspective(ir_frame, H, (ir_frame.shape[1], ir_frame.shape[0]))
    return pi_frame

# 예시: IR 카메라 영상과 PiCamera 영상을 실시간으로 로드
ir_cap = cv2.VideoCapture(0)
pi_cap = cv2.VideoCapture(1)

cv2.namedWindow('IR Video')
cv2.setMouseCallback('IR Video', click_event_ir)

cv2.namedWindow('PiCamera Video')
cv2.setMouseCallback('PiCamera Video', click_event_pi)

while True:
    ret_ir, ir_frame = ir_cap.read()
    ret_pi, pi_frame = pi_cap.read()
    
    if not ret_ir or not ret_pi:
        break
    
    ir_frame_display = ir_frame.copy()
    pi_frame_display = pi_frame.copy()

    cv2.imshow('IR Video', ir_frame_display)
    cv2.imshow('PiCamera Video', pi_frame_display)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('c'):
        # 대응점이 충분한지 확인
        if len(ir_points) >= 4 and len(pi_points) >= 4:
            ir_points_np, pi_points_np = find_corresponding_points()
            H = compute_homography(ir_points_np, pi_points_np)

            # 호모그래피를 사용하여 IR 카메라의 영상을 PiCamera 영상에 보정
            pi_frame_corrected = map_ir_to_pi(ir_frame, H)
            cv2.imshow('Corrected PiCamera Video', pi_frame_corrected)
        else:
            print("적어도 4개의 대응점을 선택해야 합니다.")

cv2.destroyAllWindows()
ir_cap.release()
pi_cap.release()

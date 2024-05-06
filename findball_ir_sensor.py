import serial
import cv2
import numpy as np
import time
from picamera2 import Picamera2
from collections import deque
import argparse
import imutils
import threading 
import utils 

lf = b'\n'  # Linefeed in ASCII
myString = None

# Open the serial port
# Replace '/dev/ttyUSB0' with your actual serial port
myPort = serial.Serial('/dev/ttyUSB0', 19200)
time.sleep(2)  # Wait for serial connection to establish

# Clear serial buffer
myPort.reset_input_buffer()

flag = 0
start_x, start_y, end_x, end_y = 0, 0, 0, 0
previous_frame = None
pts = deque(maxlen=64)

# Function to check if circles go out of the screen boundary
def check_circles_out_of_screen(circles, SCREEN_WIDTH):
    # Set the boundary
    BOUNDARY_X = SCREEN_WIDTH // 3 # 1/3 of the screen
    for (x, y, r) in circles:
        if x - r < BOUNDARY_X:
            print("Circle is going out of screen boundary!")
            if not utils.is_beeping:
                beep_thread = threading.Thread(target=utils.generate_alert_beep)
                beep_thread.start()
                print("Running alert beep")

# Function to get the position of mouse click
def get_position(event, x, y, flags, params):
    global start_x 
    global start_y 
    global end_x 
    global end_y 
    global flag
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Clicked at (x={}, y={})".format(x, y))
        if flag == 0:
            start_x = x
            start_y = y
            flag = 1
        elif flag == 1:
            end_x = x
            end_y = y
            flag = 2  # Set flag to 2 for cropping
            utils.pixel_to_cm(end_y-start_y)

# Argument parsing for video file and buffer size
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
args = vars(ap.parse_args())

# HSV color range for detecting circles
colorLower = (0, 138, 138)  
colorUpper = (40, 255, 255) 

picam2 = Picamera2()
picam2.preview_configuration.main.size=(600, 400)
picam2.preview_configuration.main.format = "RGB888"
picam2.start()

while True:
    cap = picam2.capture_array()

    # Use previous frame if no current frame is available
    if cap is None:
        print('no frame')
        cap = previous_frame
    else:
        previous_frame = cap

    cap = utils.camera_calibration(cap)

    # Set mouse callback function for getting position
    cv2.setMouseCallback('cap', get_position)
    
    # Crop the frame if flag is 2
    if flag == 2:
        frame = cap[start_y:end_y, start_x:end_x]

        SCREEN_WIDTH = end_x - start_x
        
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
        mask = cv2.inRange(hsv, colorLower, colorUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        edges = cv2.Canny(mask, 50, 150)

        circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1, minDist=5,
                                param1=70, param2=30, minRadius=2, maxRadius=300)

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

                center = (x, y)
                print(center)
                pts.appendleft(center)
            
            check_circles_out_of_screen(circles, SCREEN_WIDTH)

        # Draw trails of previous positions
        for i in range(1, len(pts)):
            if pts[i - 1] is None or pts[i] is None:
                continue
            thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
            cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

        cv2.imshow("Frame", frame)
    else:
        cv2.imshow('cap', cap)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cv2.destroyAllWindows()

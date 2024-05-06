import serial
import cv2
import numpy as np
import time

lf = b'\n'  # Linefeed in ASCII
myString = None

# Open the serial port
# Replace '/dev/ttyUSB0' with your actual serial port
myPort = serial.Serial('/dev/ttyUSB0', 19200)
time.sleep(2)  # Wait for serial connection to establish

def setup():
    # Clear serial buffer
    myPort.reset_input_buffer()

def draw():
    global myString
    while True:
        myString = myPort.readline().decode().strip()
        if myString:
            output = list(map(int, myString.split(',')))
            print(output)
            # Assuming the received data represents coordinates
            x1, y1, x2, y2 = output[:4]  # Assuming x1, y1, x2, y2
            # Create a black image
            img = np.zeros((800, 800, 3), dtype=np.uint8)
            # Draw circles on the image
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), -1)  # Red circle at (x1, y1)
            cv2.circle(img, (x2, y2), 10, (0, 255, 0), -1)  # Green circle at (x2, y2)
            # Show the image
            cv2.imshow('Image', img)
            cv2.waitKey(1)

setup()
draw()

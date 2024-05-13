import serial
import cv2
import numpy as np
import time

lf = b'\n'  # Linefeed in ASCII
myString = None
myString1 = None

# Open the serial port
# Replace '/dev/ttyUSB0' with your actual serial port
myPort = serial.Serial('/dev/ttyUSB0', 19200)
myPort1 = serial.Serial('/dev/ttyUSB1', 19200)
time.sleep(2)  # Wait for serial connection to establish

def is_valid_string(input_string):
    for char in input_string:
        if not (char.isdigit() or char == ','):
            return False
    return True

def setup():
    # Clear serial buffer
    myPort.reset_input_buffer()
    myPort1.reset_input_buffer()

def draw(): 
    global myString, myString1
    while True:
        myString = myPort.readline().decode().rstrip()
        myString1 = myPort1.readline().decode().rstrip()
        
        if myString or myString1:
            if is_valid_string(myString) and is_valid_string(myString1):
                # print(myString)
                # print(myString1)
                output = list(map(float, myString.split(',')))
                output1 = list(map(float, myString1.split(',')))
                output = list(map(int, output))
                output1 = list(map(int, output1))
                print(f"output 0 : {output}")
                print(f"output 1 : {output1}")
                # print(output1)
                x1, x2, y1, y2, x3, x4, y3, y4 = 0, 0, 0, 0, 0, 0, 0, 0
                # Assuming the received data represents coordinates
                if output[0]:
                    x1 = output[0]  # Assuming x1, y1, x2, y2
                if len(output) >= 2:
                    y1 = output[1]  # Assuming x1, y1, x2, y2
                if len(output) >= 3:
                    x2 = output[2]  # Assuming x1, y1, x2, y2
                if len(output) >= 4:
                    y2 = output[3]  # Assuming x1, y1, x2, y2
                
                if output1[0]:
                    x3 = output1[0]  # Assuming x1, y1, x2, y2
                if len(output1) >= 2:
                    y3 = output1[1]  # Assuming x1, y1, x2, y2
                if len(output1) >= 3:
                    x4 = output1[2]  # Assuming x1, y1, x2, y2
                if len(output1) >= 4:
                    y4 = output1[3]  # Assuming x1, y1, x2, y2
                
                # Create a black image
                img = np.zeros((800, 800, 3), dtype=np.uint8)
                # Draw circles on the image
                if x1 and y1:
                    cv2.circle(img, (x1, y1), 10, (0, 0, 255), -1)  # Red circle at (x1, y1)
                if x2 and y2:
                    cv2.circle(img, (x2, y2), 10, (0, 255, 0), -1)  # Green circle at (x2, y2)
                
                if x3 and y3:
                    cv2.circle(img, (y3, x3), 10, (255, 0, 255), -1)  # Red circle at (x1, y1)
                if x4 and y4:
                    cv2.circle(img, (y4, x4), 10, (0, 255, 255), -1)  # Green circle at (x2, y2)

                # Show the image
                cv2.imshow('Image', img)
                cv2.waitKey(1)

# setup()
draw()

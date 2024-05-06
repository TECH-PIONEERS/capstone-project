import serial
import time
import math

led_gap = 34.004  # mm
led_index = 1  # LED의 인덱스 (0부터 시작)
camera_angle = 33  # degrees
camera_resolution = 128

lf = b'\n'  # Linefeed in ASCII
myString = None

# Open the serial port
# Replace 'dev/ttyUSB0' with your actual serial port
myPort = serial.Serial('/dev/ttyUSB0', 19200)
#myPort = serial.Serial('COM6', 19200)
time.sleep(2)  # Wait for serial connection to establish

def setup():
    # Clear serial buffer
    myPort.reset_input_buffer()
    #size(800, 800)
    #frameRate(30)

def draw():
    global myString
    #background(77)
    print(myPort)
    while True:#myPort.in_waiting > 0:
        myString = myPort.readline().decode().strip()
        #print(myString)
        if myString:
            output = list(map(int, myString.split(',')))
            #print(myString)  # display the incoming string
            print(output)
            print(calculate_led_distance(output[0] - output[2], camera_angle, camera_resolution))
            #xx, yy, ww, zz, xxx, yyy, www, zzz = output



def calculate_led_distance(led_gap, led_index, camera_angle, camera_resolution):
    # 카메라의 시야각을 라디안으로 변환
    camera_angle_rad = math.radians(camera_angle)
    
    # 물체가 카메라에 보이는 영역 계산
    visible_object_width = led_gap * (camera_resolution - 1)
    
    # 물체와 카메라 사이의 거리 계산
    object_distance = visible_object_width / (2 * math.tan(camera_angle_rad / 2))
    
    # LED의 카메라로부터의 거리 계산
    led_distance = object_distance - led_index * led_gap
    
    return led_distance


setup()
draw()



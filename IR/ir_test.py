import serial
import time

lf = b'\n'  # Linefeed in ASCII
myString = None

# Open the serial port
# Replace 'dev/ttyUSB0' with your actual serial port
myPort = serial.Serial('/dev/ttyAMA10', 19200)
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
        print(myString)
        if myString:
            output = list(map(int, myString.split(',')))
            print(myString)  # display the incoming string
            print(output)
            xx, yy, ww, zz, xxx, yyy, www, zzz = output

setup()
draw()
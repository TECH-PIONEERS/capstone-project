import serial
import time


#ser = serial.Serial('/dev/ttyAMA10',19200)
ser = serial.Serial('/dev/ttyUSB0',19200)
print(ser)
time.sleep(2)  
i=0
#try:
while True:
    print(i)
    data = ser.readline()
    print(data)
        # if ser.in_waiting > 0:
        #     data = ser.readline().decode().strip()
        #     print("Received:", data)
# except KeyboardInterrupt:
#     print("Keyboard Interrupt detected. Exiting...")
# finally:
#     ser.close()

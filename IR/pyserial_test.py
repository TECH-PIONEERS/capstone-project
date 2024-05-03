import serial
import time


#ser = serial.Serial('/dev/ttyAMA10',19200)
ser = serial.Serial('/dev/ttyUSB0',19200)
ser1 = serial.Serial('/dev/ttyUSB1',19200)
#print(ser)
time.sleep(2)  

#try:
while True:
    # data = ser.readline()
    # data1 = ser1.readline()
    # print(data)
    if ser.in_waiting > 0 and ser1.in_waiting > 0:
        data = ser.readline().strip()
        data1 = ser1.readline().strip()
        print("data 0 Received:", data)
        print("data 1 Received:", data1)
    #time.sleep(2)  
# except KeyboardInterrupt:
#     print("Keyboard Interrupt detected. Exiting...")
# finally:
#     ser.close()

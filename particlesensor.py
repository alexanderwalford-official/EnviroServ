import serial, time

ser = serial.Serial('/dev/ttyUSB0')

while True:
        data = []
        for index in range(0,10):
                datanum = ser.read()
                data.append(datanum)
                
        pmten = int.from_bytes(b''.join(data[4:6]), byteorder='little')
        print(pmten)
        time.sleep(10)
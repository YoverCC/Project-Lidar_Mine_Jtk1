import serial
ser = serial.Serial('/dev/ttyACM0', baudrate = 9600)
ser_bytes = ser.readline()
print(ser_bytes)


# Importing Sensor Data Into An SQLite Database
# Renovate Software LTD 2021
# Alexander Walford
#
# Sensors:
# SDS011
# SensorHub
# PiJuice


import smbus
import time
import datetime
import os
import sqlite3
from sqlite3 import Error
import psutil
import serial
from pijuice import PiJuice


DEVICE_BUS = 1
DEVICE_ADDR = 0x17

TEMP_REG = 0x01
LIGHT_REG_L = 0x02
LIGHT_REG_H = 0x03
STATUS_REG = 0x04
ON_BOARD_TEMP_REG = 0x05
ON_BOARD_HUMIDITY_REG = 0x06
ON_BOARD_SENSOR_ERROR = 0x07
BMP280_TEMP_REG = 0x08
BMP280_PRESSURE_REG_L = 0x09
BMP280_PRESSURE_REG_M = 0x0A
BMP280_PRESSURE_REG_H = 0x0B
BMP280_STATUS = 0x0C
HUMAN_DETECT = 0x0D

bus = smbus.SMBus(DEVICE_BUS)

aReceiveBuf = []

aReceiveBuf.append(0x00) 


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn


def create_record(conn, savedata):
    """
    Create a new record
    :param conn:
    :param ResourceLog:
    :return:
    """
    sql = ''' INSERT INTO MainFrame_sensordata(datetime,dustlevel,enviro_temprature,sys_temprature,brightness,humidity,barometer_temperature,barometer_pressure,human_detection,batterylevel)
              VALUES(?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, savedata)
    conn.commit()
    return cur.lastrowid

def main():
    # Declaration of blank, initial variables.
    enviro_temprature = ""
    sys_temprature = ""
    brightness = ""
    humidity = ""
    barometer_temperature = ""
    barometer_pressure = ""
    human_detection = ""
    dustlevel = ""
    batterylevel = ""
    
    # Get the battery level
    pijuice = PiJuice(1, 0x14)
    batterylevel = pijuice.status.GetChargeLevel()[9] * 10 + pijuice.status.GetChargeLevel()[10]
    print("Battery Level: " + str(batterylevel) + "%")
    
    # Get the SensorHub data range.
    for i in range(TEMP_REG,HUMAN_DETECT + 1):
        aReceiveBuf.append(bus.read_byte_data(DEVICE_ADDR, i))
    
    # Overrange detection and malfunctioning for each sensor.
    if aReceiveBuf[STATUS_REG] & 0x01 :
        print("Off-chip temperature sensor overrange!")
        
    elif aReceiveBuf[STATUS_REG] & 0x02 :
        print("No external temperature sensor!")
        
    else :
        print("Current off-chip sensor temperature = %d Celsius" % aReceiveBuf[TEMP_REG])
        enviro_temprature = "%d" % aReceiveBuf[TEMP_REG]
        
    if aReceiveBuf[STATUS_REG] & 0x04 :
        print("Onboard brightness sensor overrange!")
        
    elif aReceiveBuf[STATUS_REG] & 0x08 :
        print("Onboard brightness sensor failure!")
        
    else :
        print("Current onboard sensor brightness = %d Lux" % (aReceiveBuf[LIGHT_REG_H] << 8 | aReceiveBuf[LIGHT_REG_L]))
        brightness = "%d" % (aReceiveBuf[LIGHT_REG_H] << 8 | aReceiveBuf[LIGHT_REG_L])
        
    print("Current onboard sensor temperature = %d Celsius" % aReceiveBuf[ON_BOARD_TEMP_REG])
    sys_temprature = "%d" % aReceiveBuf[ON_BOARD_TEMP_REG]
    
    print("Current onboard sensor humidity = %d %%" % aReceiveBuf[ON_BOARD_HUMIDITY_REG])
    humidity = "%d" % aReceiveBuf[ON_BOARD_HUMIDITY_REG]
   
    if aReceiveBuf[ON_BOARD_SENSOR_ERROR] != 0 :
        print("Onboard temperature and humidity sensor data may not be up to date!")

    if aReceiveBuf[BMP280_STATUS] == 0 :
        print("Current barometer temperature = %d Celsius" % aReceiveBuf[BMP280_TEMP_REG])
        barometer_temperature = "%d" % aReceiveBuf[BMP280_TEMP_REG]
        
        print("Current barometer pressure = %d pascal" % (aReceiveBuf[BMP280_PRESSURE_REG_L] | aReceiveBuf[BMP280_PRESSURE_REG_M] << 8 | aReceiveBuf[BMP280_PRESSURE_REG_H] << 16))
        barometer_pressure = "%d" % (aReceiveBuf[BMP280_PRESSURE_REG_L] | aReceiveBuf[BMP280_PRESSURE_REG_M] << 8 | aReceiveBuf[BMP280_PRESSURE_REG_H] << 16)
    
    else :
        print("Onboard barometer works abnormally!")

    if aReceiveBuf[HUMAN_DETECT] == 1 :
        print("Live body detected within 5 seconds!")
        os.system("raspistill -o Desktop/movement.png -w 1920 -h 1080") # Take a photo
        human_detection = "1"
        
    else:
        print("No humans detected!")     
        human_detection = "0"        
        
    # SDS011 Dust Sensor - Get Data
    ser = serial.Serial('/dev/ttyUSB0')
    data = []
    for index in range(0,10):
        datanum = ser.read()
        data.append(datanum)               
    dustlevel = int.from_bytes(b''.join(data[4:6]), byteorder='little')
    print("Dust Level: " + str(dustlevel))
        
    database = r"db.sqlite3"
    # create a database connection
    conn = create_connection(database)
    with conn:
        try:
            # create a new record
            dateandtime = datetime.datetime.now()
            savedata = (dateandtime, dustlevel, enviro_temprature, sys_temprature, brightness, humidity, barometer_temperature, barometer_pressure, human_detection, batterylevel)
            create_record(conn, savedata)
            print("Saved the sensor data correctly.")
            print("System is configured to run every 10 minutes.")
            time.sleep(600) # Sleep for 10 minutes.
            main()     
        except Error as e:
            print(e) # Print database writing error.
            
main()
# Importing Sensor Data Into An SQLite Database
# Renovate Software LTD 2021
# Alexander Walford
#
# Sensors:
# SDS011
# SensorHub
# PiJuice
# I2C LCD Display
# GPS
# 3G Cellular


import smbus
import time
import datetime
import os
import sqlite3
from sqlite3 import Error
import psutil
import serial
from pijuice import PiJuice
import I2C_LCD_driver
import socket
import fcntl
import struct
import serial


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
ser = serial.Serial('/dev/ttyACM3')

bus = smbus.SMBus(DEVICE_BUS)
aReceiveBuf = []
aReceiveBuf.append(0x00) 
serGPS = serial.Serial('/dev/ttyACM3')


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
    sql = ''' INSERT INTO MainFrame_SensorData(datetime,dustlevel,enviro_temprature,sys_temprature,brightness,humidity,barometer_temperature,barometer_pressure,human_detection,batterylevel)
              VALUES(?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, savedata)
    conn.commit()
    return cur.lastrowid
    
def create_record2(conn, savedata2):
    """
    Create a new record
    :param conn:
    :param Diagnostic_Issue:
    :return:
    """
    sql = ''' INSERT INTO MainFrame_Diagnostic_Issue(datetime,issue,severity)
              VALUES(?,?,?,) '''
    cur = conn.cursor()
    cur.execute(sql, savedata2)
    conn.commit()
    return cur.lastrowid
  
def errorRecord(conn, savedata2, issuenow, severitynow):
    # create a new record
    dateandtime = datetime.datetime.now()
    savedata2 = (dateandtime, issuenow, severitynow)
    create_record2(conn, savedata2)
    conn.close()
    print("Saved the error data correctly.")

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
    ISSUE_COUNTER = 0
    GPSdata = str(serGPS.readline())
    
    # GPS monitoring
    if "b'$GNRMC" in str(GPSdata):
        # GPRMC = Recommended minimum specific GPS/Transit data
        # Reading the GPS fix data is an alternative approach that also works
        parts = GPSdata.split(",")
        if parts[2] == 'V':
            # V = Warning, most likel. There aren't any satellites in view...
            print("GPS receiver warning. Ensure that the device has a clear view to the sky.")
            mylcd = I2C_LCD_driver.lcd()
            mylcd.lcd_clear()
            mylcd.lcd_display_string("GPS Warn", 1)
            mylcd.lcd_display_string("Unclear View", 2)
        else:
            # Get the position data that was transmitted with the GPRMC message
            # In this example, I'm only interested in the longitude and latitude
            # for other values, that can be read, refer to: http://aprs.gids.nl/nmea/#rmc
            longitude = formatDegreesMinutes(parts[5], 3)
            latitude = formatDegreesMinutes(parts[3], 2)
            print("Your position: lon = " + str(longitude) + ", lat = " + str(latitude))
            mylcd = I2C_LCD_driver.lcd()
            mylcd.lcd_clear()
            mylcd.lcd_display_string("GPS Rec", 1)
            mylcd.lcd_display_string("Collected", 2)
    else:
        # Handle other NMEA messages and unsupported strings
        mylcd = I2C_LCD_driver.lcd()
        mylcd.lcd_clear()
        mylcd.lcd_display_string("GPS Rec", 1)
        mylcd.lcd_display_string("ERROR", 2)
        print(GPSdata)
        pass
    
    # Get the battery level
    pijuice = PiJuice(1, 0x14)
    batterylevel = int(pijuice.status.GetChargeLevel()['data'])
    print("Battery Level: " + str(pijuice.status.GetChargeLevel()['data']) + "%")
    
    # Get the SensorHub data range.
    for i in range(TEMP_REG,HUMAN_DETECT + 1):
        aReceiveBuf.append(bus.read_byte_data(DEVICE_ADDR, i))
    
    # Overrange detection and malfunctioning for each sensor.
    if aReceiveBuf[STATUS_REG] & 0x01 :
        issuenow = "Off-Chip Temperature: Issue detected (over range)."
        severitynow = "High"
        ISSUE_COUNTER = ISSUE_COUNTER + 1
        errorRecord(conn, savedata2, issuenow, severitynow)
        
    elif aReceiveBuf[STATUS_REG] & 0x02 :
        issuenow = "Issue Detected: No external temperature sensor."
        severitynow = "Medium"
        ISSUE_COUNTER = ISSUE_COUNTER + 1
        errorRecord(conn, savedata2, issuenow, severitynow)
        
    else:
        print("Current off-chip sensor temperature = %d Celsius" % aReceiveBuf[TEMP_REG])
        enviro_temprature = "%d" % aReceiveBuf[TEMP_REG]
        
    if aReceiveBuf[STATUS_REG] & 0x04 :
        issuenow = "Onboard brightness: Issue detected (over range)."
        severitynow = "High"
        ISSUE_COUNTER = ISSUE_COUNTER + 1
        errorRecord(conn, savedata2, issuenow, severitynow)
        
    elif aReceiveBuf[STATUS_REG] & 0x08 :
        issuenow = "Onboard Brightness: Issue detected."  
        severitynow = "Medium"
        ISSUE_COUNTER = ISSUE_COUNTER + 1
        errorRecord(conn, savedata2, issuenow, severitynow)
        
    else:
        print("Current onboard sensor brightness = %d Lux" % (aReceiveBuf[LIGHT_REG_H] << 8 | aReceiveBuf[LIGHT_REG_L]))
        brightness = "%d" % (aReceiveBuf[LIGHT_REG_H] << 8 | aReceiveBuf[LIGHT_REG_L])
        
    print("Current onboard sensor temperature = %d Celsius" % aReceiveBuf[ON_BOARD_TEMP_REG])
    sys_temprature = "%d" % aReceiveBuf[ON_BOARD_TEMP_REG]
    
    print("Current onboard sensor humidity = %d %%" % aReceiveBuf[ON_BOARD_HUMIDITY_REG])
    humidity = "%d" % aReceiveBuf[ON_BOARD_HUMIDITY_REG]
   
    if aReceiveBuf[ON_BOARD_SENSOR_ERROR] != 0 :
        issuenow = "Onboard Temperature & Humidity: Issues detected."
        severitynow = "High"
        ISSUE_COUNTER = ISSUE_COUNTER + 1
        errorRecord(conn, savedata2, issuenow, severitynow)

    if aReceiveBuf[BMP280_STATUS] == 0 :
        print("Current barometer temperature = %d Celsius" % aReceiveBuf[BMP280_TEMP_REG])
        barometer_temperature = "%d" % aReceiveBuf[BMP280_TEMP_REG]
        
        print("Current barometer pressure = %d pascal" % (aReceiveBuf[BMP280_PRESSURE_REG_L] | aReceiveBuf[BMP280_PRESSURE_REG_M] << 8 | aReceiveBuf[BMP280_PRESSURE_REG_H] << 16))
        barometer_pressure = "%d" % (aReceiveBuf[BMP280_PRESSURE_REG_L] | aReceiveBuf[BMP280_PRESSURE_REG_M] << 8 | aReceiveBuf[BMP280_PRESSURE_REG_H] << 16)
    
    else:
        # issue with barometer
        issuenow = "Onboard Barometer: Issue detected."
        severitynow = "Medium"
        ISSUE_COUNTER = ISSUE_COUNTER + 1
        errorRecord(conn, savedata2, issuenow, severitynow)

    if aReceiveBuf[HUMAN_DETECT] == 1 :
        print("Live body detected within 5 seconds!")
        os.system("raspistill -o Desktop/movement.png -w 1920 -h 1080") # Take a photo (optional)
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
    # get the IP
    conn = create_connection(database)
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    # create a database connection
    with conn:
        try:
            # display LCD text
            mylcd = I2C_LCD_driver.lcd()
            mylcd.lcd_clear()
            mylcd.lcd_display_string("Sensor Data", 1)
            mylcd.lcd_display_string("Collected", 2)
            time.sleep(2)
            mylcd.lcd_clear()
            mylcd.lcd_display_string("Dust Level:", 1)
            mylcd.lcd_display_string(str(dustlevel), 2)   
            time.sleep(2)
            mylcd.lcd_clear()
            mylcd.lcd_display_string("Environment Temp:", 1)
            mylcd.lcd_display_string(str(enviro_temprature) + "C", 2)   
            time.sleep(2)
            mylcd.lcd_clear()
            mylcd.lcd_display_string("Battery Level:", 1)
            mylcd.lcd_display_string(str(batterylevel) + "%", 2)
            time.sleep(2)
            mylcd.lcd_clear()
            mylcd.lcd_display_string("IP Address:", 1) 
            mylcd.lcd_display_string(str(ip_address), 2)
            time.sleep(2)
            mylcd.lcd_clear()
            if ISSUE_COUNTER == 0:
                mylcd.lcd_display_string("System Status:", 1)
                mylcd.lcd_display_string("Operational", 2)
            else:
                mylcd.lcd_display_string("System Status:", 1)
                mylcd.lcd_display_string(str(ISSUE_COUNTER) + " Issues", 2)
            # end of LCD text, the system status will remain displayed
            # create a new record
            dateandtime = datetime.datetime.now()
            savedata = (dateandtime, dustlevel, enviro_temprature, sys_temprature, brightness, humidity, barometer_temperature, barometer_pressure, human_detection, batterylevel)
            create_record(conn, savedata)
            conn.close()
            print("Saved the sensor data correctly.")
            print("System is configured to run every 2 minutes and 30 seconds.")
            time.sleep(150) # Sleep for 2 minutes 30 seconds.
            main() # run the script again
        except Error as e:
            mylcd = I2C_LCD_driver.lcd()
            mylcd.lcd_display_string("Database", 1)
            mylcd.lcd_display_string("Error", 2)
            time.sleep(2)
            mylcd.lcd_clear()
            mylcd.lcd_display_string("Database", 1)
            mylcd.lcd_display_string("Error", 2)
            time.sleep(2)
            mylcd.lcd_clear()
            mylcd.lcd_display_string("Database", 1)
            mylcd.lcd_display_string("Error", 2)
            print(e) # Print database writing error.
            time.sleep(150) # Sleep for 2 minutes 30 seconds.
            main() # run the script again
            
main()

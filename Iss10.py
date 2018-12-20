# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 11:52:11 2018

@author: jbrought

TODO:
    Database connection error handling:
        - Currently logs data to csv in case of database connection failing
        - Cron tab to restart script every hour? (small amount of missing data)
        - Trying to reconnect causes script to hang
"""

#!/usr/bin/python

#Import necessary packages
import serial
import sys
import mysql.connector as mariadb
import datetime
import csv
import time

#Set serial connection parameters
port = "COM6"
baudrate = 9600
mode = 1
i = 0

#Infinite loop (except for system exits)
while True:
        
    #---------------------------------------------------->
    while True:
        try:
            #Connect to remote database as user jbrought
            mariadb_connection = mariadb.connect(host='51.68.196.174', user='jbrought', password='raspberry17', database='connectorsDB')
            #Set up cursor for row entries
            cursor = mariadb_connection.cursor()
            print("# Successfully connected to database")
            #Connection succeeded without error, so move out of loop
            break
        
        except:
            #If connection fails
            print("# Could not connect to database...")
            time.sleep(5)
            #Check which mode is set (line 26)
            if mode == 1:
                print("# Continuing without connection")
                #Break from loop without db connection
                break
        else:
            #Check which mode is set (line 26)
            print("Trying again in 5 seconds...")
            time.sleep(5)
            #Since connection has failed, continue connection attempt loop
            continue
    
    #Connect to serial port
    #---------------------------------------------------->
    while True:    
        try:
            #Set serial connction parameters 
            ser = serial.Serial(port, baudrate)
            print("# Successfully connected to serial port")
            #Since connection successful, break from serial connection loop
            break
        except:
            print("# Could not connect to serial port, cable unplugged? Trying again in 5 seconds...")
            #sys.exit('Connection to serial port failed so exiting')
            time.sleep(5)
            #Connection failed, so continue serial connection loop
            continue
    
    #---------------------------------------------------->
    #Read serial data and upload/write csv
    while True:            
        try:
            while True:
                try:
                    #Read serial port
                    line = ser.readline()
                    #Flush serial port
                    sys.stdout.flush()
                    #Split the data by comma into array data
                    data = line.decode().split(',')
                    #Code succeeded so break from while loop
                    break
                except PermissionError:
                    print("# Failed to split serial data")
                    continue
                except:
                    sys.exit('Unknown system error during split so exiting')
                    time.sleep(1)
                    
            #Fetch current date and time, put into mySQL datetime format
            datestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #Print received data to the console
            print(datestamp + ", Humidity: " + data[0] + ", Temperature: " + data[1] + ", Insertion: " + data[2] + ", Acceleration: " + data[3])
                    
            
            try:
                #Insert line into mySQL database
                cursor.execute("INSERT INTO connectors (DateTime,Humidity,Temperature,Cycles,G_Force) VALUES (%s,%s,%s,%s,%s)", (datestamp,float(data[0]),float(data[1]),float(data[2]),float(data[3])))
                #Commit data to row
                mariadb_connection.commit()
                #print("# Inserted line into database")
            except:
                #Runs if the data could not be inserted into the database
                print("# Could not insert into database, using csv backup instead")
                #Opens data_backup.csv in append mode, file created if it does not exist
                with open('data_backup.csv', mode='a', newline='') as data_backup:
                    employee_writer = csv.writer(data_backup, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    employee_writer.writerow([datestamp, data[0], data[1], data[2], data[3].strip()])

        except KeyboardInterrupt:
            print("Keyboard interrupt! Closing program")
            print("# Closing serial port")
            ser.close()
            time.sleep(1)
            break
            
        except Exception as e:
            print(e)
            print("# Exception raised, position 4")
            print("# Closing serial port")
            ser.close()
            time.sleep(1)
            break
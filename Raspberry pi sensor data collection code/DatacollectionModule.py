import serial
import threading
import time
import string
import datetime
import pynmea2
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250
import csv

mpu = MPU9250(
    address_ak=AK8963_ADDRESS, 
    address_mpu_master=MPU9050_ADDRESS_68, # In 0x68 Address
    address_mpu_slave=None, 
    bus=1,
    gfs=GFS_1000, 
    afs=AFS_8G, 
    mfs=AK8963_BIT_16, 
    mode=AK8963_MODE_C100HZ)

lat=0 
lng=0
delay=0.009025
spd=0
def getGPS():
	global lat,lng,spd
	while(1):
		port="/dev/ttyAMA0"
		ser=serial.Serial(port, baudrate=9600, timeout=0.2)
		dataout = pynmea2.NMEAStreamReader()
		newdata=ser.readline()
		if(newdata[0:6] == "$GPRMC"):
			newmsg=pynmea2.parse(newdata)
			lat=newmsg.latitude
			lng=newmsg.longitude
			spd=newmsg.spd_over_grnd
			
filename="data"+str(datetime.datetime.now())+".csv"
datafile=open(filename, 'w')
writer = csv.writer(datafile, delimiter=',')
mpu.configure() # Apply the settings to the registers.
t1 = threading.Thread(target=getGPS)
t1.start()
time.sleep(5)
rowlist=[]
def pushdata(l):
	writer.writerows(l)
	print(l[2999][0],"Finished")
try:
	while(1):
		for i in range(3000):
			rowlist.append([datetime.datetime.now()]+mpu.readAccelerometerMaster()+mpu.readGyroscopeMaster()+mpu.readMagnetometerMaster()+[spd]+[lat]+[lng])
			time.sleep(delay)
		print(len(rowlist),rowlist[0][0])
		t2=threading.Thread(target=pushdata,args=(rowlist,))
		t2.start()
		rowlist=[]
except KeyboardInterrupt:
	datafile.close()
finally:
	datafile.close()

#!/usr/bin/env python

import rospy
from std_msgs.msg import String
import serial

def talker():

	pub = rospy.Publisher('chatter', String)
	rospy.init_node('talker')

	ser = serial.Serial('/dev/ttyACM0', baudrate=9600)
	ser.setDTR(False)
	time_to_sleep = rospy.Rate(1)
	time_to_sleep.sleep()
	ser.flushInput()
	ser.setDTR(True)

	
	while not rospy.is_shutdown():
		data = ser.readline() #grado 120
		if not data:
			continue
		angle = int(data[6:9])
		angle_rad = angle*3.1416/180 - 1.5708
		print(angle_rad)
		rospy.loginfo(data)
		pub.publish(String(data))

if __name__=='__main__':
	try:
		talker()
	except rospy.ROSInterruptException:
		pass
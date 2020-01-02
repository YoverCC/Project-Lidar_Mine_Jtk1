#! /usr/bin/env python

import rospy
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
from std_msgs.msg import String
import serial

def talker():

	pub = rospy.Publisher('joint_states',JointState,queue_size = 1)
	pub2 = rospy.Publisher('servo_angle',String, queue_size=10)
	#rospy.init_node('join_state_publisher')
	rospy.init_node('talker')
	msg_angle = JointState()
	msg_angle.header = Header()
	msg_angle.name = ['base_to_arm']

	ser = serial.Serial('/dev/ttyACM0', baudrate=9600)
	ser.setDTR(False)
	# Se reinicia el serial del arduino, para evitar el conflicto del autorestart
	time_to_sleep = rospy.Rate(1)
	time_to_sleep.sleep()
	ser.flushInput()
	ser.setDTR(True)
	time_to_sleep.sleep()
	ser.write('T')
	time_to_sleep.sleep()
	msg_angle.velocity = []
	msg_angle.effort = []
	data_temp = "grado 90"
	
	while not rospy.is_shutdown():
		
		angle = int(data_temp[6:9])
		angle_rad = angle*3.1416/180 - 1.5708
		msg_angle.position = [angle_rad]
		msg_angle.header.stamp = rospy.Time.now()
		pub.publish(msg_angle)
		pub2.publish(data_temp)
		#rospy.loginfo(data_temp)
		data = ser.readline() #grado 120
		if not data:
			continue
		data_temp = data


if __name__ == '__main__':
	try:
		talker()
	except rospy.ROSInterruptException:
		pass

#! /usr/bin/env python

import rospy
from sensor_msgs.msg import JointState
from std_msgs.msg import Header

def talker():
	pub = rospy.Publisher('joint_states',JointState,queue_size = 10)
	rospy.init_node('join_state_publisher')
	#rate = rospy.Rate(500) #500Hz
	msg_angle = JointState()
	msg_angle.header = Header()
	msg_angle.name = ['base_to_arm']
	msg_angle.position = [1.5708]
	msg_angle.velocity = []
	msg_angle.effort = []

	while not rospy.is_shutdown():
		msg_angle.header.stamp = rospy.Time.now()
		pub.publish(msg_angle)
	#	rate.sleep()

if __name__ == '__main__':
	try:
		talker()
	except rospy.ROSInterruptException:
		pass
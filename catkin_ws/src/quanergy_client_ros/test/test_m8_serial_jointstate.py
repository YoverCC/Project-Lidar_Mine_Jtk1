#! /usr/bin/env python

import unittest
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
from time import sleep
import rostest

class TalkerTestCase(unittest.TestCase):
	
	joint_ok = False

	def callback(self,data):
		self.joint_ok = True

	def test_if_module_m8_publishes(self):
		rospy.init_node('test_m8_serial_joint')
		rospy.Subscriber('joint_states', JointState, self.callback)
		counter = 0
		while not rospy.is_shutdown() and counter <5 and (not self.joint_ok):
			sleep(1)
			counter += 1

		self.assertTrue(self.joint_ok)

if __name__ == '__main__':
	rostest.rosrun('quanergy_client_ros', 'test_m8_serial_joint', TalkerTestCase)

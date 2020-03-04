#! /usr/bin/env python

import unittest
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
from time import sleep
import rostest

class TalkerTestCase(unittest.TestCase):
	
	assembler_ok = False

	def callback(self,data):
		self.assembler_ok = True

	def test_if_module_m8_publishes(self):
		rospy.init_node('test_pc2_assembler')
		rospy.Subscriber("/assembled_cloud", PointCloud2, self.callback)
		counter = 0
		while not rospy.is_shutdown() and counter <10 and (not self.assembler_ok):
			sleep(1)
			counter += 1

		self.assertTrue(self.assembler_ok)

if __name__ == '__main__':
	rostest.rosrun('quanergy_client_ros', 'test_pc2_assembler', TalkerTestCase)

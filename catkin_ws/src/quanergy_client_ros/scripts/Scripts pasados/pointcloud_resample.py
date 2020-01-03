#!/usr/bin/env python

import rospy
from laser_assembler.srv import *
from sensor_msgs.msg import PointCloud2
import sensor_msgs.point_cloud2 as pc2 

processing = False
new_msg = False
msg = None

def callback(data):
	global processing, new_msg, msg
	if not processing:
		new_msg = True
		msg = data

def listener():
	global processing, new_msg, msg
	rospy.init_node('resampler')
	rospy.Subscriber("/M8_cylinder/points", PointCloud2, callback)
	pub = rospy.Publisher("/pointcloud_resample", PointCloud2, queue_size = 1)
	# Este valor tiene que estar configurado en base a la velocidad configurada en el servo
	r = rospy.Rate(10)
	while not rospy.is_shutdown():
		if new_msg:
			processing = True
			new_msg = False
			pub.publish(msg)
			r.sleep()
			processing = False

if __name__ == '__main__':
    listener()
#!/usr/bin/env python

import rospy
import numpy as np
import pandas as pd

from numpy import savetxt
from laser_assembler.srv import *
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import String

import sensor_msgs.point_cloud2 as pc2 
from std_msgs.msg import Header
import sys

# Variables para el stack de la funcion laser assembler
time_init = None
time_end = None
captura_3d = False
prev_value = 0


def callback(data):
	global time_init, time_end, captura_3d, prev_value
	value = int(data.data[6:9])
	rospy.loginfo("Angulo en servo: %d",value)
	dif = value - prev_value
	if value==170 and dif>0:
		time_init = rospy.get_rostime()
		print "Start stack"
		
	if value==0:
		time_end = rospy.get_rostime()
		captura_3d = True
		print "Finish stack"
	prev_value = value


def assembler_client():
	global time_init, time_end, captura_3d, prev_value
	rospy.init_node("assembler_client")
	rospy.wait_for_service("assemble_scans2")
	assemble_scans = rospy.ServiceProxy("assemble_scans2", AssembleScans2)
	pub = rospy.Publisher("/assembled_cloud", PointCloud2, queue_size = 10)
	r = rospy.Rate(10) # El periodo debe ser menor al periodo del arduino en el envio del angulo al procesador central
	rospy.Subscriber("servo_angle", String, callback)

	while not rospy.is_shutdown():
		if captura_3d:
			try:
				resp = assemble_scans(rospy.Time(0,0),time_end) # time_init, time_end
				pub.publish(resp.cloud)
				print "Got cloud"
				captura_3d = False

			except rospy.ServiceException, e:
				print "Service call failed %s"%e

		r.sleep()

if __name__ == '__main__':
	try:
		assembler_client()
	except rospy.ROSInterruptException:
		pass

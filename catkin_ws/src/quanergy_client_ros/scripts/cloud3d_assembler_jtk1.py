#!/usr/bin/env python

import rospy
from laser_assembler.srv import *
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import String

time_init = None
time_end = None
captura_3d = False
count_init = 0
count_end = 0

def callback(data):
	global time_init, time_end, captura_3d, count_init, count_end
	value = data.data[6:9]
	rospy.loginfo(value)
	if int(value) == 180:
		time_init = rospy.get_rostime()
		count_init = count_init + 1

	if int(value) == 5:
		captura_3d = False
		count_end = 0
		
	if int(value) == 0:
		if count_init > 0:
			count_end = count_end + 1
			time_end = rospy.get_rostime()
	if count_end > 0:
		captura_3d = True


def assembler_client():
	global time_init, time_end, captura_3d, count_init, count_end
	rospy.init_node("assembler_client")
	rospy.wait_for_service("assemble_scans2")
	assemble_scans = rospy.ServiceProxy("assemble_scans2", AssembleScans2)
	pub = rospy.Publisher("/assembled_cloud", PointCloud2, queue_size = 10)
	r = rospy.Rate(10) # El periodo debe ser menor al periodo del arduino en el envio del angulo al procesador central
	rospy.Subscriber("servo_angle", String, callback)

	while not rospy.is_shutdown():
		if captura_3d:
			try:
				resp = assemble_scans(time_init,time_end) # time_init, time_end
				print "Got cloud"
				pub.publish(resp.cloud)

			except rospy.ServiceException, e:
				print "Service call failed %s"%e

		r.sleep()

if __name__ == '__main__':
	try:
		assembler_client()
	except rospy.ROSInterruptException:
		pass

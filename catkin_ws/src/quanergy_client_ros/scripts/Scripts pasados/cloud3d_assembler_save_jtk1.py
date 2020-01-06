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

time_init = None
time_end = None
captura_3d = False
count_init = 0
count_end = 0
count_data = 0

from datetime import date
import os

today = date.today()
string_today = str(today)

path = "Desktop"
path_to_folder = path+"/Data/"+string_today

#Creating the dir
if not os.path.exists(path_to_folder):
	os.makedirs(path_to_folder)



DUMMY_FIELD_PREFIX = '__'

# mappings between PointField types and numpy types
type_mappings = [(PointField.INT8, np.dtype('int8')),
                 (PointField.UINT8, np.dtype('uint8')),
                 (PointField.INT16, np.dtype('int16')),
                 (PointField.UINT16, np.dtype('uint16')),
                 (PointField.INT32, np.dtype('int32')),
                 (PointField.UINT32, np.dtype('uint32')),
                 (PointField.FLOAT32, np.dtype('float32')),
                 (PointField.FLOAT64, np.dtype('float64'))]

pftype_to_nptype = dict(type_mappings)
nptype_to_pftype = dict((nptype, pftype) for pftype, nptype in type_mappings)

# sizes (in bytes) of PointField types
pftype_sizes = {PointField.INT8: 1, PointField.UINT8: 1, PointField.INT16: 2, PointField.UINT16: 2,
                PointField.INT32: 4, PointField.UINT32: 4, PointField.FLOAT32: 4, PointField.FLOAT64: 8}


def pointfields_to_dtype(point_fields):
    '''Convert a list of PointFields to a numpy record datatype.
    '''
    offset = 0
    np_dtype_list = []
    for f in point_fields:
        while offset < f.offset:
            # might be extra padding between fields
            np_dtype_list.append(('%s%d' % (DUMMY_FIELD_PREFIX, offset), np.uint8))
            offset += 1
        np_dtype_list.append((f.name, pftype_to_nptype[f.datatype]))
        offset += pftype_sizes[f.datatype]

    # might be extra padding between points
    #while offset < cloud_msg.point_step:
        #np_dtype_list.append(('%s%d' % (DUMMY_FIELD_PREFIX, offset), np.uint8))
        #offset += 1

    return np_dtype_list

def pointcloud2_to_dtype(cloud_msg):
    '''Convert a list of PointCloud2 to a numpy record datatype.
    '''
    offset = 0
    np_dtype_list = []
    for f in cloud_msg.fields:
        while offset < f.offset:
            # might be extra padding between fields
            np_dtype_list.append(('%s%d' % (DUMMY_FIELD_PREFIX, offset), np.uint8))
            offset += 1
        np_dtype_list.append((f.name, pftype_to_nptype[f.datatype]))
        offset += pftype_sizes[f.datatype]

    # might be extra padding between points
    while offset < cloud_msg.point_step:
        np_dtype_list.append(('%s%d' % (DUMMY_FIELD_PREFIX, offset), np.uint8))
        offset += 1

    return np_dtype_list

def arr_to_fields(cloud_arr):
    '''Convert a numpy record datatype into a list of PointFields.
    '''
    fields = []
    for field_name in cloud_arr.dtype.names:
        np_field_type, field_offset = cloud_arr.dtype.fields[field_name]
        pf = PointField()
        pf.name = field_name
        pf.datatype = nptype_to_pftype[np_field_type]
        pf.offset = field_offset
        pf.count = 1 # is this ever more than one?
        fields.append(pf)
    return fields

def pointcloud2_to_array(cloud_msg, remove_padding=True):
    ''' Converts a rospy PointCloud2 message to a numpy recordarray
    Reshapes the returned array to have shape (height, width), even if the height is 1.
    The reason for using np.fromstring rather than struct.unpack is speed... especially
    for large point clouds, this will be <much> faster.
    '''
    # construct a numpy record type equivalent to the point type of this cloud
    dtype_list = pointcloud2_to_dtype(cloud_msg)

    # parse the cloud into an array
    cloud_arr = np.fromstring(cloud_msg.data, dtype_list)

    # remove the dummy fields that were added
    if remove_padding:
        cloud_arr = cloud_arr[[fname for fname, _type in dtype_list if not (fname[:len(DUMMY_FIELD_PREFIX)] == DUMMY_FIELD_PREFIX)]]

    return np.reshape(cloud_arr, (cloud_msg.height, cloud_msg.width))

def save_cloud3d(cloud):
	global path_to_folder, count_data
	cloud_array = pointcloud2_to_array(cloud)
	data_x = cloud_array['x']
	data_y = cloud_array['y']
	data_z = cloud_array['z']
	data_i = cloud_array['intensity']
	
	cloud_points = np.append(data_x,data_y,axis = 0)
	cloud_points = np.append(cloud_points,data_z,axis = 0)
	cloud_points = np.append(cloud_points,data_i,axis = 0)
	
	print cloud_points.shape

	cloud_pd = pd.DataFrame(cloud_points.T)
	cloud_pd.columns = ["x", "y", "z", "intensity"]

	path_data = path_to_folder+"/data_"+str(count_data)+".csv"
	cloud_pd.to_csv(path_data, index = True, header = True)

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
	global time_init, time_end, captura_3d, count_init, count_end, count_data, path_to_folder
	rospy.init_node("assembler_client")
	rospy.wait_for_service("assemble_scans2")
	assemble_scans = rospy.ServiceProxy("assemble_scans2", AssembleScans2)
	pub = rospy.Publisher("/assembled_cloud", PointCloud2, queue_size = 10)
	r = rospy.Rate(5) # El periodo debe ser menor al periodo del arduino en el envio del angulo al procesador central
	rospy.Subscriber("servo_angle", String, callback)

	while not rospy.is_shutdown():
		if captura_3d:
			try:
				resp = assemble_scans(time_init,time_end) # time_init, time_end
				print "Got cloud"
				pub.publish(resp.cloud)
				save_cloud3d(resp.cloud)
				count_data = count_data + 1

			except rospy.ServiceException, e:
				print "Service call failed %s"%e

		r.sleep()

if __name__ == '__main__':
	try:
		assembler_client()
	except rospy.ROSInterruptException:
		pass

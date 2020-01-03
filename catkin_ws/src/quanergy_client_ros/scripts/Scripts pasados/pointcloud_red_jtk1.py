#!/usr/bin/env python

import rospy
import numpy as np
import struct

from laser_assembler.srv import *
from sensor_msgs.msg import PointCloud2, PointField
import sensor_msgs.point_cloud2 as pc2 
from std_msgs.msg import Header
import sys


processing = False
new_msg = False
msg_pc2 = PointCloud2()

# Agregado el parametro de resolucion por interfaz
from dynamic_reconfigure.server import Server
from quanergy_client_ros.cfg import resolutionConfig

'''
Analisis inicial de la data, este analisis es necesario para algunas partes del codigo.

1. El formato del array generado es de la siguiente forma:
	cloud_array.shape = (num_lasers, num_puntos_por_laser)
	
	Donde, el numero de lasers es de 8 y el numero de puntos por laser es de 5340 aprox.

Nota: La cantidad de puntos por laser contiene valores nan.

2. Es importante considerar la frecuencia de resample, debido al procesamiento que toma
	transformar de PointCloud2 a array y de forma inversa, pasa que se genera conflictos
	con la funcion callback, generando un error en el script.

	Si la resolucion es muy alta se genera este problema debido a la carga de procesamiento.
'''

# Constante de remuestreo
resolution_param = 1;

# New function

# prefix to the names of dummy fields we add to get byte alignment correct. this needs to not
# clash with any actual field names
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

def array_to_pointcloud2(cloud_arr, header=None):
    '''Converts a numpy record array to a sensor_msgs.msg.PointCloud2.
    '''

    # make it 2d (even if height will be 1)
    cloud_arr = np.atleast_2d(cloud_arr)

    cloud_msg = PointCloud2()

    if header is not None:
        cloud_msg.header = header

    cloud_msg.height = cloud_arr.shape[0]
    cloud_msg.width = cloud_arr.shape[1]
    cloud_msg.fields = arr_to_fields(cloud_arr)
    cloud_msg.is_bigendian = False # assumption
    cloud_msg.point_step = cloud_arr.dtype.itemsize
    cloud_msg.row_step = cloud_msg.point_step*cloud_arr.shape[1]
    cloud_msg.is_dense = all([np.isfinite(cloud_arr[fname]).all() for fname in cloud_arr.dtype.names])
    cloud_msg.data = cloud_arr.tostring()

    return cloud_msg

def array_to_pointcloud2_new(cloud_arr, header=None):
    '''Converts a numpy record array to a sensor_msgs.msg.PointCloud2.
    '''

    # make it 2d (even if height will be 1)
    data_x = cloud_arr['x'].reshape(1,cloud_arr.shape[0]*cloud_arr.shape[1])
    data_y = cloud_arr['y'].reshape(1,cloud_arr.shape[0]*cloud_arr.shape[1])
    data_z = cloud_arr['z'].reshape(1,cloud_arr.shape[0]*cloud_arr.shape[1])
    data_i = cloud_arr['intensity'].reshape(1,cloud_arr.shape[0]*cloud_arr.shape[1])
    data_r = cloud_arr['ring'].reshape(1,cloud_arr.shape[0]*cloud_arr.shape[1])
    
    x_nan = np.isnan(data_x)
    data_x = data_x[~x_nan]
    data_x = data_x.reshape(1,data_x.shape[0])
    data_y = data_y[~x_nan]
    data_y = data_y.reshape(1,data_y.shape[0])
    data_z = data_z[~x_nan]
    data_z = data_z.reshape(1,data_z.shape[0])
    data_i = data_i[~x_nan]
    data_i = data_i.reshape(1,data_i.shape[0])
    data_r = data_r[~x_nan]
    data_r = data_r.reshape(1,data_r.shape[0])
    
    dim_nan = data_x.shape[1]

    npoints = np.append(data_x,data_y,axis = 0)
    npoints = np.append(npoints,data_z,axis = 0)
    npoints = np.append(npoints,data_i,axis = 0)
    #npoints = np.append(npoints,data_r,axis = 0)
    npoints = npoints.T.tolist()

    #fields = [PointField('x', 0, PointField.FLOAT32, 1),
    #      PointField('y', 4, PointField.FLOAT32, 1),
    #      PointField('z', 8, PointField.FLOAT32, 1),
    #      PointField('intensity', 12, PointField.FLOAT32, 1),
    #      PointField('ring', 16, PointField.UINT16, 1),
    #      ]
    # Ring can not be used for generate the pc2 because this generates a bus error
    fields = [PointField('x', 0, PointField.FLOAT32, 1),
          PointField('y', 4, PointField.FLOAT32, 1),
          PointField('z', 8, PointField.FLOAT32, 1),
          PointField('intensity', 12, PointField.FLOAT32, 1)
          ]
    header = Header()
    header.frame_id = "M8_cylinder"    

    cloud_msg = pc2.create_cloud(header, fields, npoints)

    return cloud_msg , dim_nan


def callback(data_re):
	global processing, new_msg, msg_pc2, resolution_param
	if not processing:
		# Funcion que convierte a vector
		msg_array = pointcloud2_to_array(data_re)
            	dim_array = msg_array.shape[0]*msg_array.shape[1]
            	total_dim = msg_array.shape[1]		
		# Muestreo cada valor de paso_resample del pointcloud
	    	start_ind = resolution_param/8
	    	dim_max = int((total_dim-start_ind*7)/resolution_param)
	    	msg_resize_7 = msg_array[0,0:total_dim:resolution_param]
	    	msg_resize_6 = msg_array[1,int(start_ind*1):total_dim:resolution_param]
	    	msg_resize_5 = msg_array[2,int(start_ind*2):total_dim:resolution_param]
	    	msg_resize_4 = msg_array[3,int(start_ind*3):total_dim:resolution_param]
	    	msg_resize_3 = msg_array[4,int(start_ind*4):total_dim:resolution_param]
	    	msg_resize_2 = msg_array[5,int(start_ind*5):total_dim:resolution_param]
	    	msg_resize_1 = msg_array[6,int(start_ind*6):total_dim:resolution_param]
	    	msg_resize_0 = msg_array[7,int(start_ind*7):total_dim:resolution_param]
	    	msg_resize_7 = msg_resize_7[0:dim_max]
	    	msg_resize_6 = msg_resize_6[0:dim_max]
	    	msg_resize_5 = msg_resize_5[0:dim_max]
	    	msg_resize_4 = msg_resize_4[0:dim_max]
	    	msg_resize_3 = msg_resize_3[0:dim_max]
	    	msg_resize_2 = msg_resize_2[0:dim_max]
	    	msg_resize_1 = msg_resize_1[0:dim_max]
	    	msg_resize_0 = msg_resize_0[0:dim_max]
	    	msg_resize = np.array([msg_resize_7,msg_resize_6,msg_resize_5,msg_resize_4,msg_resize_3,msg_resize_2,msg_resize_1,msg_resize_0])        
	    
	    	dim_resize = msg_resize.shape[0]*msg_resize.shape[1]

		# Funcion que convierte el array a pc2
		data_pc2, dim_nan = array_to_pointcloud2_new(msg_resize, header=data_re.header)

		# Mostrando la informacion de la dimension actual de los puntos por laser
            	porcentaje = dim_resize*100.0/dim_array
            	rospy.loginfo([dim_array,dim_resize,dim_nan,porcentaje])

		# Retorno del nuevo PointCloud
		data_pc2.header.stamp = rospy.Time.now()
		msg_pc2 = data_pc2
		new_msg = True

def callback_2(config, level):
	#rospy.loginfo("""Reconfigure Request: {int_param}""".format(**config))
	resolution_p = config['int_param']
	print resolution_p
	return config

def listener():
	global processing, new_msg, msg_pc2, resolution_param
	rospy.init_node('resampler_tk1')
	rospy.Subscriber("/M8_cylinder/points", PointCloud2, callback)
	pub = rospy.Publisher("/pointcloud_tk1_resample", PointCloud2, queue_size = 10)
	srv = Server(resolutionConfig, callback_2)
	# Este valor tiene que estar configurado en base a la velocidad de envio de datos configurada en el servo
	r = rospy.Rate(5)
	while not rospy.is_shutdown():
		if new_msg:
			processing = True
			new_msg = False			
			pub.publish(msg_pc2)
			r.sleep()
			processing = False

if __name__ == '__main__':
	# Get the arguments and use the rospy function to parse those arguments to the main program
	args = rospy.myargv(argv=sys.argv)
	if len(args)!=2:
		print "ERROR: nor resolution provided"
		sys.exit(1)

	resolution_param = int(args[1]) # The parameter that we want, the first element is the path of the actual file

	listener()

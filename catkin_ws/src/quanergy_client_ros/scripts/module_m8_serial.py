#! /usr/bin/env python

import rospy
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
from std_msgs.msg import String
import serial

def talker():

	# PUBLISHERS Y NODOS
	# Publisher a los estados de la junta del modelo del robot (modulo rotatorio)
	pub = rospy.Publisher('joint_states',JointState,queue_size = 1)
	# Publisher de los valores obtenidos por serial del arduino
	pub2 = rospy.Publisher('servo_angle',String, queue_size=10)
	# Nombre del nodo Talker
	rospy.init_node('talker')

	# MENSAJE JOINT STATE - JUNTA DEL SERVO DEL MODULO
	msg_angle = JointState()
	msg_angle.header = Header()
	msg_angle.name = ['sub_to_eje']
	msg_angle.velocity = []
	msg_angle.effort = []

	# COMUNICACION SERIAL CON EL ARDUINO
	ser = serial.Serial('/dev/ttyACM0', baudrate=9600)
	# Se reinicia el serial del arduino, para evitar el conflicto del autorestart	
	ser.setDTR(False)
	time_to_sleep = rospy.Rate(1)
	time_to_sleep.sleep()
	ser.flushInput()
	ser.setDTR(True)
	time_to_sleep.sleep()
	# Condicion establecida en el programa arduino para que inicie el movimiento
	ser.write('T')
	time_to_sleep.sleep()
	# Valor inicial - Coincidente con el del programa arduino
	data_temp = "grado 90"

	# LOOP	
	while not rospy.is_shutdown():
		# Lectura del valor de angulo de servo
		angle = int(data_temp[6:9])
		# Conversion a radianes
		angle_rad = angle*3.1416/180 - 1.5708
		# Mensaje JointState
		msg_angle.position = [angle_rad]
		msg_angle.header.stamp = rospy.Time.now()
		# Publica en el JointState para la actualziacion del tf
		pub.publish(msg_angle)
		# Publica el valor del angulo en el topico 'servo_angle'
		pub2.publish(data_temp)
		# Lectura del nuevo valor
		data = ser.readline() #grado 120
		if not data:
			continue
		data_temp = data


if __name__ == '__main__':
	try:
		talker()
	except rospy.ROSInterruptException:
		pass

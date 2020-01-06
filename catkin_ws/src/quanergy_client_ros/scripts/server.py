#!/usr/bin/env python

import rospy

from dynamic_reconfigure.server import Server
from quanergy_client_ros.cfg import resolutionConfig

def callback(config, level):
    rospy.loginfo("""Reconfigure Request: {int_param}""".format(**config))
    return config

if __name__ == "__main__":
    rospy.init_node("quanergy_client_ros_tut", anonymous = False)

    srv = Server(resolutionConfig, callback)
    rospy.spin()

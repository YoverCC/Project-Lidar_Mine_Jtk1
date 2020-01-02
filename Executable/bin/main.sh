#!/bin/bash

source /opt/ros/kinetic/setup.bash
source ~/QuanergySystems/catkin_ws/devel/setup.bash

xterm -e "roslaunch quanergy_client_ros main_m8.launch host:=192.168.2.3"


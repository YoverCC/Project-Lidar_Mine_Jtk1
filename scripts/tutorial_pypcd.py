'''
Code: Yover 
Date: 11/10/19
Tutorial: https://blog.pollithy.com/python/numpy/pointcloud/tutorial-pypcd
'''

# You must be in the same directory that the pcd file.

from pypcd import pypcd
import pprint
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

cloud = pypcd.pointcloud.from_path('scan_01.pcd')
pprint.pprint(cloud.get_metadata())

cloud.pc_data[:10]

new_cloud_data = cloud.pc_data.copy()

fig = plt.figure()
ax = fig.add_subplot(111, projection = '3d')
ax.scatter(new_cloud_data['x'],new_cloud_data['y'],new_cloud_data['z'])
plt.show()
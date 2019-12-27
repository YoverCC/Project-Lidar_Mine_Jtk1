'''
Author: Yover Castro
Email: ycastroc@uni.pe 
Date: 11/10/19
'''

# You must be in the same directory that the pcd file.
# With this file you are be able to connect the points of a cloudpoint
# for the quanergy m8 and calculate his volume.

from pypcd import pypcd
import pprint
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import scipy.spatial as ss

cloud = pypcd.PointCloud.from_path('prueba_jtk1_01_12_19.pcd')
pprint.pprint(cloud.get_metadata())

cloud.pc_data[:10]

new_cloud_data = cloud.pc_data.copy()

fig = plt.figure()
ax = fig.add_subplot(111, projection = '3d')

fig2 = plt.figure()
ax2 = fig2.add_subplot(111, projection = '3d')

X = new_cloud_data['x']
Y = new_cloud_data['y']
Z = new_cloud_data['z']

total_points =  new_cloud_data.shape[0]
N= int(total_points/8) # 8 lasers
total_missing_points = np.sum(np.isnan(X))

print("De un total de {} puntos existe un total de {} valores NaN".format(total_points, total_missing_points))

X_no_nan = X[~np.isnan(X)]
Y_no_nan = Y[~np.isnan(Y)]
Z_no_nan = Z[~np.isnan(Z)]

print("Se eliminaron los valores NaN")

X_resamp = X_no_nan[1:len(X_no_nan):250]
Y_resamp = Y_no_nan[1:len(Y_no_nan):250]
Z_resamp = Z_no_nan[1:len(Z_no_nan):250]

print("Se muestrearon los puntos")
print("La dimension actual de la data es: {}".format(len(X_resamp)))

# PLOT POINTS
ax.scatter(X_resamp,Y_resamp,Z_resamp,s=0.5)

ax2.scatter(X_no_nan,Y_no_nan,Z_no_nan, s=0.5)


# PLOT 1
#ax.plot_wireframe(X_no_nan,Y_no_nan,Z_no_nan, rstride = 1000, cstride = 1000)
#plt.show()

# PLOT 2
#ax2.plot_trisurf(X_resamp,Y_resamp,Z_resamp)
#plt.show()

## VOLUME CALCULATION
points = np.column_stack((X_resamp, Y_resamp, Z_resamp))
hull = ss.ConvexHull(points)
print("El volumen dentro de los puntos es: ",hull.volume)

import pandas as pd
data = pd.read_csv('/home/jarvis/pcdfiles/example_simple_cloudpoint.txt', sep=" ", header=None)
data.columns = ["x", "y", "z", "ring", "intensity"]
del data["ring"]
del data["intensity"]
data_clean = data.dropna()
(num_points,dim) = data_clean.shape
num_points_marker = 2000
salto = int(num_points/num_points_marker)
data_resample = data_clean[1:-1:salto]
data_resample = data_resample.reset_index()
del data_resample['index']
export_csv = data_resample.to_csv ('/home/jarvis/pcdfiles/example_simple_cloudpoint.csv', index = True, header=True)
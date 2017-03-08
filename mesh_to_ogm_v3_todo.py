'''
Mesh to Occupance Map Convertor - version 0.3 (raycast with edges of faces)

Note:
This scripts depends on the place_categorization.

'''

from __future__ import print_function

import os
import sys
if sys.version_info[0] == 3:
    from importlib import reload
elif sys.version_info[0] == 2:
    pass

new_paths = [
    # u'',
    u'../place_categorization_2D/',
]
for path in new_paths:
    if not( path in sys.path):
        sys.path.append( path )

import time
import cv2
import numpy as np
import scipy.misc
import sklearn.cluster
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import plyfile

import convert_mesh 
reload(convert_mesh)
import place_categorization as plcat
reload(plcat)



################################################################################
####################################################################### dev yard
################################################################################

#################### loading ply file
file_name = '../../../Documents/tango/HIH_01_full/20170131135829.ply'

tic = time.time()
print ('\t loading ply file ...')
ply_data, faces, [Vx, Vy, Vz, Vr, Vg, Vb, Va] = convert_mesh.load_ply_file ( file_name )
print ('\b - time elapsed: {:.2f}'.format(time.time() - tic))



#################### slicing and ogm construction

offset = .6 # vertical offset - percentage of z.max -z.min
interval = 0.05 # vertical interval - percentage of z.max -z.min

mpp = .02 # meter per pixel ratio 
margin = 40 # map margin
unexplored = .5 # value for unexplored pixels (.5:127 - 1.:255)

tic = time.time()
print ('\t horizontal slicing of vertices ...')
vrt_slice_idx = convert_mesh.slice_horizontal_vertices(ply_data,
                                                      offset=offset, interval=interval)
print ('\b - time elapsed: {:.2f}'.format(time.time() - tic))


tic = time.time()
print ('\t construct ogm from sliced vertices ...')
ogm = convert_mesh.convert_2d_pointcloud_to_ogm(Vx,Vy, vrt_slice_idx,
                                                mpp=mpp,
                                                margin=margin,
                                                unexplored=unexplored,
                                                fill_neighbors=True,
                                                flip_vertically = True)

print ('\b - time elapsed: {:.2f}'.format(time.time() - tic))


#################### fixing the discrepency of the occupancy
tic = time.time()
print ('\t horizontal slicing of faces ...')
fce_slice_idx = convert_mesh.slice_horizontal_faces(ply_data, inclusion='any',
                                                   offset=offset, interval=interval)
print ('\b - time elapsed: {:.2f}'.format(time.time() - tic))






################################################################################
########################################################## visualization gallery
################################################################################

# ########## plotting edges of the sliced faces
# if 1:
#     fig = plt.figure()
#     fig.add_axes([0, 0, 1, 1])

#     for v1,v2,v3 in faces[fce_slice_idx]:
#         fig.axes[0].plot( [Vx[v1],Vx[v2]] , [Vy[v1],Vy[v2]] , 'b.-')
#         fig.axes[0].plot( [Vx[v1],Vx[v3]] , [Vy[v1],Vy[v3]] , 'b.-')
#         fig.axes[0].plot( [Vx[v3],Vx[v2]] , [Vy[v3],Vy[v2]] , 'b.-')

#     fig.axes[0].axis('equal')
#     plt.show()


# ####### plot raycast array
# x_ = rays_array_xy[0,:,:].flatten()
# y_ = rays_array_xy[1,:,:].flatten()
# rc = np.stack( (x_, y_), axis=1)    
# plot_point_sets (src=points, dst=rc)



################################################################################
########################################################################### dump
################################################################################

#################### fixing the discrepency of the occupancy

# ########## converting the faces to a graph
# import itertools
# import networkx as nx

# nodes = list(set(itertools.chain(*faces[fce_slice_idx])))
# edges = list({ pairs
#                for face in faces[fce_slice_idx]
#                for pairs in itertools.combinations(face,2) })

# G=nx.Graph()
# G.add_nodes_from(nodes)
# G.add_edges_from(edges)

# len([s for s in nx.connected_component_subgraphs(G)]) = 1340


# ########## Morphing the image to close holes
# # THIS WORKS (ALMOST), BUT ALTERS THE OGM
# ogm = convert_mesh.process_image(ogm, k_size=3, bin_thr=[126, 255])


# ########## drawing edges of faces as lines 
# # THIS DOESN'T WORK, BECAUSE ALL EDGES ARE SHORTER THAN 1
# # AND NO LINE IS DRAWN
# tic = time.time()
# val=0,
# thickness=2
# for v1,v2,v3 in faces[fce_slice_idx]:
#     p1, p2 = (Vx[v1],Vy[v1]) , (Vx[v2],Vy[v2])
#     ogm = cv2.line(ogm, p1, p2, val, thickness) 
#     p1, p2 = (Vx[v1],Vy[v1]) , (Vx[v3],Vy[v3])
#     ogm = cv2.line(ogm, p1, p2, val, thickness)
#     p1, p2 = (Vx[v3],Vy[v3]) , (Vx[v2],Vy[v2])
#     ogm = cv2.line(ogm, p1, p2, val, thickness)
# print ('\b - drawing in : {:.2f}'.format(time.time() - tic))



#################### 
# idx1 = convert_mesh.slice_horizontal_vertices(ply_data, offset=0.1, interval=0.0001)
# idx2 = convert_mesh.slice_horizontal_vertices(ply_data, offset=0.4, interval=0.0001)
# idx3 = convert_mesh.slice_horizontal_vertices(ply_data, offset=0.7, interval=0.0001)
# idx = np.concatenate((idx1,idx2,idx3), axis=0)


#################### raycast with edges of faces
# radius = 4 / mpp # meter (meter/pixel) -> pixel
# c_point = np.array([0,0]) # centre point for range scan
# points = np.stack( (Vx[vrt_slice_idx], Vy[vrt_slice_idx]), axis=1)
# dist_2_centre = (Vx[vrt_slice_idx]-c_point[1])**2 + (Vy[vrt_slice_idx]-c_point[0])**2
# in_circle_idx = 


# ls = lambda s,E,stp: np.array([ np.linspace(s,e, num=stp, endpoint=True) for e in E])



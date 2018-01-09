'''
Copyright (C) 2017 Saeed Gholami Shahbandi. All rights reserved.

This program is free software: you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this program. If not, see
<http://www.gnu.org/licenses/>
'''

'''
Mesh to Occupance Map Convertor - version 0.2 (inter-active)

This script loads a mesh (.ply) and converts it to a bitmap Occupancy Grid Map (.png).
Set of mesh vertices is treated as a point cloud. 
The point cloud is horizontally sliced (according to provided parameters),
The resulting point-set is converted into a bitmap.
Pixels who contain a vertex of the sliced pointcloud are set to occupied.
Rest of the pixels are set to a unexplored (127). 
Given a set of points in the open-space (inter-active), raycasting takes place at those points.
All pixels covered by raycast, considered "open", are set to (255).

Note
----
This scripts depends on the place_categorization.

Usage
-----

'''

# from __future__ import print_function

import sys
import numpy as np
import scipy.misc
import matplotlib.pyplot as plt

sys.path.append( '../lib/' )
import convert_mesh 


################################################################################
def main(file_name, slice_config, ogm_config, raycast_config):
    ''''''    
    ply_data, faces, [Vx, Vy, Vz, Vr, Vg, Vb, Va] = convert_mesh.load_ply_file ( file_name )    
    slice_idx = convert_mesh.slice_horizontal_vertices(ply_data, slice_config)
    ogm = convert_mesh.convert_2d_pointcloud_to_ogm(Vx,Vy, slice_idx, ogm_config)
    
    #################### interactive ROI-patching (to fix absense of walls)
    fig = plt.figure(figsize=(20,12))
    roi_patcher = convert_mesh.ROIPatcher(fig, ogm, 127)
    plt.show()
    ogm = roi_patcher.image

    #################### interactive raycasting and OGM adjustment    
    fig = plt.figure(figsize=(20,12))
    rc_patcher = convert_mesh.RayCastPatcher(fig,
                                             ogm, ogm_config['margin'],
                                             raycast_config)
    plt.show()
    ogm = rc_patcher.image
    
    #################### interactive ROI-patching (to fix absense of walls)
    fig = plt.figure(figsize=(20,12))
    roi_patcher = convert_mesh.ROIPatcher(fig, ogm, 127)
    plt.show()
    ogm = roi_patcher.image
    
    #################### save resulting file
    file_name_png =  file_name[:-3]+ 'png'
    scipy.misc.toimage(ogm, cmin=0, cmax=ogm.max()).save(file_name_png)
    
    
################################################################################
if __name__ == '__main__':


    slice_config = {
        'offset':   0.5,  # vertical offset - percentage of z.max -z.min
        'interval': 0.05, # vertical interval - percentage of z.max -z.min
    }
    
    ogm_config = {
        'mpp':             0.02, # meter per pixel ratio 
        'margin':          10, # map margin
        'unexplored':      0.5, # value for unexplored pixels (.5:127 - 1.:255)
        'fill_neighbors':  True,
        'flip_vertically': True
    }
    
    raycast_config = {
        'length_range'  : 4 / ogm_config['mpp'], # meter (meter/pixel) -> pixel
        'length_steps'  : 1 * (4 / ogm_config['mpp']), #
        'theta_range'   : 2*np.pi,
        'theta_res'     : 1/1,
        'occupancy_thr' : 126,
    }
        
    args = sys.argv
    
    # fetching parameters from input arguments
    # parameters are marked with double dash,
    # the value of a parameter is the next argument   
    listiterator = args[1:].__iter__()
    while 1:
        try:
            item = next( listiterator )
            if item[:2] == '--':
                exec(item[2:] + ' = next( listiterator )')
        except:
            break

    if 'filename' in locals():
        main (filename, slice_config, ogm_config, raycast_config)

    else:
        print ('\n *** NO FILE IS SPECIFIED, Here is how to use this script ***')
        print (__doc__)

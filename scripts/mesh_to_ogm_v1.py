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
Mesh to Occupance Map Convertor - version 0.1

This script loads a mesh (.ply) and converts it to a bitmap Occupancy Grid Map (.png).
Set of mesh vertices is treated as a point cloud. 
The point cloud is horizontally sliced (according to provided parameters),
The resulting point-set is converted into a bitmap.
Pixels who contain a vertex of the sliced pointcloud are set to occupied.
Rest of the pixels are set to a predefined value (see "unexplored" parameter). 


Options
-------
-v: visualize the result
-s: save the result of coversion (the same path and name as input, with .png extension)
If no option provided, the script will only visualize the result

Parameters
----------
--filename: name of a ply file (including the path)

Usage
-----
Options could be anywhere, but every parameter name should be followed by
the parameter value:
$ python mesh_to_ogm_v1.py -s -v --param1 param1_value --param2 param2_value

Example
-------
$ python mesh_to_ogm_v1.py -s -v --filename /home/saesha/Documents/tango/HIH_01_full/20170131135829.ply
'''

# from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
import scipy.misc
import plyfile
import sys

sys.path.append( '../lib/' )
import convert_mesh


################################################################################
def main(filename, slice_config, ogm_config, save, visu ):
    
    print ('\t loading ply file ...')
    ply_data, faces, [Vx, Vy, Vz, Vr, Vg, Vb, Va] = convert_mesh.load_ply_file( filename )

    print ('\t horizontal slicing ...')
    slice_idx = convert_mesh.slice_horizontal_vertices(ply_data, slice_config)
        
    print ('\t converting...')
    # generating the ogm
    ogm = convert_mesh.convert_2d_pointcloud_to_ogm(Vx,Vy, slice_idx, ogm_config)

    if visu:
        fig, axes = plt.subplots(1,1, figsize=(20,12))#, sharex=True, sharey=True)
        axes.imshow(ogm, cmap = 'gray', interpolation='nearest')
        plt.tight_layout()
        plt.show()

    if save:
        print ('\t saving...')
        # saving ogm in png format
        filename_png =  filename[:-4]+ '_.png'
        # scipy.misc.imsave(dir_adr+file_name_png, ogm) # this normalizes the image
        scipy.misc.toimage(ogm, cmin=0, cmax=ogm.max()).save(filename_png)


################################################################################
if __name__ == '__main__':
        
    slice_config = {
        # 'offset':   0.5,  # vertical offset - percentage of z.max -z.min
        # 'interval': 0.05, # vertical interval - percentage of z.max -z.min

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
    
    
    args = sys.argv

    # visualization/saving options
    options = []
    # fetching options from input arguments
    save, visu = False, False
    for arg in args[1:]:
        if ('-s' in arg):
            save = True
        elif ('-v' in arg):
            visu = True

    if not(visu) and not(save): visu = True 
            
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
        main (filename, slice_config, ogm_config, save, visu)

    else:
        print ('\n *** NO FILE IS SPECIFIED, Here is how to use this script ***')
        print (__doc__)


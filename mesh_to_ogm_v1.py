'''
Mesh to Occupance Map Convertor - version 0.1

This script loads a mesh (.ply) and converts it to a bitmap Occupancy Grid Map (.png).
Vertices of the point cloud are treated as a point cloud. 
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
--offset: vertical offset - percentage of [z.max-z.min] (default .5)
--interval: vertical interval - percentage of [z.max-z.min] (default .05)
--mpp: meter per pixel ratio (default .02) 
--margin: map margin in pixels (default 10) 
--unexplored - value for unexplored pixels (.5:127 - 1.:255) (default: 1.) 

Usage
-----
Options could be anywhere, but every parameter name should be followed by
the parameter value:
$ python mesh_to_ogm_v1.py -s -v --param1 param1_value --param2 param2_value

Example
-------
$ python mesh_to_ogm_v1.py -s -v --filename /home/saesha/Documents/tango/HIH_01_full/20170131135829.ply
'''

from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
import scipy.misc
import plyfile
import sys

import convert_mesh



################################################################################
def main_convert(file_name, save, visu,
                 # horizontal slicing parameters
                 offset = .5, # vertical offset - percentage of z.max -z.min
                 interval = 0.05, # vertical interval - percentage of z.max -z.min
                 # pointcloud conversion to ogm parameters
                 mpp = .02, # meter per pixel ratio 
                 margin = 10, # map margin
                 unexplored = 1., # value for unexplored pixels (.5:127 - 1.:255)
             ):
    
    print ('\t loading ply file ...')
    ply_data, faces, [Vx, Vy, Vz, Vr, Vg, Vb, Va] = convert_mesh.load_ply_file( file_name )

    print ('\t horizontal slicing ...')

    idx = convert_mesh.slice_horizontal_vertices(ply_data, offset=offset, interval=interval)
        
    print ('\t converting...')
    # generating the ogm
    ogm = convert_mesh.convert_2d_pointcloud_to_ogm (Vx,Vy, idx,
                                                     mpp=mpp,
                                                     margin=margin,
                                                     unexplored=unexplored,
                                                     fill_neighbors = False,
                                                     flip_vertically = True)

    if visu:
        fig, axes = plt.subplots(1,1, figsize=(20,12))#, sharex=True, sharey=True)
        axes.imshow(ogm, cmap = 'gray', interpolation='nearest')
        plt.tight_layout()
        plt.show()


    if save:
        print ('\t saving...')
        # saving ogm in png format
        file_name_png =  file_name[:-4]+ '_.png'
        # scipy.misc.imsave(dir_adr+file_name_png, ogm) # this normalizes the image
        scipy.misc.toimage(ogm, cmin=0, cmax=ogm.max()).save(file_name_png)


################################################################################
if __name__ == '__main__':
        
    args = sys.argv
    options = []

    # fetching options from input arguments
    # options are marked with single dash
    for arg in args[1:]:
        if ('-s' in arg) or ('-v' in arg):
            options += [arg]

    # fetching parameters from input arguments
    # parameters are marked with double dash,
    # the value of a parameter is the next argument   
    listiterator = args[1:].__iter__()
    while 1:
        try:
            item = listiterator.next()
            if item[:2] == '--':
                exec(item[2:] + ' = listiterator.next()')
        except:
            break



    # if file name is not provided, set to default
    if 'filename' in locals():

        # if option is not specified, default is set to '--v'
        if len(options) == 0:
            options += ['-v']
            
        # horizontal slicing parameters
        if 'offset' not in locals(): offset = .5 # vertical offset - percentage of z.max -z.min
        if 'interval' not in locals(): interval = 0.05 # vertical interval - percentage of z.max -z.min
    
        # pointcloud conversion to ogm parameters
        if 'mpp' not in locals(): mpp = .02 # meter per pixel ratio 
        if 'margin' not in locals(): margin = 10 # map margin
        if 'unexplored' not in locals(): unexplored = 1. # value for unexplored pixels (.5:127 - 1.:255)
        
        visu = True if '-v' in options else False
        save = True if '-s' in options else False
        main_convert( filename, save, visu,
                      offset = offset,
                      interval = interval,
                      mpp = mpp, 
                      margin = margin, 
                      unexplored = unexplored
                  )

    else:
        print ('\n *** NO FILE IS SPECIFIED, Here is how to use this script ***')
        print (__doc__)
        # raise (NameError('file name is missing'))

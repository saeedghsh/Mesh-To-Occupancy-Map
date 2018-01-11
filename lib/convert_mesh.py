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


from __future__ import print_function
import numpy as np
import plyfile
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import cv2

import sys
sys.path.append( u'../../Place-Categorization-2D/' )
try:
    from place_categorization import place_categorization as plcat
except:
    print ('WARNING: convert_mesh.py can\'t load place_categorization.py -> will fail with raycasting')


# obj file
# http://cgkit.sourceforge.net/doc2/objmtl.html
# http://strawlab.github.io/python-pcl/

# or convert to ply file and use:
# https://github.com/dranjan/python-plyfile
# http://pymesh.readthedocs.io/en/latest/
# https://plot.ly/python/surface-triangulation/
# http://moderndata.plot.ly/stanford-ply-files-visualized-in-python/

################################################################################
##################################################################### python-pcl
################################################################################
# import pcl
# cloud = pcl.load('islab_couch/20170131122821.ply')
# # Process Python[...] segmentation fault (core dumped)
# cloud = pcl.load('islab_couch/20170131122821.obj')
# # ValueError: Could not determine file format from pathname islab_couch/20170131122821.obj
# cloud = pcl.load('islab_couch/20170131122821.mtl')
# # ValueError: Could not determine file format from pathname islab_couch/20170131122821.mtl


################################################################################
def load_ply_file ( file_name, print_info=False ):
    ''' '''
    # ply_data.elements[0].data['x'] # -> array([ 0.,  0.,  1.,  1.], dtype=float32)
    # ply_data['face'].data['vertex_indices'][0] # -> array([0, 1, 2], dtype=int32)
    # ply_data['vertex']['x'] # -> array([ 0.,  0.,  1.,  1.], dtype=float32)
    # ply_data['vertex'][0] # -> (0.0, 0.0, 0.0)

    # note that ply_data['vertex'].data is a numpy structured array
    # https://docs.scipy.org/doc/numpy/user/basics.rec.html
    # b1, i1, i2, i4, i8, u1, u2, u4, u8, f2, f4, f8, c8, c16, a<n>
    # representing bytes, ints, unsigned ints, floats, complex and fixed length strings of specified byte lengths)
    # print (ply_data['vertex'].data.dtype)
    # print ply_data['vertex'].data['x']
    # print ply_data['vertex'].data[0]

    ply_data = plyfile.PlyData.read(open(file_name))

    Vx = ply_data['vertex'].data['x'] # f4 -> float32
    Vy = ply_data['vertex'].data['y'] # f4 -> float32
    Vz = ply_data['vertex'].data['z'] # f4 -> float32
    Vr = ply_data['vertex'].data['red'] # u1 -> usigned int 8
    Vg = ply_data['vertex'].data['green'] # u1 -> usigned int 8
    Vb = ply_data['vertex'].data['blue'] # u1 -> usigned int 8
    Va = ply_data['vertex'].data['alpha'] # u1 -> usigned int 8

    faces = np.array([ face[0] for face in ply_data['face'] ])

    if print_info:
        print ('\t count: ', ply_data.elements[0].count)
        print ( 'dimensions\' bound' )
        print ( 'Z-range: \t', Vz.min(),Vz.max() )
        print ( 'Y-range: \t', Vy.min(),Vy.max() )
        print ( 'X-range: \t', Vx.min(),Vx.max() )

    return  ply_data, faces, [Vx, Vy, Vz, Vr, Vg, Vb, Va]


################################################################################
def slice_horizontal_vertices(ply_data, config):
    '''
    This method returns a list of indices to all vertices whos z-coordinate is
    withing the specified interval.

    Input
    -----
    ply_data
    see the method "load_ply_file"

    Parameters
    ----------
    offset (default: .6)
    vertical offset specified as the percentage of (z.max-z.min)

    interval (default: 0.05)
    vertical interval specified as the percentage of (z.max-z.min)

    Option
    ------
    print_info (default: False)
    If True, the statistics of slicing is printed

    Output
    ------
    idx
    A list of indices to Vertices (Vx, Vy, Vz, ...) that are in the specified inverval
    '''
    ########## setting default value of variables if not available in config
    offset = .6 if 'offset' not in config.keys() else config['offset']
    interval = 0.05 if 'interval' not in config.keys() else config['interval']
    print_info = False if 'print_info' not in config.keys() else config['print_info']

    ##########
    Vz = ply_data['vertex'].data['z']

    # finding the vertical upper and lower bounds
    z_range = np.abs(Vz.max() - Vz.min())
    z_centr = Vz.min() + offset*z_range
    z_lb = z_centr - interval*z_range
    z_ub = z_centr + interval*z_range

    # indices to vertices with z-value in bound (z_lb< Vz <z_ub)
    idx = np.where ( (z_lb<Vz) & (Vz<z_ub) )[0]

    if print_info:
        msg = '\t ({:d}/{:d} ~{:.2f}%) vertices (offset:{:.2f}, interval:{:.2f})'
        print ( msg.format(len(idx), len(Vz), float(len(idx))/len(Vz), offset, interval ) )

    return idx

################################################################################
def slice_horizontal_faces(ply_data,
                           inclusion=['any', 'all'][0],
                           offset=.7, interval=0.005, print_info=False):
    '''
    This method returns a list of indices to all faces whos vertices are within
    the vertical bound (vertices whos z-coordinate is withing the specified interval).

    Input
    -----
    ply_data
    see the method "load_ply_file"


    Parameters
    ----------
    offset (default: .6)
    vertical offset specified as the percentage of (z.max-z.min)

    interval (default: 0.05)
    vertical interval specified as the percentage of (z.max-z.min)

    Option
    ------
    inclusion (default: 'any')
    If inclusion is set to 'any', those faces who has atleast one vertex in the
    specified interval all returned, otherwise if it's set to 'all', only faces
    with all veritces in the specified interval are returned.


    print_info (default: False)
    If True, the statistics of slicing is printed


    Output
    ------
    idx
    indices to faces whos (all/any) vertices are within the vertical bound


    Note
    ----
    (v1_idx, v2_idx, v3_idx) = face[i]
    '''

    Vz = ply_data['vertex'].data['z']

    # finding the vertical upper and lower bounds
    z_range = np.abs(Vz.max() - Vz.min())
    z_centr = Vz.min() + offset*z_range
    z_lb = z_centr - interval*z_range
    z_ub = z_centr + interval*z_range

    # each face in faces is an array of vertices' indices (v1_idx, v2_idx, v3_idx)
    faces = np.array([ face[0] for face in ply_data['face'] ])

    # each element [i,j] in faces_z correspoinds to z-coordinate of the
    # vertex whos index is stored in faces
    # (Vz.shape = l) and (faces.shape = mx3) -> Vz[faces].shape = mx3
    faces_z = Vz[faces]

    # faces.shape = mx3 -> np.where(cond(faces),a,b).shape = mx3
    # mask.shape =  mx3 -> mask.all(axis=1).shape == mx1
    if inclusion == 'any':
        mask = np.where((z_lb<faces_z) & (faces_z<z_ub), True, False).any(axis=1)
    elif inclusion == 'all':
        mask = np.where((z_lb<faces_z) & (faces_z<z_ub), True, False).all(axis=1)

    # indices to faces whos all/any vertices are within the vertical bound
    idx = np.where(mask)[0]

    if print_info:
        msg = '\t ({:d}/{:d} ~{:.2f}%) faces (offset:{:.2f}, interval:{:.2f})'
        print ( msg.format( len(idx), faces.shape[0],
                            float(len(idx))/faces.shape[0],
                            offset, interval ) )

    return idx


################################################################################
def convert_2d_pointcloud_to_ogm (Vx,Vy, ver_sliced_idx, config):
    '''
    Vx: x-coordinate of all vertices
    Vy: y-coordinate of all vertices
    ver_sliced_idx: the indices to vertices from horizontal slicing
    mpp: meter per pixel - 1.0 -> 1pixel = 1m|1000mm
    margin: the margin around the map
    unexplored: since this is a pseudo-ogm, unexplored could be .5 (127) or 1 (255)
    flip_vertically: since the image storing will flip the image, this will compensate

    fill_neighbors: each point will occupy a neighbourhood of 3x3
    '''

    ########## setting default value of variables if not available in config
    mpp = .02 if 'mpp' not in config.keys() else config['mpp']
    margin = 10 if 'margin' not in config.keys() else config['margin']
    unexplored = 1. if 'unexplored' not in config.keys() else config['unexplored']
    fill_neighbors = True if 'fill_neighbors' not in config.keys() else config['fill_neighbors']
    flip_vertically = True if 'flip_vertically' not in config.keys() else config['flip_vertically']



    idx = ver_sliced_idx

    # map's dimension in meter
    width = Vx[idx].max() - Vx[idx].min()
    height = Vy[idx].max() - Vy[idx].min()

    # map's dimension in pixel
    col = int(width /mpp) + 2*margin
    row = int(height /mpp) + 2*margin

    # intial occupancy map
    ogm = np.ones((row,col)) * unexplored

    # indices of the vertices from "ver_sliced_idx" in pixel coordinate (row/col)
    row_idx = ((Vy[idx]-Vy[idx].min()) /mpp).astype(np.uint32) + margin
    col_idx = ((Vx[idx]-Vx[idx].min()) /mpp).astype(np.uint32) + margin


    if fill_neighbors:
        row_idx = np.stack( (row_idx-1, row_idx-1, row_idx-1,
                             row_idx,   row_idx,   row_idx,
                             row_idx+1, row_idx+1, row_idx+1)
                            , axis=0 )
        col_idx = np.stack( (col_idx-1, col_idx, col_idx+1,
                             col_idx-1, col_idx, col_idx+1,
                             col_idx-1, col_idx, col_idx+1)
                            , axis=0 )


    # checking that all the pixel-indices are in bound
    assert col_idx.min() >= 0
    assert col_idx.max() < col
    assert row_idx.min() >= 0
    assert row_idx.max() < row

    # updating the map values - todo: this should be done much better.
    ogm[row_idx,col_idx] = 0

    # flipping the image vertically
    if flip_vertically: ogm = np.flipud(ogm)

    # scaling the image to 255, converting to uint8, and return
    return (ogm * 255).astype(np.uint8)


################################################################################
def translate_to_omg_frame(ply_data,
                           target_shape=(1585, 1585),
                           slice_config=None,
                           ogm_config=None
                       ):
    '''
    This method takes a mesh and transform it to the frame of occupancy map.
    The values to config dictionaries are comming from the settings that was
    used for generating occupancy maps from mesh.
    '''


    ##### settings of plt_to_ogm conversion
    if slice_config is None:
        slice_config = {
            'offset':   0.5,  # vertical offset - percentage of z.max -z.min
            'interval': 0.05, # vertical interval - percentage of z.max -z.min
        }

    if ogm_config is None:
        ogm_config = {
            'mpp':             0.02, # meter per pixel ratio
            'margin':          10
        }

    ##### setting for padding maps to square
    (target_row, target_col) = target_shape

    # extract vertices coordinates
    Vx = ply_data['vertex'].data['x'] # f4 -> float32
    Vy = ply_data['vertex'].data['y'] # f4 -> float32
    Vz = ply_data['vertex'].data['z'] # f4 -> float32
    '''
    note that the transformation depends on the slice, since that changes the
    extent of point cloud. So we have to perform slicing operation. hHowever,
    the conversion to bitmap doesn't matter and we can get what we want
    analytically
    '''

    # slice the map horizontally
    slice_idx = slice_horizontal_vertices(ply_data, slice_config)

    # map's dimension in meter
    width = Vx[slice_idx].max() - Vx[slice_idx].min()
    height = Vy[slice_idx].max() - Vy[slice_idx].min()
    # map's dimension in pixel
    col = int(width /ogm_config['mpp']) + 2*ogm_config['margin']
    row = int(height /ogm_config['mpp']) + 2*ogm_config['margin']
    # margin of padding to current size
    bottom_pad = (target_row - row) // 2
    left_pad = (target_col - col) // 2

    # transforming coordinates of the vertices
    # min of x-y are translated to origin, scaled by "mpp" and shifted with proper margins
    # z is only scaled by "mpp"
    new_Vx = (Vx-Vx[slice_idx].min()) /ogm_config['mpp'] + ogm_config['margin'] + left_pad
    new_Vy = (Vy-Vy[slice_idx].min()) /ogm_config['mpp'] + ogm_config['margin'] + bottom_pad
    new_Vz = Vz / ogm_config['mpp']

    return new_Vx, new_Vy, new_Vz

################################################################################
def create_mpath ( points ):
    '''
    note: points must be in order
    '''

    # start path
    verts = [ (points[0,0], points[0,1]) ]
    codes = [ mpath.Path.MOVETO ]

    # construct path - only lineto
    for point in points[1:,:]:
        verts += [ (point[0], point[1]) ]
        codes += [ mpath.Path.LINETO ]

    # close path
    verts += [ (points[0,0], points[0,1]) ]
    codes += [ mpath.Path.CLOSEPOLY ]

    # return path
    return mpath.Path(verts, codes)

################################################################################
def get_pixels_in_mpath(path, image_shape):
    '''
    convension
    pixel:(x,y)

    given a path and image_size, this method return all the pixels in the path
    that are inside the image
    '''

    # find the extent of the minimum bounding box, sunjected to image boundaries
    mbb = path.get_extents()
    xmin = int( np.max ([mbb.xmin, 0]) )
    xmax = int( np.min ([mbb.xmax, image_shape[1]-1]) )
    ymin = int( np.max ([mbb.ymin, 0]) )
    ymax = int( np.min ([mbb.ymax, image_shape[0]-1]) )

    x, y = np.meshgrid( range(xmin,xmax+1), range(ymin,ymax+1) )
    mbb_pixels = np.stack( (x.flatten().T,y.flatten().T), axis=1)

    in_path = path.contains_points(mbb_pixels)

    return mbb_pixels[in_path, :]


################################################################################
def process_image(image, k_size=3, bin_thr=[127, 255]):
    '''
    '''
    # converting to binary, for the layout-images
    thr1,thr2 = bin_thr
    ret, image = cv2.threshold(image.astype(np.uint8) , thr1,thr2 , cv2.THRESH_BINARY)

    # erode to make the ogm suitable for raycasting
    kernel = np.ones((k_size,k_size),np.uint8)
    image = cv2.erode(image, kernel, iterations = 3)
    image = cv2.medianBlur(image, k_size)

    # convert back to gray-scale (i,e unoccupied to thr1)
    yidx, xidx = np.nonzero(image > thr1)
    image[yidx, xidx] = int(thr1)

    return image

################################################################################
class RayCastPatcher:
    def __init__(self, fig, image, margin, raycast_config):
        '''
        '''
        self.fig = fig
        self.fig.add_axes([0, 0, 1, 1])
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self)

        self.image = image.copy()
        self.margin = margin
        self.points = []
        self.patched = False


        self.raycast_config = raycast_config
        self.raxy = plcat.construct_raycast_array(np.array([0,0,0]), # x,y,theta
                                                  raycast_config['length_range'],
                                                  raycast_config['length_steps'],
                                                  raycast_config['theta_range'],
                                                  raycast_config['theta_res']
                                              )

        #  draw the image
        self._reset_drawing()

    ########################################
    def __call__(self, event):
        '''
        since self is passed to mpl_connect as the callback method
        every time 'button_press_event' happens, the self (i.e. this method)
        is called
        We could simply calls this onclick and pass it to mpl_connect.
        '''
        if event.button == 1:
            # left click adds a new point to the queue
            if event.xdata is not None:
                [x, y] = [int(event.xdata), int(event.ydata)]
                self.points.append([x, y])
                self.fig.axes[0].plot(x, y, 'r*')
                plt.draw()

        elif event.button == 2:
            # mildde click resets selection
            self._reset_drawing()
            self.points = []

        elif event.button == 3:
            # right lick: sets all the pixels inside the path to open
            for pose in self.points:
                self.raycast_set_open(pose)
            self.patched = True

            # drawing modified image
            self._reset_drawing()
            self.points = []

    ########################################
    def _reset_drawing (self):
        ''' '''
        plt.cla()
        self.fig.axes[0].imshow( self.image,
                                 cmap = 'gray',
                                 interpolation='nearest',
                                 origin='lower',
                                 vmin=0, vmax=255)
        plt.draw()

    ########################################
    def raycast_set_open(self, pose):
        '''
        '''
        r,t = plcat.raycast_bitmap(pose=pose,
                                   image=self.image,
                                   occupancy_thr=self.raycast_config['occupancy_thr'],
                                   length_range=self.raycast_config['length_range'],
                                   length_steps=self.raycast_config['length_steps'],
                                   theta_range=self.raycast_config['theta_range'],
                                   theta_res=self.raycast_config['theta_res'],
                                   rays_array_xy=self.raxy,
                                   # mpp= 0.02,
                                   # range_res =1,
        )

        pts = np.stack( (pose[0]+r*np.cos(t), pose[1]+r*np.sin(t)), axis=1)
        path = create_mpath(pts)
        pixels = get_pixels_in_mpath(path, self.image.shape)
        self.image [pixels[:,1], pixels[:,0]] = 255

        # margin of the image remains unexplored
        margin = self.margin-3 # for neighbour occupiung points
        self.image [:margin ,:] = 127
        self.image [-margin:,:] = 127
        self.image [:, :margin ] = 127
        self.image [:, -margin:] = 127

################################################################################
class ROIPatcher:
    def __init__(self, fig, image, patch_value):
        self.fig = fig
        self.fig.add_axes([0, 0, 1, 1])
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self)

        self.image = image.copy()
        self.patch_value = patch_value
        self.points = []

        #  draw the image
        self._reset_drawing()

    def __call__(self, event):
        '''
        since self is passed to mpl_connect as the callback method
        every time 'button_press_event' happens, the self (i.e. this method)
        is called
        We could simply calls this onclick and pass it to mpl_connect.
        '''
        if event.button == 1:
            # left click adds a new point to the queue
            if event.xdata is not None:
                [x, y] = [int(event.xdata), int(event.ydata)]
                self.points.append([x, y])
                self.fig.axes[0].plot(x, y, 'r.')
                plt.draw()

        elif event.button == 2:
            # mildde click resets selection
            self._reset_drawing()
            self.points = []

        elif event.button == 3:
            # right lick constructs a path from selected points
            # and sets all the pixels inside the path to a predefined value
            self.path = create_mpath(np.array(self.points))
            self.pixels_in_path = get_pixels_in_mpath(self.path, self.image.shape)
            self.image[self.pixels_in_path[:,1],
                       self.pixels_in_path[:,0]] = self.patch_value

            # drawing modified image
            self._reset_drawing()

            # point selection is reset to allow iterations of patching
            self.points = []

    def _reset_drawing (self):
        ''' '''
        plt.cla()
        self.fig.axes[0].imshow( self.image,
                                 cmap = 'gray', interpolation='nearest', origin='lower',
                                 vmin=0, vmax=255)
        plt.draw()

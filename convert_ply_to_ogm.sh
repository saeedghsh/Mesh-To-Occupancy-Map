# Copyright (C) 2017 Saeed Gholami Shahbandi. All rights reserved.

# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>


#!/bin/bash -ue

file_list=(
    # '/home/saesha/Documents/tango/kpt4a_f/20170131163311.ply'
    # '/home/saesha/Documents/tango/kpt4a_kb/20170131163634.ply'
    # '/home/saesha/Documents/tango/kpt4a_kl/20170131162628.ply'
    # '/home/saesha/Documents/tango/kpt4a_lb/20170131164048.ply'
    
    # '/home/saesha/Documents/tango/HIH_01_full/20170131135829.ply'
    
    # '/home/saesha/Documents/tango/E5_1/20170131150415.ply'
    # '/home/saesha/Documents/tango/E5_2/20170131131405.ply'
    # '/home/saesha/Documents/tango/E5_3/20170131130616.ply'
    # '/home/saesha/Documents/tango/E5_4/20170131122040.ply'
    # '/home/saesha/Documents/tango/E5_5/20170205104625.ply'
    # '/home/saesha/Documents/tango/E5_6/20170205105917.ply'
    # '/home/saesha/Documents/tango/E5_7/20170205111301.ply'
    # '/home/saesha/Documents/tango/E5_8/20170205112339.ply'

    # '/home/saesha/Documents/tango/F5_1/20170131132256.ply'
    # '/home/saesha/Documents/tango/F5_2/20170131125250.ply'
    # '/home/saesha/Documents/tango/F5_3/20170205114543.ply'
    # '/home/saesha/Documents/tango/F5_4/20170205115252.ply'
    # '/home/saesha/Documents/tango/F5_5/20170205115820.ply'

    # xxx '/home/saesha/Documents/tango/backfrdeadagain/new/20170205105337.ply'
    # '/home/saesha/Documents/tango/backfrdeadagain/new/20170205110552.ply'
    # '/home/saesha/Documents/tango/backfrdeadagain/new/20170205111807.ply'
    # '/home/saesha/Documents/tango/backfrdeadagain/new/20170205114156.ply'
    # xxx '/home/saesha/Documents/tango/backfrdeadagain/new/20170205114832.ply'
)

for file_name in "${file_list[@]}"
do
    echo processing file $file_name ...
    python mesh_to_ogm_v2.py $file_name
    python mesh_to_ogm_v1.py -s --filename $file_name
done

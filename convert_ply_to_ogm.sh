#!/bin/bash -ue

file_list=(
    '/home/saesha/Documents/tango/kpt4a_f/20170131163311.ply'
    '/home/saesha/Documents/tango/kpt4a_kb/20170131163634.ply'
    '/home/saesha/Documents/tango/kpt4a_kl/20170131162628.ply'
    '/home/saesha/Documents/tango/kpt4a_lb/20170131164048.ply'
    
    '/home/saesha/Documents/tango/HIH_01_full/20170131135829.ply'
    
    '/home/saesha/Documents/tango/E5_1/20170131150415.ply'
    '/home/saesha/Documents/tango/E5_2/20170131131405.ply'
    '/home/saesha/Documents/tango/E5_3/20170131130616.ply'
    '/home/saesha/Documents/tango/E5_4/20170131122040.ply'
    '/home/saesha/Documents/tango/E5_5/20170205104625.ply'
    '/home/saesha/Documents/tango/E5_6/20170205105917.ply'
    '/home/saesha/Documents/tango/E5_7/20170205111301.ply'
    '/home/saesha/Documents/tango/E5_8/20170205112339.ply'

    '/home/saesha/Documents/tango/F5_1/20170131132256.ply'
    '/home/saesha/Documents/tango/F5_2/20170131125250.ply'
    '/home/saesha/Documents/tango/F5_3/20170205114543.ply'
    '/home/saesha/Documents/tango/F5_4/20170205115252.ply'
    '/home/saesha/Documents/tango/F5_5/20170205115820.ply'
)

for file_name in "${file_list[@]}"
do
    echo processing file $file_name ...
    # python mesh_to_ogm_v2.py $file_name
    python mesh_to_ogm_v1.py -s --filename $file_name
done

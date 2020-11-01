#!/usr/bin/env python3
import subprocess
import os
import shutil

#--- set the directory to reorganize below
dr = "../photos"
#--- set the number of files/folders per level
size = 100

level = 0
def move(fn, drn, level):
    folder = dr+"/"+str(drn)+"_"+str(level)
    if not os.path.exists(folder):
        os.mkdir(folder)
    shutil.move(dr+"/"+f, folder+"/"+f)

while len(os.listdir(dr)) > size:
    level += 1
    fn = 0; drn = 1
    for f in os.listdir(dr):
        if fn < size:
            move(fn, drn, level)
        else:
            fn = 0
            drn += 1
            move(fn, drn, level)
        fn += 1

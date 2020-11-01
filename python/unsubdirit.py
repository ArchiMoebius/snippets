#!/usr/bin/env python3
import shutil
import os

#--- set the directory, the same as the first script
dr = "./photos"
#---

# move the files back
for root, dirs, files in os.walk(dr):
    for file in files:
        shutil.move(root+"/"+file, dr+"/"+file)
# remove the (now empty) subdirectories
for d in os.listdir(dr):
    folder = dr+"/"+d
    if os.path.isdir(folder):
        shutil.rmtree(folder)

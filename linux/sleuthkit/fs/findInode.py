#!/usr/bin/python

import sys, os, subprocess, re

def runCommand(cmd):
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    return [proc.stdout.read(), proc.stderr.read()]

def locateInode(ddImage, fsoffset, soffset):

    cmd = "%s -o %s %s | %s -n 40 | %s -i \"block size:\" | %s -f3 -d' '" %(PATHS['fsstat'], fsoffset, ddImage, PATHS['head'], PATHS['grep'], PATHS['cut'])
    blockSize = runCommand(cmd)[0].strip()

    cmd = "%s \"ibase=10;(%s*512 - %s*512)/%s\" | %s" % (PATHS['echo'], soffset, fsoffset, blockSize, PATHS['bc'])
    print "Locating fileBlockLocation:\n %s \n" % (cmd)
    fileBlockLocation = runCommand(cmd)[0].strip()

    if fileBlockLocation != "":
        cmd = "%s -o %s -f ext -d %s %s" % (PATHS['ifind'], fsoffset, fileBlockLocation, ddImage)
        print "Locating inode for fileBlockLocation:\n %s \n" % (cmd)
        return runCommand(cmd)[0].strip()


def main(argv):
    print "\nUsing paths:"
    for item in PATHS:
        print "\t%s = %s" % (item, PATHS[item])

    if len(argv) < 2:
        sys.stderr.write("\nUsage: %s <dd image> <filesystem offset> <sector offset>\n" % (argv[0],))
        return 1

    if not os.path.exists(argv[1]):
        sys.stderr.write("\nERROR: an input file was not found!\n")
        return 1

    ddImage = argv[1]
    offset = argv[2]
    soffset = argv[3]

    inodes = locateInode(ddImage, offset, soffset)
    print inodes



if __name__ == "__main__":
    PATHS = {}
    PATHS['dd'] = runCommand('which dd')[0].strip()
    PATHS['echo'] = runCommand('which echo')[0].strip()
    PATHS['bc'] = runCommand('which bc')[0].strip()
    PATHS['awk'] = runCommand('which awk')[0].strip()
    PATHS['sort'] = runCommand('which sort')[0].strip()
    PATHS['grep'] = runCommand('which grep')[0].strip()
    PATHS['cut'] = runCommand('which cut')[0].strip()
    PATHS['sed'] = runCommand('which sed')[0].strip()
    PATHS['head'] = runCommand('which head')[0].strip()
    PATHS['ils'] = runCommand('which ils')[0].strip()
    PATHS['xxd'] = runCommand('which xxd')[0].strip()
    PATHS['ifind'] = runCommand('which ifind')[0].strip()
    PATHS['jls'] = runCommand('which jls')[0].strip()
    PATHS['jcat'] = runCommand('which jcat')[0].strip()
    PATHS['blkcat'] = runCommand('which blkcat')[0].strip()
    PATHS['istat'] = runCommand('which istat')[0].strip()
    PATHS['fsstat'] = runCommand('which fsstat')[0].strip()
    sys.exit(main(sys.argv))

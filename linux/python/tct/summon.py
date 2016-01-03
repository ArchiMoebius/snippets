#!/usr/bin/python

import sys, os, subprocess, re

"""
Supply with a dd image of a fs and a tct timeline we recover all files listed by inode in the timeline using icat
"""

def runCommand(cmd):
    print "\nExecuting Command:\n\n\t {c}\n\nOutput:\n".format(c=cmd)
    print subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.read()

def main(argv):
    if len(argv) < 4:
        sys.stderr.write("\nUsage: %s <hdax.dd> <timeline> <icat path>\n" % (argv[0],))
        return 1

    if not os.path.exists(argv[1]) or not os.path.exists(argv[2]) or not os.path.exists(argv[3]):
        sys.stderr.write("\nERROR: input file was not found!\n")
        return 1

    inputFile = file(argv[2], "r")
    icatPath = argv[3]

    for line in inputFile:
        m = re.search('(?<=-)\d+', line.strip().split("<")[1])
        if m:
            print "recovering Inode: %s" % m.group(0)
            runCommand("%s %s %s > %s" % (icatPath, argv[1], m.group(0), m.group(0)))


if __name__ == "__main__":
    sys.exit(main(sys.argv))


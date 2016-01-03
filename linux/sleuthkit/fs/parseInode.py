#!/usr/bin/python

import sys, os, subprocess, re

def runCommand(cmd):
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    return [proc.stdout.read(), proc.stderr.read()]

def parseInodeInfo(inode):
    cnt = 0
    size = ""
    dblks = []
    siblks = {}
    v = ""
    vi = ""
    c = 1
    for line in inode:
        cmd = "%s \"%s\" | %s -f 2,3,4,5,6,7,8,9 -d' '" % (PATHS['echo'], line.strip(), PATHS['cut'])
        line = runCommand(cmd)[0].strip().split(' ')

        for value in line:
            if value != "":
                if cnt >=4 and cnt <= 6:
                    size = size + value[1] + value[0] + value[3] + value[2]
                if cnt >=40 and cnt <= 86:
                    v = v + value[1] + value[0] + value[3] + value[2]

                    if c % 2 == 0 and v != "":
                        retval = runCommand("%s \"ibase=16;%s\" | %s" % (PATHS['echo'], v[::-1].upper(), PATHS['bc']))[0].strip()
                        if retval != "0":
                            dblks.append(retval)
                        v = ""

                if cnt >=88 and cnt <= 90:
                    vi = vi + value[1] + value[0] + value[3] + value[2]

                    if c % 2 == 0 and vi != "":
                        retval = runCommand("%s \"ibase=16;%s\" | %s" % (PATHS['echo'], vi[::-1].upper(), PATHS['bc']))[0].strip()
                        if retval != "0":

                            siblks[retval] = parseSingleIndirectBlock(retval)
                        vi = ""


                c = c + 1
                cnt = cnt + 2

            if cnt == 16:
                size = runCommand("%s \"ibase=16;%s\" | %s" % (PATHS['echo'], size[::-1].upper(), PATHS['bc']))[0].strip()

    return {'size':size,'db':dblks, 'si':siblks}

def parseSingleIndirectBlock(siBlock):
    cmd = "%s -o %s %s %s | %s | %s -f 2,3,4,5,6,7,8,9 -d' '" % (PATHS['blkcat'], offset, ddImage, siBlock, PATHS['xxd'], PATHS['cut'])
    retval = runCommand(cmd)[0].strip().split('\n')

    v = ""
    c = 0
    blks = []

    for line in retval:
        for value in line.split(' '):
            v = v + value[1] + value[0] + value[3] + value[2]
            c = c + 1

            if c % 2 == 0:
                val = runCommand("%s \"ibase=16;%s\" | %s" % (PATHS['echo'], v[::-1].upper(), PATHS['bc']))[0].strip()
                if val != "0":
                    blks.append(val)
                v = ""
    return blks


def main(argv):
    print "\nUsing paths:"
    for item in PATHS:
        print "\t%s = %s" % (item, PATHS[item])

    if len(argv) < 2:
        sys.stderr.write("\nUsage: %s <xxd input> \n" % (argv[0],))
        return 1

    if not os.path.exists(argv[1]):
        sys.stderr.write("\nERROR: an input file was not found!\n")
        return 1

    xxdData = open(argv[1], "r")
    print parseInodeInfo(xxdData.readlines())
    xxdData.close()


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
    PATHS['ils'] = runCommand('which ils')[0].strip()
    PATHS['xxd'] = runCommand('which xxd')[0].strip()
    PATHS['jls'] = runCommand('which jls')[0].strip()
    PATHS['jcat'] = runCommand('which jcat')[0].strip()
    PATHS['blkcat'] = runCommand('which blkcat')[0].strip()
    PATHS['istat'] = runCommand('which istat')[0].strip()
    PATHS['fsstat'] = runCommand('which fsstat')[0].strip()
    sys.exit(main(sys.argv))

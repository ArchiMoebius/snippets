#!/usr/bin/python

import sys, os, subprocess, re

def runCommand(cmd):
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    return [proc.stdout.read(), proc.stderr.read()]

def getInodes(ddImage, offset):
    cmd = "%s -r -o %s %s | %s -e \'s/|/ /g\' | %s -n --key=5,5 | %s -e \'/^[A-Za-z]/d\' | %s -f1 -d\' \'" % (PATHS['ils'], offset, ddImage, PATHS['sed'], PATHS['sort'], PATHS['sed'], PATHS['cut'])
    return runCommand(cmd)[0].strip().split('\n')

def getInodeGroup(ddImage, offset, inode):
    cmd = "%s -o %s %s %s | %s -i \"group:\" | %s -f2 -d\' \'" %(PATHS['istat'], offset, ddImage, inode, PATHS['grep'], PATHS['cut'])
    return runCommand(cmd)[0].strip()

def getGroupInfo(ddImage, offset, inode, group):
    cmd = "%s -o %s %s | grep -i -A 11 \"group: %s:\" | %s \"Inode Range:\" | %s -F' ' '{OFS=\":\";print $5,$3}'" %(PATHS['fsstat'], offset, ddImage, group, PATHS['grep'], PATHS['awk'])

    inodeRange = runCommand(cmd)[0].strip().split(':')

    cmd = "%s -o %s %s | grep -i -A 11 \"group: %s:\" | %s \"Inode Table:\" | %s -F' ' '{OFS=\":\";print $5,$3}'" %(PATHS['fsstat'], offset, ddImage, group, PATHS['grep'], PATHS['awk'])

    inodeTableRange = runCommand(cmd)[0].strip().split(':')

    inodeRangeSize = runCommand("%s \"%s - %s\" | %s" %(PATHS['echo'], inodeRange[0], inodeRange[1], PATHS['bc']))[0].strip()

    inodeTableRangeSize = runCommand("%s \"%s - %s\" | %s" %(PATHS['echo'], inodeTableRange[0], inodeTableRange[1], PATHS['bc']))[0].strip()

    inodesPerBlock = runCommand("%s \"%s / %s\" | %s" %(PATHS['echo'], inodeRangeSize, inodeTableRangeSize, PATHS['bc']))[0].strip()

    inodeBlockToFind = runCommand("%s \"%s + (%s - %s) / %s\" | %s" % (PATHS['echo'], inodeTableRange[1], inode, inodeRange[1], inodesPerBlock, PATHS['bc']))[0].strip()
    inodesIntoBlock = runCommand("%s \"(%s - %s)%s %s\" | %s" % (PATHS['echo'], inode, inodeRange[1], '%', inodesPerBlock, PATHS['bc']))[0].strip()

    return {'ibtf':inodeBlockToFind, 'iib':inodesIntoBlock}

def getBlocksToSearch(ddImage, offset, block):
    return runCommand("%s -o %s %s | %s \"%s\" | %s -f1 -d':'" % (PATHS['jls'], offset, ddImage, PATHS['grep'], block, PATHS['cut']))[0].strip().split('\n')

def checkBlockInode(ddImage, offset, jlsBlock, jlsBlockInode):
    cmd = "%s -o %s %s %s | %s skip=%s bs=128 count=1 | %s" % (PATHS['jcat'], offset, ddImage, jlsBlock, PATHS['dd'], jlsBlockInode, PATHS['xxd'])
    return runCommand(cmd)[0].strip()

def parseInodeInfo(ddImage, offset, inode):
    cnt = 0
    size = ""
    dblks = []
    siblks = {}
    v = ""
    vi = ""
    c = 1
    inode = inode.strip().split('\n')
    for line in inode:
        cmd = "%s \"%s\" | %s -f 2,3,4,5,6,7,8,9 -d' '" % (PATHS['echo'], line.strip(), PATHS['cut'])
        line = runCommand(cmd)[0].strip().split(' ')

        for value in line:
            if value != "":
                if cnt >=4 and cnt <= 6:
                    if value != "":
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

                            siblks[retval] = parseSingleIndirectBlock(ddImage, offset, retval)
                        vi = ""


                c = c + 1
                cnt = cnt + 2

            if cnt == 16:
                size = runCommand("%s \"ibase=16;%s\" | %s" % (PATHS['echo'], size[::-1].upper(), PATHS['bc']))[0].strip()

    return {'size':size,'db':dblks, 'si':siblks}

def parseSingleIndirectBlock(ddImage, offset, siBlock):
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

def ripBlocks(ddImage, offset, blocks, outputDir, name):
    for block in blocks:
        print "\t %s" % block
        runCommand("%s -o %s %s %s >> %s/%s" % (PATHS['blkcat'], offset, ddImage, block, outputDir, name))

def main(argv):
    print "\nUsing paths:"
    for item in PATHS:
        print "\t%s = %s" % (item, PATHS[item])

    if len(argv) < 3:
        sys.stderr.write("\nUsage: %s <hdax.dd> <offset> <output folder> \n" % (argv[0],))
        return 1

    if not os.path.exists(argv[1]):
        sys.stderr.write("\nERROR: an input file was not found!\n")
        return 1

    if not os.path.exists(argv[3]):
        os.makedirs(argv[3])

    outputDir = argv[3]
    ddImage = argv[1]
    offset = argv[2]
    inodes = getInodes(ddImage, offset)

    for inode in inodes:
        group = getInodeGroup(ddImage, offset, inode)
        jcatInfo = getGroupInfo(ddImage, offset, inode, group)
        jlsInfo = getBlocksToSearch(ddImage, offset, jcatInfo['ibtf'])
        for block in jlsInfo:
            print "Searching block: %s at inode: %s for inode: %s" %(block, jcatInfo['iib'], inode)
            xxdOutput = checkBlockInode(ddImage, offset, block, jcatInfo['iib'])
            blockInfo = parseInodeInfo(ddImage, offset, xxdOutput)

            if len(blockInfo['db']) > 0:
                print "Ripping Direct Blocks"
                ripBlocks(ddImage, offset, blockInfo['db'], outputDir, "image.%s.offset.%s.inode.%s"%(ddImage, offset, inode))

                if len(blockInfo['si']) > 0:
                    print "Ripping Single Indirect Blocks"

                    for siBlock in blockInfo['si']:
                        ripBlocks(ddImage, offset, blockInfo['si'][siBlock], outputDir, "image.%s.offset.%s.inode.%s"%(ddImage, offset, inode))

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
    PATHS['blkcat'] = runCommand('which blkcat')[0].strip()
    PATHS['jls'] = runCommand('which jls')[0].strip()
    PATHS['jcat'] = runCommand('which jcat')[0].strip()
    PATHS['istat'] = runCommand('which istat')[0].strip()
    PATHS['fsstat'] = runCommand('which fsstat')[0].strip()
    sys.exit(main(sys.argv))

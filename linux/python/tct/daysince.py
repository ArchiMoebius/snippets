#!/usr/bin/python

import sys, os, subprocess, re

"""
Given two dates this tool calculates the number of days between them.
reference: http://stackoverflow.com/questions/3385003/shell-script-to-get-difference-in-two-dates
"""

def runCommand(cmd):
    print "\nExecuting Command:\n\n\t {c}\n\nOutput:\n".format(c=cmd)
    print subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.read()

def main(argv):
    if len(argv) < 2:
        sys.stderr.write("\nUsage: %s <day-month-year> <day-month-year>\n" % (argv[0],))
        return 1

    runCommand('echo $(( ($(date -ud "{date_big}" +%s) - $(date -ud "{date_small}" +%s)) / 86400 ))'.format(date_big=argv[2], date_small=argv[1]))

if __name__ == "__main__":
    sys.exit(main(sys.argv))

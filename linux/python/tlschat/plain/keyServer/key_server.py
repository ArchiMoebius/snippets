"""
Simple server
"""

from OpenSSL import SSL
from KeyServer import *
import sys, os, select, socket

if len(sys.argv) < 2:
    print 'Usage: python key_server.py PORT'
    sys.exit(1)

keys = {}
keys['CA.cert'] = os.path.join(os.getcwd(), '../keys'+os.sep+'CA.cert')
keys['CA.pkey'] = os.path.join(os.getcwd(), '../keys'+os.sep+'CA.pkey')

keyServer = KeyServer(sys.argv[1], keys, './payload')

while keyServer.runServer:
    try:
        r,w,x = select.select(keyServer.clients.keys(), [], [])
    except:
        print "There was an error..."
        break

    keyServer.parseInput(r)

keyServer.shutdown()

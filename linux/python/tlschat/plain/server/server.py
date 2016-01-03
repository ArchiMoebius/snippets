"""
Simple server
"""

from OpenSSL import SSL
from ChatServer import *
import sys, os, select, socket

if len(sys.argv) < 2:
    print 'Usage: python[2] server.py PORT'
    sys.exit(1)

# Initialize context
keys = {}
keys['pkey'] = os.path.join(os.getcwd(), '../keys'+os.sep+'server.pkey')
keys['cert'] = os.path.join(os.getcwd(), '../keys'+os.sep+'server.cert')
keys['CAcert'] = os.path.join(os.getcwd(), '../keys'+os.sep+'CA.cert')

chatServer = ChatServer(sys.argv[1], keys, SSL.TLSv1_METHOD)

while chatServer.runServer:
    try:
        r,w,x = select.select(chatServer.clients.keys(), [], [])
    except:
        print "There was an error..."
        break

    chatServer.parseInput(r)

chatServer.shutdown()

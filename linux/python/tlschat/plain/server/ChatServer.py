from OpenSSL import SSL
from threading import Thread
import sys, os, select, socket, re, base64

class ChatServer:
    def __init__(self, port, keys, method):
        self.pkey = keys['pkey']
        self.cert = keys['cert']
        self.cacert = keys['CAcert']
        self.clients = {}
        self.writers = {}
        self.runServer = True
        self.setup(port, method)

    def dropClient(self, client, errors=None):
	    msg = 'Client left'
	    print msg;
	    self.sendMsgToAll(client, msg)

	    if errors:
	        print 'Client %s left with error(\'s) :' % (self.clients[client],)
	        print '  ', errors
	    else:
	        print 'Client %s left politely' % (self.clients[client],)

	    if self.clients.has_key(client):
	        del self.clients[client]

	    if self.writers.has_key(client):
        	del self.writers[client]

	    if not errors:
        	client.shutdown()

	    client.close()

    def sendMsgToAll(self, client, msg):
	    for c in self.writers:
        	if client != c:
		    try:
	            	c.send(msg)
	            except Exception:
                        pass
    """TODO: add better exception handling..."""

    def parseInput(self, r):
	    for cli in r:
        	if cli == self.sock:
	            cli,addr = self.sock.accept()
		    msg = '\n(Connected: New client from IP: %s:%s)' % (addr[0],addr[1])
	            print msg;
        	    self.sendMsgToAll(None, msg)
	            self.clients[cli] = addr
        	    self.writers[cli] = addr
	        elif cli == 0:
		    data = sys.stdin.readline().strip()

		    if data == 'exit':
		            self.runServer = False
			    del self.clients[0] #remove sys.stdin
			    self.shutdown()
		            break

		    if data == 'list':
			    cnt = 0
			    print "\nConnected Clients:\n"

			    for addr in self.clients.values():
				    if addr !=0 and addr != self.sock:
					    print "[%d] %s" % (cnt, addr)
				    cnt+=1
		    if data:
			m = re.search('(?<=kick#)\w+', data)

                	if m:
        	            kickindex = (int(m.group(0)))
			    print "kicking index: %d" % kickindex
			    cnt = 0

			    for client in self.clients.keys():
				    if cnt == kickindex:
					    self.dropClient(client)
					    break;
			    	    cnt+=1
	        else:
	            try:
	                ret = cli.recv(1024)
	                self.sendMsgToAll(cli, ret)
	            except (SSL.WantReadError, SSL.WantWriteError, SSL.WantX509LookupError):
	                pass
	            except SSL.ZeroReturnError:
	                self.dropClient(cli)
	            except SSL.Error, errors:
	                self.dropClient(cli, errors)

    def shutdown(self):
        self.sendMsgToAll(None, '\nThe server is shutting down...\n')

        for cli in self.clients.keys():
                cli.close()
        self.sock.close()

    def verifyCert(self, conn, cert, errnum, depth, ok):
        """This obviously has to be updated"""
        print '\nGot certificate: %s\n' % cert.get_subject()
        return ok

    def setup(self, port, method):
        self.ctx = SSL.Context(method)
        self.ctx.set_verify(SSL.VERIFY_PEER|SSL.VERIFY_FAIL_IF_NO_PEER_CERT, self.verifyCert)
        self.ctx.set_options(SSL.OP_NO_SSLv2|SSL.OP_NO_SSLv3)
        self.ctx.use_privatekey_file (self.pkey)
        self.ctx.use_certificate_file(self.cert)
        self.ctx.load_verify_locations(self.cacert)
        self.sock = SSL.Connection(self.ctx, socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self.sock.bind(('', int(port)))
        self.sock.listen(3)
        self.sock.setblocking(0)
        """without this, no go..."""
        self.clients[self.sock] = self.sock
        self.clients[0] = 0 #sys.stdin

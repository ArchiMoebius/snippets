from OpenSSL import SSL
import sys, os, select, socket, getpass, base64, shutil, json, logging

class ChatClient:
    def __init__(self, server, port, keys, method, nick):
        try:
            logging.basicConfig(filename='logs/client.log', level=logging.DEBUG)
        except Exception as err:
            print "Failed to configure log", err

        self.keys = {}
        self.server = server
        self.port = int(port)
        self.tcpport = self.port+42
        self.nick = nick

        self.setupENC()

        if not self.checkLoadKeys(keys) and not self.connectENC():
            logging.critical("\nfailed to load keys\n")
            os.sys.exit(-1)

        self.setupSSL(method)

    def checkLoadKeys(self, keys):
        ret = True
        if not 'CA.cert' in keys or not 'client.pkey' in keys or not 'client.cert' in keys or not os.path.isfile(keys['CA.cert']) or not os.path.isfile(keys['client.cert']) or not os.path.isfile(keys['client.pkey']):

            logging.critical("You must supply me with keys!\n")
            logging.critical("I need:\nCA.cert, client.pkey and client.cert\n")
            ret = False
        else:
            self.keys['CA.cert'] = keys['CA.cert']
            self.keys['client.cert'] = keys['client.cert']
            self.keys['client.pkey'] = keys['client.pkey']
        return ret

    def isRunning(self):
        return self.running

    def start(self):
        self.connectSSL()
        self.printNick()
        self.running = True

    def printNick(self):
        sys.stdout.write(self.nick+" : ")
        sys.stdout.flush()

    def stop(self):
        self.running = False

    def send(self, data):
        success = True
        try:
            self.sock.send(data)
            self.printNick()
        except SSL.Error:
            print 'Connection died unexpectedly'
            success = False
        return success

    def read(self, bufsz):
        try:
            data = self.sock.recv(bufsz)
        except Exception:
            print 'Server disconnected...'
            self.sock.close()
            sys.exit(-1)
            return False
        if not data:
	        return False
        else:
            sys.stdout.write('\n' + data + '\n')
            self.printNick()
            sys.stdout.flush()

    def shutdown(self):
	    self.sock.send('\n%s is leaving\n' % self.nick)
	    self.sock.shutdown()
	    self.sock.close()

    def verifyCert(self, conn, cert, errnum, depth, ok):
	    #update this so it's more 'secure'...   ;-P
	    print '\nGot certificate: %s\n' % cert.get_subject()
	    return ok

    def setupSSL(self, method):
	    #Define connection enc level
	    self.ctx = SSL.Context(method)
	    #Demand a cert
	    self.ctx.set_verify(SSL.VERIFY_PEER, self.verifyCert)
	    try:
	        self.ctx.use_privatekey_file(self.keys['client.pkey'])
	        self.ctx.use_certificate_file(self.keys['client.cert'])
	        self.ctx.load_verify_locations(self.keys['CA.cert'])
	    except Exception as err:
	        logging.critical("failed", err)
	    self.sock = SSL.Connection(self.ctx, socket.socket(socket.AF_INET, socket.SOCK_STREAM))

    def setupENC(self):
        print "using %s at %d" %(self.server, self.tcpport)
        self.tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connectENC(self):
        ret = True
        print "starting"
        try:
            parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sys.path.insert(0,parentdir)
            from libs import gnupg
        except Exception as err:
            print "fail", err

        """setup gpg info"""

        """
        hd = os.path.join(os.getcwd(), 'GPGKeys')

        if os.path.exists(hd):
            shutil.rmtree(hd)

        hd = os.path.join(os.getcwd(), 'GPGKeys')

        """
        self.tcpsock.connect((self.server, self.tcpport))
        """
        print "connected, making key"
        gpg = gnupg.GPG(gnupghome=hd)
        input_data = gpg.gen_key_input(name_email=getpass.getuser()+'@'+socket.gethostname(), key_type='RSA', key_length=1024)
        key = gpg.gen_key(input_data)
        print key
        pub_key = gpg.export_keys(key)
        print "using key: " + pub_key
        print "\n\nsendingkey: " + base64.b64encode(pub_key)

        self.tcpsock.send(base64.b64encode(pub_key))
        """
        kf = open("../keyServer/tk", "r")
        k = kf.read()
        kf.close()

        self.tcpsock.send(base64.b64encode(k))
        data = self.tcpsock.recv(10000)
        self.tcpsock.close()

        try:
            info = json.loads(base64.b64decode(data))
        except Exception as err:
            print "Failed", err

        CAcert = open("../keys/CA.cert", "w")
        CAcert.write(base64.b64decode(info['CA.cert']))
        CAcert.close()

        clientcert = open("../keys/client.cert","w")
        clientcert.write(base64.b64decode(info['client.cert']))
        clientcert.close()

        clientpkey = open("../keys/client.pkey","w")
        clientpkey.write(base64.b64decode(info['client.pkey']))
        clientpkey.close()
        return ret

    def connectSSL(self):
        print "start connect SSL"
        self.sock.connect((self.server, self.port))
        print "start send"
        self.sock.send('\n%s has connected\n' % self.nick)
        print "sent"

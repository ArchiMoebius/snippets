from OpenSSL import SSL, crypto
from threading import Thread
import sys, os, select, socket, re, base64, shutil, json, logging, random

"""
Two things are needed before this program can work
there must be both a CA.pkey and CA.cert sothat this
can distribute keys as needed.
"""

class KeyServer:
    def __init__(self, port, keys, payloadDir):
        self.keys = {}
        try:
            logging.basicConfig(filename='logs/keyServer.log',level=logging.DEBUG)
        except Exception as err:
            print "Failed to configure log", err

        if not self.checkLoadKeys(keys):
            logging.error("\nFailed to load server cert or pkey\n")
            os.sys.exit(-1)

        self.payloadDir = payloadDir
        self.clients = {}
        self.setup(port)
        self.runServer = True

    def checkLoadKeys(self, keys):
        ret = False
        if not 'CA.cert' in keys or not 'CA.pkey' in keys:
            logging.critical("You must supply me with keys!\n")
            logging.critical("I need:\nCA.cert and CA.pkey\n")
        try:
            if os.path.isfile(keys['CA.cert']) and os.path.isfile(keys['CA.pkey']):
                certFile = open(keys['CA.cert'], 'r')
                cert = certFile.read()
                certFile.close()
                keyFile = open(keys['CA.pkey'], 'r')
                key = keyFile.read()
                keyFile.close()
                self.keys['CA.cert'] = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
                self.keys['CA.pkey'] = crypto.load_privatekey(crypto.FILETYPE_PEM, key, '')

                ret = True
        except Exception as e:
            print "Failed", e

        return ret

    def parseInput(self, r):
        for sock in r:
            if sock == self.sock:
                cSock,addr = self.sock.accept()
                msg = '\n(Connected: New client from IP: %s:%s)' % (addr[0],addr[1])
                print msg
                logging.info(msg)
                data = cSock.recv(4094)
                logging.info("source: %s:%s, data: %s" % (addr[0], addr[1], data))
                import_result = ""
                key = ""
                try:
                    key = base64.b64decode(data)
                    logging.info("key"+ key+"\n")
                except:
                    logging.warn("Bad data, not base64 source: %s:%s" %(addr[0], addr[1]))
                    cSock.close()
                    self.sock.close()
                    sys.exit(-1)

                #cSock.send("got your data" + key)

                for k in self.gpg.list_keys():
                    log.info("already have"+k)

                try:
                    import_result = self.gpg.import_keys(key)
                except Exception as err:
                    logging.error("Unable to load key: %s:%s" %(addr[0], addr[1]))
                    cSock.close()
                    self.sock.close()
                    sys.exit(-2)

                logging.info("Sending payload: %s:%s" %(addr[0], addr[1]))

                for key_finger_print in import_result.fingerprints:
                    logging.debug("keyprint: "+key_finger_print+"\n")
                    self.sendPayload(cSock, addr[0], key_finger_print)
                    self.gpg.delete_keys(key_finger_print)

                logging.info("Payload sent: %s:%s" %(addr[0], addr[1]))

                cSock.close()

            elif sock == 0:
                data = sys.stdin.readline().strip()

                if data == 'exit':
                    self.runServer = False
                    del self.clients[0] #remove sys.stdin
                    self.shutdown()
                    break

    def sendPayload(self, client, cname, key_finger_print):
        logging.debug("\nsending data\n" + key_finger_print + "\n" + "from: "+os.getcwd())
        data = {}

        for files in os.listdir("./"):
            logging.debug("sending: " + files +"\n")
            stream = open(files, "r")
            encrypted_ascii_data = self.gpg.encrypt_file(stream, key_finger_print, passphrase='')
            stream.close()

            if encrypted_ascii_data.ok == True:
                data.update({files: base64.b64encode(str(encrypted_ascii_data))})

        serial = random.randint(0, sys.maxint)
        pkey = self.createKeyPair()
        req = self.requestX509Cert(pkey, CN=str(cname))
        cert = self.createSignX509Cert(req, (self.keys['CA.cert'], self.keys['CA.pkey']), serial, (0, 60*60*24*365*5)) # five years
        data.update({'client.pkey': base64.b64encode(crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey))})
        data.update({'client.cert': base64.b64encode(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))})

        logging.debug("\ndata to send back to client:\n" + json.dumps(data))

        client.send(base64.b64encode(json.dumps(data)))

    def createKeyPair(self, type=crypto.TYPE_RSA, len=2048):
        pkey = crypto.PKey()
        pkey.generate_key(type, len)
        return pkey

    def requestX509Cert(self, pkey, digest="md5", **name):
        req = crypto.X509Req()
        subj = req.get_subject()

        for (key,value) in name.items():
            setattr(subj, key, value)

        req.set_pubkey(pkey)
        req.sign(pkey, digest)

        return req

    def createSignX509Cert(self, req, (iCert, iKey), serial, (notBefore, notAfter), digest="md5"):
        cert = crypto.X509()
        cert.set_serial_number(serial)
        cert.gmtime_adj_notBefore(notBefore)
        cert.gmtime_adj_notAfter(notAfter)
        cert.set_issuer(iCert.get_subject())
        cert.set_subject(req.get_subject())
        cert.set_pubkey(req.get_pubkey())
        cert.sign(iKey, digest)
        return cert

    def shutdown(self):
        self.sock.close()

    def setup(self, port):
        try:
            parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sys.path.insert(0,parentdir)
            from libs import gnupg
        except Exception as err:
            print "fail", err
        """setup gpg info"""
        hd = os.path.join(os.getcwd(), 'GPGKeys')

        if os.path.exists(hd):
            shutil.rmtree(hd)

        self.gpg = gnupg.GPG(gnupghome=hd, gpgbinary='gpg')
        self.gpg.encoding = 'utf-8'
        self.homedir = hd
        os.chdir(self.payloadDir)

        """setup tcp socket"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(('', int(port)))
            self.sock.listen(1)
        except Exception as err:
            print "failed on socket init"+ str(err)
            os.sys.exit(-1)

        self.clients[self.sock] = self.sock
        self.clients[0] = 0 #also listen on stdin
        logging.info("\nServer is bound and listening\n")

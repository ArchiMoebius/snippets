"""
This is the ChatClient usage example
"""

from OpenSSL import SSL
from ChatClient import *
import sys, os, select, socket, re

"""
Change this if you wish to a value which doesn't contain any space's
"""
nickname = 'Test_User'

if len(sys.argv) < 3:
    print 'Usage: python client.py HOST PORT'
    sys.exit(1)

keys = {}
keys['client.pkey'] = os.path.join(os.getcwd(), '../keys'+os.sep+'client.pkey')
keys['client.cert'] = os.path.join(os.getcwd(), '../keys'+os.sep+'client.cert')
keys['CA.cert'] = os.path.join(os.getcwd(), '../keys'+os.sep+'CA.cert')

chatClient = ChatClient(sys.argv[1], sys.argv[2], keys, SSL.TLSv1_METHOD, nickname)

chatClient.start()

while chatClient.isRunning():
    r,w,x = select.select([0, chatClient.sock],[],[]);

    for i in r:
        if i == 0:
            data = sys.stdin.readline().strip()

            if data:
                m = re.search('(?<=nick#)\w+', data)

                if m:
                    chatClient.nick = m.group(0)
                    data = data.replace('nick#%s'%chatClient.nick, '')

                if data == 'exit':
                    chatClient.stop()
                    break

            if data != '':
                wasSent = chatClient.send(chatClient.nick+': '+data)
            else:
                chatClient.printNick()
        elif i == chatClient.sock:
            chatClient.read(1024)

chatClient.shutdown();

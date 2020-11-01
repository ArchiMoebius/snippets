from scapy.all import *
import sys

packets=rdpcap("cap.pcap")
data = {}

for p in packets:
    if p.haslayer(UDP) and p.haslayer(Raw):
      if (p[IP].dst == "10.0.0.12" and p[IP].src=="10.0.0.2") or (p[IP].src == "10.0.0.12" and p[IP].dst=="10.0.0.2"):
        key = "%s - %s" % (p[IP].src,p[IP].dst)
        if key not in data:
          data[key] = []
        data[key].append(p[Raw].load)
        # print p[Raw].load, p[IP].src, p[UDP].sport, p[IP].dst, p[IP].dport

for ip, value in data.iteritems():
  print ''.join(value), ip
  print "-========================================-\n"

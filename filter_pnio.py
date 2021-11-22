from scapy.all import *
from scapy.contrib.pnio_rpc import *
from scapy.contrib.dce_rpc import *
from scapy.contrib.pnio import *

load_contrib("pnio")
load_contrib("pnio_rpc")
load_contrib("dce_rpc")


res = sniff(filter="host 192.168.178.155", count=1, iface="Ethernet")
res.summary()
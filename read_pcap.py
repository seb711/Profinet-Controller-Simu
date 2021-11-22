from scapy.all import *
from scapy.contrib.pnio_rpc import *
from scapy.contrib.dce_rpc import *
from scapy.contrib.pnio import *

load_contrib("pnio")
load_contrib("pnio_rpc")
load_contrib("dce_rpc")

scapy_cap = rdpcap('C://Users/sebas//OneDrive//Desktop//pnio_krc4_write_req.pcapng')
for packet in scapy_cap:
    DceRpc(packet[Raw].load).show2()
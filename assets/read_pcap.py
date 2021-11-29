from scapy.all import *
from scapy.contrib.pnio_rpc import *
from scapy.contrib.dce_rpc import *
from scapy.contrib.pnio import *

load_contrib("pnio")
load_contrib("pnio_rpc")
load_contrib("dce_rpc")

scapy_cap = rdpcap('C://Users/sebas//OneDrive//Desktop//pdu_packet.pcapng')
for packet in scapy_cap:
    # ProfinetIO(packet[Raw].load).show2()
    packet.show()
    send(packet, iface="Ethernet"
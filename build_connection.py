from construct_DCP import *
from construct_pniocm import *

ident_msg = get_ident_msg(src="dc:a6:32:58:fc:88", name_of_station="rt-labs-dev")
set_ip_msg = get_set_ip_msg(src="dc:a6:32:58:fc:88", dst="00:0c:29:95:78:31", ip="192.168.178.155")
connect_msg = get_connect_dcprpc_msg(ip="192.168.178.155", path_to_gsdml="./test_project_2.xml")
write_msg = get_write_request_msg(ip="192.168.178.155", path_to_gsdml="./test_project_2.xml")
param_end_msg = get_parameter_end_msg(ip="192.168.178.155")


srp(ident_msg, iface="Ethernet")
srp(set_ip_msg, iface="Ethernet")
sr(connect_msg, iface="Ethernet")
sr(write_msg, iface="Ethernet")
sr(param_end_msg, iface="Ethernet")

res = sniff(filter="udp and host 192.168.178.155 and port 34964", count=1, iface="Ethernet")
if (DceRpc(res[0][Raw].load).haslayer("IODControlReq")): 
    if DceRpc(res[0][Raw].load).getlayer("IODControlReq").ControlCommand_ApplicationReady==1: 
        application_ready_res_msg = get_application_ready_res_msg(ip="192.168.178.155")
        send(application_ready_res_msg, iface="Ethernet")



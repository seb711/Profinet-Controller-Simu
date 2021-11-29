from messages.sim_pnio_dcp import *
from messages.sim_pnio_ps import *
from messages.sim_pnio_cm import *
import uuid
import time

auuid = str(uuid.uuid4())
mac_address_device = ""


# IDENTIFY DEVICE AND MAC
ident_msg = get_ident_msg(src="c0:3e:ba:c9:19:36", name_of_station="rt-labs-dev")
ident_msg_rsp = srp1(ident_msg, iface="Ethernet")
mac_address_device = ident_msg_rsp["Ethernet"].src


set_ip_msg = get_set_ip_msg(src="c0:3e:ba:c9:19:36", dst=mac_address_device, ip="192.168.178.155")
connect_msg = get_connect_dcprpc_msg(ip="192.168.178.155", path_to_gsdml="./gsdml/test_project.xml", auuid=auuid)


# write_msg = get_write_request_msg(ip="192.168.178.155", path_to_gsdml="./gsdml/test_project.xml", auuid=auuid)
# param_end_msg = get_parameter_end_msg(ip="192.168.178.155", auuid=auuid)

# time.sleep(2)
# srp1(set_ip_msg, iface="Ethernet")
# time.sleep(2)
# sr1(connect_msg, iface="Ethernet")
# time.sleep(2)
# sr1(write_msg, iface="Ethernet")
# time.sleep(2)
# sr1(param_end_msg, iface="Ethernet")


# res = sniff(filter="udp and host 192.168.178.155 and port 34964", count=1, iface="Ethernet")
# if (DceRpc(res[0][Raw].load).haslayer("IODControlReq")): 
#     if DceRpc(res[0][Raw].load).getlayer("IODControlReq").ControlCommand_ApplicationReady==1: 
#         DceRpc(res[0][Raw].load).show()
#         obj_uuid = DceRpc(res[0][Raw].load)["DCE/RPC"].object_uuid
#         interface_uuid = DceRpc(res[0][Raw].load)["DCE/RPC"].interface_uuid
#         activity_uuid = DceRpc(res[0][Raw].load)["DCE/RPC"].activity
#         application_ready_res_msg = get_application_ready_res_msg(ip="192.168.178.155", auuid=auuid, obj_uuid=obj_uuid, interface_uuid=interface_uuid, activity_uuid=activity_uuid)
#         send(application_ready_res_msg, iface="Ethernet")



# counter = 0
# while True: 
#     ps_msg = get_data_msg(src="c0:3e:ba:c9:19:36", dst="00:0c:29:95:78:31", counter=counter)
#     ps_msg.show()
#     srp(ps_msg, iface="Ethernet")
#     counter += 1
#     time.sleep(0.1)



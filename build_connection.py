from messages.sim_pnio_dcp import *
from messages.sim_pnio_ps import *
from messages.sim_pnio_cm import *
from getmac import get_mac_address
import uuid
import time

auuid = str(uuid.uuid4())
mac_address_device = ""
device_name = "rt-labs-dev"
mac_src=get_mac_address()
device_ip = "192.168.178.155"
iface = "Ethernet"
path_to_gsdml = "./gsdml/test_project_2.xml"
# IDENTIFY DEVICE AND MAC
ident_msg = get_ident_msg(src=mac_src, name_of_station=device_name)
ans, unans = srp(ident_msg, iface=iface, timeout=1, multi=True)
mac_address_device = ans[-1].answer["Ethernet"].src

if mac_address_device == mac_src or len(ans) < 2:
    print("MAC ADDRESS IS NOT CORRECT!!!")
    print("ABORT")

# SET IP OF DEVICE
# time.sleep(0.5)  # Time Sleep for Wireshark Detection (TODO Test minimum wait time)
set_ip_msg = get_set_ip_msg(
    src=mac_src, dst=mac_address_device, ip=device_ip
)
set_ip_msg.show()
ip_msg_rsp = srp1(set_ip_msg, iface=iface)
# time.sleep(0.5) 

# EXCHANGE CONFIGURATION OF DEVICE
time.sleep(2)
connect_msg = get_connect_dcprpc_msg(
    ip=device_ip, path_to_gsdml=path_to_gsdml, auuid=auuid
)
connect_rsp = sr1(connect_msg, iface=iface, timeout=2, retry=2)

# if not connect_rsp:
#     ping_msg = get_ping_msg(ip=device_ip)
#     ping_rsp = sr1(connect_msg, iface=iface, timeout=2)


# WRITE PARAMETERS OF DEVICE
time.sleep(0.5)
write_msg = get_write_request_msg(
    ip=device_ip, path_to_gsdml=path_to_gsdml, auuid=auuid
)
sr1(write_msg, iface=iface)

# # ANNOUNCE PARAMETER END
# time.sleep(0.5)
# param_end_msg = get_parameter_end_msg(ip=device_ip, auuid=auuid)
# sr1(param_end_msg, iface=iface)

# # WAIT FOR APPLICATION READY RESPONSE
# def send_application_ready_rsp_callback(pkt):
#     if DceRpc in pkt:
#         dce_rpc_pkt = DceRpc(pkt[Raw].load)
#         if dce_rpc_pkt.haslayer("IODControlReq"):
#             if (
#                 dce_rpc_pkt.getlayer("IODControlReq").ControlCommand_ApplicationReady
#                 == 1
#             ):
#                 dce_rpc_pkt.show()
#                 rpc_payload = dce_rpc_pkt["DCE/RPC"]
#                 obj_uuid = rpc_payload.object_uuid
#                 interface_uuid = rpc_payload.interface_uuid
#                 activity_uuid = rpc_payload.activity
#                 application_ready_res_msg = get_application_ready_res_msg(
#                     ip=device_ip,
#                     auuid=auuid,
#                     obj_uuid=obj_uuid,
#                     interface_uuid=interface_uuid,
#                     activity_uuid=activity_uuid,
#                 )
#                 send(application_ready_res_msg, iface="Ethernet")


# application_ready_rqt = sniff(
#     filter="udp and host 192.168.178.155 and port 34964",
#     count=1,
#     store=0,
#     prn=send_application_ready_rsp_callback,
#     iface=iface,
# )

# # SEND CYLIC MESSAGES
# # counter = 0
# # while True:
# #     ps_msg = get_data_msg(src="c0:3e:ba:c9:19:36", dst="00:0c:29:95:78:31", counter=counter)
# #     ps_msg.show()
# #     srp(ps_msg, iface="Ethernet")
# #     counter += 1
# #     time.sleep(0.1)

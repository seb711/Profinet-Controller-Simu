from construct_DCP import *
from construct_pniocm import *
from construct_pnio_ps import *
import uuid
import time

auuid = str(uuid.uuid4())

ident_msg = get_ident_msg(src="c0:3e:ba:c9:19:36", name_of_station="rt-labs-dev")
set_ip_msg = get_set_ip_msg(src="c0:3e:ba:c9:19:36", dst="00:0c:29:95:78:31", ip="192.168.178.155")
connect_msg = get_connect_dcprpc_msg(ip="192.168.178.155", path_to_gsdml="./test_project_2.xml", auuid=auuid)
write_msg = get_write_request_msg(ip="192.168.178.155", path_to_gsdml="./test_project_2.xml", auuid=auuid)
param_end_msg = get_parameter_end_msg(ip="192.168.178.155", auuid=auuid)

srp(ident_msg, iface="Ethernet")
time.sleep(2)
srp(set_ip_msg, iface="Ethernet")
time.sleep(2)
sr(connect_msg, iface="Ethernet")
time.sleep(2)
sr(write_msg, iface="Ethernet")
time.sleep(2)
sr(param_end_msg, iface="Ethernet")


res = sniff(filter="udp and host 192.168.178.155 and port 34964", count=1, iface="Ethernet")
if (DceRpc(res[0][Raw].load).haslayer("IODControlReq")): 
    if DceRpc(res[0][Raw].load).getlayer("IODControlReq").ControlCommand_ApplicationReady==1: 
        DceRpc(res[0][Raw].load).show()
        obj_uuid = DceRpc(res[0][Raw].load)["DCE/RPC"].object_uuid
        print(obj_uuid)
        interface_uuid = DceRpc(res[0][Raw].load)["DCE/RPC"].interface_uuid
        activity_uuid = DceRpc(res[0][Raw].load)["DCE/RPC"].activity
        application_ready_res_msg = get_application_ready_res_msg(ip="192.168.178.155", auuid=auuid, obj_uuid=obj_uuid, interface_uuid=interface_uuid, activity_uuid=activity_uuid)
        send(application_ready_res_msg, iface="Ethernet")



counter = 0
while True: 
    ps_msg = get_data_msg(src="c0:3e:ba:c9:19:36", dst="00:0c:29:95:78:31", counter=counter)
    ps_msg.show()
    srp(ps_msg, iface="Ethernet")
    counter += 1
    time.sleep(0.1)



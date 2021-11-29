from messages.sim_pnio_dcp import *
from messages.sim_pnio_ps import *
from messages.sim_pnio_cm import *
from getmac import get_mac_address
import uuid
import time
from scapy.all import *
from scapy.contrib.pnio_rpc import *
from scapy.contrib.dce_rpc import *
from scapy.contrib.pnio import *

load_contrib("pnio")
load_contrib("pnio_rpc")
load_contrib("dce_rpc")

auuid = str(uuid.uuid4())
mac_address_device = ""
device_name = "rt-labs-dev"
mac_src = get_mac_address()
device_ip = "192.168.178.155"
iface = "Ethernet"
path_to_gsdml = "./gsdml/test_project_2.xml"


def main():
    # IDENTIFY DEVICE AND MAC
    ident_msg = get_ident_msg(src=mac_src, name_of_station=device_name)
    ans, _ = srp(ident_msg, iface=iface, timeout=1, multi=True)
    mac_address_device = ans[-1].answer["Ethernet"].src

    if mac_address_device == mac_src or len(ans) < 2:
        print("MAC ADDRESS IS NOT CORRECT!!!")
        print("ABORT")
        return
    # END IDENTIFY DEVICE AND MAC

    # SET IP OF DEVICE
    set_ip_msg = get_set_ip_msg(src=mac_src, dst=mac_address_device, ip=device_ip)
    ans, _ = srp(set_ip_msg, iface=iface, timeout=1, multi=True)

    ip_rsp = ans[-1].answer
    if not ip_rsp.haslayer("Profinet DCP"):
        print("ANSWER NOT RECEIVED!!!")
        print("ABORT")
        return
    dcp_pkt = ip_rsp["Profinet DCP"]
    # DCP_SERVICE_TYPE = 0x01: "Response Success"
    # DCP_SERVICE_ID = 0x04: "Set"
    if dcp_pkt.service_type != 0x01 or dcp_pkt.service_id != 0x04:
        print("ANSWER NOT CORRECT!!!")
        print("ABORT")
        return
    # END SET IP OF DEVICE

    # EXCHANGE CONFIGURATION OF DEVICE
    time.sleep(2)
    answer_incorrect = True
    while answer_incorrect:
        connect_msg = get_connect_dcprpc_msg(
            ip=device_ip, path_to_gsdml=path_to_gsdml, auuid=auuid
        )
        ans, _ = sr(connect_msg, iface=iface, timeout=2, multi=True)

        connect_rsp = DceRpc(ans[-1].answer[Raw].load)

        if not connect_rsp.haslayer("PNIOServiceResPDU"):
            ping_msg = get_ping_msg(ip=device_ip)
            sr1(ping_msg, iface=iface, timeout=2)
            continue
        dcp_pkt = connect_rsp["PNIOServiceResPDU"]
        # status = 0: "Ok"
        if dcp_pkt.status != 0:
            ping_msg = get_ping_msg(ip=device_ip)
            sr1(ping_msg, iface=iface, timeout=2)
            continue
        answer_incorrect = False

    # END EXCHANGE CONFIGURATION OF DEVICE

    # WRITE PARAMETERS OF DEVICE
    time.sleep(0.5)
    write_msg = get_write_request_msg(
        ip=device_ip, path_to_gsdml=path_to_gsdml, auuid=auuid
    )
    ans, _ = sr(write_msg, iface=iface, timeout=2, multi=True)

    write_rsp = DceRpc(ans[-1].answer[Raw].load)

    if not write_rsp.haslayer("PNIOServiceResPDU"):
        print("WRITE NOT SUCCESSFUL!")
        print("ABORT")
    dcp_pkt = connect_rsp["PNIOServiceResPDU"]
    # status = 0: "Ok"
    if dcp_pkt.status != 0:
        print("WRITE NOT SUCCESSFUL!")
        print("ABORT")
    # END WRITE PARAMETERS OF DEVICE

    # ANNOUNCE PARAMETER END
    param_end_msg = get_parameter_end_msg(ip=device_ip, auuid=auuid)
    sr1(param_end_msg, iface=iface)
    # END ANNOUNCE PARAMETER END

    # WAIT FOR APPLICATION READY RESPONSE
    def send_application_ready_rsp_callback(pkt):
        app_rdy_rsp = DceRpc(pkt[Raw].load)
        if app_rdy_rsp.haslayer("IODControlReq"):
            if (
                app_rdy_rsp.getlayer("IODControlReq").ControlCommand_ApplicationReady
                == 1
            ):
                rpc_payload = app_rdy_rsp["DCE/RPC"]
                obj_uuid = rpc_payload.object_uuid
                interface_uuid = rpc_payload.interface_uuid
                activity_uuid = rpc_payload.activity
                application_ready_res_msg = get_application_ready_res_msg(
                    ip=device_ip,
                    auuid=auuid,
                    obj_uuid=obj_uuid,
                    interface_uuid=interface_uuid,
                    activity_uuid=activity_uuid,
                )
                send(application_ready_res_msg, iface=iface)

    sniff(
        filter=f"udp and host {device_ip} and port 34964",
        store=0,
        count=1,
        prn=send_application_ready_rsp_callback,
        iface=iface,
    )

    # END WAIT FOR APPLICATION READY RESPONSE

    # SEND CYLIC MESSAGES
    counter = 0
    while True:
        ps_msg = get_data_msg(src=mac_src, dst=mac_address_device, counter=counter, path_to_gsdml=path_to_gsdml)
        ans, _ = srp(ps_msg, iface="Ethernet")
        # ans[-1].answer.show()
        counter += 1
        time.sleep(0.1)
    # END SEND CYLIC MESSAGES

if __name__ == "__main__":
    main()

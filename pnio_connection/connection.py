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
import threading

load_contrib("pnio")
load_contrib("pnio_rpc")
load_contrib("dce_rpc")


class PNIOConnection:
    def __init__(self, device_name, device_ip, iface, path_to_gsdml):
        self.auuid = str(uuid.uuid4())
        self.mac_address_device = ""
        self.device_name = device_name
        self.mac_src = get_mac_address()
        self.device_ip = device_ip
        self.iface = iface
        self.device = XMLDevice(path_to_gsdml)
        self.input_data = ""
        self.message_data = PNIOPSMessage()
        self.output_data = []

    def sniff_for_answers(self):
        def update_load(pkt):
            if pkt.haslayer("PROFINET IO Real Time Cyclic Default Raw Data"):
                self.message_data = parse_data_message(pkt, self.device)

        sniff(
            lfilter=lambda d: d.src == self.mac_address_device,
            store=0,
            count=-1,
            prn=update_load,
            iface=self.iface,
        )

    # SEND CYLIC MESSAGES
    def send_messages(self):
        counter = 0
        while True:
            ps_msg = get_data_msg(
                src=self.mac_src,
                dst=self.mac_address_device,
                counter=counter,
                device=self.device,
                data=self.output_data
            )
            ans, _ = srp(ps_msg, iface="Ethernet", verbose=False)
            counter += 1
            time.sleep(1)

    def build_connection(self):
        # IDENTIFY DEVICE AND MAC
        ident_msg = get_ident_msg(src=self.mac_src, name_of_station=self.device_name)
        ans, _ = srp(ident_msg, iface=self.iface, timeout=1, multi=True, verbose=False)
        self.mac_address_device = ans[-1].answer["Ethernet"].src

        if self.mac_address_device == self.mac_src or len(ans) < 2:
            print("MAC ADDRESS IS NOT CORRECT!!!")
            print("ABORT")
            return
        # END IDENTIFY DEVICE AND MAC

        # SET IP OF DEVICE
        set_ip_msg = get_set_ip_msg(
            src=self.mac_src, dst=self.mac_address_device, ip=self.device_ip
        )
        ans, _ = srp(set_ip_msg, iface=self.iface, timeout=1, multi=True, verbose=False)

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
                ip=self.device_ip, device=self.device, auuid=self.auuid
            )
            ans, _ = sr(
                connect_msg, iface=self.iface, timeout=2, multi=True, verbose=False
            )

            connect_rsp = DceRpc(ans[-1].answer[Raw].load)

            if not connect_rsp.haslayer("PNIOServiceResPDU"):
                ping_msg = get_ping_msg(ip=self.device_ip)
                sr1(ping_msg, iface=self.iface, timeout=2, verbose=False)
                continue
            dcp_pkt = connect_rsp["PNIOServiceResPDU"]
            # status = 0: "Ok"
            if dcp_pkt.status != 0:
                ping_msg = get_ping_msg(ip=self.device_ip)
                sr1(ping_msg, iface=self.iface, timeout=2, verbose=False)
                continue
            answer_incorrect = False

        # END EXCHANGE CONFIGURATION OF DEVICE

        # BEGIN CYCLIC MESSAGES
        threading.Thread(target=self.send_messages).start()
        threading.Thread(target=self.sniff_for_answers).start()

        # WRITE PARAMETERS OF DEVICE
        time.sleep(0.5)
        write_msg = get_write_request_msg(
            ip=self.device_ip, device=self.device, auuid=self.auuid
        )
        ans, _ = sr(write_msg, iface=self.iface, timeout=2, multi=True, verbose=False)

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
        param_end_msg = get_parameter_end_msg(ip=self.device_ip, auuid=self.auuid)
        sr1(param_end_msg, iface=self.iface, verbose=False)
        # END ANNOUNCE PARAMETER END

        # WAIT FOR APPLICATION READY RESPONSE
        def send_application_ready_rsp_callback(pkt):
            app_rdy_rsp = DceRpc(pkt[Raw].load)
            if app_rdy_rsp.haslayer("IODControlReq"):
                if (
                    app_rdy_rsp.getlayer(
                        "IODControlReq"
                    ).ControlCommand_ApplicationReady
                    == 1
                ):
                    rpc_payload = app_rdy_rsp["DCE/RPC"]
                    obj_uuid = rpc_payload.object_uuid
                    interface_uuid = rpc_payload.interface_uuid
                    activity_uuid = rpc_payload.activity
                    application_ready_res_msg = get_application_ready_res_msg(
                        ip=self.device_ip,
                        auuid=self.auuid,
                        obj_uuid=obj_uuid,
                        interface_uuid=interface_uuid,
                        activity_uuid=activity_uuid,
                    )
                    send(application_ready_res_msg, iface=self.iface, verbose=False)

        sniff(
            filter=f"udp and host {self.device_ip} and port 34964",
            store=0,
            count=1,
            prn=send_application_ready_rsp_callback,
            iface=self.iface,
        )

        print("Application ready!!!")

    # END WAIT FOR APPLICATION READY RESPONSE

    # END SEND CYLIC MESSAGES


def main():
    con = PNIOConnection()
    con.build_connection()


if __name__ == "__main__":
    main()

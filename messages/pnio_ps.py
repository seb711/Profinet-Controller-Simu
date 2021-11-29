from scapy.all import *
from scapy.contrib.pnio import *

from xmlparser import XMLDevice

load_contrib("pnio")


def get_data_msg(dst, src, counter):
    ether = Ether(dst=dst, src=src, type=0x8892)

    first_iocs = PNIORealTime_IOxS(
        dataState=0x1, instance=0x0, reserved=0x0, extension=0x0
    )

    sec_iocs = PNIORealTime_IOxS(
        dataState=0x0, instance=0x0, reserved=0x0, extension=0x0
    )

    thir_iocs = PNIORealTime_IOxS(
        dataState=0x1, instance=0x0, reserved=0x0, extension=0x0
    )

    four_iocs = PNIORealTime_IOxS(
        dataState=0x1, instance=0x0, reserved=0x0, extension=0x0
    )

    data = PNIORealTimeCyclicDefaultRawData(data="\x80")

    fifth_iocs = PNIORealTime_IOxS(
        dataState=0x1, instance=0x0, reserved=0x0, extension=0x0
    )

    print(chr(counter & 0xff))

    pdu = PNIORealTimeCyclicPDU(
        cycleCounter=16384 * (counter % 4),
        padding="\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        "\x00\x00",
        data=[
            first_iocs,
            sec_iocs,
            thir_iocs,
            four_iocs,
            PNIORealTimeCyclicPDU.build_fixed_len_raw_type(1)(data=chr(counter & 0xff) )
            / PNIORealTime_IOxS(
                dataState=0x1, instance=0x0, reserved=0x0, extension=0x0
            ),
        ],
    )

    cyclic_packet = ProfinetIO(frameID=0x8000)

    return ether / cyclic_packet / pdu

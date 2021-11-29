from scapy.all import *
from scapy.contrib.pnio import *

from helper.gsdml_parser import XMLDevice

load_contrib("pnio")


def get_data_msg(dst, src, counter, path_to_gsdml):
    ether = Ether(dst=dst, src=src, type=0x8892)

    cyclic_packet = ProfinetIO(frameID=0x8000)

    gsdml_object = XMLDevice(path_to_gsdml)

    usable_modules = gsdml_object.body.dap_list[0].usable_modules
    output_data_objects = []
    output_iocs_objects = []

    first_iocs = PNIORealTime_IOxS(
        dataState=0x1, instance=0x0, reserved=0x0, extension=0x0
    )

    sec_iocs = PNIORealTime_IOxS(
        dataState=0x1, instance=0x0, reserved=0x0, extension=0x0
    )

    thir_iocs = PNIORealTime_IOxS(
        dataState=0x1, instance=0x0, reserved=0x0, extension=0x0
    )
    output_frame_offset = 3

    for module in usable_modules:
        if module.used_in_slots != "" and module.input_length != 0:
            output_iocs_objects.append(
                PNIORealTime_IOxS(
                    dataState=0x1, instance=0x0, reserved=0x0, extension=0x0
                )
            )
            output_frame_offset += 1
    for module in usable_modules:
        if module.used_in_slots != "" and module.output_length != 0:
            output_data_objects.append(
                PNIORealTimeCyclicPDU.build_fixed_len_raw_type(module.output_length)(
                    data=chr(counter & 0xFF)
                )
                / PNIORealTime_IOxS(
                    dataState=0x1, instance=0x0, reserved=0x0, extension=0x0
                ),
            )
            output_frame_offset = output_frame_offset + module.output_length + 1

    pdu = PNIORealTimeCyclicPDU(
        cycleCounter=16384 * (counter % 4),
        padding="".join(["\x00" for _ in range(40 - output_frame_offset)]) if output_frame_offset < 40 else "",
        data=[
            first_iocs,
            sec_iocs,
            thir_iocs,
        ] + output_iocs_objects + output_data_objects,
    )

    # four_iocs,
    #         PNIORealTimeCyclicPDU.build_fixed_len_raw_type(1)(data=chr(counter & 0xFF))
    #         / PNIORealTime_IOxS(
    #             dataState=0x1, instance=0x0, reserved=0x0, extension=0x0
    #         )

    return ether / cyclic_packet / pdu

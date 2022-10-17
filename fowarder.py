from PyQt5.QtCore import QObject

import mav_dp as mavlink
from link import SerialLink, UdpLink

mav_for_ser = mavlink.MAVLink(None)
mav_for_udp = mavlink.MAVLink(None)


class Forwarder(QObject):
    def __init__(self, ser: SerialLink, udp: UdpLink):
        super().__init__()

        self.__ser = ser
        self.__udp = udp
        
        self.__msg_reverse_filter_tab_to_udp = []
        self.__msg_reverse_filter_tab_to_ser = []

    def run(self):
        self.__ser.bytesRecieved.connect(self.to_udp)
        self.__udp.bytesRecieved.connect(self.to_ser)

    def add_reverse_filter_to_udp(self, msg_id_list):
        for id in msg_id_list:
            self.__msg_reverse_filter_tab_to_udp.append(id)

    def add_reverse_filter_to_ser(self, msg_id_list):
        for id in msg_id_list:
            self.__msg_reverse_filter_tab_to_ser.append(id)

    def to_udp(self, data: bytes):
        try:
            msg = mav_for_ser.parse_char(data)
            if msg:
                # print("mav sysid %d compid %d msgid %d to udp" %
                #       (msg.get_srcSystem(), msg.get_srcComponent(), msg.get_msgId()))
                # if msg.get_msgId() == mavlink.MAVLINK_MSG_ID_COMMAND_LONG:
                #     print("cmd:%d p1:%d p2:%d p3:%d p4:%d p5:%d p6:%d p7:%d"
                #           % (msg.command,
                #              msg.param1,
                #              msg.param2,
                #              msg.param3,
                #              msg.param4,
                #              msg.param5,
                #              msg.param6,
                #              msg.param7))
                # if msg.get_msgId() == mavlink.MAVLINK_MSG_ID_ACK_SYS_STATE:
                #     print(msg.status_id)
                # if msg.get_msgId() == mavlink.MAVLINK_MSG_ID_ACK_DEVICE_INFO:
                #     print("MAVLINK_MSG_ID_ACK_DEVICE_INFO")

                if msg.get_msgId() in self.__msg_reverse_filter_tab_to_udp:
                    print("mav sysid %d compid %d msgid %d to udp" %
                          (msg.get_srcSystem(), msg.get_srcComponent(), msg.get_msgId()))
                    if msg.get_msgId() == mavlink.MAVLINK_MSG_ID_COMMAND_LONG:
                        print("cmd:%d p1:%d p2:%d p3:%d p4:%d p5:%d p6:%d p7:%d"
                              % (msg.command,
                                 msg.param1,
                                 msg.param2,
                                 msg.param3,
                                 msg.param4,
                                 msg.param5,
                                 msg.param6,
                                 msg.param7))
                    self.__udp.write(msg.get_msgbuf())
        except Exception as e:
            # pass
            print("to_udp:", e)

    def to_ser(self, data: bytes):
        try:
            msg = mav_for_udp.parse_char(data)
            if msg:
                # print("mav sysid %d compid %d msgid %d to serial port" %
                #       (msg.get_srcSystem(), msg.get_srcComponent(), msg.get_msgId()))
                # if msg.get_srcComponent() == 193:
                #     return
                # if msg.get_msgId() == mavlink.MAVLINK_MSG_ID_ACK_SYS_STATE:
                #     print(msg.status_id)
                #     return
                # if msg.get_msgId() == mavlink.MAVLINK_MSG_ID_HEARTBEAT:
                #     return
                # if msg.get_msgId() == mavlink.MAVLINK_MSG_ID_CMD_GET_DEVICE_INFO:
                #     print("MAVLINK_MSG_ID_CMD_GET_DEVICE_INFO")

                if msg.get_msgId() in self.__msg_reverse_filter_tab_to_ser:
                    print("mav sysid %d compid %d msgid %d to serial port" %
                          (msg.get_srcSystem(), msg.get_srcComponent(), msg.get_msgId()))
                    self.__ser.write(msg.get_msgbuf())
        except Exception as e:
            print("to_ser:", e)

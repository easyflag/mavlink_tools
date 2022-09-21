from PyQt5.QtCore import QObject

import mav_common as mavlink
from link import SerialLink, UdpLink

mav_for_ser = mavlink.MAVLink(None)
mav_for_udp = mavlink.MAVLink(None)


class Forwarder(QObject):
    def __init__(self, ser: SerialLink, udp: UdpLink):
        super().__init__()

        self.__ser = ser
        self.__udp = udp

        self.__ser.bytesRecieved.connect(self.to_udp)
        self.__udp.bytesRecieved.connect(self.to_ser)

    def to_udp(self, data: bytes):
        try:
            msg = mav_for_ser.parse_char(data)
            if msg:
                print("mav sysid %d compid %d msgid %d to udp" %
                      (msg.get_srcSystem(), msg.get_srcComponent(), msg.get_msgId()))
                if msg.get_msgId() == mavlink.MAVLINK_MSG_ID_ACK_SYS_STATE:
                    print(msg.status_id)
                if msg.get_msgId() == mavlink.MAVLINK_MSG_ID_ACK_DEVICE_INFO:
                    print("MAVLINK_MSG_ID_ACK_DEVICE_INFO")

                self.__udp.write(data)
        except Exception as e:
            print("to_udp:", e)

    def to_ser(self, data: bytes):
        try:
            msg = mav_for_udp.parse_char(data)
            if msg:
                print("mav sysid %d compid %d msgid %d to serial port" %
                      (msg.get_srcSystem(), msg.get_srcComponent(), msg.get_msgId()))
                if msg.get_srcComponent() == 193:
                    return
                if msg.get_msgId() == mavlink.MAVLINK_MSG_ID_ACK_SYS_STATE:
                    print(msg.status_id)
                    return
                if msg.get_msgId() == mavlink.MAVLINK_MSG_ID_HEARTBEAT:
                    return
                if msg.get_msgId() == mavlink.MAVLINK_MSG_ID_CMD_GET_DEVICE_INFO:
                    print("MAVLINK_MSG_ID_CMD_GET_DEVICE_INFO")

                self.__ser.write(data)
        except Exception as e:
            print("to_ser:", e)


from PyQt5.QtCore import QObject, QTimer

from link import UdpLink
import mav_common as mavlink


class FakeVehicle(QObject):

    def __init__(self):
        super().__init__()

        self.__link = UdpLink("localhost", 14551)
        self.__link.add_target("localhost", 14550)
        self.__link.bytesRecieved.connect(self.handle_mav_msg)

        self.__mav = mavlink.MAVLink(self.__link, 1, 1)

        self.__tim = QTimer()
        self.__tim.timeout.connect(self.heartbeat)
        self.__tim.start(1000)

    def handle_mav_msg(self, data: bytes):
        try:
            msg = self.__mav.parse_char(data)
            if msg:
                print("mav sysid %d compid %d msgid %d" %
                      (msg.get_srcSystem(), msg.get_srcComponent(), msg.get_msgId()))
                if msg.get_msgId() == mavlink.MAVLINK_MSG_ID_COMMAND_LONG:
                    print("cmd %d" % msg.command)

        except Exception as e:
            print("to_udp:", e)

    def heartbeat(self):
        self.__mav.heartbeat_send(mavlink.MAV_TYPE_HEXAROTOR,
                                  mavlink.MAV_AUTOPILOT_PX4,
                                  mavlink.MAV_MODE_AUTO_ARMED,
                                  0,
                                  mavlink.MAV_STATE_BOOT)

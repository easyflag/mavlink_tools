
from PyQt5.QtCore import QObject, QTimer
from PyQt5.QtSerialPort import QSerialPortInfo


from link import SerialLink, UdpLink, FakeLink
import mav_common as mavlink


class FakeVehicle(QObject):

    def __init__(self):
        super().__init__()

        self.__udp_link = UdpLink("localhost", 14555)
        self.__udp_link.add_target("localhost", 14550)
        self.__udp_link.bytesRecieved.connect(self.handle_mav_msg)

        ports = QSerialPortInfo.availablePorts()
        if len(ports) > 0:
            self.__ser_link = SerialLink(ports[0].portName())
            self.__ser_link.bytesRecieved.connect(self.handle_mav_msg)

        self.__mav = mavlink.MAVLink(FakeLink(), 255, 0)

        self.__heart_tim = QTimer()
        self.__heart_tim.timeout.connect(lambda: self.heartbeat(self.udp_send))

    def start_heartbeat(self):
        self.__heart_tim.start(1000)

    def handle_mav_msg(self, data: bytes):
        try:
            msg = self.__mav.parse_char(data)
            if msg:
                print("mav sysid %d compid %d msgid %d" %
                      (msg.get_srcSystem(), msg.get_srcComponent(), msg.get_msgId()))
                if msg.get_msgId() == mavlink.MAVLINK_MSG_ID_COMMAND_LONG:
                    print("cmd:%d p1:%d p2:%d p3:%d p4:%d p5:%d p6:%d p7:%d sys:%d comp:%d"
                          % (msg.command,
                             msg.param1,
                             msg.param2,
                             msg.param3,
                             msg.param4,
                             msg.param5,
                             msg.param6,
                             msg.param7,
                             msg.target_system,
                             msg.target_component))
                if msg.get_msgId() == mavlink.MAVLINK_MSG_ID_COMMAND_ACK:
                    print("cmd:%d res:%d sys:%d comp:%d"
                          % (msg.command,
                             msg.result,
                             msg.target_system,
                             msg.target_component))

        except Exception as e:
            print("to_udp:", e)

    def udp_send(self, msg: mavlink.MAVLink_message):
        buf = msg.pack(self.__mav)
        self.__udp_link.write(buf)

    def ser_send(self, msg: mavlink.MAVLink_message):
        buf = msg.pack(self.__mav)
        self.__ser_link.write(buf)

    def heartbeat(self, send_func):
        self.__mav.set_send_callback(send_func)
        self.__mav.heartbeat_send(mavlink.MAV_TYPE_HEXAROTOR,
                                  mavlink.MAV_AUTOPILOT_PX4,
                                  mavlink.MAV_MODE_AUTO_ARMED,
                                  0,
                                  mavlink.MAV_STATE_BOOT)

    def command_long(self,
                     send_func,
                     target_sys, target_comp,
                     cmd, confirm=0,
                     p1=0, p2=0, p3=0, p4=0, p5=0, p6=0, p7=0):
        self.__mav.set_send_callback(send_func)
        self.__mav.command_long_send(target_sys, target_comp,
                                     cmd, confirm,
                                     p1, p2, p3, p4, p5, p6, p7)

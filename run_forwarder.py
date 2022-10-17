import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtSerialPort import QSerialPortInfo

import mav_dp as mavlink
from link import SerialLink, UdpLink
from fowarder import Forwarder


def main():
    app = QApplication(sys.argv)

    ports = QSerialPortInfo.availablePorts()
    print(ports)
    if len(ports) > 0:
        ser = SerialLink(ports[0].portName())
        udp = UdpLink("localhost", 15555)
        forwarder = Forwarder(ser, udp)
        forwarder.add_reverse_filter_to_udp([
            mavlink.MAVLINK_MSG_ID_HEARTBEAT,
            mavlink.MAVLINK_MSG_ID_COMMAND_LONG,
            mavlink.MAVLINK_MSG_ID_COMMAND_ACK
        ])
        forwarder.add_reverse_filter_to_ser([
            mavlink.MAVLINK_MSG_ID_COMMAND_LONG
        ])
        forwarder.run()

        # ser.write("fd0100003dff00a28601007632")
        # d0 07 28 23

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

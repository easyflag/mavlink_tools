from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtNetwork import QAbstractSocket, QHostAddress, QUdpSocket
from PyQt5.QtCore import QIODevice, QObject, pyqtSignal


class LinkInterface(QObject):
    bytesRecieved = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()

    def close(self):
        raise RuntimeError('no close() method supplied')

    def write(self, buf):
        raise RuntimeError('no write() method supplied')


class FakeLink(LinkInterface):
    def __init__(self):
        super().__init__()

    def close(self):
        pass

    def write(self, buf):
        pass

class SerialLink(LinkInterface):
    def __init__(self, port_name: str):
        super().__init__()

        self.__serial_port = QSerialPort()
        self.__serial_port.setPortName(port_name)
        self.__serial_port.setBaudRate(QSerialPort.BaudRate.Baud115200)

        self.__serial_port.readyRead.connect(self.onReadyRead)
        res = self.__serial_port.open(QIODevice.OpenModeFlag.ReadWrite)
        print("%s open" % port_name, res)

    def __del__(self):
        self.close()

    def close(self):
        if self.__serial_port.isOpen():
            try:
                self.__serial_port.close()
                self.__serial_port = None
            except Exception:
                pass

    def onReadyRead(self):
        if self.__serial_port.isOpen():
            n = self.__serial_port.bytesAvailable()
            bytes = self.__serial_port.read(n)

            # print('onReadyRead:')
            # for b in bytes:
            #     print('%02x' % b, end='')
            # print('')

            self.bytesRecieved.emit(bytes)

    def write(self, buf):
        if self.__serial_port.isOpen():
            n = self.__serial_port.write(buf)

            # print(n, 'bytes write to serialport')
            # for b in buf:
            #     print('%02x' % b, end='')
            # print('')


class UdpClient():
    def __init__(self, addr: QHostAddress, port: int):
        self.addr = addr
        self.port = port


class UdpLink(LinkInterface):
    def __init__(self, addr: str, port: int):
        super().__init__()

        self.__udpSocket = QUdpSocket()
        res = self.__udpSocket.bind(QHostAddress(addr), port,
                                    QAbstractSocket.BindFlag.ShareAddress)
        print("udp %s bind" % port, res)

        self.__udpSocket.readyRead.connect(self.onReadyRead)

        self.__sessionTarget = []

    def onReadyRead(self):
        while self.__udpSocket.hasPendingDatagrams():
            bytes, host, port = self.__udpSocket.readDatagram(
                self.__udpSocket.pendingDatagramSize())
            # print('bytes recieved:', bytes, host.toString(), port)

            self.add_target(host.toString(), port)

            self.bytesRecieved.emit(bytes)

    def write(self, buf):
        for target in self.__sessionTarget:
            n = self.__udpSocket.writeDatagram(buf, target.addr, target.port)
            # print(n, 'bytes write to udp socket:\n%s' % buf)

    def contains_target(self, target: UdpClient):
        for s in self.__sessionTarget:
            if target.addr == s.addr or target.port == s.port:
                return True

    def add_target(self, host: str, port: int):
        addr = QHostAddress(host)
        c = UdpClient(addr, port)
        if not self.contains_target(c):
            print("new udp target", host, port)
            self.__sessionTarget.append(c)

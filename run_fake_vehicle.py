import sys

from PyQt5.QtWidgets import QApplication

from fake_vehicle import FakeVehicle


def main():
    app = QApplication(sys.argv)

    vehicle = FakeVehicle()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

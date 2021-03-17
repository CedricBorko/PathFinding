import sys

from PySide6.QtWidgets import QApplication
from path_finding.mainwindow import Window


def main():
    app = QApplication(sys.argv)
    screen = Window()
    screen.show()
    sys.exit((app.exec_()))


if __name__ == "__main__":
    main()
import sys
import pathlib
from PyQt5 import QtWidgets, uic
from ballpark import business

import backends

UI_PATH = pathlib.Path(__file__).parent.absolute() / "ui" / "main_window.ui"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        uic.loadUi(str(UI_PATH), self)

        self.data_source = backends.RandomNumberMeter()
        self.max_value = 0
        self.current_value = 0
        self.values = []
        self.n_clicked = 0
        self.clicks = []

        self.getValueButton.clicked.connect(self.handle_new_value)
        self.resetMaxValueButton.clicked.connect(self.reset_max_value)

    def plot(self, x, y):
        self.graphWidget.plot(x, y)

    def handle_new_value(self):
        self.current_value = self.data_source.read()
        self.values.append(self.current_value)
        self.n_clicked += 1
        self.clicks.append(self.n_clicked)

        self.plot(self.clicks, self.values)

        self.currentValueLabel.setText(format_val(self.current_value))
        if self.max_value < self.self.current_value:
            self.max_value = self.self.current_value
            self.maxValueLabel.setText(format_val(self.current_value))

    def reset_max_value(self):
        self.max_value = 0
        self.maxValueLabel.setText(format_val(self.max_value))


def format_val(val):
    return str(business(val, precision=3, prefix=True))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

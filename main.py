import sys

from PyQt6.QtWidgets import *

import design
import outputMessage
from jsonPart.jsonObjectValidator import JsonObjectValidator
from jsonPart.jsonParser import JsonParser
import jsonPart.jsonController as jsonController
import xsdPart.xsdController as xsdController


class ExampleApp(QMainWindow, design.Ui_Form):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        jsonController.setup(self)
        xsdController.setup(self)


def main():
    app = QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    # window.showMaximized()
    app.exec()


if __name__ == '__main__':
    main()

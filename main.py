import sys
import os

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

import design
import outputMessage
from jsonObjectValidator import JsonObjectValidator
from jsonParser import JsonParser
import jsonController
import xsdController


class ExampleApp(QMainWindow, design.Ui_Form):
    def __init__(self):
        super().__init__()
        # self.textEdit.append()
        # print(self.rect())

        self.setupUi(self)
        jsonController.setup(self)
        xsdController.setup(self)


def main():
    app = QApplication(sys.argv)
    window = ExampleApp()

    # jsonParser.parseJson()

    window.show()
    # window.showMaximized()
    app.exec()


if __name__ == '__main__':
    main()

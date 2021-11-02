import sys
import os

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

import design
import outputMessage
from jsonObjectValidator import JsonObjectValidator
from jsonParser import JsonParser


class ExampleApp(QMainWindow, design.Ui_Form):
    def __init__(self):
        super().__init__()
        # self.textEdit.append()
        # print(self.rect())

        self.setupUi(self)
        self.pushButtonLoadJson.clicked.connect(self.loadJson)
        self.pushButtonValidateJson.clicked.connect(self.validateJson)
        self.textEditTextJson.dropEvent = self.jsonFileDropEvent

        self.jsonParser = JsonParser(self)
        self.jsonValidator = JsonObjectValidator(self.jsonParams)

    def jsonFileDropEvent(self, event):
        if event.mimeData().hasUrls():
            self.getJsonFromFile(event.mimeData().urls()[0])

    def loadJson(self):
        filters = 'Файлы схем json (*.json);;Файлы схем xsd (*.xsd)'
        directory, _ = QFileDialog.getOpenFileName(QFileDialog(), caption='Выберите схему',
                                                   filter=filters)

        # print('directory = ' + directory)
        self.getJsonFromFile(directory)

    def getJsonFromFile(self, fileUrl):
        if fileUrl:
            self.textEditTextJson.clear()

            if isinstance(fileUrl, QUrl):
                fileUrl = fileUrl.url()

            if fileUrl.startswith('file:'):
                splitPattern = 'file:' + (3 * os.path.altsep if os.path.altsep else '')
                fileUrl = fileUrl.split(splitPattern)[1]
                # fileUrl = 'file:' + fileUrl

            if fileUrl.endswith('.json'):
                # JsonParser(self).parseJson(directory)
                jsonString = self.jsonParser.parseFileToText(fileUrl)
                self.textEditTextJson.append(jsonString)
            else:
                self.textEditTextJson.append(
                    'Файл в формате ' + fileUrl[fileUrl.rindex('.'):] + ' не может быть загружен')

    def validateJson(self):
        self.textEditResultJson.clear()
        jsonString = self.textEditTextJson.toPlainText()

        self.printDraftVersion(jsonString)

        jsonObjects = self.jsonParser.parseTextToObjects(jsonString)

        if isinstance(jsonObjects, dict):
            fullValidationResult = []
            stringPatternValidationResult = []
            for jsonObject in jsonObjects.values():
                fullValidationResult.extend(self.jsonValidator.validate(jsonObject, jsonObjects))
                stringPatternValidationResult.extend(self.jsonValidator.checkStringPattern(jsonObject))

            if fullValidationResult:
                for msg in fullValidationResult:
                    # self.textEditResultJson.append(str(msg))
                    self.printOutputMessage(msg)
            else:
                self.textEditResultJson.addItem('Схема валидна!')
                self.textEditResultJson.item(self.textEditResultJson.count() - 1).setForeground(Qt.GlobalColor.green)

            if stringPatternValidationResult:
                self.textEditResultJson.addItem('Также отсутствуют паттерны в строковых тегах:')
                self.textEditResultJson.item(self.textEditResultJson.count() - 1).setForeground(Qt.GlobalColor.white)
                # self.textEditResultJson.item(self.textEditResultJson.count() - 1).setBackground(Qt.GlobalColor.white)

                for msg in stringPatternValidationResult:
                    self.printOutputMessage(msg)

        else:
            self.textEditResultJson.addItem(str(jsonObjects))
            self.textEditResultJson.item(self.textEditResultJson.count() - 1).setForeground(Qt.GlobalColor.red)

    def printOutputMessage(self, message):
        self.textEditResultJson.addItem(str(message))

        if message.msgType == outputMessage.MessageType.INFO_TYPE:
            itemColor = Qt.GlobalColor.yellow
        else:
            itemColor = Qt.GlobalColor.red

        self.textEditResultJson.item(self.textEditResultJson.count() - 1).setForeground(itemColor)

    def printDraftVersion(self, jsonString):
        draft = self.jsonParser.getJsonDraftVersion(jsonString)
        validationResultMessage = self.jsonValidator.checkDraftVersion(draft)
        self.printOutputMessage(validationResultMessage)


def main():
    app = QApplication(sys.argv)
    window = ExampleApp()

    # jsonParser.parseJson()

    window.show()
    # window.showMaximized()
    app.exec()


if __name__ == '__main__':
    main()

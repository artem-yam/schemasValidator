import design
import outputMessage
import sys
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from jsonObjectValidator import JsonObjectValidator
from jsonParser import JsonParser


class ExampleApp(QMainWindow, design.Ui_Form):
    def __init__(self):
        super().__init__()
        # self.textEdit.append()
        # print(self.rect())

        self.jsonParser = JsonParser(self)
        self.jsonValidator = JsonObjectValidator()

        self.setupUi(self)
        self.pushButtonLoadJson.clicked.connect(self.loadJson)
        self.pushButtonValidateJson.clicked.connect(self.validateJson)

    # self.pushButton.clicked.connect(jsonParser.parseJson)

    def loadJson(self):
        filters = 'Файлы схем json (*.json);;Файлы схем xsd (*.xsd)'
        directory, _ = QFileDialog.getOpenFileName(QFileDialog(), caption='Выберите схему',
                                                   filter=filters)

        # print('directory = ' + directory)

        if directory:
            self.textEditTextJson.clear()

            if directory.endswith('.json'):
                # JsonParser(self).parseJson(directory)
                jsonString = self.jsonParser.parseFileToText(directory)
                self.textEditTextJson.append(jsonString)
            else:
                self.textEditTextJson.append(
                    'Файл в формате ' + directory[directory.rindex('.'):] + ' не может быть загружен')

    def validateJson(self):
        self.textEditResultJson.clear()
        jsonString = self.textEditTextJson.toPlainText()

        self.printDraftVersion(jsonString)

        jsonObjects = self.jsonParser.parseTextToObjects(jsonString)

        if isinstance(jsonObjects, dict):
            fullValidationResult = []
            for objectPath, jsonObject in jsonObjects.items():
                #    self.textEditResultJson.append(str(jsonObject))
                validationResult = self.jsonValidator.validate(jsonObject)
                fullValidationResult.extend(validationResult)

            if fullValidationResult:
                for msg in fullValidationResult:
                    # self.textEditResultJson.append(str(msg))
                    self.printOutputMessage(msg)

                    # (',' if fullValidationResult.index(msg) != len(fullValidationResult) - 1 else '')
            else:
                self.textEditResultJson.addItem('Схема валидна!')
                self.textEditResultJson.item(self.textEditResultJson.count() - 1).setForeground(Qt.GlobalColor.green)
                self.textEditResultJson.item(self.textEditResultJson.count() - 1).setBackground(
                    Qt.GlobalColor.lightGray)

        else:
            self.textEditResultJson.addItem(str(jsonObjects))
            self.textEditResultJson.item(self.textEditResultJson.count() - 1).setForeground(Qt.GlobalColor.red)
            self.textEditResultJson.item(self.textEditResultJson.count() - 1).setBackground(
                Qt.GlobalColor.lightGray)

    def printOutputMessage(self, message):
        self.textEditResultJson.addItem(str(message))

        if message.msgType == outputMessage.MessageType.INFO_TYPE:
            itemColor = Qt.GlobalColor.yellow
        else:
            itemColor = Qt.GlobalColor.red

        self.textEditResultJson.item(self.textEditResultJson.count() - 1).setForeground(itemColor)
        self.textEditResultJson.item(self.textEditResultJson.count() - 1).setBackground(
            Qt.GlobalColor.lightGray)

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

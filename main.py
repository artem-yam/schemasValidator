import sys

from PyQt6 import QtWidgets

import design
from jsonObjectValidator import JsonObjectValidator
from jsonParser import JsonParser


class ExampleApp(QtWidgets.QMainWindow, design.Ui_Form):
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
        directory, _ = QtWidgets.QFileDialog.getOpenFileName(QtWidgets.QFileDialog(), caption='Выберите схему',
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

    # if directory:  # не продолжать выполнение, если пользователь не выбрал директорию
    #    for file_name in os.listdir(directory):  # для каждого файла в директории
    #        self.textEdit.append(file_name)
    #        # self.listWidget.addItem(file_name)  # добавить файл в listWidget

    def validateJson(self):
        self.textEditResultJson.clear()
        jsonString = self.textEditTextJson.toPlainText()
        # self.textEditResultJson.append(jsonString)
        jsonObjects = self.jsonParser.parseTextToObjects(jsonString)

        if isinstance(jsonObjects, list):
            fullValidationResult = []
            for jsonObject in jsonObjects:
                #    self.textEditResultJson.append(str(jsonObject))
                validationResult = self.jsonValidator.validate(jsonObject)
                fullValidationResult.extend(validationResult)

            if fullValidationResult:
                for msg in fullValidationResult:
                    self.textEditResultJson.append(str(msg))
            else:
                self.textEditResultJson.append('Схема валидна!')

        else:
            self.textEditResultJson.append(str(jsonObjects))


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()

    # jsonParser.parseJson()

    window.show()
    # window.showMaximized()
    app.exec()


if __name__ == '__main__':
    main()

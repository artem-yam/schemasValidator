import os

import pyperclip
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

import outputMessage
from jsonObjectValidator import JsonObjectValidator
from jsonParser import JsonParser


def setup(form):
    jsonController = JsonController(form)

    form.pushButtonLoadJson.clicked.connect(jsonController.loadJson)
    form.pushButtonValidateJson.clicked.connect(jsonController.validateJson)
    form.textEditTextJson.dropEvent = jsonController.jsonFileDropEvent

    form.pushButtonCopySelectedResultJson.clicked.connect(jsonController.copySelectedResult)
    form.pushButtonCopyFullResultJson.clicked.connect(jsonController.copyFullResult)

    form.textEditResultJson.keyPressEvent = jsonController.keyPressEvent

    form.jsonParser = JsonParser(form)
    form.jsonValidator = JsonObjectValidator(form.jsonParams)


class JsonController:
    def __init__(self, form):
        super().__init__()
        self.form = form

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Copy):
            # event.accept()
            self.copySelectedResult()
        else:
            return QListWidget.keyPressEvent(self.form.textEditResultJson, event)

    def copySelectedResult(self):
        # itemsTextList = [str(self.form.textEditResultXsd.item(i).text()) for i in
        #                  range(self.form.textEditResultXsd.count())
        # subprocess.run("pbcopy", universal_newlines=True, input=str(itemsTextList)) # clip
        itemsTextString = ''
        for item in self.form.textEditResultJson.selectedItems():
            itemsTextString += str(item.text() + '\n')

        pyperclip.copy(itemsTextString)
        self.form.comboBoxChooseElementsJson.setCurrentIndex(-1)

    def copyFullResult(self):
        # itemsTextList = [str(self.form.textEditResultXsd.item(i).text()) for i in
        #                  range(self.form.textEditResultXsd.count())
        # subprocess.run("pbcopy", universal_newlines=True, input=str(itemsTextList)) # clip
        itemsTextString = ''
        # for i in range(self.form.textEditResultXsd.count()):
        #     itemsTextString += str(self.form.textEditResultXsd.item(i).text() + '\n')
        self.form.textEditResultJson.selectAll()
        for item in self.form.textEditResultJson.selectedItems():
            itemsTextString += str(item.text() + '\n')

    def jsonFileDropEvent(self, event):
        if event.mimeData().hasUrls():
            self.getJsonFromFile(event.mimeData().urls()[0])

    def loadJson(self):
        filters = 'Файлы схем json (*.json)'
        directory, _ = QFileDialog.getOpenFileName(QFileDialog(), caption='Выберите схему',
                                                   filter=filters)

        # print('directory = ' + directory)
        self.getJsonFromFile(directory)

    def getJsonFromFile(self, fileUrl):
        if fileUrl:
            self.form.textEditTextJson.clear()

            if isinstance(fileUrl, QUrl):
                fileUrl = fileUrl.url()

            if fileUrl.startswith('file:'):
                splitPattern = 'file:' + (3 * os.path.altsep if os.path.altsep else '')
                fileUrl = fileUrl.split(splitPattern)[1]
                # fileUrl = 'file:' + fileUrl

            if fileUrl.endswith('.json'):
                # JsonParser(self.form).parseJson(directory)
                jsonString = self.form.jsonParser.parseFileToText(fileUrl)
                self.form.textEditTextJson.append(jsonString)
            else:
                self.form.textEditTextJson.append(
                    'Файл в формате ' + fileUrl[fileUrl.rindex('.'):] + ' не может быть загружен')

    def validateJson(self):
        self.form.textEditResultJson.clear()
        jsonString = self.form.textEditTextJson.toPlainText()

        self.printDraftVersion(jsonString)

        jsonObjects = self.form.jsonParser.parseTextToObjects(jsonString)

        if isinstance(jsonObjects, dict):
            fullValidationResult = []
            stringPatternValidationResult = []

            cardNumberCheck = self.form.jsonValidator.checkCardNumber(jsonObjects)
            for message in cardNumberCheck:
                self.printOutputMessage(message)

            for jsonObject in jsonObjects.values():
                fullValidationResult.extend(
                    self.form.jsonValidator.validate(jsonObject, jsonObjects))
                stringPatternValidationResult.extend(
                    self.form.jsonValidator.checkStringPattern(jsonObject))

            if fullValidationResult:
                for msg in fullValidationResult:
                    # self.form.textEditResultJson.append(str(msg))
                    self.printOutputMessage(msg)
            else:
                self.form.textEditResultJson.addItem('Схема валидна!')
                self.form.textEditResultJson.item(
                    self.form.textEditResultJson.count() - 1).setForeground(Qt.GlobalColor.green)

            if stringPatternValidationResult:
                self.form.textEditResultJson.addItem(
                    'Также отсутствуют паттерны в строковых тегах:')
                self.form.textEditResultJson.item(
                    self.form.textEditResultJson.count() - 1).setForeground(Qt.GlobalColor.white)
                # self.form.textEditResultJson.item(self.form.textEditResultJson.count() - 1).setBackground(Qt.GlobalColor.white)

                for msg in stringPatternValidationResult:
                    self.printOutputMessage(msg)

        else:
            self.form.textEditResultJson.addItem(str(jsonObjects))
            self.form.textEditResultJson.item(
                self.form.textEditResultJson.count() - 1).setForeground(Qt.GlobalColor.red)

    def printOutputMessage(self, message):
        self.form.textEditResultJson.addItem(str(message))

        if message.msgType == outputMessage.MessageType.INFO_TYPE:
            itemColor = Qt.GlobalColor.yellow
        else:
            itemColor = Qt.GlobalColor.red

        self.form.textEditResultJson.item(self.form.textEditResultJson.count() - 1).setForeground(
            itemColor)

    def printDraftVersion(self, jsonString):
        draft = self.form.jsonParser.getJsonDraftVersion(jsonString)
        validationResultMessage = self.form.jsonValidator.checkDraftVersion(draft)
        self.printOutputMessage(validationResultMessage)

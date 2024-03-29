import os
import threading

import pyperclip
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

import outputMessage
from baseUtils import *
from jsonPart.jsonObjectValidator import JsonObjectValidator
from jsonPart.jsonParser import JsonParser


def setup(form):
    jsonController = JsonController(form)

    form.pushButtonLoadJson.clicked.connect(jsonController.loadJson)
    form.pushButtonRefreshJson.clicked.connect(
        jsonController.refreshObjectsFromText)
    form.pushButtonValidateJson.clicked.connect(jsonController.validateJson)
    form.textEditTextJson.dropEvent = jsonController.jsonFileDropEvent

    form.pushButtonCopySelectedResultJson.clicked.connect(
        jsonController.copySelectedResult)
    form.pushButtonCopyFullResultJson.clicked.connect(
        jsonController.copyFullResult)

    form.textEditResultJson.keyPressEvent = jsonController.keyPressEvent

    form.jsonParser = JsonParser(form)
    form.jsonValidator = JsonObjectValidator(form.jsonParams)


class JsonController:
    def __init__(self, form):
        super().__init__()
        self.form = form
        self.jsonObjects = None

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Copy):
            # event.accept()
            self.copySelectedResult()
        else:
            return QListWidget.keyPressEvent(self.form.textEditResultJson,
                                             event)

    def copySelectedResult(self):
        # itemsTextList = [str(self.form.textEditResultXsd.item(i).text())
        # for i in
        #                  range(self.form.textEditResultXsd.count())
        # subprocess.run("pbcopy", universal_newlines=True, input=str(
        # itemsTextList)) # clip
        itemsTextString = ''
        for item in self.form.textEditResultJson.selectedItems():
            itemsTextString += str(item.text() + '\n')

        pyperclip.copy(itemsTextString)
        self.form.comboBoxChooseElementsJson.setCurrentIndex(-1)

    def copyFullResult(self):
        # itemsTextList = [str(self.form.textEditResultXsd.item(i).text())
        # for i in
        #                  range(self.form.textEditResultXsd.count())
        # subprocess.run("pbcopy", universal_newlines=True, input=str(
        # itemsTextList)) # clip
        itemsTextString = ''
        # for i in range(self.form.textEditResultXsd.count()):
        #     itemsTextString += str(self.form.textEditResultXsd.item(
        #     i).text() + '\n')
        self.form.textEditResultJson.selectAll()
        for item in self.form.textEditResultJson.selectedItems():
            itemsTextString += str(item.text() + '\n')

    def jsonFileDropEvent(self, event):
        if event.mimeData().hasUrls():
            self.getJsonFromFile(event.mimeData().urls()[0])

    def loadJson(self):
        filters = 'Файлы схем json (*.json)'
        directory, _ = QFileDialog.getOpenFileName(QFileDialog(),
                                                   caption='Выберите схему',
                                                   filter=filters)

        if directory:
            self.getJsonFromFile(directory)

    def getJsonFromFile(self, fileUrl):
        self.form.textEditTextJson.clear()

        if fileUrl:
            self.form.textEditTextJson.clear()

            if isinstance(fileUrl, QUrl):
                fileUrl = fileUrl.url()

            if fileUrl.startswith('file:'):
                splitPattern = 'file:' + (
                    3 * os.path.altsep if os.path.altsep else '')
                fileUrl = fileUrl.split(splitPattern)[1]
                # fileUrl = 'file:' + fileUrl

            self.form.textEditSchemaNameJson.setText(fileUrl)

            if fileUrl.endswith('.json'):
                jsonString = self.form.jsonParser.parseFileToText(fileUrl)
                self.form.textEditTextJson.append(jsonString)

                self.refreshObjectsFromText()
            else:
                self.form.textEditTextJson.append(
                    'Файл в формате ' + fileUrl[fileUrl.rindex(
                        '.'):] + ' не может быть загружен')

    def refreshObjectsFromText(self):
        self.form.textEditResultJson.clear()
        self.jsonObjects = None
        self.form.comboBoxChooseElementsJson.clear()

        for button in self.form.jsonProcessingButtons:
            button.setEnabled(False)

        for string in FILE_PROCESS_START_TEXT:
            self.printOutputMessage(string)

        t1 = threading.Thread(target=self.parseTextToObjects,
                              args=(self.form.textEditTextJson.toPlainText(),))
        t1.start()

    def parseTextToObjects(self, text):
        self.jsonObjects = self.form.jsonParser.parseTextToObjects(text)
        # self.jsonObjects = self.form.jsonParser.parseTextToObjects(
        #     self.form.textEditTextJson.toPlainText())

        self.form.textEditResultJson.clear()
        if isinstance(self.jsonObjects, dict):
            rootTagsNames = list(
                jsonObject.name for jsonObject in self.jsonObjects.values()
                if hasattr(jsonObject, 'fullPath')
                and hasattr(jsonObject, 'name')
                and (jsonObject.fullPath == '/' + jsonObject.name
                     # or jsonObject.fullPath == '#/definitions/' +
                     # jsonObject.name
                     ))

            self.form.comboBoxChooseElementsJson.addItems(rootTagsNames)

            for button in self.form.jsonProcessingButtons:
                button.setEnabled(True)

            for string in FILE_PROCESS_FINISH_TEXT:
                self.printOutputMessage(string)
            # self.printOutputMessage('Обработка файла закончена!')
            # self.printOutputMessage('Выберите элементы из выпадающего списка')
            # self.printOutputMessage('Затем нажмите кнопку "Валидировать
            # схему"')
        else:
            self.form.textEditResultJson.addItem(str(self.jsonObjects))
            self.form.textEditResultJson.item(
                self.form.textEditResultJson.count() - 1).setForeground(
                Qt.GlobalColor.red)

    def validateJson(self):
        self.form.textEditResultJson.clear()

        chosenElements = list(
            self.form.comboBoxChooseElementsJson.model().item(i).text() for i in
            range(self.form.comboBoxChooseElementsJson.count())
            if self.form.comboBoxChooseElementsJson.model().item(
                i).checkState() == Qt.CheckState.Checked)

        objectsToValidate = {}

        if hasattr(self, 'jsonObjects') and isinstance(self.jsonObjects, dict):
            for objectKey in self.jsonObjects:
                jsonObject = self.jsonObjects[objectKey]
                isChosen = False
                # while isChosen == False:
                for elem in chosenElements:
                    isChosen = jsonObject.fullPath.startswith(f'/{elem}') \
                        # or jsonObject.fullPath.startswith(f'#/definitions/{
                    # elem}')
                    if isChosen:
                        break
                if isChosen:
                    objectsToValidate[objectKey] = jsonObject
        else:
            objectsToValidate = None

        # jsonString = self.form.textEditTextJson.toPlainText()
        # jsonObjects = self.form.jsonParser.parseTextToObjects(jsonString)
        # self.printDraftVersion(jsonString)

        self.printDraftVersion(self.form.textEditTextJson.toPlainText())

        if objectsToValidate is not None:
            if isinstance(objectsToValidate, dict):
                fullValidationResult = []
                stringPatternValidationResult = []

                # cardNumberCheck = self.form.jsonValidator.checkCardNumber(
                #     objectsToValidate)
                # for message in cardNumberCheck:
                #     self.printOutputMessage(message)

                for jsonObject in objectsToValidate.values():
                    fullValidationResult.extend(
                        # self.form.jsonValidator.validate(jsonObject,
                        # objectsToValidate))
                        self.form.jsonValidator.validate(jsonObject,
                                                         self.jsonObjects))
                    stringPatternValidationResult.extend(
                        self.form.jsonValidator.checkStringPattern(jsonObject))

                if fullValidationResult:
                    for msg in fullValidationResult:
                        # self.form.textEditResultJson.append(str(msg))
                        self.printOutputMessage(msg)
                else:
                    self.form.textEditResultJson.addItem('Схема валидна!')
                    self.form.textEditResultJson.item(
                        self.form.textEditResultJson.count() - 1).setForeground(
                        Qt.GlobalColor.green)

                if stringPatternValidationResult:
                    self.form.textEditResultJson.addItem(
                        'Также отсутствуют паттерны в строковых тегах:')
                    self.form.textEditResultJson.item(
                        self.form.textEditResultJson.count() - 1).setForeground(
                        Qt.GlobalColor.white)
                    # self.form.textEditResultJson.item(
                    # self.form.textEditResultJson.count() -
                    # 1).setBackground(Qt.GlobalColor.white)

                    for msg in stringPatternValidationResult:
                        self.printOutputMessage(msg)

            else:
                self.form.textEditResultJson.addItem(str(objectsToValidate))
                self.form.textEditResultJson.item(
                    self.form.textEditResultJson.count() - 1).setForeground(
                    Qt.GlobalColor.red)
        else:
            self.form.textEditResultJson.addItem('Сначала загрузите схему!')
            self.form.textEditResultJson.item(
                self.form.textEditResultJson.count() - 1).setForeground(
                Qt.GlobalColor.red)

    def printOutputMessage(self, message):
        self.form.textEditResultJson.addItem(str(message))

        if not hasattr(message, 'msgType'):
            itemColor = Qt.GlobalColor.white
        elif message.msgType == outputMessage.MessageType.INFO_TYPE:
            itemColor = Qt.GlobalColor.yellow
        else:
            itemColor = Qt.GlobalColor.red

        self.form.textEditResultJson.item(
            self.form.textEditResultJson.count() - 1).setForeground(
            itemColor)

    def printDraftVersion(self, jsonString):
        if '/schema' in self.jsonObjects and hasattr(
                schemaObject := self.jsonObjects['/schema'], '$schema'):
            draft = schemaObject.__dict__['$schema']
        else:
            draft = self.form.jsonParser.getJsonDraftVersion(jsonString)

        validationResultMessage = self.form.jsonValidator.checkDraftVersion(
            draft)
        self.printOutputMessage(validationResultMessage)

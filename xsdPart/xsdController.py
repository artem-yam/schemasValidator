import os
import threading
import pyperclip
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

import outputMessage
import constants
from xsdPart.xsdObjectValidator import XsdObjectValidator
from xsdPart.xsdParser import XsdParser


def setup(form):
    xsdController = XsdController(form)

    form.pushButtonLoadXsd.clicked.connect(xsdController.loadXsd)
    form.pushButtonRefreshXsd.clicked.connect(xsdController.refreshObjectsFromText)
    form.pushButtonValidateXsd.clicked.connect(xsdController.validateXsd)
    form.textEditTextXsd.dropEvent = xsdController.xsdFileDropEvent

    form.pushButtonCopySelectedResultXsd.clicked.connect(
        xsdController.copySelectedResult)
    form.pushButtonCopyFullResultXsd.clicked.connect(
        xsdController.copyFullResult)

    form.textEditResultXsd.keyPressEvent = xsdController.keyPressEvent

    form.xsdParser = XsdParser(form)
    form.xsdValidator = XsdObjectValidator(form.xsdParams)


class XsdController:
    def __init__(self, form):
        super().__init__()
        self.form = form
        self.xsdObjects = None

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Copy):
            # event.accept()
            self.copySelectedResult()
        else:
            return QListWidget.keyPressEvent(self.form.textEditResultXsd, event)

    def copySelectedResult(self):
        # itemsTextList = [str(self.form.textEditResultXsd.item(i).text()) for i in
        #                  range(self.form.textEditResultXsd.count())
        # subprocess.run("pbcopy", universal_newlines=True, input=str(itemsTextList)) # clip
        itemsTextString = ''
        for item in self.form.textEditResultXsd.selectedItems():
            itemsTextString += str(item.text() + '\n')

        pyperclip.copy(itemsTextString)

    def copyFullResult(self):
        # itemsTextList = [str(self.form.textEditResultXsd.item(i).text()) for i in
        #                  range(self.form.textEditResultXsd.count())
        # subprocess.run("pbcopy", universal_newlines=True, input=str(itemsTextList)) # clip
        itemsTextString = ''
        # for i in range(self.form.textEditResultXsd.count()):
        #     itemsTextString += str(self.form.textEditResultXsd.item(i).text() + '\n')
        self.form.textEditResultXsd.selectAll()
        for item in self.form.textEditResultXsd.selectedItems():
            itemsTextString += str(item.text() + '\n')

        pyperclip.copy(itemsTextString)

    def xsdFileDropEvent(self, event):
        if event.mimeData().hasUrls():
            self.getXsdFromFile(event.mimeData().urls()[0])

    def loadXsd(self):
        filters = 'Файлы схем xsd (*.xsd)'
        directory, _ = QFileDialog.getOpenFileName(QFileDialog(),
                                                   caption='Выберите схему',
                                                   filter=filters)

        # print('directory = ' + directory)
        if directory:
            self.getXsdFromFile(directory)

    def getXsdFromFile(self, fileUrl):
        if fileUrl:
            self.form.textEditTextXsd.clear()

            if isinstance(fileUrl, QUrl):
                fileUrl = fileUrl.url()

            if fileUrl.startswith('file:'):
                splitPattern = 'file:' + (
                    3 * os.path.altsep if os.path.altsep else '')
                fileUrl = fileUrl.split(splitPattern)[1]
                # fileUrl = 'file:' + fileUrl

            self.form.textEditSchemaNameXsd.setText(fileUrl)

            if fileUrl.endswith('.xsd'):
                # XsdParser(self.form).parseXsd(directory)
                xsdString = self.form.xsdParser.parseFileToText(fileUrl)
                self.form.textEditTextXsd.append(xsdString)

                self.refreshObjectsFromText()
            else:
                self.form.textEditTextXsd.append(
                    'Файл в формате ' + fileUrl[fileUrl.rindex(
                        '.'):] + ' не может быть загружен')

    def refreshObjectsFromText(self):
        self.form.textEditResultXsd.clear()
        self.xsdObjects = None
        self.form.comboBoxChooseElementsXsd.clear()

        for button in self.form.xsdProcessingButtons:
            button.setEnabled(False)

        for string in constants.FILE_PROCESS_START_TEXT:
            self.printOutputMessage(string)

        t1 = threading.Thread(target=self.parseTextToObjects,
                              args=(self.form.textEditTextXsd.toPlainText(),))
        t1.start()

    def parseTextToObjects(self, text):
        self.xsdObjects = self.form.xsdParser.parseTextToObjects(text)
        # self.xsdObjects = self.form.xsdParser.parseTextToObjects(
        #     self.form.textEditTextXsd.toPlainText())

        self.form.textEditResultXsd.clear()
        if isinstance(self.xsdObjects, dict):
            rootTagsNames = list(
                xsdObject.name for xsdObject in self.xsdObjects.values()
                if hasattr(xsdObject, 'fullPath') and hasattr(xsdObject, 'name')
                and hasattr(xsdObject, 'tag') and xsdObject.tag == 'element'
                and xsdObject.fullPath == '/' + xsdObject.name)

            self.form.comboBoxChooseElementsXsd.addItems(rootTagsNames)

            for button in self.form.xsdProcessingButtons:
                button.setEnabled(True)

            for string in constants.FILE_PROCESS_FINISH_TEXT:
                self.printOutputMessage(string)
            # self.printOutputMessage('Обработка файла закончена!')
            # self.printOutputMessage('Выберите элементы из выпадающего списка')
            # self.printOutputMessage('Затем нажмите кнопку "Валидировать схему"')
        else:
            self.form.textEditResultXsd.addItem(str(self.xsdObjects))
            self.form.textEditResultXsd.item(
                self.form.textEditResultXsd.count() - 1).setForeground(
                Qt.GlobalColor.red)

    def validateXsd(self):
        self.form.textEditResultXsd.clear()

        chosenElements = list(
            self.form.comboBoxChooseElementsXsd.model().item(i).text() for i in
            range(self.form.comboBoxChooseElementsXsd.count())
            if self.form.comboBoxChooseElementsXsd.model().item(
                i).checkState() == Qt.CheckState.Checked)

        objectsToValidate = {}

        if hasattr(self, 'xsdObjects') and isinstance(self.xsdObjects, dict):
            for objectKey, xsdObject in self.xsdObjects.items():
                isChosen = False
                # while isChosen == False:
                for elem in chosenElements:
                    isChosen = xsdObject.fullPath.startswith(f'/{elem}/')
                    if isChosen:
                        break
                if isChosen:
                    objectsToValidate[objectKey] = xsdObject
        else:
            objectsToValidate = None

        # objectsToValidate.update(
        #     self.form.comboBoxChooseElementsXsd.model().item(i).text() for i in self.xsdObjects
        #     if i in chosenElements)
        # self.xsdObjects

        if objectsToValidate is not None:
            if isinstance(objectsToValidate, dict):
                fullValidationResult = []
                stringPatternValidationResult = []

                # cardNumberCheck = self.form.xsdValidator.checkCardNumber(
                #     objectsToValidate)
                # for message in cardNumberCheck:
                #     self.printOutputMessage(message)

                for xsdObject in objectsToValidate.values():
                    fullValidationResult.extend(
                        self.form.xsdValidator.validate(xsdObject))
                    stringPatternValidationResult.extend(
                        self.form.xsdValidator.checkStringPattern(xsdObject))

                if fullValidationResult:
                    for msg in fullValidationResult:
                        # self.form.textEditResultXsd.append(str(msg))
                        self.printOutputMessage(msg)
                else:
                    self.form.textEditResultXsd.addItem('Схема валидна!')
                    self.form.textEditResultXsd.item(
                        self.form.textEditResultXsd.count() - 1).setForeground(
                        Qt.GlobalColor.green)

                if stringPatternValidationResult:
                    self.form.textEditResultXsd.addItem(
                        'Также отсутствуют паттерны в строковых тегах:')
                    self.form.textEditResultXsd.item(
                        self.form.textEditResultXsd.count() - 1).setForeground(
                        Qt.GlobalColor.white)
                    # self.form.textEditResultXsd.item(self.form.textEditResultXsd.count() - 1).setBackground(Qt.GlobalColor.white)

                    for msg in stringPatternValidationResult:
                        self.printOutputMessage(msg)

            else:
                self.form.textEditResultXsd.addItem(str(objectsToValidate))
                self.form.textEditResultXsd.item(
                    self.form.textEditResultXsd.count() - 1).setForeground(
                    Qt.GlobalColor.red)
        else:
            self.form.textEditResultXsd.addItem('Сначала загрузите схему!')
            self.form.textEditResultXsd.item(
                self.form.textEditResultXsd.count() - 1).setForeground(
                Qt.GlobalColor.red)

    def printOutputMessage(self, message):
        self.form.textEditResultXsd.addItem(str(message))

        if not hasattr(message, 'msgType'):
            itemColor = Qt.GlobalColor.white
        elif message.msgType == outputMessage.MessageType.INFO_TYPE:
            itemColor = Qt.GlobalColor.yellow
        else:
            itemColor = Qt.GlobalColor.red

        self.form.textEditResultXsd.item(
            self.form.textEditResultXsd.count() - 1).setForeground(
            itemColor)

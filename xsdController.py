import os

import pyperclip
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

import outputMessage
from xsdObjectValidator import XsdObjectValidator
from xsdParser import XsdParser


def setup(form):
    xsdController = XsdController(form)

    form.pushButtonLoadXsd.clicked.connect(xsdController.loadXsd)
    form.pushButtonValidateXsd.clicked.connect(xsdController.validateXsd)
    form.textEditTextXsd.dropEvent = xsdController.xsdFileDropEvent

    form.pushButtonCopySelectedResultXsd.clicked.connect(xsdController.copySelectedResult)
    form.pushButtonCopyFullResultXsd.clicked.connect(xsdController.copyFullResult)

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
        directory, _ = QFileDialog.getOpenFileName(QFileDialog(), caption='Выберите схему',
                                                   filter=filters)

        # print('directory = ' + directory)
        self.getXsdFromFile(directory)


    def getXsdFromFile(self, fileUrl):
        if fileUrl:
            self.form.textEditTextXsd.clear()
            self.xsdObjects = None
            self.form.comboBoxChooseElementsXsd.clear()

            if isinstance(fileUrl, QUrl):
                fileUrl = fileUrl.url()

            if fileUrl.startswith('file:'):
                splitPattern = 'file:' + (3 * os.path.altsep if os.path.altsep else '')
                fileUrl = fileUrl.split(splitPattern)[1]
                # fileUrl = 'file:' + fileUrl

            if fileUrl.endswith('.xsd'):
                # XsdParser(self.form).parseXsd(directory)
                xsdString = self.form.xsdParser.parseFileToText(fileUrl)
                self.form.textEditTextXsd.append(xsdString)

                self.parseTextToObjects()
            else:
                self.form.textEditTextXsd.append(
                    'Файл в формате ' + fileUrl[fileUrl.rindex('.'):] + ' не может быть загружен')

    def parseTextToObjects(self):
        self.xsdObjects = self.form.xsdParser.parseTextToObjects(
            self.form.textEditTextXsd.toPlainText())

        rootTagsNames = list(xsdObject.name for xsdObject in self.xsdObjects.values()
                             if hasattr(xsdObject, 'fullPath')
                             and hasattr(xsdObject, 'name')
                             and xsdObject.fullPath == '/' + xsdObject.name)

        self.form.comboBoxChooseElementsXsd.addItems(rootTagsNames)

    def validateXsd(self):
        self.form.textEditResultXsd.clear()

        chosenElements = list(self.form.comboBoxChooseElementsXsd.model().item(i).text() for i in
                              range(self.form.comboBoxChooseElementsXsd.count())
                              if self.form.comboBoxChooseElementsXsd.model().item(
            i).checkState() == Qt.CheckState.Checked)

        objectsToValidate = {}

        if hasattr(self, 'xsdObjects') and isinstance(self.xsdObjects, dict):
            for objectPath in self.xsdObjects:
                isChosen = False
                # while isChosen == False:
                for elem in chosenElements:
                    isChosen = objectPath.startswith('/' + elem)
                    if isChosen:
                        break
                if isChosen:
                    objectsToValidate[objectPath] = self.xsdObjects.get(objectPath)
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

                cardNumberCheck = self.form.jsonValidator.checkCardNumber(objectsToValidate)
                for message in cardNumberCheck:
                    self.printOutputMessage(message)

                for xsdObject in objectsToValidate.values():
                    fullValidationResult.extend(self.form.xsdValidator.validate(xsdObject))
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

        if message.msgType == outputMessage.MessageType.INFO_TYPE:
            itemColor = Qt.GlobalColor.yellow
        else:
            itemColor = Qt.GlobalColor.red

        self.form.textEditResultXsd.item(self.form.textEditResultXsd.count() - 1).setForeground(
            itemColor)

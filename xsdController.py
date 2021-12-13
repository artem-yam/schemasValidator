import os

import pyperclip
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

import outputMessage
from xsdObjectValidator import XsdObjectValidator
from xsdParser import XsdParser


def setup(form):
    xsdController = XsdController(form)

    form.pushButtonLoadXsd.clicked.connect(xsdController.loadXsd)
    form.pushButtonValidateXsd.clicked.connect(xsdController.validateXsd)
    form.textEditTextXsd.dropEvent = xsdController.xsdFileDropEvent

    form.pushButtonCopyResultXsd.clicked.connect(xsdController.copyResult)

    form.xsdParser = XsdParser(form)
    form.xsdValidator = XsdObjectValidator(form.xsdParams)


class XsdController:
    def __init__(self, form):
        super().__init__()
        self.form = form

    def copyResult(self):
        # itemsTextList = [str(self.form.textEditResultXsd.item(i).text()) for i in
        #                  range(self.form.textEditResultXsd.count())
        # subprocess.run("pbcopy", universal_newlines=True, input=str(itemsTextList)) # clip
        itemsTextString = ''
        for i in range(self.form.textEditResultXsd.count()):
            itemsTextString += str(self.form.textEditResultXsd.item(i).text() + '\n')

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

            else:
                self.form.textEditTextXsd.append(
                    'Файл в формате ' + fileUrl[fileUrl.rindex('.'):] + ' не может быть загружен')

    def validateXsd(self):
        self.form.textEditResultXsd.clear()
        xsdString = self.form.textEditTextXsd.toPlainText()

        xsdObjects = self.form.xsdParser.parseTextToObjects(xsdString)

        if isinstance(xsdObjects, dict):
            fullValidationResult = []
            stringPatternValidationResult = []

            cardNumberCheck = self.form.jsonValidator.checkCardNumber(xsdObjects)
            if cardNumberCheck:
                self.printOutputMessage(cardNumberCheck)

            for xsdObject in xsdObjects.values():
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
                self.form.textEditResultXsd.addItem('Также отсутствуют паттерны в строковых тегах:')
                self.form.textEditResultXsd.item(
                    self.form.textEditResultXsd.count() - 1).setForeground(
                    Qt.GlobalColor.white)
                # self.form.textEditResultXsd.item(self.form.textEditResultXsd.count() - 1).setBackground(Qt.GlobalColor.white)

                for msg in stringPatternValidationResult:
                    self.printOutputMessage(msg)

        else:
            self.form.textEditResultXsd.addItem(str(xsdObjects))
            self.form.textEditResultXsd.item(self.form.textEditResultXsd.count() - 1).setForeground(
                Qt.GlobalColor.red)

    def printOutputMessage(self, message):
        self.form.textEditResultXsd.addItem(str(message))

        if message.msgType == outputMessage.MessageType.INFO_TYPE:
            itemColor = Qt.GlobalColor.yellow
        else:
            itemColor = Qt.GlobalColor.red

        self.form.textEditResultXsd.item(self.form.textEditResultXsd.count() - 1).setForeground(
            itemColor)

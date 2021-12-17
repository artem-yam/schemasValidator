# Form implementation generated from reading ui file 'qtui.ui'
#
# Created by: PyQt6 UI code generator 6.1.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.

from PyQt6 import QtCore, QtWidgets


class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self, parent):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)

        # model = QtGui.QStandardItemModel(self)
        # model.rowsInserted.connect(self.rowsInserted)
        self.model().rowsInserted.connect(self.rowsInserted)

        firstItem = "Выберите элементы"
        # firstItem = QtGui.QStandardItem("---- Select area(s) ----")
        # firstItem.setBackground(QtGui.QBrush(QtGui.QColor(200, 200, 200)))
        # firstItem.setCheckState(QtCore.Qt.CheckState.Unchecked)
        # model.setItem(0, firstItem)
        # model.appendRow(firstItem)

        # self.setModel(model)

        # self.addItem(firstItem)
        # self.model().item(0, 0).setCheckState(QtCore.Qt.CheckState.Unchecked)
        # self.model().item(0, 0).setBackground(QtGui.QBrush(QtGui.QColor(200, 200, 200)))

    def rowsInserted(self, parent, first, last):
        for index in range(first, last + 1):
            item = self.model().item(index, 0)
            if item.isSelectable:
                # TODO включить по умолчанию
                item.setCheckState(QtCore.Qt.CheckState.Checked)
                # item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                item.setSelectable(False)

    def handleItemPressed(self, index):
        # if index.row() != 0:
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.CheckState.Checked:
            item.setCheckState(QtCore.Qt.CheckState.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.CheckState.Checked)

    # self.view().reset()
    # self.super.setCurrentIndex(-1)
    # self.setCurrentText("---- Select area(s) ----")
    # self.showPopup()


class Ui_Form(object):
    TEXT_WIDGET_MIN_HEIGHT = 430
    BUTTON_WIDTH = 180
    BUTTON_HEIGHT = 50
    STANDARD_MARGIN = 20

    def resizeEvent(self, event):
        self.resizeFormObjects(self)

    def setupUi(self, form):
        # form.resize(form.maximumSize().width(), form.maximumSize().height())
        form.resize(form.width() * 2, form.height() * 2)

        self.tabWidget = QtWidgets.QTabWidget(form)

        form.setStyleSheet('QMainWindow {background-color: rgba(100, 255, 255, 0.3);}')

        self.jsonTab = QtWidgets.QWidget()
        self.xsdTab = QtWidgets.QWidget()
        self.tabWidget.addTab(self.jsonTab, "JSON")
        self.tabWidget.addTab(self.xsdTab, "XSD")

        self.setupJsonTab()
        self.setupXsdTab()

        self.resizeFormObjects(form)

        self.retranslateUi(form)
        QtCore.QMetaObject.connectSlotsByName(form)

    def setupJsonTab(self):
        self.textEditTextJson = QtWidgets.QTextEdit(self.jsonTab)
        self.textEditTextJson.setStyleSheet('QTextEdit {background-color: black; color: white;}')
        self.textEditTextJson.setMinimumHeight(Ui_Form.TEXT_WIDGET_MIN_HEIGHT)

        self.textEditResultJson = QtWidgets.QListWidget(self.jsonTab)
        self.textEditResultJson.setStyleSheet('QListWidget {background-color: rgba(0, 0, 0, 0.8);}')
        self.textEditResultJson.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.textEditResultJson.setMinimumHeight(Ui_Form.TEXT_WIDGET_MIN_HEIGHT)

        self.pushButtonLoadJson = QtWidgets.QPushButton(self.jsonTab)

        self.comboBoxChooseElementsJson = CheckableComboBox(self.jsonTab)
        self.comboBoxChooseElementsJson.setPlaceholderText("Выберите элементы")

        self.pushButtonValidateJson = QtWidgets.QPushButton(self.jsonTab)
        self.pushButtonCopySelectedResultJson = QtWidgets.QPushButton(self.jsonTab)
        self.pushButtonCopyFullResultJson = QtWidgets.QPushButton(self.jsonTab)

        self.setupJsonConfElements()

    def setupXsdTab(self):
        self.textEditTextXsd = QtWidgets.QTextEdit(self.xsdTab)
        self.textEditTextXsd.setStyleSheet('QTextEdit {background-color: black; color: white;}')
        self.textEditTextXsd.setMinimumHeight(Ui_Form.TEXT_WIDGET_MIN_HEIGHT)

        self.textEditResultXsd = QtWidgets.QListWidget(self.xsdTab)
        self.textEditResultXsd.setStyleSheet('QListWidget {background-color: rgba(0, 0, 0, 0.8);}')
        self.textEditResultXsd.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.textEditResultXsd.setMinimumHeight(Ui_Form.TEXT_WIDGET_MIN_HEIGHT)

        self.pushButtonLoadXsd = QtWidgets.QPushButton(self.xsdTab)

        self.comboBoxChooseElementsXsd = CheckableComboBox(self.xsdTab)
        self.comboBoxChooseElementsXsd.setPlaceholderText("Выберите элементы")

        self.pushButtonValidateXsd = QtWidgets.QPushButton(self.xsdTab)
        self.pushButtonCopySelectedResultXsd = QtWidgets.QPushButton(self.xsdTab)
        self.pushButtonCopyFullResultXsd = QtWidgets.QPushButton(self.xsdTab)

        self.setupXsdConfElements()

    def setupJsonConfElements(self):
        self.jsonParams = QtWidgets.QGroupBox(self.jsonTab)
        self.jsonParams.setStyleSheet('QGroupBox {background-color: rgba(100, 255, 255, 0.8);}')

        #

        self.jsonConfArrayLengthLabel = QtWidgets.QCheckBox(self.jsonParams)
        self.jsonConfArrayLengthLabel.setObjectName('jsonConfArrayLengthLabel')
        self.jsonConfArrayLengthLabel.toggle()
        self.jsonConfArrayLengthLabel.setText("Максимальное число элементов массива:")
        self.jsonConfArrayLengthLabel.setGeometry(QtCore.QRect(20, 40, 300, 30))

        self.jsonConfArrayLengthText = QtWidgets.QTextEdit(self.jsonParams)
        self.jsonConfArrayLengthText.setObjectName('jsonConfArrayLengthText')
        self.jsonConfArrayLengthText.setPlaceholderText("∞")
        self.jsonConfArrayLengthText.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.jsonConfArrayLengthText.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.jsonConfArrayLengthText.setGeometry(
            QtCore.QRect(self.jsonConfArrayLengthLabel.geometry().right(),
                         self.jsonConfArrayLengthLabel.geometry().top(), 100, 30))

        #

        self.jsonConfNumericMaxLabel = QtWidgets.QCheckBox(self.jsonParams)
        self.jsonConfNumericMaxLabel.setObjectName('jsonConfNumericMaxLabel')
        self.jsonConfNumericMaxLabel.toggle()
        self.jsonConfNumericMaxLabel.setText("Максимальный размер чисел:")
        self.jsonConfNumericMaxLabel.setGeometry(
            QtCore.QRect(20, self.jsonConfArrayLengthLabel.geometry().bottom() + 20, 300, 30))

        self.jsonConfNumericMaxText = QtWidgets.QTextEdit(self.jsonParams)
        self.jsonConfNumericMaxText.setObjectName('jsonConfNumericMaxText')
        self.jsonConfNumericMaxText.setPlaceholderText("∞")
        self.jsonConfNumericMaxText.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.jsonConfNumericMaxText.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.jsonConfNumericMaxText.setGeometry(
            QtCore.QRect(self.jsonConfNumericMaxLabel.geometry().right(),
                         self.jsonConfNumericMaxLabel.geometry().top(), 100, 30))

        #

        self.jsonConfNumericMinLabel = QtWidgets.QCheckBox(self.jsonParams)
        self.jsonConfNumericMinLabel.setObjectName('jsonConfNumericMinLabel')
        self.jsonConfNumericMinLabel.toggle()
        self.jsonConfNumericMinLabel.setText("Минимальный размер чисел:")
        self.jsonConfNumericMinLabel.setGeometry(
            QtCore.QRect(20, self.jsonConfNumericMaxLabel.geometry().bottom() + 20, 300, 30))

        self.jsonConfNumericMinText = QtWidgets.QTextEdit(self.jsonParams)
        self.jsonConfNumericMinText.setObjectName('jsonConfNumericMinText')
        self.jsonConfNumericMinText.setPlaceholderText("∞")
        self.jsonConfNumericMinText.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.jsonConfNumericMinText.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.jsonConfNumericMinText.setGeometry(
            QtCore.QRect(self.jsonConfNumericMinLabel.geometry().right(),
                         self.jsonConfNumericMinLabel.geometry().top(), 100, 30))

        #

        self.jsonConfStringLengthLabel = QtWidgets.QCheckBox(self.jsonParams)
        self.jsonConfStringLengthLabel.setObjectName('jsonConfStringLengthLabel')
        self.jsonConfStringLengthLabel.toggle()
        self.jsonConfStringLengthLabel.setText("Максимальная длина строки:")
        self.jsonConfStringLengthLabel.setGeometry(
            QtCore.QRect(20, self.jsonConfNumericMinLabel.geometry().bottom() + 20, 300, 30))

        self.jsonConfStringLengthText = QtWidgets.QTextEdit(self.jsonParams)
        self.jsonConfStringLengthText.setObjectName('jsonConfStringLengthText')
        self.jsonConfStringLengthText.setPlaceholderText("∞")
        self.jsonConfStringLengthText.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.jsonConfStringLengthText.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.jsonConfStringLengthText.setGeometry(
            QtCore.QRect(self.jsonConfStringLengthLabel.geometry().right(),
                         self.jsonConfStringLengthLabel.geometry().top(), 100, 30))

        #

        self.jsonConfCheckTypeLabel = QtWidgets.QCheckBox(self.jsonParams)
        self.jsonConfCheckTypeLabel.setObjectName("jsonConfCheckTypeLabel")
        self.jsonConfCheckTypeLabel.toggle()
        self.jsonConfCheckTypeLabel.setText("Проверка указания типа для каждого элемента")
        self.jsonConfCheckTypeLabel.setGeometry(
            QtCore.QRect(20, self.jsonConfStringLengthLabel.geometry().bottom() + 20, 500, 30))

        # print("---------")
        # children = self.confCheckTypeLabel.parent().children()
        # print(';\n'.join(map(lambda x: x.objectName(), children)))

    def setupXsdConfElements(self):
        self.xsdParams = QtWidgets.QGroupBox(self.xsdTab)
        self.xsdParams.setStyleSheet('QGroupBox {background-color: rgba(100, 255, 255, 0.8);}')

        #

        self.xsdConfArrayLengthLabel = QtWidgets.QCheckBox(self.xsdParams)
        self.xsdConfArrayLengthLabel.setObjectName('xsdConfArrayLengthLabel')
        self.xsdConfArrayLengthLabel.toggle()
        self.xsdConfArrayLengthLabel.setText("Максимальное число элементов массива:")
        self.xsdConfArrayLengthLabel.setGeometry(QtCore.QRect(20, 40, 300, 30))

        self.xsdConfArrayLengthText = QtWidgets.QTextEdit(self.xsdParams)
        self.xsdConfArrayLengthText.setObjectName('xsdConfArrayLengthText')
        self.xsdConfArrayLengthText.setPlaceholderText("∞")
        self.xsdConfArrayLengthText.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.xsdConfArrayLengthText.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.xsdConfArrayLengthText.setGeometry(
            QtCore.QRect(self.xsdConfArrayLengthLabel.geometry().right(),
                         self.xsdConfArrayLengthLabel.geometry().top(), 100, 30))

        #

        self.xsdConfNumericMaxLabel = QtWidgets.QCheckBox(self.xsdParams)
        self.xsdConfNumericMaxLabel.setObjectName('xsdConfNumericMaxLabel')
        self.xsdConfNumericMaxLabel.toggle()
        self.xsdConfNumericMaxLabel.setText("Максимальный размер чисел:")
        self.xsdConfNumericMaxLabel.setGeometry(
            QtCore.QRect(20, self.xsdConfArrayLengthLabel.geometry().bottom() + 20, 300, 30))

        self.xsdConfNumericMaxText = QtWidgets.QTextEdit(self.xsdParams)
        self.xsdConfNumericMaxText.setObjectName('xsdConfNumericMaxText')
        self.xsdConfNumericMaxText.setPlaceholderText("∞")
        self.xsdConfNumericMaxText.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.xsdConfNumericMaxText.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.xsdConfNumericMaxText.setGeometry(
            QtCore.QRect(self.xsdConfNumericMaxLabel.geometry().right(),
                         self.xsdConfNumericMaxLabel.geometry().top(), 100, 30))

        #

        self.xsdConfNumericMinLabel = QtWidgets.QCheckBox(self.xsdParams)
        self.xsdConfNumericMinLabel.setObjectName('xsdConfNumericMinLabel')
        self.xsdConfNumericMinLabel.toggle()
        self.xsdConfNumericMinLabel.setText("Минимальный размер чисел:")
        self.xsdConfNumericMinLabel.setGeometry(
            QtCore.QRect(20, self.xsdConfNumericMaxLabel.geometry().bottom() + 20, 300, 30))

        self.xsdConfNumericMinText = QtWidgets.QTextEdit(self.xsdParams)
        self.xsdConfNumericMinText.setObjectName('xsdConfNumericMinText')
        self.xsdConfNumericMinText.setPlaceholderText("∞")
        self.xsdConfNumericMinText.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.xsdConfNumericMinText.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.xsdConfNumericMinText.setGeometry(
            QtCore.QRect(self.xsdConfNumericMinLabel.geometry().right(),
                         self.xsdConfNumericMinLabel.geometry().top(), 100, 30))

        #

        self.xsdConfStringLengthLabel = QtWidgets.QCheckBox(self.xsdParams)
        self.xsdConfStringLengthLabel.setObjectName('xsdConfStringLengthLabel')
        self.xsdConfStringLengthLabel.toggle()
        self.xsdConfStringLengthLabel.setText("Максимальная длина строки:")
        self.xsdConfStringLengthLabel.setGeometry(
            QtCore.QRect(20, self.xsdConfNumericMinLabel.geometry().bottom() + 20, 300, 30))

        self.xsdConfStringLengthText = QtWidgets.QTextEdit(self.xsdParams)
        self.xsdConfStringLengthText.setObjectName('xsdConfStringLengthText')
        self.xsdConfStringLengthText.setPlaceholderText("∞")
        self.xsdConfStringLengthText.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.xsdConfStringLengthText.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.xsdConfStringLengthText.setGeometry(
            QtCore.QRect(self.xsdConfStringLengthLabel.geometry().right(),
                         self.xsdConfStringLengthLabel.geometry().top(), 100, 30))

        #

        self.xsdConfAnyCheckLabel = QtWidgets.QCheckBox(self.xsdParams)
        self.xsdConfAnyCheckLabel.setObjectName("xsdConfAnyCheckLabel")
        self.xsdConfAnyCheckLabel.toggle()
        self.xsdConfAnyCheckLabel.setText("Проверка на использование xs:any")
        self.xsdConfAnyCheckLabel.setGeometry(
            QtCore.QRect(20, self.xsdConfStringLengthLabel.geometry().bottom() + 20, 500, 30))

        # print("---------")
        # children = self.confCheckTypeLabel.parent().children()
        # print(';\n'.join(map(lambda x: x.objectName(), children)))

    def resizeFormObjects(self, form):
        self.tabWidget.setGeometry(form.rect())
        self.resizeJsonFormObjects()
        self.resizeXsdFormObjects()

    def resizeJsonFormObjects(self):
        self.textEditTextJson.setGeometry(
            QtCore.QRect(Ui_Form.STANDARD_MARGIN, 30, self.tabWidget.width() // 2 - 130,
                         self.tabWidget.height() // 2))

        self.textEditResultJson.setGeometry(
            QtCore.QRect(self.textEditTextJson.geometry().right() + 221, 30,
                         self.textEditTextJson.geometry().width(),
                         self.textEditTextJson.geometry().height()))

        self.pushButtonLoadJson.setGeometry(
            QtCore.QRect(self.textEditTextJson.geometry().right() + Ui_Form.STANDARD_MARGIN,
                         self.textEditTextJson.geometry().top() + Ui_Form.STANDARD_MARGIN,
                         Ui_Form.BUTTON_WIDTH, Ui_Form.BUTTON_HEIGHT))

        self.comboBoxChooseElementsJson.setGeometry(
            QtCore.QRect(self.pushButtonLoadJson.geometry().left(),
                         self.pushButtonLoadJson.geometry().bottom() + Ui_Form.STANDARD_MARGIN,
                         Ui_Form.BUTTON_WIDTH, 20))

        self.pushButtonValidateJson.setGeometry(
            QtCore.QRect(self.comboBoxChooseElementsJson.geometry().left(),
                         self.comboBoxChooseElementsJson.geometry().bottom()
                         + Ui_Form.STANDARD_MARGIN, Ui_Form.BUTTON_WIDTH, Ui_Form.BUTTON_HEIGHT))

        self.pushButtonCopySelectedResultJson.setGeometry(
            QtCore.QRect(self.pushButtonValidateJson.geometry().left(),
                         self.pushButtonValidateJson.geometry().bottom()
                         + Ui_Form.STANDARD_MARGIN + 50, Ui_Form.BUTTON_WIDTH,
                         Ui_Form.BUTTON_HEIGHT + 20))

        self.pushButtonCopyFullResultJson.setGeometry(
            QtCore.QRect(self.pushButtonCopySelectedResultJson.geometry().left(),
                         self.pushButtonCopySelectedResultJson.geometry().bottom() + Ui_Form.STANDARD_MARGIN,
                         Ui_Form.BUTTON_WIDTH, Ui_Form.BUTTON_HEIGHT + 20))

        self.jsonParams.setGeometry(
            QtCore.QRect(Ui_Form.STANDARD_MARGIN,
                         self.textEditTextJson.geometry().bottom() + Ui_Form.STANDARD_MARGIN,
                         self.tabWidget.geometry().width() - 40, 400))

    def resizeXsdFormObjects(self):
        self.textEditTextXsd.setGeometry(
            QtCore.QRect(Ui_Form.STANDARD_MARGIN, 30, self.tabWidget.width() // 2 - 130,
                         self.tabWidget.height() // 2))

        self.textEditResultXsd.setGeometry(
            QtCore.QRect(self.textEditTextXsd.geometry().right() + 221, 30,
                         self.textEditTextXsd.geometry().width(),
                         self.textEditTextXsd.geometry().height()))

        self.pushButtonLoadXsd.setGeometry(
            QtCore.QRect(self.textEditTextXsd.geometry().right() + Ui_Form.STANDARD_MARGIN,
                         self.textEditTextXsd.geometry().top() + Ui_Form.STANDARD_MARGIN,
                         Ui_Form.BUTTON_WIDTH, Ui_Form.BUTTON_HEIGHT))

        self.comboBoxChooseElementsXsd.setGeometry(
            QtCore.QRect(self.pushButtonLoadXsd.geometry().left(),
                         self.pushButtonLoadXsd.geometry().bottom() + Ui_Form.STANDARD_MARGIN,
                         Ui_Form.BUTTON_WIDTH, 20))

        self.pushButtonValidateXsd.setGeometry(
            QtCore.QRect(self.comboBoxChooseElementsXsd.geometry().left(),
                         self.comboBoxChooseElementsXsd.geometry().bottom()
                         + Ui_Form.STANDARD_MARGIN, Ui_Form.BUTTON_WIDTH, Ui_Form.BUTTON_HEIGHT))

        self.pushButtonCopySelectedResultXsd.setGeometry(
            QtCore.QRect(self.pushButtonValidateXsd.geometry().left(),
                         self.pushButtonValidateXsd.geometry().bottom() + Ui_Form.STANDARD_MARGIN + 50,
                         Ui_Form.BUTTON_WIDTH, Ui_Form.BUTTON_HEIGHT + 20))

        self.pushButtonCopyFullResultXsd.setGeometry(
            QtCore.QRect(self.pushButtonCopySelectedResultXsd.geometry().left(),
                         self.pushButtonCopySelectedResultXsd.geometry().bottom() + Ui_Form.STANDARD_MARGIN,
                         Ui_Form.BUTTON_WIDTH, Ui_Form.BUTTON_HEIGHT + 20))

        self.xsdParams.setGeometry(
            QtCore.QRect(Ui_Form.STANDARD_MARGIN,
                         self.textEditTextXsd.geometry().bottom() + Ui_Form.STANDARD_MARGIN,
                         self.tabWidget.geometry().width() - 40, 400))

    def retranslateUi(self, form):
        _translate = QtCore.QCoreApplication.translate
        form.setWindowTitle(_translate("Form", "Валидатор xsd / json схем"))
        self.pushButtonLoadJson.setText(_translate("Form", "Загрузить схему"))
        self.pushButtonValidateJson.setText(_translate("Form", "Валидировать схему"))
        self.pushButtonCopySelectedResultJson.setText(
            _translate("Form", "Скопировать\nвыделенные\nсообщения"))
        self.pushButtonCopyFullResultJson.setText(_translate("Form", "Скопировать\nвсе\nсообщения"))
        self.jsonParams.setTitle(_translate("Form", "Параметры валидации json"))

        self.pushButtonLoadXsd.setText(_translate("Form", "Загрузить схему"))
        self.pushButtonValidateXsd.setText(_translate("Form", "Валидировать схему"))
        self.pushButtonCopySelectedResultXsd.setText(
            _translate("Form", "Скопировать\nвыделенные\nсообщения"))
        self.pushButtonCopyFullResultXsd.setText(_translate("Form", "Скопировать\nвсе\nсообщения"))
        self.xsdParams.setTitle(_translate("Form", "Параметры валидации xsd"))

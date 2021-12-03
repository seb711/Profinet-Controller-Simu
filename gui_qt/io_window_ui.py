import time
import functools
from helper.gsdml_parser import XMLDevice

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtProperty, QObject, QVariant

import sys


from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QSpinBox

class ObservableVariable(QtCore.QObject):
    """ Represents variable with value, when value changes it emits
    signal: changed(new_value)
    """
    changed = QtCore.pyqtSignal(object)

    def __init__(self, initial_value=0):
        super(ObservableVariable, self).__init__()
        self._value = initial_value

    def get_value(self):
        return self._value

    def set_value(self, new_val):
        self._value = new_val
        self.changed.emit(new_val)

    value = property(get_value, set_value)

    def __str__(self):
        return str(self.value)

    # it can support more operators if needed
    def __iadd__(self, other):
        self.value += other
        return self

    def __isub__(self, other):
        self.value -= other
        return self

class MyClass(object):
    def __init__(self, referrer=None, value=1):
        self.referrer = referrer
        self.value = ObservableVariable(value)
        self._initial_value = value
        if referrer:
            # propagate referrer changes to subscribers
            referrer.value.changed.connect(
                lambda x: self.value.changed.emit(self.value.value)
            )

    @property
    def start(self):
        if not self.referrer:
            return self.value.value
        return self.referrer.end + 1

    @property
    def end(self):
        return self.start + self.value.value - 1

class MainWindow(QMainWindow):
    """Main Window."""
    def __init__(self, path_to_gsdml, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.device = XMLDevice(path_to_gsdml)
        self.module_output_values = []
        self.module_input_values = []


    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(733, 404)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        # Start Button
        self.start_btn = QtWidgets.QPushButton(self.centralwidget)
        self.start_btn.setGeometry(QtCore.QRect(10, 330, 351, 23))
        self.start_btn.setObjectName("start_btn")

        # Stop Button
        self.stop_btn = QtWidgets.QPushButton(self.centralwidget)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setGeometry(QtCore.QRect(380, 330, 351, 23))
        self.stop_btn.setCheckable(False)
        self.stop_btn.setChecked(False)
        self.stop_btn.setObjectName("stop_btn")

        # Basic GUI Config
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(10, 20, 721, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.output_lbl = QtWidgets.QLabel(self.centralwidget)
        self.output_lbl.setGeometry(QtCore.QRect(10, 10, 91, 16))
        self.output_lbl.setObjectName("output_lbl")
        self.input_lbl = QtWidgets.QLabel(self.centralwidget)
        self.input_lbl.setGeometry(QtCore.QRect(370, 10, 91, 16))
        self.input_lbl.setObjectName("input_lbl")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(9, 39, 721, 281))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.io_layout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.io_layout.setContentsMargins(0, 0, 0, 0)
        self.io_layout.setObjectName("io_layout")        

        # ScrollArea for Output Values
        self.output_area = QtWidgets.QScrollArea(self.horizontalLayoutWidget)
        self.output_area.setWidgetResizable(True)
        self.output_area.setObjectName("output_area")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 355, 277))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.output_area.setWidget(self.scrollAreaWidgetContents)
        self.io_layout.addWidget(self.output_area)

        self.fillOutputParameter()

        # ScrollArea for Input Values
        self.input_area = QtWidgets.QScrollArea(self.horizontalLayoutWidget)
        self.input_area.setWidgetResizable(True)
        self.input_area.setObjectName("input_area")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 354, 277))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.input_area.setWidget(self.scrollAreaWidgetContents_2)
        self.io_layout.addWidget(self.input_area)

        self.fillInputParameter()
        
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 733, 21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.start_btn.setText(_translate("MainWindow", "Start"))
        self.stop_btn.setText(_translate("MainWindow", "Stop"))
        self.output_lbl.setText(_translate("MainWindow", "Output Values:"))
        self.input_lbl.setText(_translate("MainWindow", "Input Values:"))

    def fillOutputParameter(self): 
        top_widget = QtWidgets.QWidget()
        top_layout = QtWidgets.QVBoxLayout()

        usable_modules = self.device.body.dap_list[0].usable_modules

        for module in usable_modules:
            if module.used_in_slots != "" and module.output_length != 0:
                group_box = QtWidgets.QGroupBox()
                group_box.setTitle('Module: {0}'.format(module.used_in_slots))
                layout = QtWidgets.QVBoxLayout(group_box)

                obj = None
                for pState in range(module.output_length):
                    obj = MyClass(obj, pState)
                    self.module_output_values.append(obj)
                    spin_layout = QtWidgets.QHBoxLayout()
                    spin_lbl = QtWidgets.QLabel()
                    spin_lbl.setText(f"{pState}")
                    sp = QSpinBox()
                    sp.setValue(obj.value.value)
                    sp.setEnabled(False)
                    sp.valueChanged.connect(obj.value.set_value)
                    obj.value.changed.connect(sp.setValue)
                    spin_layout.addWidget(spin_lbl)
                    spin_layout.addWidget(sp)
                    layout.addLayout(spin_layout)

                top_layout.addWidget(group_box)

        top_widget.setLayout(top_layout)
        self.output_area.setWidget(top_widget)

    def fillInputParameter(self):
        top_widget = QtWidgets.QWidget()
        top_layout = QtWidgets.QVBoxLayout()

        usable_modules = self.device.body.dap_list[0].usable_modules

        for module in usable_modules:
            if module.used_in_slots != "" and module.input_length != 0:
                group_box = QtWidgets.QGroupBox()
                group_box.setTitle('Module: {0}'.format(module.used_in_slots))
                layout = QtWidgets.QVBoxLayout(group_box)
                for pState in range(module.input_length):
                    spin_layout = QtWidgets.QHBoxLayout()
                    spin_lbl = QtWidgets.QLabel()
                    spin_lbl.setText(f"{pState}")
                    sp = QSpinBox()
                    sp.setValue(pState)
                    sp.setEnabled(False)
                    spin_layout.addWidget(spin_lbl)
                    spin_layout.addWidget(sp)
                    layout.addLayout(spin_layout)

                top_layout.addWidget(group_box)

        top_widget.setLayout(top_layout)
        self.input_area.setWidget(top_widget)


def main():
    app = QApplication(sys.argv)
    win = MainWindow('../gsdml/test_project_2.xml')
    win.setupUi()
    win.show()
    win.module_output_values[0].value = 4
    app.exec_()


if __name__ == "__main__":
    main()
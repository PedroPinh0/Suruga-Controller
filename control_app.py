"""
Author: Pedro Pinho
E-mail: ppinho@ifi.unicamp.br
"""

import sys
import os
import time
import pyvisa as visa
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# Horizontal divider class -- just a simple line
class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

# Class for the 0.01, 0.1, 1, ... buttons.
class Buttons(QPushButton):
    def __init__(self, name, lineEdit:QLineEdit=None):
        super(Buttons, self).__init__()
        #Clicking it changes the QLineEdit box passed as an argument
        self.clicked.connect(self.is_clicked)
        # Sets the name of the button taken from the argument
        self.setText(str(name))
        self.lineEdit = lineEdit

    # Increments the QLineEdit with the corresponding value of the button
    def is_clicked(self):
        self.lineEdit.setText(str(round(float(self.lineEdit.text()) + float(self.text()),2)))

# Similar to 'Buttons' but its function is to clear the QLineEdit box taken as argument
class Clear_Button(QPushButton):
    def __init__(self, lineEdit:QLineEdit=None):
        super(Clear_Button, self).__init__()
        self.clicked.connect(self.is_clicked)
        self.setText("CLEAR")
        self.lineEdit = lineEdit

    def is_clicked(self):
        self.lineEdit.setText(str(0.00))

# Main code
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        scriptDir = os.path.dirname(os.path.realpath("control_app.py"))
        self.setWindowIcon(QIcon(scriptDir + os.path.sep + 'icons/LOGO.png'))

        # Fixes the size of the screen. In my option the size I choose is visually
        # pleasant. If you want to have the option to resize the screen, comment
        # this line. But note that because I used layouts to construct the GUI
        # resizing the screen will probably not be that useful.

        #self.setFixedSize(654, 583)

        # The layout of the window are nested child layouts
        self.OuterLayout = QGridLayout() # Parent layout
        self.ArrowsLayout = QGridLayout() # Arrows layout -- in here are the XY controller
        self.UpDownLayout = QVBoxLayout() # Up and Down layout -- z controller
        self.XYLayout = QGridLayout() # XY options layout -- step size and others
        self.ZLayout = QGridLayout() # Z options layout -- step size and others

        # Adding Widgets for XYLayout
        self.XYStep_Box = QLineEdit("0.0")                                      # It starts with 0.0
        self.XYStep_Box.setReadOnly(True)                                       # Disable user input
        self.XYUnits_Box = QComboBox()                                          # A drop-down list to choose the unit
        self.XYUnits_Box.addItems([u"(µm)", "(mm)"])
        self.XYStep_Label = QLabel("STEP:")
        self.XYStep_Label.setFont(QFont("Arial", 14, weight = QFont.Bold))
        self.XYLayout.addWidget(self.XYStep_Label, 0, 0, 1, 2)
        self.XYLayout.addWidget(self.XYStep_Box, 0, 1, 1, 2)
        self.XYLayout.addWidget(self.XYUnits_Box, 0, 3)
        self.XYLayout.addWidget(Buttons(0.01, self.XYStep_Box), 1, 0)
        self.XYLayout.addWidget(Buttons(0.1, self.XYStep_Box), 1, 1)
        self.XYLayout.addWidget(Buttons(1, self.XYStep_Box), 1, 2)
        self.XYLayout.addWidget(Buttons(10, self.XYStep_Box), 2, 0)
        self.XYLayout.addWidget(Buttons(100, self.XYStep_Box), 2, 1)
        self.XYLayout.addWidget(Buttons(1000, self.XYStep_Box), 2, 2)

        # Horizontal dividers
        self.OuterLayout.addWidget(QHLine(), 3, 0, 1, 2)
        self.OuterLayout.addWidget(QHLine(), 5, 0, 1, 2)
        self.OuterLayout.addWidget(QHLine(), 1, 0, 1, 2)

        # Net Z distance
        self.Z_Distance = QLineEdit("0.0")
        self.Z_Distance.setReadOnly(True)
        self.OuterLayout.addWidget(self.Z_Distance, 6,1)
        self.ZDistance_label = QLabel(u"Current net Z distance (µm):")
        self.ZDistance_label.setFont(QFont("Arial", 14, weight = QFont.Bold))
        self.OuterLayout.addWidget(self.ZDistance_label, 6, 0)

        # Adding Widgets for ZLayout
        self.ZStep_Box = QLineEdit("0.0")
        self.ZStep_Box.setReadOnly(True)
        self.ZUnits_Box = QComboBox()
        self.ZUnits_Box.addItems([u"(µm)", "(mm)"])
        self.ZStep_Label = QLabel("STEP:")
        self.ZStep_Label.setFont(QFont("Arial", 14, weight = QFont.Bold))
        self.ZLayout.addWidget(self.ZStep_Label, 0, 0, 1, 2)
        self.ZLayout.addWidget(self.ZStep_Box, 0, 1, 1, 2)
        self.ZLayout.addWidget(self.ZUnits_Box, 0, 3)
        self.ZLayout.addWidget(Buttons(0.01, self.ZStep_Box), 1, 0)
        self.ZLayout.addWidget(Buttons(0.1, self.ZStep_Box), 1, 1)
        self.ZLayout.addWidget(Buttons(1, self.ZStep_Box), 1, 2)
        self.ZLayout.addWidget(Buttons(10, self.ZStep_Box), 2, 0)
        self.ZLayout.addWidget(Buttons(100, self.ZStep_Box), 2, 1)
        self.ZLayout.addWidget(Buttons(1000, self.ZStep_Box), 2, 2)

        # Adding a Warning Label for when the user chooses mm in the unit box
        self.ZUnits_Box.currentIndexChanged.connect(self.Combo_changed)         # Changing the XY unit value triggers the function 'Combo_changed'
        self.XYUnits_Box.currentIndexChanged.connect(self.Combo_changed)        # Changing the Z unit value trigger the function 'Combo_changed'
        self.Warning_label = QLabel("All good")
        self.Warning_label.setStyleSheet("color: green")
        self.Warning_label.setFont(QFont("Arial", 14, weight = QFont.Bold))
        self.Warning_title = QLabel("WARNINGS:")
        self.Warning_title.setFont(QFont("Arial", 14, weight = QFont.Bold))
        self.OuterLayout.addWidget(self.Warning_label, 0, 1)
        self.OuterLayout.addWidget(self.Warning_title, 0, 0)

        # Adding Widgets for Z-Up, Z-Down and Z-Clear
        self.up_button_z = QPushButton(self)
        self.up_button_z.setIcon(QIcon('icons/UP.png'))
        self.down_button_z = QPushButton(self)
        self.down_button_z.setIcon(QIcon('icons/DOWN.png'))
        self.UpDownLayout.addWidget(self.up_button_z)
        self.UpDownLayout.addWidget(Clear_Button(self.ZStep_Box))
        self.UpDownLayout.addWidget(self.down_button_z)

        # Grouping the buttons Z-Up and Z-Down
        self.btnZ_grp = QButtonGroup()
        self.btnZ_grp.setExclusive(True)
        self.btnZ_grp.addButton(self.up_button_z, 0)                            # Z-Up button has Id #0
        self.btnZ_grp.addButton(self.down_button_z, 1)                          # Z-Down button has Id #1
        self.btnZ_grp.buttonClicked.connect(self.on_clickZ)                     # Clicking any of the buttons trigger the function 'on_clickZ'

        # Adding Widgets for ArrowsLayout
        self.up_button_xy = QPushButton(self)
        self.up_button_xy.setIcon(QIcon('icons/UP.png'))
        self.left_button_xy = QPushButton(self)
        self.left_button_xy.setIcon(QIcon('icons/LEFT.png'))
        self.right_button_xy = QPushButton(self)
        self.right_button_xy.setIcon(QIcon('icons/RIGHT.png'))
        self.down_button_xy = QPushButton(self)
        self.down_button_xy.setIcon(QIcon('icons/DOWN.png'))
        self.ArrowsLayout.addWidget(self.up_button_xy, 0, 1)
        self.ArrowsLayout.addWidget(self.down_button_xy, 2, 1)
        self.ArrowsLayout.addWidget(self.left_button_xy, 1, 0)
        self.ArrowsLayout.addWidget(self.right_button_xy, 1, 2)
        self.ArrowsLayout.addWidget(Clear_Button(self.XYStep_Box), 1, 1)

        # Grouping the buttons XY-Up and XY-Down, XY-Left and XY-Right
        self.btnXY_grp = QButtonGroup()
        self.btnXY_grp.setExclusive(True)
        self.btnXY_grp.addButton(self.up_button_xy, 0)                          # XY-Up has ID #0
        self.btnXY_grp.addButton(self.down_button_xy, 1)                        # XY-Down has ID #1
        self.btnXY_grp.addButton(self.left_button_xy, 2)                        # XY-Left has ID #2
        self.btnXY_grp.addButton(self.right_button_xy, 3)                       # XY-Right has ID #3
        self.btnXY_grp.buttonClicked.connect(self.on_clickXY)                   # Clicking any of the buttons trigger the function 'on_clickXY'

        # Fixing some grid elements spacings
        self.XYLayout.setHorizontalSpacing(0)                                   # Thigtens the space between the buttons on the right side
        self.ZLayout.setHorizontalSpacing(0)                                    # Thigtens the space between the buttons on the right side
        self.OuterLayout.setHorizontalSpacing(100)                              # Gives a bit of space between the direction controls and step buttons
        self.OuterLayout.setVerticalSpacing(20)
        self.ArrowsLayout.setVerticalSpacing(10)
        self.ArrowsLayout.setHorizontalSpacing(10)
        self.UpDownLayout.setSpacing(10)

        # Nesting all layouts
        self.OuterLayout.addLayout(self.ArrowsLayout, 2, 0)
        self.OuterLayout.addLayout(self.XYLayout, 2, 1)
        self.OuterLayout.addLayout(self.UpDownLayout, 4, 0)
        self.OuterLayout.addLayout(self.ZLayout, 4, 1)

        self.widget = QWidget(self)
        self.widget.setLayout(self.OuterLayout)
        self.setCentralWidget(self.widget)

    # This function is triggered when any of the ComboBoxs are changed
    def Combo_changed(self, combo):
        warning = [0,0]
        # The warning vector hold the information of what ComboBox has the mm unit selected
        if self.XYUnits_Box.currentText() == "(mm)": warning[0] = 1
        if self.ZUnits_Box.currentText() == "(mm)": warning[1] = 1

        # The warning mensage is different depending on whether the Z-Unit is mm, XY-unit is mm or both
        if warning[0] == 1:
            self.Warning_label.setText("XY UNIT IS HIGH!! CAREFULL!!")
            self.Warning_label.setStyleSheet("color: red")

        if warning[1] == 1:
            self.Warning_label.setText("Z UNIT IS HIGH!! CAREFULL!!")
            self.Warning_label.setStyleSheet("color: red")

        if warning[1] == 1 and warning[0] == 1:
            self.Warning_label.setText("ALL UNITS ARE HIGH!! CAREFULL!!")
            self.Warning_label.setStyleSheet("color: red")

        if warning[1] == 0 and warning[0] == 0:
            self.Warning_label.setText("All good")
            self.Warning_label.setStyleSheet("color: green")

    # This is the function that send the signal to SURUGA to move in the
    # direction corresponding to the XY-button pressed and distance given by the
    # XY Step_box value and the unit choosen. The ´step´ function is defined
    # at the end of the code.
    def on_clickXY(self, btn):
        if self.XYUnits_Box.currentText() == u"(µm)":
            if self.btnXY_grp.id(btn) == 0:
                step(1,round(float(self.XYStep_Box.text())*1E-6, 8), 1)
                print(round(float(self.XYStep_Box.text()), 8), u"µm in the Y+")         # Moves in the positive y-direction
            if self.btnXY_grp.id(btn) == 1:
                step(1,round(float(self.XYStep_Box.text())*1E-6, 8), -1)
                print(round(float(self.XYStep_Box.text()), 8), u"µm in the Y-")         # Moves in the negative y-direction
            if self.btnXY_grp.id(btn) == 2:
                step(2,round(float(self.XYStep_Box.text())*1E-6, 8), 1)
                print(round(float(self.XYStep_Box.text()), 8), u"µm in the X-")         # Moves in the negative x-direction
            if self.btnXY_grp.id(btn) == 3:
                step(2,round(float(self.XYStep_Box.text())*1E-6, 8), -1)
                print(round(float(self.XYStep_Box.text()), 8), u"µm in the X+")         # Moves in the positive x-direction

        if self.XYUnits_Box.currentText() == "(mm)":
            if self.btnXY_grp.id(btn) == 0:
                step(1,round(float(self.XYStep_Box.text())*1E-3, 8), 1)
                print(round(float(self.XYStep_Box.text()), 8), "mm in the Y+")         # Moves in the positive y-direction
            if self.btnXY_grp.id(btn) == 1:
                step(1,round(float(self.XYStep_Box.text())*1E-3, 8), -1)
                print(round(float(self.XYStep_Box.text()), 8), "mm in the Y-")         # Moves in the negative y-direction
            if self.btnXY_grp.id(btn) == 2:
                step(2,round(float(self.XYStep_Box.text())*1E-3, 8), 1)
                print(round(float(self.XYStep_Box.text()), 8), "mm in the X-")         # Moves in the negative x-direction
            if self.btnXY_grp.id(btn) == 3:
                step(2,round(float(self.XYStep_Box.text())*1E-3, 8), -1)
                print(round(float(self.XYStep_Box.text()), 8), "mm in the X+")         # Moves in the positive x-direction

    # This is the function that send the signal to SURUGA to move in the
    # direction corresponding to the Z-button pressed and distance given by the
    # Z Step_box value and the unit choosen. It also updates the current net z
    # distance traveled.
    def on_clickZ(self, btn):
        if self.ZUnits_Box.currentText() == u"(µm)":
            if self.btnZ_grp.id(btn) == 0:
                step(3,round(float(self.ZStep_Box.text())*1E-6, 8),1)
                self.Z_Distance.setText(str(round(float(self.Z_Distance.text()) + float(self.ZStep_Box.text()),2)))             # Moves in the positive Z direction (um)
                print(round(float(self.ZStep_Box.text()), 8), u"µm in the Z+")

            if self.btnZ_grp.id(btn) == 1:
                step(3,round(float(self.ZStep_Box.text())*1E-6, 8),-1)
                self.Z_Distance.setText(str(round(float(self.Z_Distance.text()) - float(self.ZStep_Box.text()),2)))             # Moves in the negative Z direction (um)
                print(round(float(self.ZStep_Box.text()), 8), u"µm in the Z-")

        if self.ZUnits_Box.currentText() == "(mm)":
            if self.btnZ_grp.id(btn) == 0:
                step(3,round(float(self.ZStep_Box.text())*1E-3, 8),1)
                self.Z_Distance.setText(str(round(float(self.Z_Distance.text()) + float(self.ZStep_Box.text())*10E3,2)))       # Moves in the positive Z direction (mm)
                print(round(float(self.ZStep_Box.text()), 8), "mm in the Z+")

            if self.btnZ_grp.id(btn) == 1:
                step(3,round(float(self.ZStep_Box.text())*1E-3, 8),-1)
                self.Z_Distance.setText(str(round(float(self.Z_Distance.text()) - float(self.ZStep_Box.text())*10E3,2)))       # Moves in the negative z direction (mm)
                print(round(float(self.ZStep_Box.text()), 8), "mm in the Z-")


rm=visa.ResourceManager()
dev = rm.open_resource('ASRL9::INSTR')
dev.write_termination = '\r'
dev.read_termination = '\r'
dev.baud_rate = 9600
dev.query('*IDN?')
dev.close()

inst_xy = visa.ResourceManager().open_resource('ASRL9::INSTR')
inst_z = visa.ResourceManager().open_resource('ASRL8::INSTR')
inst_xy.write_termination='\r'
inst_xy.read_termination='\r'
inst_z.write_termination='\r'
inst_z.read_termination='\r'
inst_xy.baud_rate = 9600
inst_z.baud_rate = 9600

def step(axis, step_meters, direction):
    #print values
    str_dir = 'CCW'
    str_dir_z = 'CW'

    if direction == 1:
        str_dir = 'CW'
        str_dir_z = 'CCW'

    if abs(step_meters)<50e-9:
        speed='0'
    elif abs(step_meters)<100e-9:
        speed='1'
    elif abs(step_meters)<500e-9:
        speed='2'
    elif abs(step_meters)<1e-6:
        speed='3'
    elif abs(step_meters)<5e-6:
        speed='4'
    elif abs(step_meters)<10e-6:
        speed='5'
    elif abs(step_meters)<100e-6:
        speed='6'
    elif abs(step_meters)<500e-6:
        speed='7'
    elif abs(step_meters)<1e-3:
        speed='8'
    else:
        speed='9'

    #Controlador-> 1 pulso = 1 micron
    #Pág. 72 do manual - position C--> 1 step = 10 nm
    step = round(step_meters/10e-9);
    step_str = str(step);

    if float(step) != 0.001:
        #driv_div = str(0)
        if axis == 1:
            cmd = 'AXI1:selsp ' + speed + ' :PULS ' + step_str + ':GO ' + str_dir + ':DW'
            inst_xy.write(cmd)
        if axis == 2:
            cmd = 'AXI2:selsp ' + speed + ' :PULS ' + step_str + ':GO ' + str_dir + ':DW'
            inst_xy.write(cmd)
        elif axis == 3:
            cmd = 'AXI1:selsp ' + speed + ' :PULS ' + step_str + ':GO ' + str_dir_z + ':DW'
            inst_z.write(cmd)


app = QApplication(sys.argv)
window = MainWindow()
window.setWindowTitle("Suruga Controller")
window.show()
sys.exit(app.exec())

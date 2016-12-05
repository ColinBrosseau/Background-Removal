#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Import csv GUI
      
* Select .csv file to import
* adjust header and column name to reflect x and y-axis
* Click Export

Colin Brosseau (colin@erzatz.info)
License: MIT
Last modified: 2016/12/02
"""

import csv

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import argparse
import numpy as np

from PyQt4.QtGui import QDialog, QVBoxLayout, QDialogButtonBox, QDateTimeEdit, QApplication
from PyQt4.QtCore import Qt, QDateTime


class importExternalData(QtGui.QWidget):
    
    def __init__(self, filename=False, parameters=None, parent=None):
        super(importExternalData, self).__init__()
        self.parameters = parameters
        self.initUI()
        
    def initUI(self):      

        self.btn = QtGui.QPushButton('Import .csv', self)
        self.btn.move(20, 20)
        self.btn.clicked.connect(self.showDialog)
        
        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Input dialog')
        self.show()
        
    def showDialog(self):
        x, y, parameters, ok = importCsv.getData(parameters=self.parameters)
        if ok:
            print("mean of x: " + str(np.mean(x)))
            print("mean of y: " + str(np.mean(y)))
            print("import parameters")
            print(parameters)

        
class importCsvParameters():
    def __init__(self, xIndex=1, yIndex=2, headerValue=0, filetype='csv'):
        self.xIndex = xIndex  # column index of the x axis (1-based)
        self.yIndex = yIndex  # column index of the y axis (1-based)
        self.headerValue = headerValue  # number of lines of header
        self.filetype = filetype

    def __str__(self):
        return self.filetype + chr(10) + "xIndex: " + str(self.xIndex) + chr(10) + "yIndex: " + str(self.yIndex) + chr(10) + "headerValue: " + str(self.headerValue)

class importCsv(QtGui.QDialog):    
    def __init__(self, filename=False, parameters=None, parent=None):
        super(importCsv, self).__init__(parent)
        self.filename = filename

        # self.parameters contains column indexes for x and y, header length
        if not parameters:
            self.parameters = importCsvParameters()
        else:
            self.parameters = parameters
        self.hasData = False  # True when data load from file
        
        header_label = QLabel('Header')
        self.header = QSpinBox()
        self.header.setValue(self.parameters.headerValue)
        self.header.setMinimum(0)
        self.header.setMaximum(99999)
        self.header.valueChanged.connect(self.header_changed)
        header = QHBoxLayout()
        header.addWidget(header_label)
        header.addWidget(self.header)

        xaxis_label = QLabel('x-axis')
        self.xaxis = QSpinBox()
        self.xaxis.setValue(self.parameters.xIndex)
        self.xaxis.setMinimum(1)
        self.xaxis.setMaximum(99999)
        self.xaxis.valueChanged.connect(self.axes_changed)
        xaxis = QHBoxLayout()
        xaxis.addWidget(xaxis_label)
        xaxis.addWidget(self.xaxis)

        yaxis_label = QLabel('y-axis')
        self.yaxis = QSpinBox()
        self.yaxis.setValue(self.parameters.yIndex)
        self.yaxis.setMinimum(1)
        self.yaxis.setMaximum(99999)
        self.yaxis.valueChanged.connect(self.axes_changed)
        yaxis = QHBoxLayout()
        yaxis.addWidget(yaxis_label)
        yaxis.addWidget(self.yaxis)
        
        self.model = QtGui.QStandardItemModel(self)
        self.model.setHorizontalHeaderItem(self.parameters.xIndex - 1, QStandardItem("x"))
        self.model.setHorizontalHeaderItem(self.parameters.yIndex - 1, QStandardItem("y"))
        
        self.tableView = QtGui.QTableView(self)
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)

        selectionModel = QItemSelectionModel(self.model)
        self.tableView.setSelectionModel(selectionModel)
        
        self.loadButton = QtGui.QPushButton(self)
        self.loadButton.setText("Load .csv from file")
        self.loadButton.clicked.connect(self.loadButton_clicked)

        self.exportButton = QtGui.QPushButton(self)
        self.exportButton.setText("Export .csv (not fully functionnal, look on terminal)")
        self.exportButton.clicked.connect(self.exportButton_clicked)

        # OK and Cancel buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok,
            Qt.Horizontal, self)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layoutVertical = QtGui.QVBoxLayout(self)
        self.layoutVertical.addLayout(header)
        self.layoutVertical.setAlignment(header, Qt.AlignVCenter)
        self.layoutVertical.addLayout(xaxis)
        self.layoutVertical.setAlignment(xaxis, Qt.AlignVCenter)
        self.layoutVertical.addLayout(yaxis)
        self.layoutVertical.setAlignment(yaxis, Qt.AlignVCenter)
        self.layoutVertical.addWidget(self.tableView)
        self.layoutVertical.addWidget(self.loadButton)
        self.layoutVertical.addWidget(self.exportButton)
        self.layoutVertical.addWidget(self.buttons)
        
        if not self.filename:
            self.filename = str(QFileDialog.getOpenFileName(self, 
                                    'Load file', '', 
                                    "CSV (*.csv);;All Files (*)"))
        self.loadCsv(self.filename)
        self.update()

    def axes_changed(self, value):
        self.parameters.xIndex = int(self.xaxis.text())
        self.parameters.yIndex = int(self.yaxis.text())
        self.update()
        
    def header_changed(self, value):
        self.parameters.headerValue = self.header.value()
        self.update()

    def update(self):
        # Clear header
        nColumns = self.model.columnCount()
        for i in range(nColumns):
            self.model.setHorizontalHeaderItem(i, QStandardItem(""))
        # Fill header with new values
        self.model.setHorizontalHeaderItem(self.parameters.xIndex - 1, QStandardItem("x"))
        self.model.setHorizontalHeaderItem(self.parameters.yIndex - 1, QStandardItem("y"))

        if self.hasData:
            first_line = self.header.value()
            last_line = self.model.rowCount()
            
            self.tableView.setFocus()
            selectionModel = self.tableView.selectionModel()
            selectionModel.clear()
            
            index1 = self.tableView.model().index(first_line, self.parameters.xIndex-1)
            index2 = self.tableView.model().index(last_line-1, self.parameters.yIndex-1)
            itemSelection = QItemSelection(index1, index2)
            selectionModel.select(itemSelection, QItemSelectionModel.Rows | QItemSelectionModel.Select)
            
    def loadCsv(self, filename):
        with open(filename, "r") as fileInput:
            i = 1
            for row in csv.reader(fileInput):    
                items = [
                    QtGui.QStandardItem(field)
                    for field in row
                ]
                self.model.appendRow(items)
                i += 1

        self.hasData = True
        self.update()
        nColumn = self.model.columnCount()
        self.xaxis.setMaximum(nColumn)
        self.yaxis.setMaximum(nColumn)
        
    def writeCsv(self):
#        print("columns:")
#        print("x: " + str(self.parameters.xIndex-1))
#        print("y: " + str(self.parameters.yIndex-1))

        first_line = self.header.value()
        last_line = self.model.rowCount()
#        print("rows:")
#        print("first: " + str(first_line))
#        print("last : " + str(last_line))

        # Extract data to numpy arrays
        # Far far from optimal
        xArray = np.zeros([last_line-first_line,1 ])
        yArray = np.zeros_like(xArray)
        i = 0
        for rowNumber in range(first_line, last_line):
            x = self.model.data(self.model.index(rowNumber, self.parameters.xIndex-1),QtCore.Qt.DisplayRole)
            y = self.model.data(self.model.index(rowNumber, self.parameters.yIndex-1),QtCore.Qt.DisplayRole)
            xArray[i] = x
            yArray[i] = y
            i += 1
        return np.squeeze(xArray), np.squeeze(yArray), self.parameters        

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getData(parent=None, parameters=None):
        import numpy as np
        dialog = importCsv(parent, parameters=parameters)
        result = dialog.exec_()
        x, y, parameters = dialog.writeCsv()
        return (x, y, parameters, result == QDialog.Accepted)

    @QtCore.pyqtSlot()
    def exportButton_clicked(self):
        self.writeCsv(self.filename)

    @QtCore.pyqtSlot()
    def loadButton_clicked(self):
        path = str(QFileDialog.getOpenFileName(self, 
                    'Load file', '', 
                    "CSV (*.csv);;All Files (*)"))
        
        if path:
            self.loadCsv(path)
            self.update()


if __name__ == "__main__":
    import sys

    # parse commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="input file (.csv format)")
    parser.add_argument("--x", default=1, type=int, help="column of x-axis")
    parser.add_argument("--y", default=2, type=int, help="column of y-axis")
    parser.add_argument("--header", default=0, type=int, help="number of lines of header")
    args = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('Import .csv')

    parameters = importCsvParameters(xIndex=args.x, yIndex=args.y, headerValue=args.header, filetype='csv')
    print(parameters)
    main = importExternalData(filename=args.file, parameters=parameters)
    main.show() 

    sys.exit(app.exec_())

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

class importCsv(QtGui.QWidget):
    def __init__(self, filename=False, xIndex=1, yIndex=2, headerValue=0, parent=None):
        super(importCsv, self).__init__(parent)
        self.filename = filename
        self.x = xIndex  # column reprensenting x-axis (1-based)
        self.y = yIndex  # column reprensenting y-axis (1-based)
        self.headerValue = headerValue  # Number of rows for the header
        self.hasData = False  # True when data load from file
        
        header_label = QLabel('Header')
        self.header = QSpinBox()
        self.header.setValue(self.headerValue)
        self.header.setMinimum(0)
        self.header.setMaximum(99999)
        self.header.valueChanged.connect(self.header_changed)
        header = QHBoxLayout()
        header.addWidget(header_label)
        header.addWidget(self.header)

        xaxis_label = QLabel('x-axis')
        self.xaxis = QSpinBox()
        self.xaxis.setValue(self.x)
        self.xaxis.setMinimum(1)
        self.xaxis.setMaximum(99999)
        self.xaxis.valueChanged.connect(self.axes_changed)
        xaxis = QHBoxLayout()
        xaxis.addWidget(xaxis_label)
        xaxis.addWidget(self.xaxis)

        yaxis_label = QLabel('y-axis')
        self.yaxis = QSpinBox()
        self.yaxis.setValue(self.y)
        self.yaxis.setMinimum(1)
        self.yaxis.setMaximum(99999)
        self.yaxis.valueChanged.connect(self.axes_changed)
        yaxis = QHBoxLayout()
        yaxis.addWidget(yaxis_label)
        yaxis.addWidget(self.yaxis)
        
        self.model = QtGui.QStandardItemModel(self)
        self.model.setHorizontalHeaderItem(self.x - 1, QStandardItem("x"))
        self.model.setHorizontalHeaderItem(self.y - 1, QStandardItem("y"))
        
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

        if not self.filename:
            self.filename = str(QFileDialog.getOpenFileName(self, 
                                    'Load file', '', 
                                    "CSV (*.csv);;All Files (*)"))
        self.loadCsv(self.filename)
        self.update()

    def axes_changed(self, value):
        self.x = int(self.xaxis.text())
        self.y = int(self.yaxis.text())
        self.update()
        
    def header_changed(self, value):
        self.headerValue = self.header.value()
        self.update()

    def update(self):
        # Clear header
        nColumns = self.model.columnCount()
        for i in range(nColumns):
            self.model.setHorizontalHeaderItem(i, QStandardItem(""))
        # Fill header with new values
        self.model.setHorizontalHeaderItem(self.x - 1, QStandardItem("x"))
        self.model.setHorizontalHeaderItem(self.y - 1, QStandardItem("y"))

        if self.hasData:
            first_line = self.header.value()
            last_line = self.model.rowCount()
            
            self.tableView.setFocus()
            selectionModel = self.tableView.selectionModel()
            selectionModel.clear()
            
            index1 = self.tableView.model().index(first_line, self.x-1)
            index2 = self.tableView.model().index(last_line-1, self.y-1)
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
        
    def writeCsv(self, filename):
        # indexes = self.tableView.selectionModel().selectedRows()
        # for index in sorted(indexes):
        #     print('Row %d is selected' % index.row())

        # indexes = self.tableView.selectionModel().selectedColumns()
        # for index in sorted(indexes):
        #     print('Column %d is selected' % index.column())

        print("columns:")
        print("x: " + str(self.x-1))
        print("y: " + str(self.y-1))

        first_line = self.header.value()
        last_line = self.model.rowCount()
        print("rows:")
        print("first: " + str(first_line))
        print("last : " + str(last_line))

        # with open('output_' + filename, "w") as fileOutput:
        #     writer = csv.writer(fileOutput)
        #     for rowNumber in range(self.model.rowCount()):
        #         fields = [
        #             self.model.data(
        #                 self.model.index(rowNumber, columnNumber),
        #                 QtCore.Qt.DisplayRole
        #             )
        #             for columnNumber in range(self.model.columnCount())
        #         ]
        #         writer.writerow(fields)

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
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('Import .csv')
#    main = importCsv("test_file.csv")
    main = importCsv()
    main.show()

    sys.exit(app.exec_())

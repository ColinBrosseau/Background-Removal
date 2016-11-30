"""
Remove background from dataset
      
* Import data (.csv): 
*     File > Load File
*         OR
*     Ctrl+L
* Set Order and Threshold parameters
* Calculate Background
*     File > Calculate Background
*         OR
*     Ctrl+B
*         OR
*     Click "Background"
* Export data
*     File > Export (.csv)
*         OR
*     Ctrl+E

Colin Brosseau (colin@erzatz.info)
License: 
Last modified: 2016/11/29
"""

"""
TODO
display error message if background absent while saving
"""

#import sys, os, random
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np

import matplotlib

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import backcor

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.showMaximized()
        self.x = 0
        self.y = 0
        self.setWindowTitle('Background removal')

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.order.setText('6')
        self.threshold.setText('50')
        self.has_background = False
        self.background_removed = False
        #self.plot_data()

    def export_csv(self):
        header = ''
        if self.background_removed:
            header = header + ' > Background removed'

        file_choices = "CSV (*.csv)|*.csv"
        
        path = str(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
#            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)

            np.savetxt(path, np.array([self.x, self.y-self.background]).transpose(), fmt='%1.7e', delimiter=',', header=header)
        
    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = str(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def load_csv(self):
        file_choices = "CSV (*.csv)|*.csv"
#        file_choices = "*|*"
        
        path = str(QFileDialog.getOpenFileName(self, 
                        'Load file', '', 
                        "CSV (*.csv);;All Files (*)"))
        
        if path:
            self.draw_button.setEnabled(True)
            data = np.loadtxt(path, delimiter=',', unpack=True, skiprows=1)
            self.x = data[0]
            self.y = data[1]
            self.has_background = False
            self.background_removed = False
            self.plot_data()
            
    def on_about(self):
        msg = """ 
         Remove background from dataset
        
         * Import data (.csv): 
         *     File > Load File
         * Set Order and Threshold parameters
         * Calculate Background
         *     File > Calculate Background
         * Export data
         *     File > Export (.csv)
        """
        QMessageBox.about(self, "Basic usage", msg.strip())
    
    def plot_data(self):
        """ Redraws the figure
        """
        self.axes.clear()        
        self.axes.grid(self.grid_cb.isChecked())

        self.axes.plot(self.x, self.y, '.', label='data')
        self.axes.set_xlim([np.min(self.x), np.max(self.x)])
        self.axes.set_ylim([np.min(self.y), np.max(self.y)])
        self.axes.set_title('Data')
        self.axes.set_xticklabels([])
        
        self.axes2.clear()        
        if self.has_background:
            self.axes.set_title('Data & Background')
            self.axes.plot(self.x,self.background,'', label='background')

            z = self.y - self.background
            self.axes2.grid(self.grid_cb.isChecked())
            
            self.axes2.plot(self.x, z, '.', label='data - background')
            self.axes2.set_xlim([np.min(self.x), np.max(self.x)])
            self.axes2.set_ylim([np.min(z), np.max(z)])
            self.axes2.set_title('Difference')
            self.axes2.legend()
            
        self.axes.legend()
        self.canvas.draw()
    
    def calculate_background(self):
        """ Calculate the background
        """
        # fit method
        text = str(self.fit_method.currentText())
        if text == "symmetric Huber function":
            method = 'sh'
        elif text == "asymmetric Huber function":
            method = 'ah'
        elif text == "symmetric truncated quadratic":
            method = 'stq'
        elif text == "asymmetric truncated quadratic":
            method = 'atq'
            
        self.statusBar().showMessage('Calculating background...')  # problem here: it just make status bar to blink. Like it print this line after it make calculation
        order = int(self.order.text())
        threshold = float(self.threshold.text())
        z, a, it = backcor.backcor(self.x, self.y, order, threshold, method)
        self.statusBar().showMessage('')
        self.has_background = True
        self.background = z
        self.plot_data()
    
    def create_main_frame(self):
        self.main_frame = QWidget()
        
        self.dpi = 100
#        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.fig = Figure(dpi=self.dpi, tight_layout=True)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        self.axes = self.fig.add_subplot(211)
        self.axes2 = self.fig.add_subplot(212)
        
        # Create the navigation toolbar, tied to the canvas
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        # Other GUI controls

        # Order of the polynomial
        order_label = QLabel('Order')
        self.order = QLineEdit()
        self.order.setValidator(QIntValidator(0, 101, self))
        self.order.setMinimumWidth(3)
        self.order.setMaxLength(3)
        order = QVBoxLayout()
        order.addWidget(order_label)
        order.addWidget(self.order)

        # Threshold (peak detection)
        threshold_label = QLabel('Threshold')
        self.threshold = QLineEdit()
        self.threshold.setMinimumWidth(3)
        self.threshold.setValidator(QDoubleValidator(bottom=0))
        threshold = QVBoxLayout()
        threshold.addWidget(threshold_label)
        threshold.addWidget(self.threshold)
        
        # Fit method
        fit_method_label = QLabel('Fit Method')

        self.fit_method = QComboBox(self)
        self.fit_method.addItem("symmetric Huber function")
        self.fit_method.addItem("asymmetric Huber function")
        self.fit_method.addItem("symmetric truncated quadratic")
        self.fit_method.addItem("asymmetric truncated quadratic")
        index = self.fit_method.findText('asymmetric truncated quadratic')
        if index >= 0:
            self.fit_method.setCurrentIndex(index)
        fit_method = QVBoxLayout()
        fit_method.addWidget(fit_method_label)
        fit_method.addWidget(self.fit_method)
        
        self.draw_button = QPushButton("&Background")
        self.draw_button.setEnabled(False)
        self.connect(self.draw_button, SIGNAL('clicked()'), self.calculate_background)

        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.plot_data)
        
        # Layout with box sizers
        hbox = QHBoxLayout()

        hbox.addLayout(order)
        hbox.setAlignment(order, Qt.AlignVCenter)
        hbox.addLayout(threshold)
        hbox.setAlignment(threshold, Qt.AlignVCenter)
        hbox.addLayout(fit_method)
        hbox.setAlignment(fit_method, Qt.AlignVCenter)
#        for w in [  self.order, self.threshold, self.draw_button, self.remove_button, self.grid_cb,
        for w in [ self.draw_button, self.grid_cb,]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)

        # Main window (everything together)
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
    
    def create_status_bar(self):
        self.status_text = QLabel("")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        load_file_action = self.create_action("&Load file",
            shortcut="Ctrl+O", slot=self.load_csv, 
            tip="Load data")
        calculate_action = self.create_action("Calculate &Background",
            shortcut="Ctrl+B", slot=self.calculate_background, 
            tip="Calculate Background")
        save_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        export_csv_action = self.create_action("&Export (.csv)",
            shortcut="Ctrl+E", slot=self.export_csv, 
            tip="Export to csv")
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (load_file_action, calculate_action, save_file_action, export_csv_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About this program')
        
        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()

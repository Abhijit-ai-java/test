import sys
#import xlrd
import wht
import serial
import sqlite3
import glob
#import xlsxwriter
import RPi.GPIO as GPIO
#from xlutils.copy import copy
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from datetime import datetime, date, time
import time
import os.path
import math
import thread

global flag1
global flag2
global ser
global serial_port  
global serial_data
global serial_state
global serial_data_buffer
global serial_trigger_data
global window_state

serial_port=0
rate=0
per=0
flag1=0
flag2=0
x=0
buff=0
Tester_data=0
current_port=0
serial_state=0
serial_data=0
serial_data=0

model=0
str1=0
serial_state=0
window_state=0
Send_Print_Flag=0
serial_trigger_flag=0
serial_data_buffer='\0'
end_index=0
File_handling_exception=0



#################################################################################################
serial_port = serial.Serial(
    port='/dev/ttyAMA0',
    #port='/dev/ttyUSB0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0.01
    )
#################################################################################################   
class Ui_MainWindow(QtGui.QMainWindow,wht.Ui_MainWindow):
    
    def __init__(self):
        super(Ui_MainWindow,self).__init__()
        self.setupUi(self)
        self.w=QWidget()

        global serial_trigger_data
        global serial_data
        global serial_state
        global serial_data_buffer
        global window_state
        
        
        try:
            thread.start_new_thread(self.serial_receive,())#started T_1
        except:
            print("threading Error")
            while 1:
                pass  

        ports = glob.glob('/dev/tty[A-Za-z]*')
        count=0
        for port in ports:
            combo=self.comboBox.addItem(ports[count])
            count = count+1
            
        combo_3=self.comboBox_3.addItems(['None','Even','Odd'])
        combo_4=self.comboBox_4.addItems(['STOPBITS_ONE','None'])
        combo_5=self.comboBox_5.addItems(['EIGHT','SEVEN'])
        combo_2=self.comboBox_2.addItems(['9600','2400','4800','19200'])
        self.comboBox.currentIndexChanged.connect(self.test)
        self.comboBox_2.currentIndexChanged.connect(self.SelectBaudrate)
        self.comboBox_3.currentIndexChanged.connect(self.SelectParity)
        self.comboBox_4.currentIndexChanged.connect(self.SelectStopbit)
        self.comboBox_5.currentIndexChanged.connect(self.SelectDatabit)

     ##==================LOGIN TAB==================================##
        #self.pushButton_2.clicked.connect(self.btnLogin)        
     ##===============================================================##
     ##==================SETTING TAB==================================##
        self.pushButton_20.clicked.connect(self.btnConnect)
        self.pushButton_21.clicked.connect(self.btnDissconnect)  
     ##===============================================================##
        self.pushButton.clicked.connect(self.btnShutdown)
     ##===============================================================##


        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit Application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        copyAction = QtGui.QAction(QtGui.QIcon('copy.png'), '&Copy', self)
        copyAction.setShortcut('Ctrl+C')
        copyAction.setStatusTip('Copy to the Clipboard')
        copyAction.triggered.connect(self.lineEdit_5.copy)

        pasteAction = QtGui.QAction(QtGui.QIcon('paste.png'), '&Paste', self)
        pasteAction.setShortcut('Ctrl+V')
        pasteAction.setStatusTip('Paste from the Clipboard')
        pasteAction.triggered.connect(self.lineEdit_5.paste)

        cutAction = QtGui.QAction(QtGui.QIcon('cut.png'), '&Cut', self)
        cutAction.setShortcut('Ctrl+X')
        cutAction.setStatusTip('Copy text to the clipboard and delet from editor')
        cutAction.triggered.connect(self.lineEdit_5.cut)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(copyAction)
        editMenu.addAction(pasteAction)
        editMenu.addAction(cutAction)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAction)
        toolbar.addAction(copyAction)
        toolbar.addAction(pasteAction)
        toolbar.addAction(cutAction)
        
        self.setGeometry(10, 10, 500, 500)
        #self.setWindowTitle('Text Editor')
        #self.setWindowIcon(QtGui.QIcon('favicon.png'))
        self.show()

##        edit = self.lineEdit_5('', self)
##        edit.setStatusTip('Input Text Here')
##        edit.resize(480, 400)
##        edit.move(10, 60)
##        edit.setToolTip('Input Text Here')
##        edit.show()


        
        
    def test(self):
        global current_port
        com = self.comboBox.currentText()
        combo="'/dev/"+com+"'"
        print combo
            
    def SelectBaudrate(self):
        rate = self.comboBox_2.currentText()
        print rate
    def SelectParity(self):
        per = self.comboBox_3.currentText()
        print per
    def SelectStopbit(self):
        stop = self.comboBox_4.currentText()
        print stop
    def SelectDatabit(self):
        data = self.comboBox_5.currentText()
        print data

##    def btnLogin(self):
##        
##        a = self.lineEdit.text()
##        b = self.lineEdit_2.text()
##        print a
##        print b
##        if (a=="ADMIN"):
##            if (b == "1234"):
##                print("Login successfully!!!!")
##                QMessageBox.about(self.w,"About","Login Successfully")
##                self.pushButton_2.setText('LOGOUT')
##                self.lineEdit_2.clear()
##                self.tabWidget.setCurrentIndex(3)
##                self.tabWidget.setTabEnabled(0, True)
##                self.tabWidget.setTabEnabled(1, True)
##                self.tabWidget.setTabEnabled(2, True)
##                self.tabWidget.setTabEnabled(3, True)
##                self.tabWidget.setTabEnabled(4, True)
##                self.tabWidget.setTabEnabled(5, True)
##
##            else:
##                print("Invalid User")
##                self.lineEdit_2.clear()
##                QMessageBox.about(self.w,"About","Invalid User")
##                self.pushButton_2.setText('LOGIN')
##                current_text = self.pushButton_2.text()
##                print ''.format(current_text)
##                self.tabWidget.setTabEnabled(0, False)
##                self.tabWidget.setTabEnabled(1, False)
##                self.tabWidget.setTabEnabled(2, False)
##                self.tabWidget.setTabEnabled(3, False)
##                self.tabWidget.setTabEnabled(4, True)
##                self.tabWidget.setTabEnabled(5, False)

    def serial_receive(self):
        global serial_trigger_data
        global serial_data
        global serial_state
        global serial_data_buffer
        global window_state
        global serial_trigger_flag
        while True:
            #serial_data=Trigger_port.read(1)
            serial_data=serial_port.readline(1)
            ##print(serial_data)
            if len(serial_data)>0:
                if serial_state==0:
                    if serial_data=='*':
                        serial_state=1
                        ##print("* Received")
                    else:
                        serial_state=0
                elif serial_state==1:
                    if serial_data!='#':

                        if serial_data_buffer=='\0':
                            serial_data_buffer=serial_data
                        else:
                            serial_data_buffer +=serial_data
                    elif  serial_data=='#':
                        serial_trigger_data=serial_data_buffer
                        serial_trigger_flag=1
                        #serial_data_buffer='0'
                    
                    else:
                        serial_state=0
                
                serial_data=0


    def btnConnect(self): 
        global flag1
        global flag2
        global ser
        global buff
        global count
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        global model
        global str1
        count=0
        mylist=[]
        model=[]
        serial_port.write('*010101#')
        print("transmit")

        if(len(serial_trigger_data)>0):
            print 'hi'
            if('*' in serial_trigger_data):
                if ('01' in  serial_trigger_data):
                    print 'hihihihi'
            

    def btnDissconnect(self):
        global flag1
        if(flag2==0):
            flag1=0
            self.lineEdit_5.setText('device Not connected')
            self.thread.stop()
        
        
        
    
    def btnShutdown(self, event):
        quit_msg = "Are you sure you want to Shutdown?"
        reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            os.system("sudo shutdown -h now")
        else:
            event.ignore()


    @pyqtSlot()
    def showTime(self):
        self.lcdNumber_2.display(QTime.currentTime().toString(QString("hh:mm:ss")))

    @pyqtSlot()
    def showData(self):
        self.lcdNumber.display(QDate.currentDate().toString(QString("dd-MM-yyyy")))

    @pyqtSlot()
    def serial_test(self):
        global Send_Print_Flag
        global serial_trigger_flag
        global serial_trigger_data
        global serial_data_buffer
        
        if(serial_trigger_flag==1):
            serial_trigger_flag=0
            #print('in main')
            print str(serial_trigger_data)
            #str1=list(serial_trigger_data)
            #print str1
            
    
        
def main():
    app = QtGui.QApplication(sys.argv)
    f = Ui_MainWindow()
    f.checkBox_10.setEnabled(False)
    f.checkBox_9.setEnabled(True)
    f.lineEdit_7.setEnabled(False)
    f.pushButton_22.setEnabled(False)
##    f.tabWidget.setTabEnabled(0, False)
##    f.tabWidget.setTabEnabled(1, False)
##    f.tabWidget.setTabEnabled(2, False)
##    f.tabWidget.setTabEnabled(3, False)
##    f.tabWidget.setTabEnabled(4, True)
##    f.tabWidget.setTabEnabled(5, False)
    timer = QTimer()
    timer.start(1000)   
    #========================= Time ==========================#
    f.lcdNumber_2.setDigitCount(8)
    f.connect(timer,SIGNAL("timeout()"),f,SLOT("showTime()"))
    #=========================================================#   
    #======================== Date ===========================#
    f.lcdNumber.setDigitCount(10)
    f.connect(timer,SIGNAL("timeout()"),f,SLOT("showData()"))
    #=========================================================#
    timer = QTimer()
    f.connect(timer,SIGNAL("timeout()"),f,SLOT("serial_test()"))
    timer.start(100)
    
   
    f.show()
    app.exec_()

    

    
if __name__ == '__main__':
     main()

        


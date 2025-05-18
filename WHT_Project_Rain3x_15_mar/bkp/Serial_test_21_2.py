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

global ser
global serial_port  
global serial_data
global serial_state
global serial_data_buffer
global serial_trigger_data
global window_state
global data_01
global data_02
global data_03
global data_05
global data_09
global data_10
global data_11
global data_12
global data_17
global data_19
global data_20
global index
global tester_model
global version
global test
global cable_no
global cable_name
global update_cable_no
global pass_count
global pass_1
global fail_1
global pass_count_1
global fail_count_1
global fail_count
global total_count
global Total
global cable_no_list



serial_port=0
rate=0
per=0
x=0
Tester_data=0
current_port=0
serial_state=0
serial_data=0
window_state=0
Send_Print_Flag=0
serial_trigger_flag=0
serial_data_buffer='\0'
File_handling_exception=0
index=0
data_01=0
data_02=0
data_03=0
data_05=0
data_09=0
data_10=0
data_11=0
data_12=0
data_17=0
data_19=0
data_20=0
tester_model=0
version=0
test=0
cable_no=0
cable_name=0
cable_no_list=0
update_cable_no=0
pass_count=0
pass_1=0
fail_1=0
pass_count_1=0
fail_count_1=0
fail_count=0
total_count=0
Total=0
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
ports = glob.glob('/dev/tty[A-Za-z]*')
ser=serial.Serial(ports[0])
x=serial_port.isOpen()
print x
#################################################################################################   
class Ui_MainWindow(QtGui.QMainWindow,wht.Ui_MainWindow):
    
    def __init__(self):
        super(Ui_MainWindow,self).__init__()
        self.setupUi(self)   

        global serial_trigger_data
        global serial_data
        global serial_state
        global serial_data_buffer
        global window_state
        global data_01
        global data_02
        global data_05
        global data_09
        global data_10
        global data_11
        global data_19
        global tester_model
        global version
        global test
        global cable_no
        global cable_name
        global cable_status
        global update_cable_no
        global pass_count
        global fail_count
        global pass_1
        global fail_1
        global pass_count_1
        global fail_count_1
        global total_count
        global cable_no_list
        
        
        try:
            thread.start_new_thread(self.serial_receive,())#started T_1
        except:
            print("threading Error")
            while 1:
                pass
            
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
        #self.comboBox_6.currentIndexChanged.connect(self.change_cable_no)
        #self.comboBox_6.setCurrentIndex(int(update_cable_no)-1)
        self.lineEdit_5.setText('device not connected')
     ##==================LOGIN TAB==================================##
        #self.pushButton_2.clicked.connect(self.btnLogin)        
     ##===============================================================##
     ##==================SETTING TAB==================================##
        self.pushButton_20.clicked.connect(self.btnConnect)
        self.pushButton_24.clicked.connect(self.btnEnter)
        self.pushButton_21.clicked.connect(self.btnDissconnect)  
     ##===============================================================##
     ##=======================BOARD TEST TAB==========================##
        self.checkBox_2.stateChanged.connect(self.CheckBoard)
        self.checkBox_4.stateChanged.connect(self.CheckContinuity)
        self.checkBox_5.stateChanged.connect(self.SelfTest)
        self.checkBox_6.stateChanged.connect(self.LearnHarness)
        self.checkBox_3.stateChanged.connect(self.ShowPoints)
        #self.checkBox_7.stateChanged.connect(self.GroupFile)
        #self.checkBox_8.stateChanged.connect(self.ShowGroupPoints)
     ##===============================================================##
     ##===============================================================##
        self.pushButton.clicked.connect(self.btnShutdown)
     ##===============================================================##
        self.w=QWidget()

        
        
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

##    def change_cable_no(self):
##        global cable_no_list
##        cable_no_list=self.comoBox_6.currentText()
##        print cable_no_list

    #def btnLogin(self):
        
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
        global index
        global data_01
        global data_02
        global data_05
        global data_09
        global data_10
        global data_11
        global data_12
        global data_17
        global data_19
        global index
        global tester_model
        global version
        global test
        global cable_no
        global cable_name
        global update_cable_no
        global pass_count
        global pass_1
        global fail_1
        global pass_count_1
        global fail_count_1
        global fail_count
        global total_count
        global Total
        global cable_no_list
        global data_20
        
        while True:
            state=0
            #serial_data=Trigger_port.read(1)
            serial_data=serial_port.readline()
            
            #print(serial_data)
            if len(serial_data)>0:
                if ('*' in serial_data):
                    if ('#' in serial_data):
                        ##-----------------##
                        if ('*01' in serial_data):
                            print('01 Command Received')
                            serial_port.write('*300101#')
                        if ('*02' in serial_data):
                            print('02 Command Received')
                            serial_port.write('*300101#')
                        if ('*03' in serial_data):
                            print('03 Command Received')
                            serial_port.write('*300101#')
                        if ('*04' in serial_data):
                            print('04 Command Received')
                            serial_port.write('*300101#')
                        if ('*05' in serial_data):
                            print('05 Command Received')
                            serial_port.write('*300101#')
                        if ('*06' in serial_data):
                            print('06 Command Received')
                            serial_port.write('*300101#')
                        if ('*07' in serial_data):
                            print('07 Command Received')
                            serial_port.write('*300101#')
                        if ('*08' in serial_data):
                            print('08 Command Received')
                            serial_port.write('*300101#')
                        if ('*09' in serial_data):
                            print('09 Command Received')
                            serial_port.write('*300101#')
                        if ('*10' in serial_data):
                            print('10 Command Received')
                            serial_port.write('*300101#')
                        if ('*11' in serial_data):
                            print('11 Command Received')
                            serial_port.write('*300101#')
                        if ('*12' in serial_data):
                            print('12 Command Received')
                            serial_port.write('*300101#')
                        if ('*13' in serial_data):
                            print('13 Command Received')
                            serial_port.write('*300101#')
                        if ('*14' in serial_data):
                            print('14 Command Received')
                            serial_port.write('*300101#')
                        if ('*15' in serial_data):
                            print('15 Command Received')
                            serial_port.write('*300101#')
                        if ('*16' in serial_data):
                            print('16 Command Received')
                            serial_port.write('*300101#')
                        if ('*17' in serial_data):
                            print('17 Command Received')
                            serial_port.write('*300101#')
                        if ('*18' in serial_data):
                            print('18 Command Received')
                            serial_port.write('*300101#')
                        if ('*19' in serial_data):
                            print('19 Command Received')
                            serial_port.write('*300101#')
                        if ('*20' in serial_data):
                            print('20 Command Received')
                            serial_port.write('*300101#')
                        if ('*21' in serial_data):
                            print('21 Command Received')
                            serial_port.write('*300101#')
                        if ('*22' in serial_data):
                            print('22 Command Received')
                            serial_port.write('*300101#')
                        if ('*23' in serial_data):
                            print('23 Command Received')
                            serial_port.write('*300101#')
                        if ('*24' in serial_data):
                            print('24 Command Received')
                            serial_port.write('*300101#')
                        if ('*25' in serial_data):
                            print('25 Command Received')
                            serial_port.write('*300101#')
                        if ('*26' in serial_data):
                            print('26 Command Received')
                            serial_port.write('*300101#')
                        if ('*28' in serial_data):
                            print('28 Command Received')
                            serial_port.write('*300101#')
                        if ('*29' in serial_data):
                            print('29 Command Received')
                            serial_port.write('*300101#')
                        if ('*30' in serial_data):
                            print('30 Command Received')
                            serial_port.write('*300101#')
                        if ('*31' in serial_data):
                            print('31 Command Received')
                            serial_port.write('*300101#')
                        if ('*32' in serial_data):
                            print('32 Command Received')
                            serial_port.write('*300101#')
                        if ('*33' in serial_data):
                            print('33 Command Received')
                            serial_port.write('*300101#')
                        if ('*34' in serial_data):
                            print('34 Command Received')
                            serial_port.write('*300101#')
                        if ('*35' in serial_data):
                            print('35 Command Received')
                            serial_port.write('*300101#')
                        if ('*36' in serial_data):
                            print('36 Command Received')
                            serial_port.write('*300101#')
                        if ('*37' in serial_data):
                            print('37 Command Received')
                            serial_port.write('*300101#')
                        if ('*38' in serial_data):
                            print('38 Command Received')
                            serial_port.write('*300101#')
                        if ('*39' in serial_data):
                            print('39 Command Received')
                            serial_port.write('*300101#')
                        if ('*40' in serial_data):
                            print('40 Command Received')
                            serial_port.write('*300101#')
                        if ('*41' in serial_data):
                            print('41 Command Received')
                            serial_port.write('*300101#')
                        if ('*42' in serial_data):
                            print('42 Command Received')
                            serial_port.write('*300101#')
                        if ('*43' in serial_data):
                            print('43 Command Received')
                            serial_port.write('*300101#')
                        ##-----------------##
                    
                print(serial_data)
    ##================================================================================##

    def btnConnect(self): 
        global ser
        global buff
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        count=0   
        serial_port.write('*010101#')
        print("transmit connection")

    def btnDissconnect(self):
        #ports = glob.glob('/dev/tty[A-Za-z]*')
        #print(ports)
        result = []
        for port in ports:
            print(port)
            try:        
                s = serial.Serial(port)
                s.close()
                print("port close")
                self.lineEdit_5.setText('device not connected')
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def btnEnter(self): 
        global ser
        global buff
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        count=0   
        serial_port.write('*060101#')
        print("transmit Enter")
    
    def CheckBoard(self):
        global ser
        global serial_port
        global serial_data
        global serial_state
        global serial_data_buffer
        global data_10
        
        if self.checkBox_2.isChecked():
            count=0   
            serial_port.write('*100101#')
            print("check_board")
            self.textEdit.setText(str(data_10))
        else:
            print "NOPE"
            self.textEdit.setText(' ')


    def ShowPoints(self):
        global ser
        global buff
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        global data_11

        if self.checkBox_3.isChecked():
            count=0   
            serial_port.write('*110101#')
            print("Learn_hrn")
            self.textEdit.setText(str(data_11))
        else:
            print "NOPE"
            self.textEdit.setText(' ')

    def CheckContinuity(self):
        global ser
        global serial_port
        global serial_data
        global serial_state
        global serial_data_buffer
        global data_12
        
        if self.checkBox_4.isChecked():
            count=0   
            serial_port.write('*120101#')
            print("check_continuity")
            self.textEdit.setText(str(data_12))
        else:
            print "NOPE"
            self.textEdit.setText(' ')


    def SelfTest(self):
        global ser
        global serial_port
        global serial_data
        global serial_state
        global serial_data_buffer
        global data_17
        
        if self.checkBox_5.isChecked():
            count=0   
            serial_port.write('*170101#')
            print("check_continuity")
            self.textEdit.setText(str(data_17))
        else:
            print "NOPE"
            self.textEdit.setText(' ')

    def LearnHarness(self):
        global ser
        global buff
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        global data_20

        if self.checkBox_6.isChecked():
            count=0   
            serial_port.write('*200101#')
            print("Learn_hrn")
            self.textEdit.setText(str(data_20))
        else:
            print "NOPE"
            self.textEdit.setText(' ')         
            
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
    global pass_count
    
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
    timer1 = QTimer()
    f.lcdNumber_2.setDigitCount(8)
    f.connect(timer1,SIGNAL("timeout()"),f,SLOT("showTime()"))
    timer1.start(1000)
    #=========================================================#   
    #======================== Date ===========================#
    timer2 = QTimer()
    f.lcdNumber.setDigitCount(10)
    f.connect(timer2,SIGNAL("timeout()"),f,SLOT("showData()"))
    timer2.start(1500)
    #====================== Serial_test ======================#
    f.connect(timer,SIGNAL("timeout()"),f,SLOT("serial_test()"))
    #=========================================================#
    f.showMaximized()
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Background,QtCore.Qt.white)
    f.setPalette(palette)
    s = QtGui.QGroupBox()
    s.setEnabled(True)
    f.show()
    app.exec_()

    

    
if __name__ == '__main__':
     main()

        


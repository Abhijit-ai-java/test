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
import threading
from colorama import Fore, Back, Style
import colorama

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
Tester_data=0
current_port=0
serial_state=0
serial_data=0
window_state=0
serial_trigger_flag=0
serial_data_buffer='\0'
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

ports = glob.glob('/dev/tty[A-Za-z]*')
##ser=serial.Serial(ports[0])
##x=serial_port.isOpen()
##print x
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
        self.comboBox_6.currentIndexChanged.connect(self.change_cable_no)
        self.lineEdit_5.setText('device not connected')
     ##=====================LOGIN TAB==================================##
        self.pushButton_2.clicked.connect(self.btnLogin)        
     ##================================================================##
     ##====================SETTING TAB=================================##
        self.pushButton_20.clicked.connect(self.btnConnect)
        self.pushButton_21.clicked.connect(self.btnDissconnect)
     ##================================================================##
    ##=======================MONITOR===================================##
        self.pushButton_24.clicked.connect(self.btnEnter)
        self.pushButton_4.clicked.connect(self.btSend)        
     ##===================BOARD TEST TAB===============================##
        #self.checkBox_2.stateChanged.connect(self.CheckBoard)
        #self.checkBox_4.stateChanged.connect(self.CheckContinuity)
        #self.checkBox_5.stateChanged.connect(self.SelfTest)
        #self.checkBox_6.stateChanged.connect(self.LearnHarness)
        #self.checkBox_3.stateChanged.connect(self.ShowPoints)
        #self.checkBox_7.stateChanged.connect(self.GroupFile)
        #self.checkBox_8.stateChanged.connect(self.ShowGroupPoints)
     ##================================================================##

     ##=====================TEACHING TAB===============================##
        #self.pushButton_27.clicked.connect(self.getfile)
     ##================================================================##
     ##=====================MAIN WINDOW================================##
        self.pushButton.clicked.connect(self.btnShutdown)
     ##================================================================##

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

    def change_cable_no(self):
        cable = self.comboBox_6.currentText()
        print cable

    def btnLogin(self):
        
        a = self.lineEdit.text()
        b = self.lineEdit_2.text()
        print a
        print b
        if (a=="ADMIN"):
            if (b == "1234"):
                print("Login successfully!!!!")
                QMessageBox.about(self.w,"About","Login Successfully")
                self.pushButton_2.setText('LOGOUT')
                self.lineEdit_2.clear()
                self.tabWidget.setCurrentIndex(3)
                self.tabWidget.setTabEnabled(0, True)
                self.tabWidget.setTabEnabled(1, True)
                self.tabWidget.setTabEnabled(2, True)
                self.tabWidget.setTabEnabled(3, True)
                self.tabWidget.setTabEnabled(4, True)
                self.tabWidget.setTabEnabled(5, True)

            else:
                print("Invalid User")
                self.lineEdit_2.clear()
                QMessageBox.about(self.w,"About","Invalid User")
                self.pushButton_2.setText('LOGIN')
                current_text = self.pushButton_2.text()
                print ''.format(current_text)
                self.tabWidget.setTabEnabled(0, False)
                self.tabWidget.setTabEnabled(1, False)
                self.tabWidget.setTabEnabled(2, False)
                self.tabWidget.setTabEnabled(3, False)
                self.tabWidget.setTabEnabled(4, True)
                self.tabWidget.setTabEnabled(5, False)

    def serial_receive(self):
        global serial_trigger_data
        global serial_data
        global serial_state
        global serial_data_buffer
        global window_state
        global serial_trigger_flag
        
        while True:
            state=0
            serial_data=serial_port.readline()
            if len(serial_data)>0:
                if ('*' in serial_data):
                    if ('#' in serial_data):
                        ##-----------------##
                        if ('*01' in serial_data):
                            print('01 Command Received')
                            self.cmd_01()
                            serial_port.write('*300101#')
                        elif ('*02' in serial_data):
                            print('02 Command Received')
                            self.cmd_02()
                            serial_port.write('*300101#')
                        elif ('*03' in serial_data):
                            print('03 Command Received')
                            self.cmd_03()
                            serial_port.write('*300101#')
                        elif ('*04' in serial_data):
                            print('04 Command Received')
                            serial_port.write('*300101#')
                        elif ('*05' in serial_data):
                            print('05 Command Received')
                            self.cmd_05()
                            serial_port.write('*300101#')
                        elif ('*06' in serial_data):
                            print('06 Command Received')
                            serial_port.write('*300101#')
                        elif ('*07' in serial_data):
                            print('07 Command Received')
                            serial_port.write('*300101#')
                        elif ('*08' in serial_data):
                            print('08 Command Received')
                            self.cmd_08()
                            serial_port.write('*300101#')
                        elif ('*09' in serial_data):
                            print('09 Command Received')
                            self.cmd_09()
                            serial_port.write('*300101#')
                        elif ('*10' in serial_data):
                            print('10 Command Received')
                            #self.CheckBoard()
                            serial_port.write('*300101#')
                        elif ('*11' in serial_data):
                            print('11 Command Received')
                            serial_port.write('*300101#')
                        elif ('*12' in serial_data):
                            print('12 Command Received')
                            serial_port.write('*300101#')
                        elif ('*13' in serial_data):
                            print('13 Command Received')
                            serial_port.write('*300101#')
                        elif ('*14' in serial_data):
                            print('14 Command Received')
                            serial_port.write('*300101#')
                        elif ('*15' in serial_data):
                            print('15 Command Received')
                            serial_port.write('*300101#')
                        elif ('*16' in serial_data):
                            print('16 Command Received')
                            serial_port.write('*300101#')
                        elif ('*17' in serial_data):
                            print('17 Command Received')
                            serial_port.write('*300101#')
                        elif ('*18' in serial_data):
                            print('18 Command Received')
                            serial_port.write('*300101#')
                        elif ('*19' in serial_data):
                            print('19 Command Received')
                            self.cmd_19()
                            serial_port.write('*300101#')
                        elif ('*20' in serial_data):
                            print('20 Command Received')
                            serial_port.write('*300101#')
                        elif ('*21' in serial_data):
                            print('21 Command Received')
                            serial_port.write('*300101#')
                        elif ('*22' in serial_data):
                            print('22 Command Received')
                            serial_port.write('*300101#')
                        elif ('*23' in serial_data):
                            print('23 Command Received')
                            serial_port.write('*300101#')
                        elif ('*24' in serial_data):
                            print('24 Command Received')
                            serial_port.write('*300101#')
                        elif ('*25' in serial_data):
                            print('25 Command Received')
                            serial_port.write('*300101#')
                        elif ('*26' in serial_data):
                            print('26 Command Received')
                            serial_port.write('*300101#')
                        elif ('*28' in serial_data):
                            print('28 Command Received')
                            serial_port.write('*300101#')
                        elif ('*29' in serial_data):
                            print('29 Command Received')
                            serial_port.write('*300101#')
                        elif ('*30' in serial_data):
                            print('30 Command Received')
                            serial_port.write('*300101#')
                        elif ('*31' in serial_data):
                            print('31 Command Received')
                            serial_port.write('*300101#')
                        elif ('*32' in serial_data):
                            print('32 Command Received')
                            serial_port.write('*300101#')
                        elif ('*33' in serial_data):
                            print('33 Command Received')
                            serial_port.write('*300101#')
                        elif ('*34' in serial_data):
                            print('34 Command Received')
                            serial_port.write('*300101#')
                        elif ('*35' in serial_data):
                            print('35 Command Received')
                            serial_port.write('*300101#')
                        elif ('*36' in serial_data):
                            print('36 Command Received')
                            serial_port.write('*300101#')
                        elif ('*37' in serial_data):
                            print('37 Command Received')
                            serial_port.write('*300101#')
                        elif ('*38' in serial_data):
                            print('38 Command Received')
                            serial_port.write('*300101#')
                        elif ('*39' in serial_data):
                            print('39 Command Received')
                            serial_port.write('*300101#')
                        elif ('*40' in serial_data):
                            print('40 Command Received')
                            serial_port.write('*300101#')
                        elif ('*41' in serial_data):
                            print('41 Command Received')
                            serial_port.write('*300101#')
                        elif ('*42' in serial_data):
                            print('42 Command Received')
                            self.cmd_42()
                            serial_port.write('*300101#')
                        elif ('*43' in serial_data):
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

        serial_port.write('*010101#')
        print("transmit connection")
    
    def btnDissconnect(self):
        result = []
        for port in ports:
            print(port)
            try:        
                serial_port = serial.Serial(port)
                serial_port.close()
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
        
        serial_port.write('*060101#')
        print("transmit Enter")

    def btSend(send):
        global ser
        global buff
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
 
        serial_port.write('*420101#')
        print("transmit operator")
        

##    def getfile(self):
##        global source_path
##        source_path='\0'
##        file_ext='*'
##        file_ext+=self.comboBox_16.currentText()       
##        fname = QFileDialog.getOpenFileName(self, 'Open file', '/media/usb0', str(file_ext))
##        
##        print(fname)
##        source_path=fname
##        print(source_path)
##
##        f = open(fname, 'r')
##        data = f.read()
##        print("file data")
##        print(data)
##        #self.plainTextEdit.setPlainText(data)
##        self.textEdit_2.setText(fname)
        
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
     ##--------------------Command Functions---------------------------##

    def cmd_01(self): ##-------Connect
        global serial_data
        
        length=len(serial_data)
                
        if(serial_data[length-2]=='1'):
            self.lineEdit_5.setText('device is connected')
        else:
            self.lineEdit_5.setText('device is Not connected')


    def cmd_02(self): ##-------Version And model
        global serial_data
        length=len(serial_data)
        model_ver=serial_data[5:length-1] #removing '#'
        #print(model_ver)
        
        seperation_len=model_ver.find('/')
        
        model=model_ver[0:seperation_len]#model seperation
        self.lineEdit_8.setText(model)
        version=model_ver[seperation_len+1:length]#version seperation
        self.lineEdit_9.setText(version)
        #print(model)
        #print(version)

    def cmd_03(self): ##-------cable_number_name
        global serial_data
        length=len(serial_data)
        cable_number_name=serial_data[5:length-1] #removing '#'
        #print(cable_number_name)
        
        seperation_len=cable_number_name.find('/')
        
        cable_number=cable_number_name[0:seperation_len]#number seperation
        cable_name=cable_number_name[seperation_len+1:length]#Name seperation
        self.lineEdit_11.setText(cable_name)
        #print(cable_number)
        #print(cable_name)
        combo_6=self.comboBox_6.addItem(cable_number)

    def cmd_05(self): ##-------Auto/mannual
        global serial_data
        
        length=len(serial_data)
                
        if(serial_data[length-2]=='0'):
            True #Auto
            #print("AUTO")
            self.pushButton_25.setText('AUTO')
        elif(serial_data[length-2]=='1'):
            True#Mannual
            #print("Mannual")
            self.pushButton_25.setText('MANNUAL')

    def cmd_06(self): ##-------Testing
        global serial_data

    def cmd_07(self): ##-------error code update
        global serial_data
        
    def cmd_08(self): ##-------Cable Status Update
        global serial_data
        length=len(serial_data)
        colourcode=serial_data[4]
        text=serial_data[5:length-1] # command and #removed
        print(text)
        if(colourcode=='1'):
            #blue Text
            self.lineEdit_13.setText(text)




                        
        elif(colourcode=='2'):
            #Red Text
            self.lineEdit_13.setText(text)
     
                       
        elif(colourcode=='3'):
            #green text
            self.lineEdit_13.setText(text)
            
                
    def cmd_09(self): ##-------Pass/Fail/Total Count
        global serial_data
        length=len(serial_data)
        pass_fail_count=serial_data[5:length-1] #removing '#'
        print pass_fail_count
        pass_count=int(pass_fail_count[0:5])
        fail_count=int(pass_fail_count[5:10])
        total_count= pass_count+fail_count
        #print (pass_count)
        #print (fail_count)
        #print (total_count)
        self.lineEdit_14.setText(str(pass_count))
        self.lineEdit_16.setText(str(fail_count))
        self.lineEdit_17.setText(str(total_count))
        self.lineEdit_20.setText(str(pass_count))
        self.lineEdit_25.setText(str(fail_count))

    def cmd_19(self): ##-------Cards status
        global serial_data
        length=len(serial_data)
        card_status=serial_data[5:length-1] #removing '#'
        print card_status
        self.lineEdit_10.setText(str(card_status))

    def cmd_42(self):
        global serial_data
        length=len(serial_data)
        print serial_data

##    def cmd_10(self): ##-------Check Board
##        global serial_data
##        length=len(serial_data)
##        check_board=serial_data[0:length-1] #removing '#'
##        print check_board
##        self.textEdit.setText(check_board)

##    def cmd_11(self): ##-------Showpoints
##        global serial_data
##        length=len(serial_data)

##    def cmd_12(self): ##-------Check Continuity
##        global serial_data
##        length=len(serial_data)
        
    ##---------------------END command function------------------------##
    
        
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

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

global ser
global serial_port  
global serial_data
global serial_state
global serial_data_buffer
global serial_trigger_data
global window_state
global self_test
global cmd
global cable_number
global savedata
global barcode_matching_flag


cmd=0
self_test=0
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
cable_number=0
savedata=0

barcode_matching_flag=0
#################################################################################################
serial_port = serial.Serial(
    port='/dev/ttyAMA0',
    #port='/dev/ttyUSB0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0.1
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
        self.lineEdit_3.hide()
        self.pushButton_4.setVisible(self.isVisible())
        global serial_trigger_data
        global serial_data
        global serial_state
        global serial_data_buffer
        global window_state
        global self_test
        global savedata
        global cmd
        
        
        try:
            thread.start_new_thread(self.serial_receive,())#started T_1
        except:
            print("threading Error")
            while 1:
                pass
            
        combo_7=self.comboBox_7.addItems([' ','Op-1','Op-2'])
        
        self.comboBox_7.currentIndexChanged.connect(self.operator)
        self.lineEdit_5.setText('device not connected')
     ##=====================LOGIN TAB==================================##
        self.pushButton_2.clicked.connect(self.btnLogin)        
     ##================================================================##
     ##====================SETTING TAB=================================##
        self.checkBox_9.stateChanged.connect(self.SerialCheckBox)
        self.pushButton_20.clicked.connect(self.btnConnect)
        self.pushButton_21.clicked.connect(self.btnDissconnect)
     ##================================================================##
    ##=======================MONITOR===================================##
        self.pushButton_24.clicked.connect(self.btnEnter)
        self.pushButton_25.clicked.connect(self.btnAutoMannual)
        self.pushButton_4.clicked.connect(self.btSend)
        self.comboBox_6.currentIndexChanged.connect(self.change_cable_no)
        self.checkBox_11.stateChanged.connect(self.Sample_Production)
     ##===================BOARD TEST TAB===============================##
        self.checkBox.stateChanged.connect(self.Stop)
        self.checkBox_2.stateChanged.connect(self.CheckBoard)
        self.checkBox_3.stateChanged.connect(self.ShowPoints)
        self.checkBox_4.stateChanged.connect(self.CheckContinuity)
        self.checkBox_5.stateChanged.connect(self.SelfTest)
        self.checkBox_6.stateChanged.connect(self.LearnHarness)   
        self.checkBox_7.stateChanged.connect(self.GroupFile)
        self.checkBox_8.stateChanged.connect(self.ShowGroupPoints)
        self.pushButton_3.clicked.connect(self.SaveFile)
     ##=====================TEACHING TAB===============================##
        self.checkBox_12.stateChanged.connect(self.Harness_parameter)
        self.checkBox_21.stateChanged.connect(self.CurrentTime)
        self.pushButton_26.clicked.connect(self.Create_setting_file)
        self.pushButton_5.clicked.connect(self.getfile)
        self.pushButton_27.clicked.connect(self.UsbBrowse)
        self.pushButton_28.clicked.connect(self.SendFile)
        self.pushButton_29.clicked.connect(self.SendTime)
        self.pushButton_7.clicked.connect(self.OK)
        
     ##================================================================##
     ##=====================MAIN WINDOW================================##
        self.pushButton.clicked.connect(self.btnShutdown)
     ##================================================================##

    def operator(self):
        combo=self.comboBox_7.currentText()
        print combo
        if(self.comboBox_7.currentText()==" "):
            self.lineEdit_3.hide()
            self.pushButton_4.hide()
            self.lineEdit_3.clear()
        elif(self.comboBox_7.currentText()=="Op-1"):
            self.lineEdit_3.setVisible(self.isVisible())
            self.pushButton_4.setVisible(self.isVisible())
            self.lineEdit_3.setFocus()
            
        elif(self.comboBox_7.currentText()=="Op-2"):
            self.lineEdit_3.setVisible(self.isVisible())
            self.pushButton_4.setVisible(self.isVisible())
            self.lineEdit_3.setFocus()

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
        global index
        global cmd
        
        while True:
            
           
           # if(cmd!=10):
                
            serial_data=serial_port.read()
            while(('*' in serial_data)==0):
                serial_data=serial_port.read()
            while(('#' in serial_data)==0):
                serial_data+=serial_port.read()
                
            
            if len(serial_data)>0:
                print("in Serial receive")
                print(serial_data)
                if (('*' in serial_data) & (cmd==0)):
                    #if ('#' in serial_data):
                        ##-----------------##
                    if ('*01' in serial_data):
                        print('01 Command Received')
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        cmd=1                                                  
                        
                    elif ('*02' in serial_data):
                        print('02 Command Received')
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        cmd=2
                    elif ('*03' in serial_data):
                        print('03 Command Received')
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        cmd=3
                    elif ('*04' in serial_data):
                        print('04 Command Received')
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        cmd=4
                    elif ('*05' in serial_data):
                        print('05 Command Received')
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        cmd=5
                    elif ('*06' in serial_data):
                        print('06 Command Received')
                        
                        cmd=6
                    elif ('*07' in serial_data):
                        print('07 Command Received')
                        cmd=7
                    elif ('*08' in serial_data):
                        print('08 Command Received')
##                            while(('#' in serial_data)==0):
##                                serial_data+=serial_port.read()
                        cmd=8
                    elif ('*09' in serial_data):
                        print('09 Command Received')
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        cmd=9
                    elif ('*10' in serial_data):
                        print('10 Command Received')
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        cmd=10
                    elif ('*11' in serial_data):
                        print('11 Command Received')
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        cmd=11
                    elif ('*12' in serial_data):
                        print('12 Command Received')
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        cmd=12
                        
                    elif ('*13' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        
                        cmd=13
                        
                    elif ('*14' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        
                        cmd=14
                    elif ('*15' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        
                        cmd=15
                    elif ('*16' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=16

                    elif ('*17' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=17

                    elif ('*18' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        
                        cmd=18

                    elif ('*19' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=19

                    elif ('*20' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                            
                        cmd=20
                    elif ('*21' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=21

                    elif ('*22' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=22

                    elif ('*23' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=23

                    elif ('*24' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=24

                    elif ('*25' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=25

                    elif ('*26' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=26

                    elif ('*28' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=28

                    elif ('*29' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=29

                    elif ('*30' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=30
        
                    elif ('*31' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=31
                   
                    elif ('*32' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=32

                        
                    elif ('*33' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=33

                      
                    elif ('*34' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=34

                       
                    elif ('*35' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=35

                        
                    elif ('*36' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()

                        cmd=36
                    elif ('*37' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        cmd=37

                      
                    elif ('*38' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        cmd=38
                       
                    elif ('*39' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        cmd=39
                      
                    elif ('*40' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        cmd=40
                       
                    elif ('*41' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        cmd=41
                        
                    elif ('*42' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        cmd=42
                      
                    elif ('*43' in serial_data):
##                        while(('#' in serial_data)==0):
##                            serial_data+=serial_port.readline()
                        cmd=43
                        
                    ##-----------------##
                
                    print(serial_data)
    ##================================================================================##
    def SerialCheckBox(self):
        if self.checkBox_9.isChecked():
            self.groupBox_2.setEnabled(True)
        else:
            self.groupBox_2.setEnabled(False)
    
    def btnConnect(self):
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
    
    def change_cable_no(self):
        cable_no=(self.comboBox_6.currentText())
        print(cable_no)
        
        serial_port.write('*2601' + str(cable_no) + '#')
        
        
    
    def btnEnter(self): 
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        
        serial_port.write('*060101#')
        print("transmit Enter")
        cmd=0

    def btnAutoMannual(self):
        global serial_port  
        global serial_data
        
        serial_port.write('*050101#')
        print("transmit Enter")

    def btSend(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer

        if(self.comboBox_7.currentText()=="Op-1"):
            Operator_data = str(self.lineEdit_3.text())
            Operator_1 = ('*420101#'+'#'+Operator_data+'#')
            serial_port.write(Operator_1)
            print("transmit operator_1")
        elif(self.comboBox_7.currentText()=="Op-2"):
            Operator_data = str(self.lineEdit_3.text())
            Operator_2 = ('*430101#'+'#'+Operator_data+'#')
            serial_port.write(Operator_2)
            print("transmit operator_2")
        
    def CheckBoard(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer

        if self.checkBox_2.isChecked():
            serial_port.write('*100101#')
            print("transmit ckeckboard data")
            self.checkBox_3.setEnabled(False)
            self.checkBox_4.setEnabled(False)
            self.checkBox_5.setEnabled(False)
            self.checkBox_6.setEnabled(False)
            self.checkBox_7.setEnabled(False)
            self.checkBox_8.setEnabled(False)
        else:
            self.textEdit.clear()
            self.checkBox_3.setEnabled(True)
            self.checkBox_4.setEnabled(True)
            self.checkBox_5.setEnabled(True)
            self.checkBox_6.setEnabled(True)
            self.checkBox_7.setEnabled(True)
            self.checkBox_8.setEnabled(True)
        
    def ShowPoints(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        
        if self.checkBox_3.isChecked():
            serial_port.write('*110101#')
            print("transmit showpoints data")
            self.checkBox_2.setEnabled(False)
            self.checkBox_4.setEnabled(False)
            self.checkBox_5.setEnabled(False)
            self.checkBox_6.setEnabled(False)
            self.checkBox_7.setEnabled(False)
            self.checkBox_8.setEnabled(False)
        else:
            self.textEdit.clear()
            self.checkBox_2.setEnabled(True)
            self.checkBox_4.setEnabled(True)
            self.checkBox_5.setEnabled(True)
            self.checkBox_6.setEnabled(True)
            self.checkBox_7.setEnabled(True)
            self.checkBox_8.setEnabled(True)
        
    def CheckContinuity(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer

        if self.checkBox_4.isChecked():
            serial_port.write('*120101#')
            print("transmit CheckContinuity data")
            self.checkBox_2.setEnabled(False)
            self.checkBox_3.setEnabled(False)
            self.checkBox_5.setEnabled(False)
            self.checkBox_6.setEnabled(False)
            self.checkBox_7.setEnabled(False)
            self.checkBox_8.setEnabled(False)
        else:
            self.textEdit.clear()
            self.checkBox_2.setEnabled(True)
            self.checkBox_3.setEnabled(True)
            self.checkBox_5.setEnabled(True)
            self.checkBox_6.setEnabled(True)
            self.checkBox_7.setEnabled(True)
            self.checkBox_8.setEnabled(True)
                    
    def SelfTest(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        global self_test
        
        if self.checkBox_5.isChecked():
            serial_port.write('*170101#')
            print("transmit selfTest data")
            self.checkBox_2.setEnabled(False)
            self.checkBox_3.setEnabled(False)
            self.checkBox_4.setEnabled(False)
            self.checkBox_6.setEnabled(False)
            self.checkBox_7.setEnabled(False)
            self.checkBox_8.setEnabled(False)
        else:
            self.textEdit.clear()
            self.checkBox_2.setEnabled(True)
            self.checkBox_3.setEnabled(True)
            self.checkBox_4.setEnabled(True)
            self.checkBox_6.setEnabled(True)
            self.checkBox_7.setEnabled(True)
            self.checkBox_8.setEnabled(True)

    def LearnHarness(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        global self_test
        
        if self.checkBox_6.isChecked():
            serial_port.write('*200101#')
            print("transmit harness data")
            self.checkBox_2.setEnabled(False)
            self.checkBox_3.setEnabled(False)
            self.checkBox_4.setEnabled(False)
            self.checkBox_5.setEnabled(False)
            self.checkBox_7.setEnabled(False)
            self.checkBox_8.setEnabled(False)
        else:
            self.textEdit.clear()
            self.checkBox_2.setEnabled(True)
            self.checkBox_3.setEnabled(True)
            self.checkBox_4.setEnabled(True)
            self.checkBox_5.setEnabled(True)
            self.checkBox_7.setEnabled(True)
            self.checkBox_8.setEnabled(True)

    def GroupFile(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        global self_test
        
        if self.checkBox_7.isChecked():
            self.checkBox_2.setEnabled(False)
            self.checkBox_3.setEnabled(False)
            self.checkBox_4.setEnabled(False)
            self.checkBox_5.setEnabled(False)
            self.checkBox_6.setEnabled(False)
            self.checkBox_8.setEnabled(False)
        else:
            self.textEdit.clear()
            self.checkBox_2.setEnabled(True)
            self.checkBox_3.setEnabled(True)
            self.checkBox_4.setEnabled(True)
            self.checkBox_5.setEnabled(True)
            self.checkBox_6.setEnabled(True)
            self.checkBox_8.setEnabled(True)

    def ShowGroupPoints(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        global self_test
        
        if self.checkBox_8.isChecked():
            serial_port.write('*360101#')
            print("transmit groupfile data")
            self.checkBox_2.setEnabled(False)
            self.checkBox_3.setEnabled(False)
            self.checkBox_4.setEnabled(False)
            self.checkBox_5.setEnabled(False)
            self.checkBox_6.setEnabled(False)
            self.checkBox_7.setEnabled(False)
        else:
            self.textEdit.clear()
            self.checkBox_2.setEnabled(True)
            self.checkBox_3.setEnabled(True)
            self.checkBox_4.setEnabled(True)
            self.checkBox_5.setEnabled(True)
            self.checkBox_6.setEnabled(True)
            self.checkBox_7.setEnabled(True)


    def Sample_Production(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        global self_test

        serial_port.write('*290101#')
        
        

    def SaveFile(self):
        
        read_data = str(self.textEdit.toPlainText())
        savefile = ("#"+read_data+"#")
        print savefile
        self.textEdit_3.setText(str(savefile))
             
    def Stop(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        global self_test
        
        if self.checkBox.isChecked():
            serial_port.write('*270101#')
            print("transmit data")
        else:
            self.textEdit.clear()

    def Harness_parameter(self):
        if self.checkBox_12.isChecked():
            serial_port.write('*280101#')
            print("transmit data")
            self.groupBox.setEnabled(True)
            print("group box enable")
        else:
            self.groupBox.setEnabled(False)
            print("group box disable")

    def SendTime(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer

        second = str(self.lineEdit_32.text())
        print second
        Minute = str(self.lineEdit_33.text())
        print Minute
        Hours = str(self.lineEdit_34.text())
        print Hours
        Weekday = str(self.lineEdit_35.text())
        print Weekday
        Days = str(self.lineEdit_36.text())
        print Days
        Months = str(self.lineEdit_37.text())
        print Months
        Years = str(self.lineEdit_38.text())
        print Years

        sending_time = ('*240101#'+'#'+second+Minute+Hours+Weekday+Days+Months+Years+'#')
        print sending_time
        serial_port.write(sending_time)
        print("transmit data")
        
    def CurrentTime(self):
        if self.checkBox_21.isChecked():
            serial_port.write('*310101#')
            print("transmit data")
            
                
    def UsbBrowse(self):
        self.tabWidget.hide()
        self.textEdit_3.show()
        self.lineEdit_6.show()       
        self.pushButton_5.show()
        self.pushButton_7.show() 
        
    def getfile(self):    
        
        file_ext=self.comboBox_16.currentText()
        if(file_ext=="Setting File"):
            file_ext='*.HS'

        elif(file_ext=="Harness File"):
             file_ext='*.HRN'

        elif(file_ext=="Lable File"):
             file_ext='*.LBL'

        elif(file_ext=="Group File"):
             file_ext='*.GRP'

        elif(file_ext=="Barcode1 File"):
             file_ext='*.BAR1'
            

        elif(file_ext=="Barcode2 File"):
             file_ext='*.BAR2'           

        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home/pi/Desktop', str(file_ext))

        if(fname==""):
            True
        else:
            print(fname)
            source_path=fname
            print(source_path)
            f = open(fname, 'r')
            data = f.read()
            print("file data")
            print(data)
            self.textEdit_3.setText(str(data))
                
    def SendFile(self):
        
        global savedata
        file_data=self.comboBox_16.currentText()
        if(file_data=="Setting File"):
            setting_file_data = ('*210101#'+str(savedata))
            print setting_file_data
            serial_port.write(setting_file_data)
            print("transmit setting data")

        elif(file_data=="Harness File"):
            Harness_file_data = ('*220101#'+str(savedata))
            print Harness_file_data
            serial_port.write(Harness_file_data)
            print("transmit harness data")
             

        elif(file_data=="Lable File"):
            Lable_file_data = ('*230101#'+str(savedata))
            print Lable_file_data
            serial_port.write(Lable_file_data)
            print("transmit Lable data")

        elif(file_data=="Group File"):
            Group_file_data = ('*330101#'+str(savedata))
            print Group_file_data
            serial_port.write(Group_file_data)
            print("transmit Group data")

        elif(file_data=="Barcode1 File"):
            Barcode_1_file_data = ('*38101#'+str(savedata))
            print Barcode_1_file_data
            serial_port.write(Barcode_1_file_data)
            print("transmit Barcode_1 data")
 
            

        elif(file_data=="Barcode2 File"):
            Barcode_2_file_data = ('*39101#'+str(savedata))
            print Barcode_2_file_data
            serial_port.write(Barcode_2_file_data)
            print("transmit Barcode_2 data")           
                
    def OK(self):
        global savedata
        self.tabWidget.show()
        self.lineEdit_6.hide()       
        self.pushButton_5.hide()
        self.pushButton_7.hide()
        self.textEdit_3.hide()

        read_text = str(self.textEdit_3.toPlainText())
        savedata = ('#' + read_text + '#')
        print savedata
        self.textEdit_3.clear()

    def Create_setting_file(self):
        
        cable_name = str(self.lineEdit_19.text())
        length=len(cable_name)
        if(length>16):
            self.lineEdit_19.clear()
        elif(length<16):
            for x in range(length, 16):
                cable_name+=' '
    
            
            
        #print cable_name
        
        if(self.comboBox_13.currentText()=="Mannual"):
            automannual='0'
            
        elif(self.comboBox_13.currentText()=="Auto"):
            automannual='1'
        #print automannual

        if(self.comboBox_8.currentText()=="On_Fail"):
            relay_1_setting='0'
            
        elif(self.comboBox_8.currentText()=="On_Pass"):
            relay_1_setting='1'
        #print relay_1_setting

        relay_1_time = str(self.lineEdit_22.text())
        if(len(relay_1_time)!=0):

            relay_1_time=int(relay_1_time)
            if(relay_1_time<=9):
                relay_1_time='0'+'0'+str(relay_1_time)
            elif(relay_1_time<=99):
                relay_1_time='0'+str(relay_1_time)
            elif(relay_1_time<=999):
                relay_1_time=str(relay_1_time)
            else:
                relay_1_time='000'
        else:
            relay_1_time='000'
              

        if(self.comboBox_9.currentText()=="On_Fail"):
            relay_2_setting='0'
            
        elif(self.comboBox_9.currentText()=="On_Pass"):
            relay_2_setting='1'
        #print relay_2_setting

        relay_2_time = str(self.lineEdit_23.text())
        #print relay_2_time
        if(len(relay_2_time)!=0):
            relay_2_time=int(relay_2_time)
            if(relay_2_time<=9):
                relay_2_time='0'+'0'+str(relay_2_time)
            elif(relay_2_time<=99):
                relay_2_time='0'+str(relay_2_time)
            elif(relay_2_time<=999):
                relay_2_time=str(relay_2_time)
            else:
                relay_2_time='000'
        else:
            relay_2_time='000'


        if(self.comboBox_10.currentText()=="On_Fail"):
            relay_3_setting='0'
            
        elif(self.comboBox_10.currentText()=="On_Pass"):
            relay_3_setting='1'
        #print relay_3_setting

        relay_3_time = str(self.lineEdit_24.text())
        #print relay_3_time
        if(len(relay_3_time)!=0):
            
            relay_3_time=int(relay_3_time)
            if(relay_3_time<=9):
                relay_3_time='0'+'0'+str(relay_3_time)
            elif(relay_3_time<=99):
                relay_3_time='0'+str(relay_3_time)
            elif(relay_3_time<=999):
                relay_3_time=str(relay_3_time)
            else:
                relay_3_time='000'
        else:
            relay_3_time='000'

        pass_count_receive = str(self.lineEdit_20.text())
        #print pass_count_receive
        if(len(pass_count_receive)!=0):
            pass_count_receive=int(pass_count_receive)
            if(pass_count_receive<=9):
                pass_count_receive='0'+'0'+'0'+'0'+str(pass_count_receive)
            elif(pass_count_receive<=99):
                pass_count_receive='0'+'0'+'0'+str(pass_count_receive)
            elif(pass_count_receive<=999):
                pass_count_receive='0' + '0' + str(pass_count_receive)
            elif(pass_count_receive<=9999):
                pass_count_receive='0' + str(pass_count_receive)
            elif(pass_count_receive<=99999):
                pass_count_receive=str(pass_count_receive)
            else:
                pass_count_receive='00000'
        else:
            pass_count_receive='00000'

        fail_count_receive = str(self.lineEdit_25.text())
        #print fail_count_receive
        if(len(fail_count_receive)!=0):
            fail_count_receive=int(fail_count_receive)
            if(fail_count_receive<=9):
                fail_count_receive='0'+'0'+'0'+'0'+str(fail_count_receive)
            elif(fail_count_receive<=99):
                fail_count_receive='0'+'0'+'0'+str(fail_count_receive)
            elif(fail_count_receive<=999):
                fail_count_receive='0' + '0' + str(fail_count_receive)
            elif(fail_count_receive<=9999):
                fail_count_receive='0' + str(fail_count_receive)
            elif(fail_count_receive<=99999):
                fail_count_receive=str(fail_count_receive)
            else:
                fail_count_receive='00000'
        else:
            fail_count_receive='00000'

        if(self.comboBox_11.currentText()=="No"):
            Label_printer='0'
            
        elif(self.comboBox_11.currentText()=="Yes"):
            Label_printer='1'
        #print Label_printer

        if(self.comboBox_14.currentText()=="No"):
            Barcode_scanner='0'
            
        elif(self.comboBox_14.currentText()=="Yes"):
            Barcode_scanner='1'
        #print Barcode_scanner

        if(self.comboBox_12.currentText()=="No"):
            Extra_point='0'
            
        elif(self.comboBox_12.currentText()=="Yes"):
            Extra_point='1'
        #print Extra_point

        if(self.comboBox_15.currentText()=="No"):
            Two_stage='0'
            
        elif(self.comboBox_15.currentText()=="Yes"):
            Two_stage='1'
        #print Two_stage

        if self.checkBox_13.isChecked():
            Cutter_module='1'
        else:
            Cutter_module='0'
        #print Cutter_module

        if self.checkBox_14.isChecked():
            Open_point_cut='1'
        else:
            Open_point_cut='0'
        #print Open_point_cut

        if self.checkBox_15.isChecked():
            Short_point_cut='1'
        else:
            Short_point_cut='0'
        #print Short_point_cut

        if self.checkBox_16.isChecked():
            Interchange_point='1'
        else:
            Interchange_point='0'
        #print Interchange_point

        if self.checkBox_17.isChecked():
            Extra_point_cut='1'
        else:
            Extra_point_cut='0'
        #print Extra_point_cut

        if self.checkBox_18.isChecked():
            Barcode_matching='1'
        else:
            Barcode_matching='0'
        #print Barcode_matching

        if self.checkBox_19.isChecked():
            Barcode_matching_single_double='1'
        else:
            Barcode_matching_single_double='0'
        #print Barcode_matching_single_double
            

        Open_point_cut_time = str(self.lineEdit_26.text())
        #print Open_point_cut_time
        if(len(Open_point_cut_time)!=0):
            Open_point_cut_time=int(Open_point_cut_time)
            if(Open_point_cut_time<=9):
                Open_point_cut_time='0'+str(Open_point_cut_time)
            elif(Open_point_cut_time<=99):
                Open_point_cut_time=str(Open_point_cut_time)
            else:
                Open_point_cut_time='00'
        else:
            Open_point_cut_time='00'

        Short_point_cut_time = str(self.lineEdit_27.text())
        #print Short_point_cut_time
        if(len(Short_point_cut_time)!=0):
            Short_point_cut_time=int(Short_point_cut_time)
            if(Short_point_cut_time<=9):
                Short_point_cut_time='0'+str(Short_point_cut_time)
            elif(Short_point_cut_time<=99):
                Short_point_cut_time=str(Short_point_cut_time)
            else:
                Short_point_cut_time='00'
        else:
            Short_point_cut_time='00'


        Interchange_point_time = str(self.lineEdit_28.text())
        #print Interchange_point_time
        if(len(Interchange_point_time)!=0):
            Interchange_point_time=int(Interchange_point_time)
            if(Interchange_point_time<=9):
                Interchange_point_time='0'+str(Interchange_point_time)
            elif(Interchange_point_time<=99):
                Interchange_point_time=str(Interchange_point_time)
            else:
                Interchange_point_time='00'
        else:
            Interchange_point_time='00'

        Extra_point_cut_time = str(self.lineEdit_29.text())
        #print Extra_point_cut_time
        if(len(Extra_point_cut_time)!=0):
            Extra_point_cut_time=int(Extra_point_cut_time)
            if(Extra_point_cut_time<=9):
                Extra_point_cut_time='0'+str(Extra_point_cut_time)
            elif(Extra_point_cut_time<=99):
                Extra_point_cut_time=str(Extra_point_cut_time)
            else:
                Extra_point_cut_time='00'
        else:
            Extra_point_cut_time='00'

        Barcode_1_length = str(self.lineEdit_21.text())
        #print Barcode_1_length
        if(len(Barcode_1_length)!=0):
            Barcode_1_length=int(Barcode_1_length)
            if(Barcode_1_length<=9):
                Barcode_1_length='0'+'0'+str(Barcode_1_length)
            elif(Barcode_1_length<=99):
                Barcode_1_length='0'+str(Barcode_1_length)
            elif(Barcode_1_length<=999):
                Barcode_1_length=str(Barcode_1_length)
            else:
                Barcode_1_length='000'
        else:
            Barcode_1_length='000'


        
        Barcode_2_length = str(self.lineEdit_30.text())
        #print Barcode_2_length
        if(len(Barcode_2_length)!=0):
            Barcode_2_length=int(Barcode_2_length)
            if(Barcode_2_length<=9):
                Barcode_2_length='0'+'0'+str(Barcode_2_length)
            elif(Barcode_2_length<=99):
                Barcode_2_length='0'+str(Barcode_2_length)
            elif(Barcode_2_length<=999):
                Barcode_2_length=str(Barcode_2_length)
            else:
                Barcode_2_length='000'
        else:
            Barcode_2_length='000'

        
        Setting_File = (cable_name+automannual+relay_1_setting+relay_1_time+relay_2_setting+relay_2_time+relay_3_setting+relay_3_time+pass_count_receive+fail_count_receive+Label_printer+Barcode_scanner+Extra_point+Cutter_module+Open_point_cut+Open_point_cut_time+Short_point_cut+Short_point_cut_time+Interchange_point+Interchange_point_time+Extra_point_cut+Extra_point_cut_time+Two_stage+Barcode_matching+Barcode_matching_single_double+Barcode_1_length+Barcode_2_length)
        print Setting_File
        self.textEdit_3.setText(str(Setting_File))
        
        
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
    @pyqtSlot()
    def Barcode_Read(self):
        
        global barcode_matching_flag
        #print("in barcode")
        barcode_data=self.lineEdit_12.text()
        ##print(barcode_data)
        if(barcode_matching_flag==1):
            if(len(barcode_data)>0):
                data='*370101#'+'#'+ (barcode_data) + '#'
                print(data)
                serial_port.write('*370101#'+'#'+ str(barcode_data) + '#')
                print('*370101#'+'#'+ str(barcode_data) + '#')
                barcode_matching_flag=0
                self.lineEdit_12.clear()
                
    @pyqtSlot()
    def cmd_execution(self):
        global cmd
        global serial_data
        global cable_number
        global barcode_matching_flag

        

        ##print("in cmd_execution slot")
        if(cmd!=0):
            if(cmd==1): ##-------Connect
        
                ##length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                        
                if(serial_data[length-2]=='1'):
                    self.lineEdit_5.setText('device is connected')
                else:
                    self.lineEdit_5.setText('device is Not connected')

                serial_port.write('*300101#')
                cmd=0

            elif(cmd==2): ##-------Version And model
                
                ##length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                model_ver=serial_data[5:length-1] #removing '#'
                #print(model_ver)
                
                seperation_len=model_ver.find('/')
                
                model=model_ver[0:seperation_len]#model seperation
                self.lineEdit_8.setText(model)
                version=model_ver[seperation_len+1:length]#version seperation
                self.lineEdit_9.setText(version)
                #print(model)
                #print(version)
                serial_port.write('*300101#')
                cmd=0
                
            elif(cmd==3): ##-------cable_number_name
                
                ##length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                cable_number_name=serial_data[5:length-1] #removing '#'
                #print(cable_number_name)
                
                seperation_len=cable_number_name.find('/')
                
                cable_number=cable_number_name[0:seperation_len]#number seperation
                #print(cable_number)
                cable_name=cable_number_name[seperation_len+1:length]#Name seperation
                self.lineEdit_11.setText(cable_name)  
                #print(cable_name)
                index = self.comboBox_6.findText(cable_number, QtCore.Qt.MatchFixedString)
                if index >= 0:
                    self.comboBox_6.setCurrentIndex(index)
                #combo_6=self.comboBox_6.addItem(cable_number)
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==4): ##-------operator code
                length=serial_data.find('#')
                length=length+1
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==5): ##-------Auto/mannual
                
                ##length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                if(serial_data[length-2]=='0'): #Auto
                    self.pushButton_25.setText('AUTO')
                elif(serial_data[length-2]=='1'):#Mannual
                    self.pushButton_25.setText('MANNUAL')
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==6): ##-------Testing
                length=serial_data.find('#')
                length=length+1
                    

                serial_port.write('*300101#')
                cmd=0

            elif(cmd==7): ##-------error code update
                length=serial_data.find('#')
                length=length+1
                
                serial_port.write('*300101#')
                cmd=0
            
            elif(cmd==8): ##-------Cable Status Update
                
                ##length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                colourcode=serial_data[4]
                text=serial_data[5:length-1] # command and #removed
                print(text)
                if(colourcode=='1'):
                    #blue Text
                    self.lineEdit_13.setText(text)
                    self.lineEdit_13.setStyleSheet("color: blue")
                                
                elif(colourcode=='2'):
                    #Red Text
                    self.lineEdit_13.setText(text)
                    self.lineEdit_13.setStyleSheet("color: red")         
                               
                elif(colourcode=='3'):
                    #green text
                    self.lineEdit_13.setText(text)
                    self.lineEdit_13.setStyleSheet("color: green")
                
                serial_port.write('*300101#')
                
                cmd=0
                    
            elif(cmd==9): ##-------Pass/Fail/Total Count
                
                ##length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                pass_fail_count=serial_data[5:length-1] #removing '#'
                print pass_fail_count
                pass_count=int(pass_fail_count[0:5])
                fail_count=int(pass_fail_count[5:10])
                total_count= pass_count+fail_count
                print (pass_count)
                print (fail_count)
                print (total_count)
                self.lineEdit_14.setText(str(pass_count))
                self.lineEdit_16.setText(str(fail_count))
                self.lineEdit_17.setText(str(total_count))
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==10): ##-------CheckBoard
                
                #length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                #print(serial_data)
                check_board=serial_data[5:length-1] #removing '#'
                #print check_board
                self.textEdit.setText(check_board)
                ##self.textEdit.setStyleSheet("color: blue")
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==11): ##-------show points
                
                ##length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
##                print(serial_data)
                show_points=serial_data[5:length]
                print show_points
                
                seperation_len=show_points.find('#')

                show_data=show_points[0:seperation_len]
                print show_data
                self.textEdit.setText(show_data)
                serial_port.write('*300101#')
                cmd=0
                
            elif(cmd==12): ##-------check continuity
                
                ##length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                print(serial_data)
                continuity=serial_data[5:length-1] #removing '#'
                print str(continuity)
                self.textEdit.setText(continuity)
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==17): ##-------self test
                
                #length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                self_test=serial_data[5:length-1] #removing '#'
                print str(self_test)
                self.textEdit.setText(self_test)
                serial_port.write('*300101#')
                cmd=0


            elif(cmd==19): ##-------Cards status
                
                #length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                card_status=serial_data[5:length-1] #removing '#'
                print card_status
                self.lineEdit_10.setText(str(card_status))
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==20): ##-------LearnHarness
##                length=serial_data.find('#')
##                length=length+1
                
                serial_data=serial_data[5:len(serial_data)]
                length=serial_data.find('#')
                learn_harness=serial_data[0:length]
                print learn_harness
                self.textEdit.setText(learn_harness)
                self.textEdit.setStyleSheet("color: blue")
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==24): ##--------send_time
                #length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                send_time=serial_data[5:length-1] #removing '#'
                print send_time
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==27): ##-------Stop
                
                #length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                stop=serial_data[5:length-1] #removing '#'
                print stop
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==28): ##-------setting file received from tester
                
                ##length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                received_setting_file=serial_data[5:length-1] #removing '#'
##                while True:
##                    True

                cable_name=received_setting_file[0:17]
                #print cable_name
                automannual=received_setting_file[17:18]
                #print automannual
                relay_1_setting=received_setting_file[18:19]
                #print relay_1_setting
                relay_1_time=received_setting_file[19:22]
                #print relay_1_time
                relay_2_setting=received_setting_file[22:23]
                #print relay_2_setting
                relay_2_time=received_setting_file[23:26]
                #print relay_2_time
                relay_3_setting=received_setting_file[26:27]
                #print relay_3_setting
                relay_3_time=received_setting_file[27:30]
                #print relay_3_time
                pass_count_receive=int(received_setting_file[30:35])
                #print pass_count_receive
                fail_count_receive=int(received_setting_file[35:40])
                #print fail_count_receive
                Label_printer=received_setting_file[40:41]
                #print Label_printer
                Barcode_scanner=received_setting_file[41:42]
                #print Barcode_scanner
                Extra_point=received_setting_file[42:43]
                #print Extra_point
                Cutter_module=received_setting_file[43:44]
                #print Cutter_module
                Open_point_cut=received_setting_file[44:45]
                #print Open_point_cut
                Open_point_cut_time=received_setting_file[45:47]
                #print Open_point_cut_time
                Short_point_cut=received_setting_file[47:48]
                #print Short_point_cut
                Short_point_cut_time=received_setting_file[48:50]
                #print Short_point_cut_time
                Interchange_point=received_setting_file[50:51]
                #print Interchange_point
                Interchange_point_time=received_setting_file[51:53]
                #print Interchange_point_time
                Extra_point_cut=received_setting_file[53:54]
                #print Extra_point_cut
                Extra_point_cut_time=received_setting_file[54:56]
                #print Extra_point_cut_time
                Two_stage=received_setting_file[56:57]
                #print Two_stage
                Barcode_matching=received_setting_file[57:58]
                #print Barcode_matching
                Barcode_matching_single_double=received_setting_file[58:59]
                #print Barcode_matching_single_double
                Barcode_1_length=received_setting_file[59:62]
                #print Barcode_1_length
                Barcode_2_length=received_setting_file[62:65]
                #print Barcode_2_length
##
                self.lineEdit_19.setText(cable_name)
##
                if(automannual=='0'): #MANNUAL
                    self.comboBox_13.setCurrentIndex(int(automannual))
                    ##index = self.comboBox_13.findText('Mannual', QtCore.Qt.MatchFixedString)
##                    if index >= 0:
##                        self.comboBox_13.setCurrentIndex(index)
                elif(automannual=='1'): #Auto
                    self.comboBox_13.setCurrentIndex(int(automannual))
                    ##index = self.comboBox_13.findText('Auto', QtCore.Qt.MatchFixedString)
##                    if index >= 0:
##                        self.comboBox_13.setCurrentIndex(index)

                if(relay_1_setting=='0'): #On_fail
                    self.comboBox_8.setCurrentIndex(int(relay_1_setting))
                    ##index = self.comboBox_8.findText('On_Fail', QtCore.Qt.MatchFixedString)
##                    if index >= 0:
##                        self.comboBox_8.setCurrentIndex(index)
                elif(relay_1_setting=='1'): #On_Pass
                    self.comboBox_8.setCurrentIndex(int(relay_1_setting))
##                    index = self.comboBox_8.findText('On_Pass', QtCore.Qt.MatchFixedString)
##                    if index >= 0:
##                        self.comboBox_8.setCurrentIndex(index)

                self.lineEdit_22.setText(relay_1_time)

                if(relay_2_setting=='0'): # On_fail
                    self.comboBox_9.setCurrentIndex(int(relay_2_setting))
##                    index = self.comboBox_9.findText('On_Fail', QtCore.Qt.MatchFixedString)
##                    if index >= 0:
##                        self.comboBox_9.setCurrentIndex(index)
                elif(relay_2_setting=='1'): #On_pass
                    self.comboBox_9.setCurrentIndex(int(relay_2_setting))
##                    index = self.comboBox_9.findText('On_Pass', QtCore.Qt.MatchFixedString)
##                    if index >= 0:
##                        self.comboBox_9.setCurrentIndex(index)

                self.lineEdit_23.setText(relay_2_time)

                if(relay_3_setting=='0'): #On_fail
                    self.comboBox_10.setCurrentIndex(int(relay_3_setting))
##                    index = self.comboBox_10.findText('On_Fail', QtCore.Qt.MatchFixedString)
##                    if index >= 0:
##                        self.comboBox_10.setCurrentIndex(index)
                elif(relay_3_setting=='1'): #On_pass
                    self.comboBox_10.setCurrentIndex(int(relay_3_setting))
##                    index = self.comboBox_10.findText('On_Pass', QtCore.Qt.MatchFixedString)
##                    if index >= 0:
##                        self.comboBox_10.setCurrentIndex(index)

                self.lineEdit_24.setText(relay_3_time)
                self.lineEdit_20.setText(str(pass_count_receive))
                self.lineEdit_25.setText(str(fail_count_receive))

                if(Label_printer=='0'): #No
                    self.comboBox_11.setCurrentIndex(int(Label_printer))
##                    index = self.comboBox_11.findText('No', QtCore.Qt.MatchFixedString)
##                    if index >= 0:
##                        self.comboBox_11.setCurrentIndex(index)

                elif(Label_printer=='1'): #Yes
                    self.comboBox_11.setCurrentIndex(int(Label_printer))
##                    index = self.comboBox_11.findText('Yes', QtCore.Qt.MatchFixedString)
##                    if index >= 0:
##                        self.comboBox_11.setCurrentIndex(index)

                if(Barcode_scanner=='0'): #No
                    self.comboBox_14.setCurrentIndex(int(Barcode_scanner))
##                    index = self.comboBox_14.findText('No', QtCore.Qt.MatchFixedString)
##                    if index >= 0:
##                        self.comboBox_14.setCurrentIndex(index)
                elif(Barcode_scanner=='1'): #Yes
                    self.comboBox_14.setCurrentIndex(int(Barcode_scanner))
##                    index = self.comboBox_14.findText('Yes', QtCore.Qt.MatchFixedString)
##                    if index >= 0:
##                        self.comboBox_14.setCurrentIndex(index)

                if(Extra_point=='0'): #No
                    self.comboBox_12.setCurrentIndex(int(Extra_point))
##                    index = self.comboBox_12.findText('No', QtCore.Qt.MatchFixedString)
##                    if index >= 0:
##                        self.comboBox_12.setCurrentIndex(index)
                elif(Extra_point=='1'): #Yes
                    self.comboBox_12.setCurrentIndex(int(Extra_point))
##                    index = self.comboBox_12.findText('Yes', QtCore.Qt.MatchFixedString)
##                    if index >= 0:
##                        self.comboBox_12.setCurrentIndex(index)

                if(Cutter_module=='0'): #No
                    self.checkBox_13.setChecked(False)
                elif(Cutter_module=='1'): #Yes
                    self.checkBox_13.setChecked(True)

                if(Open_point_cut=='0'): #No
                    self.checkBox_14.setChecked(False)
                elif(Open_point_cut=='1'): #Yes
                    self.checkBox_14.setChecked(True)

                if(Short_point_cut=='0'): #No
                    self.checkBox_15.setChecked(False)
                elif(Short_point_cut=='1'): #Yes
                    self.checkBox_15.setChecked(True)

                if(Interchange_point=='0'): #No
                    self.checkBox_16.setChecked(False)
                elif(Interchange_point=='1'): #Yes
                    self.checkBox_16.setChecked(True)

                if(Extra_point_cut=='0'): #No
                    self.checkBox_17.setChecked(False)
                elif(Extra_point_cut=='1'): #Yes
                    self.checkBox_17.setChecked(True)
                    
                    
                self.lineEdit_26.setText(Open_point_cut_time)
                self.lineEdit_27.setText(Short_point_cut_time)
                self.lineEdit_28.setText(Interchange_point_time)

                if(Two_stage=='0'): #No
                    self.comboBox_15.setCurrentIndex(int(Two_stage))
##                    index = self.comboBox_15.findText('No', QtCore.Qt.MatchFixedString)
##                    if index >= 0:
##                        self.comboBox_15.setCurrentIndex(index)
                elif(Two_stage=='1'): #Yes
                    self.comboBox_15.setCurrentIndex(int(Two_stage))
##                    index = self.comboBox_15.findText('Yes', QtCore.Qt.MatchFixedString)
##                    if index >= 0:
##                        self.comboBox_15.setCurrentIndex(index)

                if(Barcode_matching=='0'): #No
                    self.checkBox_18.setChecked(False)
                elif(Barcode_matching=='1'): #Yes
                    self.checkBox_18.setChecked(True)

                if(Barcode_matching_single_double=='0'): #No
                    self.checkBox_19.setChecked(False)
                elif(Barcode_matching_single_double=='1'): #Yes
                    self.checkBox_19.setChecked(True)

                
                self.lineEdit_29.setText(Extra_point_cut_time)
                self.lineEdit_21.setText(Barcode_1_length)
                self.lineEdit_30.setText(Barcode_2_length)                
                                
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==29): ##--------------Sample/production
                ##length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                sample_production=serial_data[5:length-1] #removing '#'
                print sample_production
                if(sample_production=='01'):
                    self.checkBox_11.setChecked(False)
                    self.lineEdit_7.setText('Sample')
                elif(sample_production=='00'):
                    self.checkBox_11.setChecked(True)
                    self.lineEdit_7.setText('Production')
                serial_port.write('*300101#')
                cmd=0
            elif(cmd==31): ##--------------Current_time             
                ##length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                print serial_data
                current_time=serial_data[5:length-1] #removing '#'
                print current_time

                Sec   = current_time[0:2]
                #print Sec
                self.lineEdit_32.setText(Sec)
                Min   = current_time[2:4]
                #print Min
                self.lineEdit_33.setText(Min)
                Hour  = current_time[4:6]
                #print Hour
                self.lineEdit_34.setText(Hour)
                Wd    = current_time[6:8]
                #print Wd
                self.lineEdit_35.setText(Wd)
                Day   = current_time[8:10]
                #print Day
                self.lineEdit_36.setText(Day)
                Month = current_time[10:12]
                #print Month
                self.lineEdit_37.setText(Month)
                Year  = current_time[12:14]
                #print Year
                self.lineEdit_38.setText(Year)
                
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==36): ##-------show group file
                serial_data=serial_data[5:len(serial_data)]
                length=serial_data.find('#')
                show_group_points=serial_data[0:length]
                print show_group_points
                self.textEdit.setText(show_group_points)
                #self.textEdit.setStyleSheet("color: blue")
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==40): ##-------barcode matching
                
                serial_data=serial_data[5:len(serial_data)]
                length=serial_data.find('#')
                barcode_matching_flag=1
                self.lineEdit_12.setFocus()
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==42): ##----------Operator_1
                
                ##length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                print serial_data
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==43): ##-----------Operator_2
                
                ##length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                print serial_data
                serial_port.write('*300101#')
                cmd=0
    
    ##---------------------END command function------------------------##

   
                
                
            
        
       
def main():
    app = QtGui.QApplication(sys.argv)
    f = Ui_MainWindow()
    f.checkBox_9.setEnabled(True)
    f.pushButton_5.hide()
    f.pushButton_7.hide()
    f.lineEdit_6.hide()
    f.textEdit_3.hide()
    f.textEdit.clear()
    
##    f.tabWidget.setTabEnabled(0, False)
##    f.tabWidget.setTabEnabled(1, False)
##    f.tabWidget.setTabEnabled(2, False)
##    f.tabWidget.setTabEnabled(3, False)
##    f.tabWidget.setTabEnabled(4, True)
##    f.tabWidget.setTabEnabled(5, False)
    f.textEdit.setStyleSheet("color: blue")
    f.textEdit_3.setStyleSheet("color: blue")
    f.groupBox.setEnabled(False)
    f.groupBox_2.setEnabled(False)
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
    #=========================================================#   
    #====================== Serial_test ======================#
    f.connect(timer,SIGNAL("timeout()"),f,SLOT("serial_test()"))
    #=========================================================#
    #======================== serial ===========================#
    timer3 = QTimer()
    
    f.connect(timer3,SIGNAL("timeout()"),f,SLOT("cmd_execution()"))
    timer3.start(0.010)
    #==========================================================#

    #======================== barcode_matching ===========================#
    timer4 = QTimer()
    
    f.connect(timer4,SIGNAL("timeout()"),f,SLOT("Barcode_Read()"))
    
    timer4.start(100)
    #======================================================================#

    
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

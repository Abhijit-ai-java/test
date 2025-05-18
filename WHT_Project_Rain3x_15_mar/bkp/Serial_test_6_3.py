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
global self_test
global cmd

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
        self.lineEdit_3.hide()
        self.pushButton_4.setVisible(self.isVisible())
        global serial_trigger_data
        global serial_data
        global serial_state
        global serial_data_buffer
        global window_state
        global self_test
        global cmd
        
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
        combo_2=self.comboBox_2.addItems(['9600','2400','4800','19200'])
        
        combo_3=self.comboBox_3.addItems(['None','Even','Odd'])
        combo_4=self.comboBox_4.addItems(['STOPBITS_ONE','None'])
        combo_5=self.comboBox_5.addItems(['EIGHT','SEVEN'])
        combo_7=self.comboBox_7.addItems([' ','Op-1','Op-2'])

        self.comboBox.currentIndexChanged.connect(self.test)
        self.comboBox_2.currentIndexChanged.connect(self.SelectBaudrate)
        self.comboBox_3.currentIndexChanged.connect(self.SelectParity)
        self.comboBox_4.currentIndexChanged.connect(self.SelectStopbit)
        self.comboBox_5.currentIndexChanged.connect(self.SelectDatabit)
        self.comboBox_6.currentIndexChanged.connect(self.change_cable_no)
        self.comboBox_7.currentIndexChanged.connect(self.operator)
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
        self.checkBox.stateChanged.connect(self.Stop)
        self.checkBox_2.stateChanged.connect(self.CheckBoard)
        self.checkBox_3.stateChanged.connect(self.ShowPoints)
        self.checkBox_4.stateChanged.connect(self.CheckContinuity)
        self.checkBox_5.stateChanged.connect(self.SelfTest)
        self.checkBox_6.stateChanged.connect(self.LearnHarness)   
        #self.checkBox_7.stateChanged.connect(self.GroupFile)
        #self.checkBox_8.stateChanged.connect(self.ShowGroupPoints)
     ##=====================TEACHING TAB===============================##
        self.checkBox_12.stateChanged.connect(self.Harness_parameter)
        self.pushButton_27.clicked.connect(self.getfile)
        
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

    def operator(self):
        combo=self.comboBox_7.currentText()
        print combo
        if(self.comboBox_7.currentText()==" "):
            self.lineEdit_3.hide()
            self.pushButton_4.hide()
        elif(self.comboBox_7.currentText()=="Op-1"):
            self.lineEdit_3.setVisible(self.isVisible())
            self.pushButton_4.setVisible(self.isVisible())
        elif(self.comboBox_7.currentText()=="Op-2"):
            self.lineEdit_3.setVisible(self.isVisible())
            self.pushButton_4.setVisible(self.isVisible())

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
        global cmd
        
        while True:
            if(cmd==0):
                
                serial_data=serial_port.readline()
                if len(serial_data)>0:
                    if ('*' in serial_data):
                        if ('#' in serial_data):
                            ##-----------------##
                            if ('*01' in serial_data):
                                
                                print('01 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=1
                                
                            elif ('*02' in serial_data):
                                print('02 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=2
                                
                            elif ('*03' in serial_data):
                                print('03 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=3
                                
                            elif ('*04' in serial_data):
                                print('04 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=4
                                
                            elif ('*05' in serial_data):
                                print('05 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=5
                                
                            elif ('*06' in serial_data):
                                print('06 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=6
                                
                            elif ('*07' in serial_data):
                                print('07 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=7
                                
                            elif ('*08' in serial_data):
                                print('08 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=8
                                
                            elif ('*09' in serial_data):
                                print('09 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=9
                                
                            elif ('*10' in serial_data):
                                print('10 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=10
                                                                
                            elif ('*11' in serial_data):
                                print('11 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=11
                                
                            elif ('*12' in serial_data):
                                print('12 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=12
                                
                            elif ('*13' in serial_data):
                                print('13 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=13
                                
                            elif ('*14' in serial_data):
                                print('14 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=14
                                
                            elif ('*15' in serial_data):
                                print('15 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=15
                                
                            elif ('*16' in serial_data):
                                print('16 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=16

                            elif ('*17' in serial_data):
                                print('17 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=17

                            elif ('*18' in serial_data):
                                print('18 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=18

                            elif ('*19' in serial_data):
                                print('19 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=19

                            elif ('*20' in serial_data):
                                print('20 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=20
                                
                            elif ('*21' in serial_data):
                                print('21 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=21

                            elif ('*22' in serial_data):
                                print('22 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=22

                            elif ('*23' in serial_data):
                                print('23 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=23

                            elif ('*24' in serial_data):
                                print('24 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=24

                            elif ('*25' in serial_data):
                                print('25 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=25

                            elif ('*26' in serial_data):
                                print('26 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=26

                            elif ('*28' in serial_data):
                                print('28 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=28

                            elif ('*29' in serial_data):
                                print('29 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=29

                            elif ('*30' in serial_data):
                                print('30 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=30
                
                            elif ('*31' in serial_data):
                                print('31 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=31
                           
                            elif ('*32' in serial_data):
                                print('32 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=32
                                
                            elif ('*33' in serial_data):
                                print('33 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=33
                              
                            elif ('*34' in serial_data):
                                print('34 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=34
                               
                            elif ('*35' in serial_data):
                                print('35 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=35
                                
                            elif ('*36' in serial_data):
                                print('36 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=36
                                
                            elif ('*37' in serial_data):
                                print('37 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=37
                              
                            elif ('*38' in serial_data):
                                print('38 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=38
                               
                            elif ('*39' in serial_data):
                                print('39 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=39
                              
                            elif ('*40' in serial_data):
                                print('40 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=40
                               
                            elif ('*41' in serial_data):
                                print('41 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=41
                                
                            elif ('*42' in serial_data):
                                print('42 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=42
                              
                            elif ('*43' in serial_data):
                                print('43 Command Received')
                                while(('#' in serial_data)==0):
                                    serial_data+=serial_port.readline()
                                cmd=43
                                
                            ##-----------------##
                        
                            print(serial_data)
    ##================================================================================##
    
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
    
    def btnEnter(self): 
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        
        serial_port.write('*060101#')
        print("transmit Enter")

    def btSend(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer

        if(self.comboBox_7.currentText()=="Op-1"):
            serial_port.write('*420101#')
            print("transmit operator_1")
        elif(self.comboBox_7.currentText()=="Op-2"):
            serial_port.write('*430101#')
            print("transmit operator_2")
        
    def CheckBoard(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer

        if self.checkBox_2.isChecked():
            serial_port.write('*100101#')
            print("transmit ckeckboard data") 
        else:
            self.textEdit.clear()
        
    def ShowPoints(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        
        if self.checkBox_3.isChecked():
            serial_port.write('*110101#')
            print("transmit showpoints data")
        else:
            self.textEdit.clear()
        
    def CheckContinuity(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer

        if self.checkBox_4.isChecked():
            serial_port.write('*120101#')
            print("transmit CheckContinuity data")
        else:
            self.textEdit.clear()
                    
    def SelfTest(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        global self_test
        
        if self.checkBox_5.isChecked():
            serial_port.write('*170101#')
            print("transmit selfTest data")
        else:
            self.textEdit.clear()

    def LearnHarness(self):
        global serial_port  
        global serial_data
        global serial_state
        global serial_data_buffer
        global self_test
        
        if self.checkBox_6.isChecked():
            serial_port.write('*200101#')
            print("transmit harness data")
        else:
            self.textEdit.clear()

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

    
        #if self.checkBox_2.isChecked():
            #self.textEdit.setText("CHECKED!")
        #else:
            #self.textEdit.setText("UNCHECKED!")

    def Harness_parameter(self):
        if self.checkBox_12.isChecked():
            serial_port.write('*280101#')
            print("transmit data")
        
    def getfile(self):
        global source_path
        source_path='\0'
        file_ext='*'
        file_ext+=self.comboBox_16.currentText()       
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/media/usb0', str(file_ext))
        
        print(fname)
        source_path=fname
        print(source_path)

        f = open(fname, 'r')
        data = f.read()
        print("file data")
        print(data)
        #self.plainTextEdit.setPlainText(data)
        self.textEdit_2.setText(fname)
        
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
    def cmd_execution(self):
        global cmd
        global serial_data

        ##print("in cmd_execution slot")
        if(cmd!=0):
            if(cmd==1): ##-------Connect
        
                length=len(serial_data)
                        
                if(serial_data[length-2]=='1'):
                    self.lineEdit_5.setText('device is connected')
                else:
                    self.lineEdit_5.setText('device is Not connected')

                serial_port.write('*300101#')
                cmd=0

            elif(cmd==2): ##-------Version And model
                
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
                serial_port.write('*300101#')
                cmd=0
                
            elif(cmd==3): ##-------cable_number_name
                
                length=len(serial_data)
                cable_number_name=serial_data[5:length-1] #removing '#'
                #print(cable_number_name)
                
                seperation_len=cable_number_name.find('/')
                
                cable_number=cable_number_name[0:seperation_len]#number seperation
                #print(cable_number)
                cable_name=cable_number_name[seperation_len+1:length]#Name seperation
                self.lineEdit_11.setText(cable_name)  
                #print(cable_name)
                combo_6=self.comboBox_6.addItem(cable_number)
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==4): ##-------operator code
                    

                    serial_port.write('*300101#')
                    cmd=0


            elif(cmd==5): ##-------Auto/mannual
                
                length=len(serial_data)
                        
                if(serial_data[length-2]=='0'): #Auto
                    self.pushButton_25.setText('AUTO')
                elif(serial_data[length-2]=='1'):#Mannual
                    self.pushButton_25.setText('MANNUAL')
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==6): ##-------Testing
                    

                serial_port.write('*300101#')
                cmd=0

            elif(cmd==7): ##-------error code update
                

                serial_port.write('*300101#')
                cmd=0
            
            elif(cmd==8): ##-------Cable Status Update
                
                length=len(serial_data)
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
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==10): ##-------CheckBoard
                
                #length=len(serial_data)
                length=serial_data.find('#')
                length=length+1
                print(serial_data)
                check_board=serial_data[5:length-1] #removing '#'
                print check_board
                self.textEdit.setText(check_board)
                self.textEdit.setStyleSheet("color: blue")
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==11): ##-------show points
                
                length=len(serial_data)
                print(serial_data)
                show_points=serial_data[5:length]
                print show_points
                
                seperation_len=show_points.find('#')

                show_data=show_points[0:seperation_len]
                print show_data
                self.textEdit.setText(show_data)
                serial_port.write('*300101#')
                cmd=0
                
            elif(cmd==12): ##-------check continuity
                
                length=len(serial_data)
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
                
                length=len(serial_data)
                card_status=serial_data[5:length-1] #removing '#'
                print card_status
                self.lineEdit_10.setText(str(card_status))
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==20): ##-------LearnHarness
                
                serial_data=serial_data[6:len(serial_data)]
                length=serial_data.find('#')
                learn_harness=serial_data[0:length]
                print learn_harness
                self.textEdit.setText(learn_harness)
                self.textEdit.setStyleSheet("color: blue")
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==27): ##-------Stop
                
                length=len(serial_data)
                stop=serial_data[5:length-1] #removing '#'
                print stop
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==28): ##-------setting file received from tester
                
                length=len(serial_data)
                received_setting_file=serial_data[5:length-1] #removing '#'
                
                print received_setting_file

                cable_name=received_setting_file[0:17]
                print cable_name
                automannual=received_setting_file[17:18]
                print automannual
                relay_1_setting=received_setting_file[18:19]
                print relay_1_setting
                relay_1_time=received_setting_file[19:22]
                print relay_1_time
                relay_2_setting=received_setting_file[22:23]
                print relay_2_setting
                relay_2_time=received_setting_file[23:26]
                print relay_2_time
                relay_3_setting=received_setting_file[26:27]
                print relay_3_setting
                relay_3_time=received_setting_file[27:30]
                print relay_3_time
                pass_count_receive=int(received_setting_file[30:35])
                print pass_count_receive
                fail_count_receive=int(received_setting_file[35:40])
                print fail_count_receive
                Label_printer=received_setting_file[40:41]
                print Label_printer
                Barcode_scanner=received_setting_file[41:42]
                print Barcode_scanner
                Extra_point=received_setting_file[42:43]
                print Extra_point
                Cutter_module=received_setting_file[43:44]
                print Cutter_module
                Open_point_cut=received_setting_file[44:45]
                print Open_point_cut
                Open_point_cut_time=received_setting_file[45:47]
                print Open_point_cut_time
                Short_point_cut=received_setting_file[47:48]
                print Short_point_cut
                Short_point_cut_time=received_setting_file[48:50]
                print Short_point_cut_time
                Interchange_point=received_setting_file[50:51]
                print Interchange_point
                Interchange_point_time=received_setting_file[51:53]
                print Interchange_point_time
                Extra_point_cut=received_setting_file[53:54]
                print Extra_point_cut
                Extra_point_cut_time=received_setting_file[54:56]
                print Extra_point_cut_time
                Two_stage=received_setting_file[56:57]
                print Two_stage
                Barcode_matching=received_setting_file[57:58]
                print Barcode_matching
                Barcode_matching_single_double=received_setting_file[58:59]
                print Barcode_matching_single_double
                Barcode_1_length=received_setting_file[59:62]
                print Barcode_1_length
                Barcode_2_length=received_setting_file[62:65]
                print Barcode_2_length
##
                self.lineEdit_19.setText(cable_name)
##
                if(received_setting_file[17:18]=='0'): #MANNUAL
                    combo_13=self.comboBox_13.addItems(["Mannual"])
                elif(received_setting_file[17:18]=='1'): #Auto
                    combo_13=self.comboBox_13.addItems(["Auto"])

                if(received_setting_file[18:19]=='0'): #On_fail
                    combo_8=self.comboBox_8.addItems(["On_Fail"])
                elif(received_setting_file[18:19]=='1'): #On_Pass
                    combo_8=self.comboBox_8.addItems(["On_Pass"])

                self.lineEdit_22.setText(relay_1_time)

                if(received_setting_file[22:23]=='0'): # On_fail
                    combo_9=self.comboBox_9.addItems(["On_Fail"])
                elif(received_setting_file[22:23]=='1'): #On_pass
                    combo_9=self.comboBox_9.addItems(["On_Pass"])

                self.lineEdit_23.setText(relay_2_time)

                if(received_setting_file[26:27]=='0'): #On_fail
                    combo_10=self.comboBox_10.addItems(["On_Fail"])
                elif(received_setting_file[22:23]=='1'): #On_pass
                    combo_10=self.comboBox_10.addItems(["On_Pass"])

                self.lineEdit_24.setText(relay_3_time)
                self.lineEdit_20.setText(str(pass_count_receive))
                self.lineEdit_25.setText(str(fail_count_receive))

                if(received_setting_file[40:41]=='0'): #No
                    combo_11=self.comboBox_11.addItems(["No"])
                elif(received_setting_file[40:41]=='1'): #Yes
                    combo_11=self.comboBox_11.addItems(["Yes"])

                if(received_setting_file[41:42]=='0'): #No
                    combo_14=self.comboBox_14.addItems(["No"])
                elif(received_setting_file[41:42]=='1'): #Yes
                    combo_14=self.comboBox_14.addItems(["Yes"])

                if(received_setting_file[42:43]=='0'): #No
                    combo_12=self.comboBox_12.addItems(["No"])
                elif(received_setting_file[42:43]=='1'): #Yes
                    combo_12=self.comboBox_12.addItems(["Yes"])

                if(received_setting_file[43:44]=='0'): #No
                    self.checkBox_13.setChaked(False)
                elif(received_setting_file[43:44]=='1'): #Yes
                    self.checkBox_13.setChecked(True)

                if(received_setting_file[44:45]=='0'): #No
                    self.checkBox_14.setChaked(False)
                elif(received_setting_file[43:44]=='1'): #Yes
                    self.checkBox_14.setChecked(True)

                if(received_setting_file[47:48]=='0'): #No
                    self.checkBox_15.setChaked(False)
                elif(received_setting_file[47:48]=='1'): #Yes
                    self.checkBox_15.setChecked(True)

                if(received_setting_file[50:51]=='0'): #No
                    self.checkBox_16.setChaked(False)
                elif(received_setting_file[50:51]=='1'): #Yes
                    self.checkBox_16.setChecked(True)

                if(received_setting_file[53:54]=='0'): #No
                    self.checkBox_17.setChaked(False)
                elif(received_setting_file[53:54]=='1'): #Yes
                    self.checkBox_17.setChecked(True)
                    
                    
                self.lineEdit_26.setText(Open_point_cut_time)
                self.lineEdit_27.setText(Short_point_cut_time)
                self.lineEdit_28.setText(Interchange_point_time)

                if(received_setting_file[56:57]=='0'): #No
                    combo_15=self.comboBox_15.addItems(["No"])
                elif(received_setting_file[56:57]=='1'): #Yes
                    combo_15=self.comboBox_15.addItems(["Yes"])

                if(received_setting_file[57:58]=='0'): #No
                    self.checkBox_18.setChaked(False)
                elif(received_setting_file[57:58]=='1'): #Yes
                    self.checkBox_18.setChecked(True)

                if(received_setting_file[58:59]=='0'): #No
                    self.checkBox_19.setChaked(False)
                elif(received_setting_file[58:59]=='1'): #Yes
                    self.checkBox_19.setChecked(True)

                
                self.lineEdit_29.setText(Extra_point_cut_time)
                self.lineEdit_21.setText(Barcode_1_length)
                self.lineEdit_30.setText(Barcode_2_length)
                
                
                                
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==42):
                
                length=len(serial_data)
                print serial_data
                serial_port.write('*300101#')
                cmd=0

            elif(cmd==43):
                
                length=len(serial_data)
                print serial_data
                serial_port.write('*300101#')
                cmd=0
    
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
    #=========================================================#   
    #====================== Serial_test ======================#
    f.connect(timer,SIGNAL("timeout()"),f,SLOT("serial_test()"))
    #=========================================================#
    #======================== serial ===========================#
    timer3 = QTimer()
    
    f.connect(timer3,SIGNAL("timeout()"),f,SLOT("cmd_execution()"))
    timer3.start(0.10)
    #==========================================================#

    
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

# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 14:34:07 2021

@author: Mike
"""

from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox

from PyQt5.QtWidgets import QTableWidgetItem
import sys
import os
import pandas as pd

from pymongo import MongoClient

# Local Path for compiler resources
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# User Interface
class Ui(QtWidgets.QDialog):

    def refreshList(self):
        try:
            #client = MongoClient("mongodb+srv://Mike:Atlantium@cluster0.xyexc.mongodb.net/<dbname>?retryWrites=true&w=majority")
            client = MongoClient("mongodb+srv://AtlantiumAdmin:AtlantiumDB@cluster0.xyexc.mongodb.net/<dbname>?retryWrites=true&w=majority")
            db = client.get_database('CalcUsers')
            records = db.Calculator            
            users = list(records.find({}))
            Data = pd.DataFrame(users)
            Data = Data[["UserName", "Password","Role","Expiration Date"]]
            
            self.UsersTable.setColumnCount(len(Data.columns))
            self.UsersTable.setRowCount(len(Data.index))
            
            for i in range(len(Data.index)):
                for j in range(len(Data.columns)):
                    self.UsersTable.setItem(i,j,QTableWidgetItem(str(Data.iloc[i, j])))
            
            self.UsersTable.setHorizontalHeaderLabels(Data.columns)
            self.UsersTable.verticalHeader().hide()
            self.UsersTable.setAlternatingRowColors(True)
            self.UsersTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.UsersTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            self.UsersTable.resizeRowsToContents()
            
            self.UsersTable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)            
            self.UsersTable.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
            self.UsersTable.setSortingEnabled(True)
        except:
            print("Could not connect to the DataBase")
    
    def closeEvent(self, event):
        self.close()
    
    def __init__(self):
        super(Ui, self).__init__()
        uic_path = resource_path("UserDatabase_v1.ui")        
        uic.loadUi(uic_path, self)
        self.setFixedSize(self.size())        
        # Connect UI elements
        self.AddUser.clicked.connect(addUserDialog)
        self.ChangeParameters.clicked.connect(changeUserData)
        self.RemoveUser.clicked.connect(removeUserDialog)
        self.Exit.clicked.connect(self.closeEvent)
        self.refreshList()
    
class addUserDialog(QtWidgets.QDialog):
    #adding some user
    
    def __init__(self):
        super(addUserDialog, self).__init__()
        AddUser_path = resource_path("AddUser.ui")        
        uic.loadUi(AddUser_path, self)
        
        self.AddUser.clicked.connect(self.handleUser)
        self.Cancel.clicked.connect(self.closeEvent)
        self.setFixedSize(self.size()) 
        self.dateEdit.setDateTime(QtCore.QDateTime.currentDateTime())
        
        self.exec_()
  
    def closeEvent(self, event):
        self.close()
        
    def handleUser(self, event):
        client = MongoClient("mongodb+srv://Mike:Atlantium@cluster0.xyexc.mongodb.net/<dbname>?retryWrites=true&w=majority")
        db = client.get_database('CalcUsers')
        collection = db.Calculator
        
        isduplicate = list(collection.find({"UserName":str(self.UserName.text())}))
        if len(isduplicate)>0:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("This UserName allready exists")
            msgBox.setWindowTitle("Error")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec()
        elif (self.UserName.text()=="") or (self.UserPassword.text()==""): # No Username/Pass entered
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("Please ener valid Username and Password")
            msgBox.setWindowTitle("Error")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec()
        else:        
            user = {
                "UserName":str(self.UserName.text()),
                "Password":str(self.UserPassword.text()),
                "Role":str(self.UserRole.currentText()),
                "Expiration Date":self.dateEdit.date().toString("dd-MMM-yyyy")
                }
            collection.insert_one(user)
            window.refreshList()
            self.close()

class changeUserData(QtWidgets.QDialog):
    #changing user data entry    
    
    def __init__(self):
        global olduser
        Role = {"Marketing":0,
                "Developer":1,
                "Admin":2}
        
        super(changeUserData, self).__init__()
        ChangeUser_path = resource_path("UpdateUser.ui")        
        uic.loadUi(ChangeUser_path, self)

        self.UpdateUser.clicked.connect(self.handleUser)
        self.Cancel.clicked.connect(self.closeEvent)
        self.setFixedSize(self.size())
        
        if len(window.UsersTable.selectedItems())>0: #if row selected
           self.UserName.setText(window.UsersTable.selectedItems()[0].text())
           self.UserPassword.setText(window.UsersTable.selectedItems()[1].text())           
           self.UserRole.setCurrentIndex(int(Role[window.UsersTable.selectedItems()[2].text()]))
           self.dateEdit.setDate(QtCore.QDate.fromString(window.UsersTable.selectedItems()[3].text()))
           olduser = {"UserName":str(self.UserName.text())}
           self.exec_()
        else:
           msgBox = QMessageBox()
           msgBox.setIcon(QMessageBox.Information)
           msgBox.setText("No User selected")
           msgBox.setWindowTitle("Error")
           msgBox.setStandardButtons(QMessageBox.Ok)
           msgBox.exec()
        
    def closeEvent(self, event):
        self.close()
        
    def handleUser(self, event):        
        client = MongoClient("mongodb+srv://Mike:Atlantium@cluster0.xyexc.mongodb.net/<dbname>?retryWrites=true&w=majority")
        db = client.get_database('CalcUsers')
        collection = db.Calculator        
        
        isduplicate = list(collection.find({"UserName":str(self.UserName.text())}))
        if (len(isduplicate)>0) and (olduser['UserName']!=self.UserName.text()):
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("This UserName allready exists")
            msgBox.setWindowTitle("Error")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec()
        elif (self.UserName.text()=="") or (self.UserPassword.text()==""): # No Username/Pass entered
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("Please ener valid Username and Password")
            msgBox.setWindowTitle("Error")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec()
        else:        
            user = {
                "UserName":str(self.UserName.text()),
                "Password":str(self.UserPassword.text()),
                "Role":str(self.UserRole.currentText()),
                "Expiration Date":self.dateEdit.date().toString("dd-MMM-yyyy")
                }
            newuser = { "$set": user }
            collection.update_one(olduser,newuser,True)
            window.refreshList()
            self.close()

def removeUserDialog(self):
   msgBox = QMessageBox()
   msgBox.setIcon(QMessageBox.Information)
   msgBox.setText("Are you sure?")
   msgBox.setWindowTitle("Removing User")
   msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
   
   returnValue = msgBox.exec()
   if returnValue == QMessageBox.Yes:
       client = MongoClient("mongodb+srv://Mike:Atlantium@cluster0.xyexc.mongodb.net/<dbname>?retryWrites=true&w=majority")
       db = client.get_database('CalcUsers')
       collection = db.Calculator
       
       if len(window.UsersTable.selectedItems())>0: #if row selected
           collection.delete_one( { "UserName" : window.UsersTable.selectedItems()[0].text() } );
           window.refreshList()
       else:
           msgBox = QMessageBox()
           msgBox.setIcon(QMessageBox.Information)
           msgBox.setText("No User selected")
           msgBox.setWindowTitle("Error")
           msgBox.setStandardButtons(QMessageBox.Ok)
           msgBox.exec()

if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)        

    window = Ui()    
    window.show()
    sys.exit(app.exec_())
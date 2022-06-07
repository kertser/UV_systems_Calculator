#%%
"""
Calculator - Version 11.11 (04.04.2022)
Modifications:
    - Added the hidden D1-Log in Marketing version
"""
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget
from PyQt5.QtWidgets import QTreeWidgetItem, QInputDialog
import sys
import os
import config
from re import findall
from math import exp as exp
from pymongo import MongoClient
from datetime import datetime

# Global Variables Definition
ValidInput = True # Defines whether the input values are valid

# Local Path for compiler resources
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Login User Interface
class Login(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.setWindowTitle("Enter Login and Password")
        self.setFixedSize(260, 100)
        self.setWhatsThis("Login and Password - Atlantium Calculator")
        self.textName = QtWidgets.QLineEdit(self)
        self.textPass = QtWidgets.QLineEdit(self)
        self.textPass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.buttonLogin = QtWidgets.QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        #self.closeButton.clicked.connect(self.closeIt)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.textName)
        layout.addWidget(self.textPass)
        layout.addWidget(self.buttonLogin)

    def handleLogin(self):
        #Connect to Atlantium MongoDB with usernames
        #client = MongoClient("mongodb+srv://Mike:Atlantium@cluster0.xyexc.mongodb.net/<dbname>?retryWrites=true&w=majority")
        client = MongoClient("mongodb+srv://CalcUser:CalcUser@cluster0.xyexc.mongodb.net/<dbname>?retryWrites=true&w=majority")
        db = client.get_database('CalcUsers')
        records = db.Calculator

        try:
            user = list(records.find({'UserName':self.textName.text()}))
            #uname = user[0].get('UserName')
            pwd = user[0].get('Password')
            expDate = user[0].get('Expiration Date')
            today = datetime.now().strftime("%d-%b-%Y")
            datetime.strptime(today, "%d-%b-%Y").date()
            datetime.strptime(expDate, "%d-%b-%Y").date()
            #
            role = user[0].get('Role')

            if role == 'Marketing':
                config.CalculatorType = 'Marketing'                
            elif role == 'Developer' or role == 'Admin':
                config.CalculatorType = 'Developer'

            if (self.textPass.text() == pwd):
                #Check for exiration date:
                if (datetime.strptime(today, "%d-%b-%Y").date())>(datetime.strptime(expDate, "%d-%b-%Y").date()):
                    QtWidgets.QMessageBox.warning(self, 'Error', 'Password Date Expired')
                else:
                    self.accept()
            else:
                QtWidgets.QMessageBox.warning(self, 'Error', 'Wrong Password')
        except:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Wrong Login Name')

    def closeEvent(self, event):
        event.accept()

# User Interface
class Ui(QtWidgets.QDialog):
    def __init__(self):
        super(Ui, self).__init__()
        uic_path = resource_path("Calculator_UI.ui")
        uic.loadUi(uic_path, self)

        # Connect the radio buttons
        self.FullRangeRED.clicked.connect(FullRanged)
        self.EPA.clicked.connect(EPA)
        #self.PMO.clicked.connect(PMO)
        self.Dechlorination.clicked.connect(Dechlorination)

        # Connect Hg regular, OF and VUV factors
        self.HgUV.clicked.connect(LampFactor_Reg)
        self.HgOF.clicked.connect(LampFactor_OF)
        self.HgVUV.clicked.connect(LampFactor_VUV)

        self.OzoneIn.setText(str(config.OzoneIn))
        self.ChlorineIn.setText(str(config.ChlorineIn))
        self.OzoneOut.setText(str(config.OzoneOut))
        self.ChlorineOut.setText(str(config.ChlorineOut))

        # Connect the vertical option checkbox
        self.vertical.clicked.connect(UVModel)

        # Connect the rest of the UI elements
        self.LampEfficiency.setText(str(config.LampEfficiency))
        self.LampEfficiency.setAlignment(QtCore.Qt.AlignCenter)
        self.LampEfficiency.textChanged.connect(LampEfficiency)

        self.Power.setText(str(config.Drive))
        self.Power.setAlignment(QtCore.Qt.AlignCenter)
        self.Power.textChanged.connect(Power)

        self.UVT.setText(str(config.UVT))
        self.UVT.setAlignment(QtCore.Qt.AlignCenter)
        self.UVT.textChanged.connect(UVT)

        # creating a blur effect for Graphs
        
        self.ge0 = QtWidgets.QGraphicsBlurEffect()
        self.GraphBox.setGraphicsEffect(self.ge0)
        self.ge0.setBlurRadius(5)
    
        self.UVT215.setText(str(config.UVT215))
        #self.UVT215.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.UVT215.setAlignment(QtCore.Qt.AlignCenter)
        #self.UVT.textChanged.connect(UVT215)
        
        # Disable in Marketing version

        #self.PMO.setEnabled(False) #Marketing
        self.EPA.setEnabled(True) #Marketing
        self.Dechlorination.setEnabled(True)
        self.FullRangeRED.setEnabled(True)
        self.EPA.setChecked(True)

        if config.CalculatorType == 'Developer':
            config.UV_Systems = config.ValidatedDoseFamilies
        else:
            config.UV_Systems = config.MunicipalFamilies

        # Hide UVT215 and Graphs in Marketing version
        self.UVT215.setVisible(False)
        self.UVT215units.setVisible(False)
        self.UVT215Label.setVisible(False)

        # Hide D1Log in Marketing Version         
        self.D1Log.setEnabled(False)
        #self.Pathogens_Table.setEnabled(False)

        self.HgOF.setEnabled(False)
        self.HgVUV.setEnabled(False)

        self.ge1 = QtWidgets.QGraphicsBlurEffect()
        self.UVT215Label.setGraphicsEffect(self.ge1)
        self.ge1.setBlurRadius(5)

        self.ge2 = QtWidgets.QGraphicsBlurEffect()
        self.UVT215.setGraphicsEffect(self.ge2)
        self.ge2.setBlurRadius(5)

        self.ge3 = QtWidgets.QGraphicsBlurEffect()
        self.UVT215units.setGraphicsEffect(self.ge3)
        self.ge3.setBlurRadius(5)

        self.UVT215.setVisible(True)
        self.UVT215units.setVisible(True)
        self.UVT215Label.setVisible(True)

        self.FlowRate.setText(str(config.FlowRate_m3h))
        self.FlowRate.setAlignment(QtCore.Qt.AlignCenter)
        self.FlowRate.textChanged.connect(FlowRate)

        self.UVBranches.setText(str(config.nBranches))
        self.UVBranches.setAlignment(QtCore.Qt.AlignCenter)
        self.UVBranches.textChanged.connect(UVBranches)

        self.ResetCalc.clicked.connect(resetCalc)
        self.FlowDoseCalc.clicked.connect(FlowForDose)

        self.FlowUnits.currentIndexChanged.connect(FlowUnits)
        self.PressureUnits.currentIndexChanged.connect(PressureUnits)

        self.UVSystem.addItems(config.UV_Systems)
        self.UVModel.addItems(config.Modules)

        self.UVSystem.currentIndexChanged.connect(UVSystem)
        self.UVModel.currentIndexChanged.connect(UVModel)

        self.DisplayTree.clicked.connect(TreeView)
        self.DisplayTable.clicked.connect(TableView)
        self.FullTable.clicked.connect(FullTable)
        self.ResetPathogen.clicked.connect(ResetPathogen)

        self.Pathogens.itemClicked.connect(SelectPathogen)
        self.LogReductionTable.itemClicked.connect(SelectFromTable)
        self.D1Log.textChanged.connect(D1LogManual)

        self.OzoneIn.textChanged.connect(DechloCalc)
        self.ChlorineIn.textChanged.connect(DechloCalc)

        #Developer or Marketing
        self.Developer.clicked.connect(Developer)
        self.Marketing.clicked.connect(Marketing)

        #Plots
        self.PlotRedUVT.clicked.connect(PlotREDvsUVT)
        self.PlotRedFlow.clicked.connect(PlotREDvsFlow)
        self.PlotRedPower.clicked.connect(PlotREDvsDrive)

        #Sliders
        self.LampEffSlider.setValue(int(config.LampEfficiency))
        self.LampEffSlider.setMinimum(0)
        self.LampEffSlider.setMaximum(100)
        self.LampEffSlider.valueChanged.connect(LampEfficiencySlider)

        self.PowerSlider.setValue(int(config.Drive))
        self.PowerSlider.setMinimum(0)
        self.PowerSlider.setMaximum(100)
        self.PowerSlider.valueChanged.connect(PowerSlider)

        self.UVT254Slider.setValue(int(config.UVT))
        self.UVT254Slider.setMinimum(config.minUVT)
        self.UVT254Slider.setMaximum(config.maxUVT)
        self.UVT254Slider.valueChanged.connect(UVT254Slider)

        self.FlowSlider.setValue(int(config.FlowRate_m3h))
        self.FlowSlider.setMinimum(config.minFlow)
        self.FlowSlider.setMaximum(config.maxFlow)
        self.FlowSlider.valueChanged.connect(FlowSlider)

        self.setFixedSize(self.size())
        

        if config.CalculatorType == 'Developer':

            self.PlotRedUVT.setEnabled(True)
            self.PlotRedFlow.setEnabled(True)
            self.PlotRedPower.setEnabled(True)

            self.D1Log.setEnabled(True)
            self.Pathogens_Table.setEnabled(True)

            self.ge0.setEnabled(False)
            self.ge1.setEnabled(False)
            self.ge2.setEnabled(False)
            self.ge3.setEnabled(False)
            
            # Enable EPA/PMO and Dechlorination in Developer version
            self.EPA.setEnabled(True)
            #self.PMO.setEnabled(True)
            self.Dechlorination.setEnabled(True)

            self.FullRangeRED.setEnabled(True)
            self.FullRangeRED.setChecked(True)
            

#%% Data table load - pathogens

        Data = config.KillData[['Microbial Type',1,2,3]]

        self.LogReductionTable.setColumnCount(len(Data.columns))
        self.LogReductionTable.setRowCount(len(Data.index))
        for i in range(len(Data.index)):
            for j in range(len(Data.columns)):
                self.LogReductionTable.setItem(i,j,QTableWidgetItem(str(Data.iloc[i, j])))

        self.LogReductionTable.setHorizontalHeaderLabels(['Pathogen Type', '1-Log','2-Log','3-log'])

        self.LogReductionTable.verticalHeader().hide()
        self.LogReductionTable.setAlternatingRowColors(True)
        self.LogReductionTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.LogReductionTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.LogReductionTable.resizeRowsToContents()

        self.LogReductionTable.setVisible(False) # Hide by default

        # Reset Pathogen to Default Values
        self.SelectedPathogen.setText(config.SelectedPathogen)
        self.SelectedPathogen.setAlignment(QtCore.Qt.AlignLeft)
        self.D1Log.blockSignals(True)
        self.D1Log.setText(str(config.DefaultD1Log))
        self.D1Log.blockSignals(False)

        #%% Tree-Widget for pathogens

        PTree=[]
        PathogenTypes = config.KillData['Type'].unique().tolist()
        for pat in PathogenTypes:
            PTree.append(QTreeWidgetItem([pat]))


            for i in range(len(config.KillData[config.KillData['Type']==pat].iloc[:,0:2])):
                child1 = QTreeWidgetItem(list(map(str,config.KillData[config.KillData['Type']==pat].iloc[i,0:2])))
                PTree[len(PTree)-1].addChild(child1)

        self.Pathogens.setColumnCount(2)
        self.Pathogens.setHeaderLabels(["Pathogen Type", "1-Log Dose [mJ/cm²]"])

        for i in range(0,len(PTree)):
            self.Pathogens.addTopLevelItem(PTree[i])

        self.Pathogens.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

#%% End of constructed elements

    def keyPressEvent(self, qKeyEvent): #Reacts to Enter button
        #print(qKeyEvent.key())
        if (qKeyEvent.key() == QtCore.Qt.Key_Return) | (qKeyEvent.key() == QtCore.Qt.Key_Enter):
            #UVSystem()
            recalculate
        else:
            super().keyPressEvent(qKeyEvent)

# =============================================================================
#     Connected Logics
# =============================================================================

def roundup(number,n): # for minimum flow
    return round(number+0.5,n)

def rounddn(number,n): # for maximum flow
    return round(number-0.5,n)

def recalculate():

    if window.Dechlorination.isChecked(): #If dechlorination is available
        DechloCalc()

    if window.UVSystem.currentText() == 'R-200':
        from R200_SDL import RED as RED
        from R200_SDL import HeadLoss as HL
        from R200_SDL import LampPower as LampPower

        # Calculate RED and HeadLoss
        window.RED.setText(str(round(config.LampFactor*RED(config.Drive,config.Drive,config.LampEfficiency,config.LampEfficiency
                                   ,config.FlowRate_m3h/config.nBranches,config.UVT,config.D1Log,config.NLamps),1)))
        if (float(window.RED.toPlainText())<0):
            window.RED.setText('0')
        window.RED.setAlignment(QtCore.Qt.AlignCenter)
        window.HeadLoss.setText(str(round(config.HL_Multiplier*HL(config.FlowRate_m3h/config.nBranches,config.NLamps),2)))
        window.HeadLoss.setAlignment(QtCore.Qt.AlignCenter)

        config.MaxLampsPower = LampPower * config.NLamps
        config.AveragePowerConsumption = int(config.MaxLampsPower*(config.Drive/100)*0.9)
        window.MaxLampsPower.setText(str(config.MaxLampsPower/1000))
        window.MaxLampsPower.setAlignment(QtCore.Qt.AlignCenter)
        window.AveragePowerConsumption.setText(str(config.AveragePowerConsumption/1000))
        window.AveragePowerConsumption.setAlignment(QtCore.Qt.AlignCenter)

    if window.UVSystem.currentText() == 'RZ-163-UHP':
        from RZ_163_UHP2 import RED as RED
        from RZ_163_UHP2 import HeadLoss as HL
        from RZ_163_UHP2 import LampPower as LampPower

        #from RZ_163_UHP2 import minFlow as minFlow
        #from RZ_163_UHP2 import maxFlow as maxFlow

        #config.minFlow = minFlow
        #config.maxFlow = maxFlow

        # Calculate RED and HeadLoss
        window.RED.setText(str(round(config.LampFactor*RED(config.Drive,config.LampEfficiency,config.FlowRate_m3h/config.nBranches,
                                   config.UVT,config.UVT215,config.D1Log,config.NLamps),1)))
        if (float(window.RED.toPlainText())<0):
            window.RED.setText('0')
        window.RED.setAlignment(QtCore.Qt.AlignCenter)
        window.HeadLoss.setText(str(round(config.HL_Multiplier*HL(config.FlowRate_m3h/config.nBranches,config.NLamps),2)))
        window.HeadLoss.setAlignment(QtCore.Qt.AlignCenter)

        config.MaxLampsPower = LampPower * config.NLamps
        config.AveragePowerConsumption = int(config.MaxLampsPower*(config.Drive/100)*0.9)
        window.MaxLampsPower.setText(str(config.MaxLampsPower/1000))
        window.MaxLampsPower.setAlignment(QtCore.Qt.AlignCenter)
        window.AveragePowerConsumption.setText(str(config.AveragePowerConsumption/1000))
        window.AveragePowerConsumption.setAlignment(QtCore.Qt.AlignCenter)

    if window.UVSystem.currentText() == 'RZ-104':

        if ((window.UVModel.currentText() == '11')): #RZ-104-11 or RZ-104-21 - 1 lamp per module
            from RZ_104_1L import RED as RED # single lamp = RZ-104-11 and RZ-104-21
            from RZ_104_1L import HeadLoss as HL
            from RZ_104_1L import LampPower as LampPower
        else: #RZ-104-12 or RZ-104-22 - 2 lamps per module
            from RZ_104_2L import RED as RED # single lamp = RZ-104-11 and RZ-104-21
            from RZ_104_2L import HeadLoss as HL
            from RZ_104_2L import LampPower as LampPower

        # Calculate RED and HeadLoss
        lampsPerBranch = {
            '11':1,
            '12':2,
            '21':1,
            '22':2
        }

        window.RED.setText(str(round(config.LampFactor*RED(config.Drive,config.Drive,config.LampEfficiency,config.LampEfficiency
                                   ,config.FlowRate_m3h/config.nBranches,config.UVT,config.D1Log,lampsPerBranch[window.UVModel.currentText()]),1)))
        if (float(window.RED.toPlainText())<0):
            window.RED.setText('0')
        window.RED.setAlignment(QtCore.Qt.AlignCenter)
        window.HeadLoss.setText(str(round(config.HL_Multiplier*HL(config.FlowRate_m3h/config.nBranches,lampsPerBranch[window.UVModel.currentText()]),2)))
        window.HeadLoss.setAlignment(QtCore.Qt.AlignCenter)

        config.MaxLampsPower = LampPower * config.NLamps
        config.AveragePowerConsumption = int(config.MaxLampsPower*(config.Drive/100)*0.9)
        window.MaxLampsPower.setText(str(config.MaxLampsPower/1000))
        window.MaxLampsPower.setAlignment(QtCore.Qt.AlignCenter)
        window.AveragePowerConsumption.setText(str(config.AveragePowerConsumption/1000))
        window.AveragePowerConsumption.setAlignment(QtCore.Qt.AlignCenter)

    if window.UVSystem.currentText() == 'RZ-163':

        if ((window.UVModel.currentText() == '11')): #1 lamp per module
            from RZ_163_1L import RED as RED # single lamp
            from RZ_163_1L import HeadLoss as HL
            from RZ_163_1L import LampPower as LampPower

            #from RZ_163_1L import minFlow as minFlow
            #from RZ_163_1L import maxFlow as maxFlow

            #config.minFlow = minFlow
            #config.maxFlow = maxFlow

        else: #Multi-lamps per module
            from RZ_163_ML import RED as RED # single lamp
            from RZ_163_ML import HeadLoss as HL
            from RZ_163_ML import LampPower as LampPower

            #from RZ_163_ML import minFlow as minFlow
            #from RZ_163_ML import maxFlow as maxFlow

            #config.minFlow = minFlow
            #config.maxFlow = maxFlow

        # Calculate RED and HeadLoss
        lampsPerBranch = {
            '11':1,
            '12':2,
            '13':3,
            '14':4
        }

        window.RED.setText(str(round(config.LampFactor*RED(config.Drive,config.Drive,config.Drive,config.Drive,config.LampEfficiency,config.LampEfficiency,
                                   config.LampEfficiency,config.LampEfficiency,config.FlowRate_m3h/config.nBranches,config.UVT,config.D1Log,
                                   lampsPerBranch[window.UVModel.currentText()]),1)))
        if (float(window.RED.toPlainText())<0):
            window.RED.setText('0')
        window.RED.setAlignment(QtCore.Qt.AlignCenter)
        window.HeadLoss.setText(str(round(config.HL_Multiplier*HL(config.FlowRate_m3h/config.nBranches,lampsPerBranch[window.UVModel.currentText()]),2)))
        window.HeadLoss.setAlignment(QtCore.Qt.AlignCenter)

        config.MaxLampsPower = LampPower * config.NLamps
        config.AveragePowerConsumption = int(config.MaxLampsPower*(config.Drive/100)*0.9)
        window.MaxLampsPower.setText(str(config.MaxLampsPower/1000))
        window.MaxLampsPower.setAlignment(QtCore.Qt.AlignCenter)
        window.AveragePowerConsumption.setText(str(config.AveragePowerConsumption/1000))
        window.AveragePowerConsumption.setAlignment(QtCore.Qt.AlignCenter)

    if window.UVSystem.currentText() == 'RZ-163-HP':

        if ((window.UVModel.currentText() == '11')): #1 lamp per branch
            from RZ_163HP_1L import RED as RED # single lamp
            from RZ_163HP_1L import HeadLoss as HL
            from RZ_163HP_1L import LampPower as LampPower

            #from RZ_163HP_1L import minFlow as minFlow
            #from RZ_163HP_1L import maxFlow as maxFlow

            #config.minFlow = minFlow
            #config.maxFlow = maxFlow

        else: #Multi-lamps per module
            from RZ_163HP_ML import RED as RED # single lamp
            from RZ_163HP_ML import HeadLoss as HL
            from RZ_163HP_ML import LampPower as LampPower

            #from RZ_163HP_ML import minFlow as minFlow
            #from RZ_163HP_ML import maxFlow as maxFlow

            #config.minFlow = minFlow
            #config.maxFlow = maxFlow

        # Calculate RED and HeadLoss
        lampsPerBranch = {
            '11':1,
            '12':2,
            '13':3,
            '14':4
        }

        window.RED.setText(str(round(config.LampFactor*RED(config.Drive,config.Drive,config.Drive,config.Drive,config.LampEfficiency,config.LampEfficiency,
                                   config.LampEfficiency,config.LampEfficiency,config.FlowRate_m3h/config.nBranches,config.UVT,config.D1Log,
                                   lampsPerBranch[window.UVModel.currentText()]),1)))
        if (float(window.RED.toPlainText())<0):
            window.RED.setText('0')
        window.RED.setAlignment(QtCore.Qt.AlignCenter)
        window.HeadLoss.setText(str(round(config.HL_Multiplier*HL(config.FlowRate_m3h/config.nBranches,lampsPerBranch[window.UVModel.currentText()]),2)))
        window.HeadLoss.setAlignment(QtCore.Qt.AlignCenter)

        config.MaxLampsPower = LampPower * config.NLamps
        config.AveragePowerConsumption = int(config.MaxLampsPower*(config.Drive/100)*0.9)
        window.MaxLampsPower.setText(str(config.MaxLampsPower/1000))
        window.MaxLampsPower.setAlignment(QtCore.Qt.AlignCenter)
        window.AveragePowerConsumption.setText(str(config.AveragePowerConsumption/1000))
        window.AveragePowerConsumption.setAlignment(QtCore.Qt.AlignCenter)

    if window.UVSystem.currentText() == 'RS-104':
        from RS_104 import RED as RED
        from RS_104 import HeadLoss as HL
        from RS_104 import LampPower as LampPower

        #from RS_104 import minFlow as minFlow
        #from RS_104 import maxFlow as maxFlow

        #config.minFlow = minFlow
        #config.maxFlow = maxFlow

        lampsPerBranch = {
            '11':1,
            '12':2
            }

        # Calculate RED and HeadLoss
        window.RED.setText(str(round(lampsPerBranch[window.UVModel.currentText()]*config.LampFactor*RED(config.Drive,config.LampEfficiency,
                                   config.FlowRate_m3h/config.nBranches,config.UVT,config.D1Log,config.NLamps),1)))
        if (float(window.RED.toPlainText())<0):
            window.RED.setText('0')
        window.RED.setAlignment(QtCore.Qt.AlignCenter)
        window.HeadLoss.setText(str(round(config.HL_Multiplier*HL(config.FlowRate_m3h/config.nBranches,config.NLamps),2)))
        window.HeadLoss.setAlignment(QtCore.Qt.AlignCenter)

        config.MaxLampsPower = LampPower * config.NLamps
        config.AveragePowerConsumption = int(config.MaxLampsPower*(config.Drive/100)*0.9)
        window.MaxLampsPower.setText(str(config.MaxLampsPower/1000))
        window.MaxLampsPower.setAlignment(QtCore.Qt.AlignCenter)
        window.AveragePowerConsumption.setText(str(config.AveragePowerConsumption/1000))
        window.AveragePowerConsumption.setAlignment(QtCore.Qt.AlignCenter)

    if window.UVSystem.currentText() == 'RZB-300':
        from RZB_300_1X import RED as RED
        from RZB_300_1X import HeadLoss as HL
        from RZB_300_1X import LampPower as LampPower

        #from RZB_300_1X import minFlow as minFlow
        #from RZB_300_1X import maxFlow as maxFlow

        #config.minFlow = minFlow
        #config.maxFlow = maxFlow

        #config.minFlowgpm = round(minFlow*config.m3h2gpm,1) # same in gpm
        #config.maxFlowgpm = round(maxFlow*config.m3h2gpm,1) # same in gpm

        # Calculate RED and HeadLoss
        window.RED.setText(str(round(config.LampFactor*RED(config.Drive,config.Drive,config.LampEfficiency,config.LampEfficiency,config.FlowRate_m3h/config.nBranches,
                               config.UVT,config.D1Log,config.NLamps),1)))
        if (float(window.RED.toPlainText())<0):
            window.RED.setText('0')
        window.RED.setAlignment(QtCore.Qt.AlignCenter)
        window.HeadLoss.setText(str(round(config.HL_Multiplier*HL(config.FlowRate_m3h/config.nBranches,config.NLamps),2)))
        window.HeadLoss.setAlignment(QtCore.Qt.AlignCenter)

        config.MaxLampsPower = LampPower * config.NLamps
        config.AveragePowerConsumption = int(config.MaxLampsPower*(config.Drive/100)*0.9)
        window.MaxLampsPower.setText(str(config.MaxLampsPower/1000))
        window.MaxLampsPower.setAlignment(QtCore.Qt.AlignCenter)
        window.AveragePowerConsumption.setText(str(config.AveragePowerConsumption/1000))
        window.AveragePowerConsumption.setAlignment(QtCore.Qt.AlignCenter)

    if window.UVSystem.currentText() == 'EP-600':
        from EP_600 import RED as RED
        from EP_600 import HeadLoss as HL
        from EP_600 import LampPower as LampPower

        #from EP_600 import minFlow as minFlow
        #from EP_600 import maxFlow as maxFlow

        #config.minFlow = minFlow
        #config.maxFlow = maxFlow

        # Calculate RED and HeadLoss
        window.RED.setText(str(round(config.LampFactor*RED(config.Drive,config.Drive,config.Drive,config.Drive,config.LampEfficiency,config.LampEfficiency,
                                   config.LampEfficiency,config.LampEfficiency,config.FlowRate_m3h/config.nBranches,config.UVT,config.D1Log,config.NLamps),1)))
        if (float(window.RED.toPlainText())<0):
            window.RED.setText('0')
        window.RED.setAlignment(QtCore.Qt.AlignCenter)
        window.HeadLoss.setText(str(round(config.HL_Multiplier*HL(config.FlowRate_m3h/config.nBranches,config.NLamps),2)))
        window.HeadLoss.setAlignment(QtCore.Qt.AlignCenter)

        config.MaxLampsPower = LampPower * config.NLamps
        config.AveragePowerConsumption = int(config.MaxLampsPower*(config.Drive/100)*0.9)
        window.MaxLampsPower.setText(str(config.MaxLampsPower/1000))
        window.MaxLampsPower.setAlignment(QtCore.Qt.AlignCenter)
        window.AveragePowerConsumption.setText(str(config.AveragePowerConsumption/1000))
        window.AveragePowerConsumption.setAlignment(QtCore.Qt.AlignCenter)

    if window.UVSystem.currentText() == 'RZM-200':

        if ((window.UVModel.currentText() == '5 Lamps')): #5 out of 5 lamps per branch
            from RZM_200_5 import RED as RED
            from RZM_200_5 import HeadLoss as HL
            from RZM_200_5 import LampPower as LampPower
        elif ((window.UVModel.currentText() == '3 Lamps')): #3 out of 5 lamps per branch
            from RZM_200_3 import RED as RED
            from RZM_200_3 import HeadLoss as HL
            from RZM_200_3 import LampPower as LampPower
        elif ((window.UVModel.currentText() == '2 Lamps')): #2 out of 5 lamps per branch
            from RZM_200_2 import RED as RED
            from RZM_200_2 import HeadLoss as HL
            from RZM_200_2 import LampPower as LampPower

        #from RZM_200 import minFlow as minFlow
        #from RZM_200 import maxFlow as maxFlow

        #config.minFlow = minFlow
        #config.maxFlow = maxFlow

        # Calculate RED and HeadLoss
        window.RED.setText(str(round(config.LampFactor*RED(config.Drive,config.Drive,config.Drive,config.Drive,config.Drive,
                                   config.LampEfficiency,config.LampEfficiency,config.LampEfficiency,
                                   config.LampEfficiency,config.LampEfficiency,config.FlowRate_m3h/config.nBranches,
                                   config.UVT,config.D1Log,config.NLamps),1)))
        if (float(window.RED.toPlainText())<0):
            window.RED.setText('0')
        window.RED.setAlignment(QtCore.Qt.AlignCenter)
        window.HeadLoss.setText(str(round(config.HL_Multiplier*HL(config.FlowRate_m3h/config.nBranches,config.NLamps),2)))
        window.HeadLoss.setAlignment(QtCore.Qt.AlignCenter)

        config.MaxLampsPower = LampPower * config.NLamps
        config.AveragePowerConsumption = int(config.MaxLampsPower*(config.Drive/100)*0.9)
        window.MaxLampsPower.setText(str(round(config.MaxLampsPower/1000,1)))
        window.MaxLampsPower.setAlignment(QtCore.Qt.AlignCenter)
        window.AveragePowerConsumption.setText(str(config.AveragePowerConsumption/1000))
        window.AveragePowerConsumption.setAlignment(QtCore.Qt.AlignCenter)


    if window.UVSystem.currentText() == 'RZMW-350':

        if ((window.UVModel.currentText() == '11 Lamps')): #11 out of 11 lamps per branch
            from RZMW_350_11 import RED as RED
            from RZMW_350_11 import HeadLoss as HL
            from RZMW_350_11 import LampPower as LampPower
        elif ((window.UVModel.currentText() == '7 Lamps')): #7 out of 11 lamps per branch
            from RZMW_350_7 import RED as RED
            from RZMW_350_7 import HeadLoss as HL
            from RZMW_350_7 import LampPower as LampPower

        #from RZM_200 import minFlow as minFlow
        #from RZM_200 import maxFlow as maxFlow

        #config.minFlow = minFlow
        #config.maxFlow = maxFlow

        # Calculate RED and HeadLoss

        if ((window.UVModel.currentText() == '11 Lamps')): #11 out of 11 lamps per branch:
            window.RED.setText(str(round(config.LampFactor*RED(config.Drive,config.Drive,config.Drive,config.Drive,config.Drive,
                                             config.Drive,config.Drive,config.Drive,config.Drive,config.Drive,
                                             config.Drive,
                                             config.LampEfficiency,config.LampEfficiency,config.LampEfficiency,
                                             config.LampEfficiency,config.LampEfficiency,config.LampEfficiency,
                                             config.LampEfficiency,config.LampEfficiency,config.LampEfficiency,
                                             config.LampEfficiency,config.LampEfficiency,
                                             config.FlowRate_m3h/config.nBranches,config.UVT,config.D1Log,config.NLamps),1)))
        elif ((window.UVModel.currentText() == '7 Lamps')): #7 out of 11 lamps per branch:
            window.RED.setText(str(round(config.LampFactor*RED(config.Drive,config.Drive,config.Drive,config.Drive,config.Drive,
                                             config.Drive,config.Drive,
                                             config.LampEfficiency,config.LampEfficiency,config.LampEfficiency,
                                             config.LampEfficiency,config.LampEfficiency,config.LampEfficiency,
                                             config.LampEfficiency,config.FlowRate_m3h/config.nBranches,
                                             config.UVT,config.D1Log,config.NLamps),1)))

        if (float(window.RED.toPlainText())<0):
            window.RED.setText('0')
        window.RED.setAlignment(QtCore.Qt.AlignCenter)
        window.HeadLoss.setText(str(round(config.HL_Multiplier*HL(config.FlowRate_m3h/config.nBranches,config.NLamps),2)))
        window.HeadLoss.setAlignment(QtCore.Qt.AlignCenter)

        config.MaxLampsPower = LampPower * config.NLamps
        config.AveragePowerConsumption = int(config.MaxLampsPower*(config.Drive/100)*0.9)
        window.MaxLampsPower.setText(str(round(config.MaxLampsPower/1000,1)))
        window.MaxLampsPower.setAlignment(QtCore.Qt.AlignCenter)
        window.AveragePowerConsumption.setText(str(config.AveragePowerConsumption/1000))
        window.AveragePowerConsumption.setAlignment(QtCore.Qt.AlignCenter)

    if window.UVSystem.currentText() == 'RZ-300':
        #implement RZ-300 HDR model
        from RZ_300_HDR import RED as RED
        from RZ_300_HDR import HeadLoss as HL
        from RZ_300_HDR import LampPower as LampPower

        #from RZ_300_HDR import minFlow as minFlow
        #from RZ_300_HDR import maxFlow as maxFlow

        #config.minFlow = minFlow
        #config.maxFlow = maxFlow

        # Calculate RED and HeadLoss
        window.RED.setText(str(round(config.LampFactor*RED(config.Drive,config.LampEfficiency,config.FlowRate_m3h/config.nBranches,config.UVT,config.D1Log,config.NLamps),1)))
        if (float(window.RED.toPlainText())<0):
            window.RED.setText('0')
        window.RED.setAlignment(QtCore.Qt.AlignCenter)
        window.HeadLoss.setText(str(round(config.HL_Multiplier*HL(config.FlowRate_m3h/config.nBranches,config.NLamps),2)))
        window.HeadLoss.setAlignment(QtCore.Qt.AlignCenter)

        config.MaxLampsPower = LampPower * config.NLamps
        config.AveragePowerConsumption = int(config.MaxLampsPower*(config.Drive/100)*0.9)
        window.MaxLampsPower.setText(str(config.MaxLampsPower/1000))
        window.MaxLampsPower.setAlignment(QtCore.Qt.AlignCenter)
        window.AveragePowerConsumption.setText(str(config.AveragePowerConsumption/1000))
        window.AveragePowerConsumption.setAlignment(QtCore.Qt.AlignCenter)

    if (window.UVSystem.currentText() == 'RZM-350') | (window.UVSystem.currentText() == 'RZM-350-Marine'):
        #implement RZM model

        if ((window.UVModel.currentText() == '8 Lamps')): #8 out of 8 lamps per branch
            from RZM_350_8 import RED as RED
            from RZM_350_8 import HeadLoss as HL
            from RZM_350_8 import LampPower as LampPower
            from RZM_350_8 import Dose_VF as VF #Validation Factor
        elif ((window.UVModel.currentText() == '5 Lamps')): #5 out of 8 lamps per branch
            from RZM_350_5 import RED as RED
            from RZM_350_5 import HeadLoss as HL
            from RZM_350_5 import LampPower as LampPower
            from RZM_350_5 import Dose_VF as VF #Validation Factor

        #from RZM_350 import minFlow as minFlow
        #from RZM_350 import maxFlow as maxFlow

        #config.minFlow = minFlow
        #config.maxFlow = maxFlow

        if (window.UVSystem.currentText() == 'RZM-350'):
            VF=VF['Regular']
        else:
            VF=VF['Marine']

        # Calculate RED and HeadLoss
        window.RED.setText(str(round(VF*config.LampFactor*RED(config.Drive,config.Drive,config.Drive,config.Drive,config.Drive,config.Drive,config.Drive,config.Drive,
                                   config.LampEfficiency,config.LampEfficiency,config.LampEfficiency,config.LampEfficiency,
                                   config.LampEfficiency,config.LampEfficiency,config.LampEfficiency,config.LampEfficiency,
                                   config.FlowRate_m3h/config.nBranches,config.UVT,config.D1Log,config.NLamps),1)))
        if (float(window.RED.toPlainText())<0):
            window.RED.setText('0')
        window.RED.setAlignment(QtCore.Qt.AlignCenter)
        window.HeadLoss.setText(str(round(config.HL_Multiplier*HL(config.FlowRate_m3h/config.nBranches,config.NLamps),2)))
        window.HeadLoss.setAlignment(QtCore.Qt.AlignCenter)

        config.MaxLampsPower = LampPower * config.NLamps
        config.AveragePowerConsumption = int(config.MaxLampsPower*(config.Drive/100)*0.9)
        window.MaxLampsPower.setText(str(config.MaxLampsPower/1000))
        window.MaxLampsPower.setAlignment(QtCore.Qt.AlignCenter)
        window.AveragePowerConsumption.setText(str(config.AveragePowerConsumption/1000))
        window.AveragePowerConsumption.setAlignment(QtCore.Qt.AlignCenter)

    # Calculate the achieved LI
    if (window.RED.toPlainText() != ''):
        if (config.SelectedPathogen == 'Manual Input'): #Manual input of D1-Log = LI = RED/D1Log
            config.AchievedLI = int(float(window.RED.toPlainText())/float(window.D1Log.text()))

            if config.AchievedLI > 5:
                window.LI.setText('>5')
                window.inactivationBar.setValue(5)
            else:
                window.LI.setText(str(config.AchievedLI))
                window.inactivationBar.setValue(config.AchievedLI)
        else: #D1Log from the table
            Data = config.KillData[['Microbial Type',1,1.5,2,2.5,3,3.5,4,4.5,5]]
            D_log = (Data.loc[Data['Microbial Type']==config.SelectedPathogen]).values.tolist()[0]
            config.AchievedLI = 0 #Default value is zero
            for i in range(1,9):

                try: #If it is a numerical value

                    LIi = float(float(D_log[i])/float(window.RED.toPlainText()))

                    if (LIi>1):
                        config.AchievedLI = list((Data.loc[Data['Microbial Type']==config.SelectedPathogen]))[i]
                        window.LI.setText(str(config.AchievedLI))
                        #window.inactivationBar.setValue(int(config.AchievedLI))
                        break

                except: #non-numerical, from table
                    window.LI.setText(str(D_log[i]))
                    config.achievedLI = int(findall(r'\d+',str(D_log[i]))[0])
                    #window.inactivationBar.setValue(config.achievedLI)
            window.inactivationBar.setValue(int(config.AchievedLI))

    if (float(window.HeadLoss.toPlainText())>config.HeadLossWarning*config.HL_Multiplier): # Set warning on HeadLoss >2m
        window.HeadLoss.setStyleSheet("background-color: rgb(255, 0, 0);")
    else:
        window.HeadLoss.setStyleSheet("background-color: rgb(255, 255, 255);")

def UVBranches(): #Set the number of Branches
    global ValidInput
    try:
        if (int(window.UVBranches.text()))>0:
            config.nBranches = int(window.UVBranches.text()) #Store Branches
            window.UVBranches.setStyleSheet("background-color: rgb(255, 255, 255);")
            UVSystem()
            recalculate()
            ValidInput = True
        else:
            window.UVBranches.setStyleSheet("background-color: rgb(255, 0, 0);")
            ValidInput = True
    except:
        window.UVBranches.setStyleSheet("background-color: rgb(255, 0, 0);")
        ValidInput = True

def PlotREDvsUVT():
    import pyqtgraph as pg
    import types

    title = "RED vs. UVT"
    y1,y2,y3 = [],[],[]

    UV_range = range(40, 98, 1)

    # Remember all the values
    rememberLampEfficiency = float(window.LampEfficiency.text()) # Store Eff
    rememberPower = float(window.Power.text()) # Store Drive
    rememberUVT = float(window.UVT.text()) # Store UVT
    rememberUVT215 = float(window.UVT215.text()) # Store UVT215
    rememberFlow = float(window.FlowRate.text()) # Store Flow

    Flows = [config.minFlow,int((config.minFlow+config.maxFlow)/2),config.maxFlow]
    # import max and min system flows

    for UV in UV_range:

        config.UVT = UV

        config.FlowRate_m3h = Flows[0]
        recalculate()
        if float(window.RED.toPlainText()) < 0:
            y1.append(0)
        else:
            y1.append(float(window.RED.toPlainText()))

        config.FlowRate_m3h = Flows[1]
        recalculate()
        if float(window.RED.toPlainText()) < 0:
            y2.append(0)
        else:
            y2.append(float(window.RED.toPlainText()))

        config.FlowRate_m3h = Flows[2]
        recalculate()
        if float(window.RED.toPlainText()) < 0:
            y3.append(0)
        else:
            y3.append(float(window.RED.toPlainText()))

    #Restore all vallues back
    config.UVT = rememberUVT
    config.LampEfficiency = rememberLampEfficiency
    config.Drive = rememberPower
    config.UVT = rememberUVT
    config.UVT215 = rememberUVT215
    config.FlowRate_m3h = rememberFlow # Pay attention to the units
    recalculate()

    ######### Graphical Plot ########

    #Ui.win = pg.GraphicsWindow()
    Ui.win = pg.GraphicsLayoutWidget()

    Ui.win.setWindowTitle(title)
    label = pg.LabelItem(justify='left')

    Ui.win.addItem(label, row=1, col=0)
    p1 = Ui.win.addPlot(row=2, col=0)

    p1.showGrid(x = True, y = True)

    p1.setLabel('left', 'RED', units ='[mJ/cm²]')
    p1.setLabel('bottom', 'UVT254', units ='[%-1cm]')

    p1.setXRange(40, 100)
    p1.setYRange(0, max(max(y1),max(y2),max(y3)))

    p1.setLimits(xMin=38, xMax=102,
             #minXRange=0, maxXRange=102,
             yMin=-25, yMax=max(max(y1),max(y2),max(y3))+100,
             #minYRange=-2, maxYRange=max(max(y1),max(y2),max(y3))+2
             )

    Ui.win.setBackground('w') # Set background to White

    leg = p1.addLegend(offset=(50,50))

    def paint(self, p, *args):
        p.setPen(pg.mkPen('k'))
        p.setBrush(pg.mkBrush('w'))
        p.drawRect(self.boundingRect())

    leg.paint = types.MethodType(paint,leg)
    label.paint = types.MethodType(paint,label)

    p1.plot(UV_range, y1, pen ='g', symbol ='x', symbolPen ='g',
                           symbolBrush = 0.2, name = 'Flow='+str(Flows[0])+'m³/h')
    p1.plot(UV_range, y2, pen ='b', symbol ='o', symbolPen ='b',
                             symbolBrush = 0.2, name = 'Flow='+str(Flows[1])+'m³/h')
    p1.plot(UV_range, y3, pen ='r', symbol ='+', symbolPen ='r',
                             symbolBrush = 0.2, name = 'Flow='+str(Flows[2])+'m³/h')


    #cross hair
    vLine = pg.InfiniteLine(angle=90, movable=False)
    hLine = pg.InfiniteLine(angle=0, movable=False)
    p1.addItem(vLine, ignoreBounds=True)
    p1.addItem(hLine, ignoreBounds=True)

    vb = p1.vb

    def mouseMoved(evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if p1.sceneBoundingRect().contains(pos):
            mousePoint = vb.mapSceneToView(pos)
            if mousePoint.y()<0:
                label.setText("<span style='color: black'>UVT=%0.1f[%%-1cm],   <span style='color: red'>RED=%0.1f[mJ/cm²]</span>" % (mousePoint.x(), 0))
            else:
                label.setText("<span style='color: black'>UVT=%0.1f[%%-1cm],   <span style='color: red'>RED=%0.1f[mJ/cm²]</span>" % (mousePoint.x(), mousePoint.y()))
            vLine.setPos(mousePoint.x())
            hLine.setPos(mousePoint.y())

    Ui.proxy = pg.SignalProxy(p1.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)

    Ui.win.show()


def PlotREDvsFlow():
    import pyqtgraph as pg
    import types

    title = "RED vs. Flow"
    y1,y2,y3 = [],[],[]

    UV_range = range(int(config.minFlow), int(config.maxFlow), 10)

    # Remember all the values
    rememberLampEfficiency = float(window.LampEfficiency.text()) # Store Eff
    rememberPower = float(window.Power.text()) # Store Drive
    rememberUVT = float(window.UVT.text()) # Store UVT
    rememberUVT215 = float(window.UVT215.text()) # Store UVT215
    rememberFlow = float(window.FlowRate.text()) # Store Flow

    UVTs = [config.minUVT,int((config.minUVT+config.maxUVT)*2/3),config.maxUVT]
    # import max and min system flows

    for Flow in UV_range:

        config.FlowRate_m3h = Flow

        config.UVT = UVTs[0]
        recalculate()
        if float(window.RED.toPlainText()) < 0:
            y1.append(0)
        else:
            y1.append(float(window.RED.toPlainText()))

        config.UVT = UVTs[1]
        recalculate()
        if float(window.RED.toPlainText()) < 0:
            y2.append(0)
        else:
            y2.append(float(window.RED.toPlainText()))

        config.UVT = UVTs[2]
        recalculate()
        if float(window.RED.toPlainText()) < 0:
            y3.append(0)
        else:
            y3.append(float(window.RED.toPlainText()))

    #Restore all vallues back
    config.UVT = rememberUVT
    config.LampEfficiency = rememberLampEfficiency
    config.Drive = rememberPower
    config.UVT = rememberUVT
    config.UVT215 = rememberUVT215
    config.FlowRate_m3h = rememberFlow # Pay attention to the units
    recalculate()

    ######### Graphical Plot ########

    #Ui.win = pg.GraphicsWindow()
    Ui.win = pg.GraphicsLayoutWidget()

    Ui.win.setWindowTitle(title)
    label = pg.LabelItem(justify='left')

    Ui.win.addItem(label, row=1, col=0)
    p1 = Ui.win.addPlot(row=2, col=0)

    p1.setLabel('left', 'RED', units ='[mJ/cm²]')
    p1.setLabel('bottom', 'Flow Rate [m³/h]')

    p1.showGrid(x = True, y = True)


    p1.setXRange(config.minFlow, config.maxFlow)
    p1.setYRange(0, max(max(y1),max(y2),max(y3)))

    p1.setLimits(xMin=(config.minFlow-10), xMax=(config.maxFlow+10),
             #minXRange=0, maxXRange=102,
             yMin=-25, yMax=max(max(y1),max(y2),max(y3))+100,
             #minYRange=-2, maxYRange=max(max(y1),max(y2),max(y3))+2
             )

    Ui.win.setBackground('w') # Set background to White

    leg = p1.addLegend(offset=(-50,50))

    def paint(self, p, *args):
        p.setPen(pg.mkPen('k'))
        p.setBrush(pg.mkBrush('w'))
        p.drawRect(self.boundingRect())

    leg.paint = types.MethodType(paint,leg)
    label.paint = types.MethodType(paint,label)

    p1.plot(UV_range, y1, pen ='g', symbol ='x', symbolPen ='g',
                           symbolBrush = 0.2, name = 'UVT='+str(UVTs[0])+'%-1cm')
    p1.plot(UV_range, y2, pen ='b', symbol ='o', symbolPen ='b',
                             symbolBrush = 0.2, name = 'UVT='+str(UVTs[1])+'%-1cm')
    p1.plot(UV_range, y3, pen ='r', symbol ='+', symbolPen ='r',
                             symbolBrush = 0.2, name = 'UVT='+str(UVTs[2])+'%-1cm')


    #cross hair
    vLine = pg.InfiniteLine(angle=90, movable=False)
    hLine = pg.InfiniteLine(angle=0, movable=False)
    p1.addItem(vLine, ignoreBounds=True)
    p1.addItem(hLine, ignoreBounds=True)

    vb = p1.vb

    def mouseMoved(evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if p1.sceneBoundingRect().contains(pos):
            mousePoint = vb.mapSceneToView(pos)
            if mousePoint.y()<0:
                label.setText("<span style='color: black'>Flow=%i[m³/h],   <span style='color: red'>RED=%0.1f[mJ/cm²]</span>" % (mousePoint.x(), 0))
            else:
                label.setText("<span style='color: black'>Flow=%i[m³/h],   <span style='color: red'>RED=%0.1f[mJ/cm²]</span>" % (mousePoint.x(), mousePoint.y()))
            vLine.setPos(mousePoint.x())
            hLine.setPos(mousePoint.y())

    Ui.proxy = pg.SignalProxy(p1.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)

    Ui.win.show()

def PlotREDvsDrive():
    import pyqtgraph as pg
    import types

    title = "RED vs. Electrical Power"
    y1,y2,y3 = [],[],[]

    UV_range = range(25, 100, 5)

    # Remember all the values
    rememberLampEfficiency = float(window.LampEfficiency.text()) # Store Eff
    rememberPower = float(window.Power.text()) # Store Drive
    rememberUVT = float(window.UVT.text()) # Store UVT
    rememberUVT215 = float(window.UVT215.text()) # Store UVT215
    rememberFlow = float(window.FlowRate.text()) # Store Flow

    UVTs = [60,80,92]
    # import max and min system flows

    for Drive in UV_range:

        config.Drive = Drive

        config.UVT = UVTs[0]
        recalculate()
        if float(window.RED.toPlainText()) < 0:
            y1.append(0)
        else:
            y1.append(float(window.RED.toPlainText()))

        config.UVT = UVTs[1]
        recalculate()
        if float(window.RED.toPlainText()) < 0:
            y2.append(0)
        else:
            y2.append(float(window.RED.toPlainText()))

        config.UVT = UVTs[2]
        recalculate()
        if float(window.RED.toPlainText()) < 0:
            y3.append(0)
        else:
            y3.append(float(window.RED.toPlainText()))

    #Restore all vallues back
    config.UVT = rememberUVT
    config.LampEfficiency = rememberLampEfficiency
    config.Drive = rememberPower
    config.UVT = rememberUVT
    config.UVT215 = rememberUVT215
    config.FlowRate_m3h = rememberFlow # Pay attention to the units
    recalculate()

    ######### Graphical Plot ########

    #Ui.win = pg.GraphicsWindow()
    Ui.win = pg.GraphicsLayoutWidget()

    Ui.win.setWindowTitle(title)
    label = pg.LabelItem(justify='left')

    Ui.win.addItem(label, row=1, col=0)
    p1 = Ui.win.addPlot(row=2, col=0)

    p1.setLabel('left', 'RED', units ='[mJ/cm²]')
    p1.setLabel('bottom', 'Power [%]')

    p1.showGrid(x = True, y = True)


    p1.setXRange(25, 100)
    p1.setYRange(0, max(max(y1),max(y2),max(y3)))

    p1.setLimits(xMin=(25-5), xMax=(100+5),
             #minXRange=0, maxXRange=102,
             yMin=-30, yMax=max(max(y1),max(y2),max(y3))+100,
             #minYRange=-2, maxYRange=max(max(y1),max(y2),max(y3))+2
             )

    Ui.win.setBackground('w') # Set background to White

    leg = p1.addLegend(offset=(50,50))

    def paint(self, p, *args):
        p.setPen(pg.mkPen('k'))
        p.setBrush(pg.mkBrush('w'))
        p.drawRect(self.boundingRect())

    leg.paint = types.MethodType(paint,leg)
    label.paint = types.MethodType(paint,label)

    p1.plot(UV_range, y1, pen ='g', symbol ='x', symbolPen ='g',
                           symbolBrush = 0.2, name = 'UVT='+str(UVTs[0])+'%-1cm')
    p1.plot(UV_range, y2, pen ='b', symbol ='o', symbolPen ='b',
                             symbolBrush = 0.2, name = 'UVT='+str(UVTs[1])+'%-1cm')
    p1.plot(UV_range, y3, pen ='r', symbol ='+', symbolPen ='r',
                             symbolBrush = 0.2, name = 'UVT='+str(UVTs[2])+'%-1cm')


    #cross hair
    vLine = pg.InfiniteLine(angle=90, movable=False)
    hLine = pg.InfiniteLine(angle=0, movable=False)
    p1.addItem(vLine, ignoreBounds=True)
    p1.addItem(hLine, ignoreBounds=True)

    vb = p1.vb

    def mouseMoved(evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if p1.sceneBoundingRect().contains(pos):
            mousePoint = vb.mapSceneToView(pos)
            if mousePoint.y()<0:
                label.setText("<span style='color: black'>Power=%i[%%],   <span style='color: red'>RED=%0.1f[mJ/cm²]</span>" % (mousePoint.x(), 0))
            else:
                label.setText("<span style='color: black'>Power=%i[%%],   <span style='color: red'>RED=%0.1f[mJ/cm²]</span>" % (mousePoint.x(), mousePoint.y()))
            vLine.setPos(mousePoint.x())
            hLine.setPos(mousePoint.y())

    Ui.proxy = pg.SignalProxy(p1.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)

    Ui.win.show()

def SelectFromTable():
    global ValidInput

    if config.CalculatorType == 'Developer':

        items = window.LogReductionTable.selectedItems()
        PatName = str(items[0].text())
        D1Log = str(items[1].text())

        config.ManualD1Log = False

        if D1Log != '':
            config.D1Log = float(D1Log)
            config.SelectedPathogen = str(PatName)
            window.SelectedPathogen.setStyleSheet("background-color: rgb(255, 255, 255);")
            window.D1Log.blockSignals(True)
            window.D1Log.setText(str(D1Log))
            window.D1Log.blockSignals(False)
            window.SelectedPathogen.setText(str(PatName))
            ValidInput = True
            recalculate()
        else:
            window.SelectedPathogen.setStyleSheet("background-color: rgb(0, 255, 0);")
            window.D1Log.blockSignals(True)
            window.D1Log.setText('Please select specific')
            window.D1Log.blockSignals(False)
            ValidInput = False

        window.SelectedPathogen.setText(str(PatName))

def SelectPathogen():
    global ValidInput

    if config.CalculatorType == 'Developer':

        getSelected = window.Pathogens.selectedItems()
        if getSelected:
            baseNode = getSelected[0]
            PatName = baseNode.text(0) #Name of the pathogen
            D1Log = (baseNode.text(1)) #D-1Log value
            config.ManualD1Log = False

        if D1Log != '':
            config.D1Log = float(D1Log)
            config.SelectedPathogen = str(PatName)
            window.SelectedPathogen.setStyleSheet("background-color: rgb(255, 255, 255);")
            window.D1Log.blockSignals(True)
            window.D1Log.setText(str(D1Log))
            window.D1Log.blockSignals(False)
            window.SelectedPathogen.setText(str(PatName))
            ValidInput = True
            recalculate()
        else:
            window.SelectedPathogen.setStyleSheet("background-color: rgb(0, 255, 0);")
            window.D1Log.blockSignals(True)
            window.D1Log.setText('Please select specific')
            window.D1Log.blockSignals(False)
            ValidInput = False

        window.SelectedPathogen.setText(str(PatName))

def D1LogManual():
    global ValidInput

    window.Pathogens.collapseAll()

    try:
        config.D1Log = float(window.D1Log.text())
        window.D1Log.setStyleSheet("background-color: rgb(255, 255, 255);")
        config.SelectedPathogen = 'Manual Input'
        ValidInput = True
        recalculate()
    except ValueError:
        window.D1Log.setStyleSheet("background-color: rgb(255, 0, 0);")
        ValidInput = False

    if ValidInput == True:
        #config.D1Log = float(window.LampEfficiency.text())
        window.SelectedPathogen.setText(config.SelectedPathogen)

def ResetPathogen():
    config.D1Log = config.DefaultD1Log
    config.SelectedPathogen = 'Manual Input'
    window.SelectedPathogen.setText('Manual Input')
    window.SelectedPathogen.setAlignment(QtCore.Qt.AlignLeft)
    window.D1Log.setText(str(config.DefaultD1Log))
    recalculate()

def TableView():
    window.LogReductionTable.setVisible(True)
    window.Pathogens.setVisible(False)

def TreeView():
    window.LogReductionTable.setVisible(False)
    window.Pathogens.setVisible(True)

def Developer():
    if (config.CalculatorType == 'Marketing'):
        Pass , pressed = QInputDialog.getText(window, "Password", "Please Enter Developer Password: ",
                                               QtWidgets.QLineEdit.Password, "")
        if pressed:
            if (Pass == config.DeveloperPassword): #Developer Password Entered
                window.PlotRedUVT.setEnabled(True)
                window.PlotRedFlow.setEnabled(True)
                window.PlotRedPower.setEnabled(True)

                window.D1Log.setEnabled(True)
                #window.D1Log.setVisible(True)
                window.Pathogens_Table.setEnabled(True)

                #window.UVT215.setVisible(True)
                #window.UVT215units.setVisible(True)
                #window.UVT215Label.setVisible(True)
                #window.GraphBox.setVisible(True)
                #window.frame.setVisible(False)

                window.ge0.setEnabled(False)
                window.ge1.setEnabled(False)
                window.ge2.setEnabled(False)
                window.ge3.setEnabled(False)
                
                window.EPA.setEnabled(True)
                #window.PMO.setEnabled(True)
                window.FullRangeRED.setEnabled(True)
                window.FullRangeRED.setChecked(True)

                window.Dechlorination.setEnabled(True)

                window.HgOF.setEnabled(True)
                window.HgVUV.setEnabled(True)

                FullRanged()
                config.CalculatorType = 'Developer'
                UVModel()



def Marketing():
    if (config.CalculatorType == 'Developer'):
        window.PlotRedUVT.setEnabled(False)
        window.PlotRedFlow.setEnabled(False)
        window.PlotRedPower.setEnabled(False)

        window.D1Log.setEnabled(False)
        #window.D1Log.setVisible(False)
        #window.Pathogens_Table.setEnabled(False)

        window.UVT215.setVisible(False)
        window.UVT215units.setVisible(False)
        window.UVT215Label.setVisible(False)

        window.ge0.setEnabled(True)
        window.ge1.setEnabled(True)
        window.ge2.setEnabled(True)
        window.ge3.setEnabled(True)

        window.UVT215.setVisible(True)
        window.UVT215units.setVisible(True)
        window.UVT215Label.setVisible(True)

        window.EPA.setEnabled(True)
        #window.PMO.setEnabled(False)
        window.FullRangeRED.setEnabled(True)

        #window.Dechlorination.setEnabled(False)
        #window.FullRangeRED.setChecked(True)
        window.EPA.setChecked(True)

        window.HgOF.setEnabled(False)
        window.HgVUV.setEnabled(False)
        LampFactor_Reg()

        ResetPathogen()
        EPA()

        config.CalculatorType = 'Marketing'
        UVModel()

def FullTable():

    Data = config.KillData[['Microbial Type',1,1.5,2,2.5,3,3.5,4,4.5,5,5.5]]
    Ui.tableWidget = QTableWidget()
    Ui.tableWidget.setWindowTitle('Pathogen Log-Inactivation [mJ/cm²] - Full Data Table')
    Ui.tableWidget.left = window.pos().x()+50
    Ui.tableWidget.top = window.pos().y()+100
    Ui.tableWidget.width = 700
    Ui.tableWidget.height = 500
    Ui.tableWidget.setGeometry(Ui.tableWidget.left, Ui.tableWidget.top, Ui.tableWidget.width, Ui.tableWidget.height)

    Ui.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
    Ui.tableWidget.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
    Ui.tableWidget.setSortingEnabled(True)


    Ui.tableWidget.setColumnCount(len(Data.columns))
    Ui.tableWidget.setRowCount(len(Data.index))
    for i in range(len(Data.index)):
        for j in range(len(Data.columns)):
            Ui.tableWidget.setItem(i,j,QTableWidgetItem(str(Data.iloc[i, j])))
    #Ui.tableFont = QtGui.QFont("Times", 9, QtGui.QFont.Times)
    #self.LogReductionTable.setFont(tableFont)

    Ui.tableWidget.setHorizontalHeaderLabels(['Pathogen Type', '1-Log','1.5-Log','2-Log','2.5-Log'
                                              ,'3-log','3.5-Log','4-Log','4.5-Log','5-Log','5.5-Log'])

    Ui.tableWidget.verticalHeader().hide()
    Ui.tableWidget.setAlternatingRowColors(True)
    Ui.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    Ui.tableWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
    Ui.tableWidget.resizeRowsToContents()
    Ui.tableWidget.show()

def FullRanged():
    # Developer mode - full list of Reactor Systems
    config.FullRangeRED = True
    config.EPA = False
    #config.PMO = False

    window.UVT.setEnabled(True)
    config.UVT = config.userUVT
    window.UVT.setText(str(config.UVT))
    window.UVT.setAlignment(QtCore.Qt.AlignCenter)
    window.UVT.setEnabled(True)
    window.UVT254Slider.blockSignals(True)
    window.UVT254Slider.setValue(int(config.UVT))
    window.UVT254Slider.blockSignals(False)

    config.UV_Systems = config.ValidatedDoseFamilies
    window.UVSystem.blockSignals(True)
    window.UVSystem.clear()
    window.UVSystem.addItems(config.UV_Systems)
    window.UVSystem.blockSignals(False)

    window.OzoneIn.blockSignals(True)
    window.ChlorineIn.blockSignals(True)
    window.OzoneIn.setText('0.0')
    window.OzoneOut.setText('0.0')
    window.OzoneOut.setAlignment(QtCore.Qt.AlignCenter)
    window.ChlorineIn.setText('0.0')
    window.ChlorineOut.setText('0.0')
    window.ChlorineOut.setAlignment(QtCore.Qt.AlignCenter)
    window.OzoneIn.blockSignals(False)
    window.ChlorineIn.blockSignals(False)

    window.OzoneIn.setEnabled(False)
    window.ChlorineIn.setEnabled(False)
    recalculate()

def EPA():
    #
    config.FullRangeRED = False
    config.EPA = True
    #config.PMO = False

    window.UVT.setEnabled(True)
    config.UVT = config.userUVT
    window.UVT.setText(str(config.UVT))
    window.UVT.setAlignment(QtCore.Qt.AlignCenter)
    window.UVT.setEnabled(True)
    window.UVT254Slider.blockSignals(True)
    window.UVT254Slider.setValue(int(config.UVT))
    window.UVT254Slider.blockSignals(False)

    config.UV_Systems = config.MunicipalFamilies
    window.UVSystem.blockSignals(True)
    window.UVSystem.clear()
    window.UVSystem.addItems(config.UV_Systems)
    window.UVSystem.blockSignals(False)

    window.OzoneIn.blockSignals(True)
    window.ChlorineIn.blockSignals(True)
    window.OzoneIn.setText('0.0')
    window.OzoneOut.setText('0.0')
    window.OzoneOut.setAlignment(QtCore.Qt.AlignCenter)
    window.ChlorineIn.setText('0.0')
    window.ChlorineOut.setText('0.0')
    window.ChlorineOut.setAlignment(QtCore.Qt.AlignCenter)
    window.OzoneIn.blockSignals(False)
    window.ChlorineIn.blockSignals(False)

    window.OzoneIn.setEnabled(False)
    window.ChlorineIn.setEnabled(False)
    UVSystem()
    recalculate()

def PMO():
    # Depricated function
    config.FullRangeRED = False
    config.EPA = False
    #config.PMO = True

    window.UVT.setEnabled(True)
    config.UVT = config.userUVT
    window.UVT.setText(str(config.UVT))
    window.UVT.setAlignment(QtCore.Qt.AlignCenter)
    window.UVT.setEnabled(True)
    window.UVT254Slider.blockSignals(True)
    window.UVT254Slider.setValue(int(config.UVT))
    window.UVT254Slider.blockSignals(False)

    config.UV_Systems = config.DairyFamilies
    window.UVSystem.blockSignals(True)
    window.UVSystem.clear()
    window.UVSystem.addItems(config.UV_Systems)
    window.UVSystem.blockSignals(False)

    window.OzoneIn.blockSignals(True)
    window.ChlorineIn.blockSignals(True)
    window.OzoneIn.setText('0.0')
    window.OzoneOut.setText('0.0')
    window.OzoneOut.setAlignment(QtCore.Qt.AlignCenter)
    window.ChlorineIn.setText('0.0')
    window.ChlorineOut.setText('0.0')
    window.ChlorineOut.setAlignment(QtCore.Qt.AlignCenter)
    window.OzoneIn.blockSignals(False)
    window.ChlorineIn.blockSignals(False)

    window.OzoneIn.setEnabled(False)
    window.ChlorineIn.setEnabled(False)
    UVSystem()
    recalculate()

def Dechlorination(): # Dechlorination and ozone decomposition for specific RED
    config.userUVT = config.UVT
    config.UVT = 97
    window.UVT.setText(str(config.UVT))
    window.UVT.setAlignment(QtCore.Qt.AlignCenter)
    #window.UVT.setEnabled(False)
    window.UVT254Slider.blockSignals(True)
    window.UVT254Slider.setValue(int(config.UVT))
    window.UVT254Slider.blockSignals(False)

    window.OzoneIn.setEnabled(True)
    if config.CalculatorType == 'Developer':
        window.ChlorineIn.setEnabled(True)

    window.OzoneIn.blockSignals(True)
    if config.CalculatorType == 'Developer':
        window.ChlorineIn.blockSignals(True)

    window.OzoneIn.setText(str(config.OzoneIn))
    window.OzoneOut.setText(str(config.OzoneOut))

    if config.CalculatorType == 'Developer':
        window.ChlorineIn.setText(str(config.ChlorineIn))
        window.ChlorineOut.setText(str(config.ChlorineOut))

    window.OzoneIn.blockSignals(False)
    if config.CalculatorType == 'Developer':
        window.ChlorineIn.blockSignals(False)

    window.OzoneOut.setAlignment(QtCore.Qt.AlignCenter)
    if config.CalculatorType == 'Developer':
        window.ChlorineOut.setAlignment(QtCore.Qt.AlignCenter)

def DechloCalc(): # Recalculate Dechlorination and ozone decomposition
    global ValidInput
    try:
        config.OzoneIn = float(window.OzoneIn.text())
        config.ChlorineIn = float(window.ChlorineIn.text())

        config.OzoneOut = round((config.OzoneIn)*(0.5)**(float(window.RED.toPlainText())/(config.OzoneD_05)),2)
        config.ChlorineOut = round((config.ChlorineIn)*(0.5)**(float(window.RED.toPlainText())/(config.ChlorineD_05)),2)

        window.OzoneOut.setText(str(config.OzoneOut))
        window.OzoneOut.setAlignment(QtCore.Qt.AlignCenter)
        window.ChlorineOut.setText(str(config.ChlorineOut))
        window.ChlorineOut.setAlignment(QtCore.Qt.AlignCenter)
        window.OzoneIn.setStyleSheet("background-color: rgb(255, 255, 255);")
        window.ChlorineIn.setStyleSheet("background-color: rgb(255, 255, 255);")
        ValidInput = True
    except ValueError:
        window.OzoneIn.setStyleSheet("background-color: rgb(255, 0, 0);")
        window.ChlorineIn.setStyleSheet("background-color: rgb(255, 0, 0);")
        ValidInput = False

def UVSystem():
    System = window.UVSystem.currentText()
    config.Modules = list((config.Systems[System].dropna()))
    window.UVModel.blockSignals(True)
    window.UVModel.clear()
    window.UVModel.addItems(config.Modules)

    UVModel()
    recalculate()
    window.UVModel.blockSignals(False)

def UVModel():
    try: # Module modifiers in list
        NLamps = config.Lamp_Modules.get(window.UVModel.currentText())*config.lamps_in_single_Module.get(window.UVSystem.currentText())
    except: # Not in list, just get the number as is
        NLamps = config.Lamp_Modules.get(window.UVModel.currentText())
    config.NLamps = NLamps

    params = config.SystemParameters.loc[(config.SystemParameters['UV-System']==window.UVSystem.currentText()) & (config.SystemParameters['Model']==window.UVModel.currentText())]

    if config.CalculatorType == 'Developer' or config.CalculatorType == 'Admin':
        config.minFlow = 1 #This is an absolute minimum
    else:
        if window.vertical.isChecked():
            config.minFlow = (round(float(params['Qmin vertical [m^3/h]']),0)) # Vertical
        else:
            config.minFlow = (round(float(params['Qmin [m^3/h]']),0)) # Horizontal
    config.maxFlow = (round(float(params['Qmax [m^3/h]']),0))

    #Beanches flow dividers
    config.minFlow = config.minFlow*config.nBranches
    config.maxFlow = config.maxFlow*config.nBranches
    config.minFlowgpm = (round(config.minFlow*config.m3h2gpm,0))
    config.maxFlowgpm = (round(config.maxFlow*config.m3h2gpm,0))
    config.FlowRate_m3h = config.FlowRate_m3h*config.nBranches
    config.FlowRate_USgpm = config.FlowRate_m3h*config.m3h2gpm

    config.minUVT = float(params['UVTmin [%-1cm]'])
    config.maxUVT = float(params['UVTmax [%-1cm]'])
    config.minPower = float(params['Pmin [%]'])
    config.maxPower = float(params['Pmax [%]'])

    #Reset the sliders and values:
    #Reset Power
    if (config.Drive < config.minPower):
        config.Drive = config.minPower
    elif (config.Drive > config.maxPower):
        config.Drive = config.maxPower

    window.Power.setText(str(config.Drive))
    Power()
    PowerSlider()

    #Reset Efficiency
    if (config.LampEfficiency < config.minEfficiency):
        config.LampEfficiency = config.minEfficiency

    elif (config.LampEfficiency > config.maxEfficiency):
        config.LampEfficiency = config.maxEfficiency

    window.LampEfficiency.setText(str(config.LampEfficiency))
    LampEfficiency()
    LampEfficiencySlider()

    #Reset UVT
    if (config.UVT < config.minUVT):
        config.Drive = config.minUVT
        window.UVT.setText(str(config.UVT))
    elif (config.UVT > config.maxUVT):
        config.UVT = config.maxUVT
        window.UVT.setText(str(config.UVT))
    UVT()
    UVT254Slider()

    #Reset Branches
    window.UVBranches.setText(str(config.nBranches))

    #fix Flow Range changes
    if (config.FlowUnits == 'm3h'): # units in [m^3/h]
        if (float(window.FlowRate.text()) < config.minFlow):
            window.FlowSlider.blockSignals(True)
            window.FlowRate.setText(str(config.minFlow))
            window.FlowSlider.setValue(int(round(config.minFlow,1)))
            window.FlowSlider.blockSignals(False)
        elif (float(window.FlowRate.text()) > config.maxFlow):
            window.FlowSlider.blockSignals(True)
            window.FlowRate.setText(str(config.maxFlow))
            window.FlowSlider.setValue(int(round(config.maxFlow,1)))
            window.FlowSlider.blockSignals(False)
        else: # if everything is OK
            window.FlowSlider.blockSignals(True)
            window.FlowSlider.setValue(int(round(config.FlowRate_m3h,1)))
            window.FlowSlider.blockSignals(False)
    else: # Units in [gpm]
        if (float(window.FlowRate.text()) < config.minFlowgpm):
            window.FlowSlider.blockSignals(True)
            window.FlowRate.setText(str(config.minFlowgpm))
            window.FlowSlider.setValue(int(round(config.minFlowgpm,1)))
            window.FlowSlider.blockSignals(False)
        elif (float(window.FlowRate.text()) > config.maxFlowgpm):
            window.FlowSlider.blockSignals(True)
            window.FlowRate.setText(str(config.maxFlowgpm))
            window.FlowSlider.setValue(int(round(config.maxFlowgpm,1)))
            window.FlowSlider.blockSignals(False)
        else: # if everything is OK
            window.FlowSlider.blockSignals(True)
            window.FlowSlider.setValue(int(round(config.FlowRate_USgpm,1)))
            window.FlowSlider.blockSignals(False)
    FlowRate()
    FlowSlider()
    recalculate()

def LampEfficiency():
    global ValidInput
    try:
        float(window.LampEfficiency.text())
        if (float(window.LampEfficiency.text()) >= config.minEfficiency) & (float(window.LampEfficiency.text()) <= config.maxEfficiency):
            window.LampEfficiency.setStyleSheet("background-color: rgb(255, 255, 255);")
            config.LampEfficiency = float(window.LampEfficiency.text())
            window.LampEffSlider.blockSignals(True)
            window.LampEffSlider.setValue(int(config.LampEfficiency))
            window.LampEffSlider.setMinimum(int(round(config.minEfficiency,2)))
            window.LampEffSlider.setMaximum(int(round(config.maxEfficiency,2)))
            window.LampEffSlider.blockSignals(False)
            ValidInput = True
            recalculate()
        else:
            window.LampEfficiency.setStyleSheet("background-color: rgb(255, 0, 0);")
            ValidInput = False
    except ValueError:
        window.LampEfficiency.setStyleSheet("background-color: rgb(255, 0, 0);")
        ValidInput = False

def LampEfficiencySlider():
    global ValidInput
    config.LampEfficiency = window.LampEffSlider.value()
    window.LampEfficiency.setText(str(config.LampEfficiency))
    window.LampEfficiency.setAlignment(QtCore.Qt.AlignCenter)
    ValidInput = True
    recalculate()

def Power():
    global ValidInput
    try:
        float(window.Power.text())
        if (float(window.Power.text()) >= config.minPower) & (float(window.Power.text()) <= config.maxPower):
            window.Power.setStyleSheet("background-color: rgb(255, 255, 255);")
            config.Drive = float(window.Power.text())
            window.PowerSlider.blockSignals(True)
            window.PowerSlider.setValue(int(config.Drive))
            window.PowerSlider.setMinimum(int(round(config.minPower,2)))
            window.PowerSlider.setMaximum(int(round(config.maxPower,2)))
            window.PowerSlider.blockSignals(False)
            ValidInput = True
            recalculate()
        else:
            window.Power.setStyleSheet("background-color: rgb(255, 0, 0);")
            ValidInput = False
    except ValueError:
        window.Power.setStyleSheet("background-color: rgb(255, 0, 0);")
        ValidInput = False

def PowerSlider():
    global ValidInput
    config.Drive = window.PowerSlider.value()
    window.Power.setText(str(config.Drive))
    window.Power.setAlignment(QtCore.Qt.AlignCenter)
    ValidInput = True
    recalculate()

def UVT():
    global ValidInput
    try:
        float(window.UVT.text())
        if (float(window.UVT.text()) >= config.minUVT) & (float(window.UVT.text()) <= config.maxUVT):
            window.UVT.setStyleSheet("background-color: rgb(255, 255, 255);")
            config.UVT = float(window.UVT.text())
            config.UVT215 = round(config.UVT215_A*exp(config.UVT215_B*config.UVT),1)
            if config.UVT215>config.UVT: #Limiting mechanism. May be changed in future
                config.UVT215=config.UVT
            window.UVT215.setText(str(config.UVT215))
            window.UVT254Slider.blockSignals(True)
            window.UVT254Slider.setValue(int(config.UVT))
            window.UVT254Slider.setMinimum(int(round(config.minUVT,2)))
            window.UVT254Slider.setMaximum(int(round(config.maxUVT,2)))
            window.UVT254Slider.blockSignals(False)
            ValidInput = True
            recalculate()
        else:
            window.UVT.setStyleSheet("background-color: rgb(255, 0, 0);")
            ValidInput = False
    except ValueError:
        window.UVT.setStyleSheet("background-color: rgb(255, 0, 0);")
        ValidInput = False

def UVT254Slider():
    global ValidInput
    config.UVT = window.UVT254Slider.value()
    config.UVT215 = round(config.UVT215_A*exp(config.UVT215_B*config.UVT),1)
    if config.UVT215>config.UVT: #Limiting mechanism. May be changed in future
                config.UVT215=config.UVT
    window.UVT.setText(str(config.UVT))
    window.UVT215.setText(str(config.UVT215))
    window.UVT.setAlignment(QtCore.Qt.AlignCenter)
    window.UVT215.setAlignment(QtCore.Qt.AlignCenter)
    ValidInput = True
    recalculate()

def FlowRate():
    global ValidInput
    try:
        float(window.FlowRate.text())
        if (float(window.FlowRate.text()) >= config.minFlow) & (float(window.FlowRate.text()) <= config.maxFlow):
            window.FlowRate.setStyleSheet("background-color: rgb(255, 255, 255);")
            window.RED.setStyleSheet("background-color: rgb(255, 255, 255);")

        params = config.SystemParameters.loc[(config.SystemParameters['UV-System']==window.UVSystem.currentText()) & (config.SystemParameters['Model']==window.UVModel.currentText())]
        if window.vertical.isChecked():
            TempMinFlow = (round(float(params['Qmin vertical [m^3/h]']),0)) # Vertical
        else:
            TempMinFlow = (round(float(params['Qmin [m^3/h]']),0)) # Horizontal
        if  config.FlowRate_m3h<TempMinFlow:
            window.FlowRate.setStyleSheet("background-color: rgb(255, 0, 0);")
            window.RED.setStyleSheet("background-color: rgb(255, 0, 0);")
        else:
            window.FlowRate.setStyleSheet("background-color: rgb(255, 255, 255);")
            window.RED.setStyleSheet("background-color: rgb(255, 255, 255);")

        if ((config.FlowUnits == 'm3h') & (float(window.FlowRate.text()) >= (config.minFlow)) & (float(window.FlowRate.text()) <= (config.maxFlow))):
            config.FlowRate_m3h = float(window.FlowRate.text())
            config.FlowRate_USgpm = round(config.FlowRate_m3h * config.m3h2gpm,1) #unit conversion
            window.FlowSlider.blockSignals(True)
            window.FlowSlider.setValue(int(round(config.FlowRate_m3h,1)))
            window.FlowSlider.setMinimum(int(round(config.minFlow,1)))
            window.FlowSlider.setMaximum(int(round(config.maxFlow,1)))
            window.FlowSlider.blockSignals(False)
            window.FlowRate.setStyleSheet("background-color: rgb(255, 255, 255);")
            window.RED.setStyleSheet("background-color: rgb(255, 255, 255);")
            ValidInput = True
            recalculate()
        elif ((config.FlowUnits == 'gpm') & (float(window.FlowRate.text()) >= (config.minFlowgpm)) & (float(window.FlowRate.text()) <= (config.maxFlowgpm))): #USgpm units
            config.FlowRate_USgpm = float(window.FlowRate.text())
            config.FlowRate_m3h = round(config.FlowRate_USgpm / config.m3h2gpm,1) #unit conversion
            window.FlowSlider.blockSignals(True)
            window.FlowSlider.setValue(int(round(config.FlowRate_USgpm,1)))
            window.FlowSlider.setMinimum(int(round(config.minFlowgpm,1)))
            window.FlowSlider.setMaximum(int(round(config.maxFlowgpm,1)))
            window.FlowSlider.blockSignals(False)
            window.FlowRate.setStyleSheet("background-color: rgb(255, 255, 255);")
            window.RED.setStyleSheet("background-color: rgb(255, 255, 255);")
            ValidInput = True
            recalculate()
        else:
            window.FlowRate.setStyleSheet("background-color: rgb(255, 0, 0);")
            ValidInput = False
    except ValueError:
        window.FlowRate.setStyleSheet("background-color: rgb(255, 0, 0);")
        ValidInput = False

def FlowSlider():
    global ValidInput
    if config.FlowUnits == 'm3h':
        config.FlowRate_m3h = float(window.FlowSlider.value())
        window.FlowRate.setText(str(config.FlowRate_m3h))
        window.FlowRate.setAlignment(QtCore.Qt.AlignCenter)
    elif config.FlowUnits == 'gpm':
        config.FlowRate_USgpm = float(window.FlowSlider.value())
        window.FlowRate.setText(str(config.FlowRate_USgpm))
        window.FlowRate.setAlignment(QtCore.Qt.AlignCenter)
    ValidInput = True
    recalculate()

def FlowUnits():
    if (window.FlowUnits.currentText()=='[m³/hr]'):
        config.FlowUnits = 'm3h'
        window.FlowRate.setText(str((round(config.FlowRate_m3h,0))))

        window.FlowSlider.setValue(int(round(config.FlowRate_m3h,1)))
        window.FlowSlider.setMinimum(int(round(config.minFlow,1)))
        window.FlowSlider.setMaximum(int(round(config.maxFlow,1)))
        window.FlowRate.setAlignment(QtCore.Qt.AlignCenter)
        recalculate()
    else: # units were in gpm
        config.FlowUnits = 'gpm'
        window.FlowRate.setText(str((round(config.FlowRate_USgpm,0))))

        window.FlowSlider.setValue(int(round(config.FlowRate_USgpm,1)))
        window.FlowSlider.setMinimum(int(round(config.minFlowgpm,1)))
        window.FlowSlider.setMaximum(int(round(config.maxFlowgpm,1)))
        window.FlowRate.setAlignment(QtCore.Qt.AlignCenter)
        recalculate()

def PressureUnits():
    if (window.PressureUnits.currentText()=='[mH₂O]'):
        config.FlowUnits = 'mH2O'
        config.HL_Multiplier = 1
    if (window.PressureUnits.currentText()=='[cmH₂O]'):
        config.FlowUnits = 'cmH2O'
        config.HL_Multiplier = 100
    if (window.PressureUnits.currentText()=='[inH₂O]'):
        config.FlowUnits = 'inH2O'
        config.HL_Multiplier = 0.0254
    if (window.PressureUnits.currentText()=='[inH₂O]'):
        config.FlowUnits = 'bar'
        config.HL_Multiplier = 0.098064
    if (window.PressureUnits.currentText()=='[PSI]'):
        config.FlowUnits = 'psi'
        config.HL_Multiplier = 1.42233
    if (window.PressureUnits.currentText()=='[bar]'):
        config.FlowUnits = 'bar'
        config.HL_Multiplier = 10.1971621
    FlowUnits()
    recalculate()

def FlowForDose():
    Tolerance = 0.1 #[m^3/h]
    #Flow1 = 1 # lower bound
    #Flow2 = 10000 # upper bound

    Flow1 = config.minFlow
    Flow2 = config.maxFlow

    TargetDose, okPressed = QtWidgets.QInputDialog.getDouble(window, "Calculate Flow","Dose Value:", float(window.RED.toPlainText()), 0, 10000, 2)
    if okPressed:
        while (abs(Flow2-Flow1) > Tolerance):
            Flow = Flow1 + ((Flow2 - Flow1) / 2)
            #config.FlowRate_m3h = Flow
            window.FlowRate.setText(str(round(Flow,1)))
            window.FlowRate.setAlignment(QtCore.Qt.AlignCenter)
            recalculate()
            CurrentDose = float(window.RED.toPlainText())
            if (CurrentDose < TargetDose):
                Flow2 = Flow
            else:
                Flow1 = Flow

def LampFactor_Reg(): # Regular UV lamp
    config.LampFactor = config.Hg_Reg
    window.HgUV.setChecked(True)
    window.HgOF.setChecked(False)
    window.HgVUV.setChecked(False)
    recalculate()

def LampFactor_OF(): # Regular UV lamp
    config.LampFactor = config.Hg_OF
    window.HgUV.setChecked(False)
    window.HgOF.setChecked(True)
    window.HgVUV.setChecked(False)
    recalculate()

def LampFactor_VUV(): # Regular UV lamp
    config.LampFactor = config.Hg_VUV
    window.HgUV.setChecked(False)
    window.HgOF.setChecked(False)
    window.HgVUV.setChecked(True)
    recalculate()

def resetCalc(self):

    window.LampEfficiency.setText(str(80))
    window.LampEfficiency.setAlignment(QtCore.Qt.AlignCenter)
    window.Power.setText(str(100))
    window.Power.setAlignment(QtCore.Qt.AlignCenter)
    window.UVT.setText(str(95))
    window.UVT.setAlignment(QtCore.Qt.AlignCenter)
    window.UVT215.setText(str(config.UVT215))
    window.UVT215.setAlignment(QtCore.Qt.AlignCenter)
    
    if config.minFlow<100:
        window.FlowRate.setText(str(100))
    else:
        window.FlowRate.setText(str(config.minFlow))
    window.FlowRate.setAlignment(QtCore.Qt.AlignCenter)
    
    config.FlowUnits = 'm3h'
    window.FlowUnits.setCurrentIndex(0) #set to m3/h


    FlowUnits()
    recalculate()

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    login = Login() #Log-in dialog

    if login.exec_() == QtWidgets.QDialog.Accepted:
        window = Ui()
        recalculate()
        window.show()
        sys.exit(app.exec_())

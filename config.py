# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 09:45:50 2020
Store the configuration variables and stuff

@author: Mike
"""
from pandas import read_excel as rX
from math import exp as exp
import os,sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

FullRangeRED = True #Full Range RED selected
EPA = False #Municipal EPA selected
PMO = False #Dairy Market PMO selected

#%% Calculator default type - Developer or Marketing

CalculatorType = 'Marketing' #by default some dev. options are grayed-out
DeveloperPassword = 'Atlantium'

#%%  UVT Coefficients for estimated calculation of UVT215 from UVT254:
UVT215_A = 0.2804
UVT215_B = 0.0609

#%%

m3h2gpm = 4.403 #Unit Conversion Factor from [m^3/hr] to [USgpm]

# Basic variables
DefaultD1Log = 18#19.869 #1-Log inactivation dose - default
LampEfficiency = 80 #[%]
Drive = 100 #[%]
UVT = 95 #[%-1cm]
UVT215 = round(UVT215_A*exp(UVT215_B*UVT),1) #This is only a relative estimate
FlowRate_m3h = 100 #[m^3/hr]
HeadLossWarning = 2 #[m]

# Dechlorination and Deozonation values
userUVT = UVT #it is just a saved UVT value for Dechlorination
ChlorineIn = 0.0
ChlorineOut = 0.0
OzoneIn = 0.0
OzoneOut = 0.0

OzoneD_05 = 50 #[mJ/cm^2]
ChlorineD_05 = 310#[mJ/cm^2]

# Default Parameters (they are actual parameters for RZ-163-11)
minFlow = 4 # Minimum Flow Rate in m3h
minFlowgpm = round(minFlow*m3h2gpm,1) # same in gpm
maxFlow = 2000 # Maximum Flow Rate in m3h
maxFlowgpm = round(maxFlow*m3h2gpm,1) # same in gpm
minUVT = 25 # minimum UVT245 in %-1cm
maxUVT = 99 # maximum UVT245 in %-1cm
minPower = 40 # minimum Power in %
maxPower = 100 # maximum Power in %
minEfficiency = 25 # minimum Efficiency in %
maxEfficiency = 100 # minimum Efficiency in %

nBranches = 1 #Number of Branches
FlowRate_USgpm = FlowRate_m3h*m3h2gpm
FlowUnits = 'm3h' #'m3h' or 'gpm'
D1Log = DefaultD1Log
NLamps = 1 #Number of Lamps by default
SelectedPathogen = 'Manual Input' #Custom type for default
AchievedLI = 0 #Achieved Log Inactivation

MaxLampsPower = 0 #Initioal Value in Watts
AveragePowerConsumption = 0 # Initial Value in Watts

Lamp_Modules = {
    '11' : 1,
    '12' : 2,
    '13' : 3,
    '14' : 4,
    'SL'  : 1,
    'DL'  : 2,
    'x2'  : 2,
    'x4'  : 4,
    }

lamps_in_single_Module = {
    'RZB-300'        : 2,
    'RZM-200'        : 5,
    'RZM-350'        : 8,
    'RZM-350-Marine' : 8,
    'RZM-500'        : 11
    }

Modules = ['11','12','13','14'] #Just for the initial value per RZ-163

ValidatedDoseFamilies = ['RZ-163','RZ-163-HP','RZ-163-UHP','RS-104','RZ-104','RZ-300',
                         'RZB-300','EP-600','RZM-350','RZM-350-Marine','RZM-200','R-200']
MunicipalFamilies = ['RZ-163','RZ-104','RZ-300','R-200']
DairyFamilies = ['RZ-163','RZ-163-HP','RZ-104','RZ-300','RZB-300','R-200']

UV_Systems = ValidatedDoseFamilies # Default Values

Systems_path = resource_path("UV Systems.xls")
KillData_path = resource_path("KillData.xls")
SystemParameters_path = resource_path("SystemParameters.xls")

Systems = rX(Systems_path, dtype='str') # All Models and Branches
KillData = rX(KillData_path) # All patogen types log-inactivation
SystemParameters = rX(SystemParameters_path, dtype='str') # System Parameters file
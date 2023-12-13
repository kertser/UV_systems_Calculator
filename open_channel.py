# -*- coding: utf-8 -*-
"""
Created on Thu Dec 11 09:22:00 2023

File for Open Channel Dose Calculator

@author: Mike
"""

from math import log10 as log, log as ln, exp as exp

LampPower = 1000  # [W]


# Dose Coefficients for 11 lamps module
class WW11:
    """
    Dose Coefficients for 11 lamps module
    """
    Z = 0.135874136777391
    A = 9635.277234
    B = 0.183480671
    C = 0.11383287
    D = 0.157836067
    alfa = 1
    beta = 1.095684204
    gama = 4.001104871

    @staticmethod
    def HeadLoss(Flow):
        A = 0.00000033
        B = 0.00043283
        """
        Calculates the head loss in [m] on single module
        :param Flow:
        :return: dP
        """
        return (A * Flow ** 2 + B * Flow)/100


class WW6:
    """
    Dose Coefficients for 6 lamps module
    """
    Z = 0.032972962
    A = 5706.120763
    B = 0.34350945
    C = 0.11383287
    D = 0.157836067
    alfa = 1
    beta = 1.095684204
    gama = 4.001104871

    @staticmethod
    def HeadLoss(Flow):
        A = 0.00000033
        B = 0.00043283
        """
        Calculates the head loss in [m] on single module
        :param Flow:
        :return: dP
        """
        return (A * Flow ** 2 + B * Flow)/100


# General scheme:
# Davg(P,Q,UVT)=A*((P^α)/(Q^β))*exp(γ*UVT/100)
# TUF(Q,UVT,D1Log)=Z*(Q^B)*(D1Log^C)*EXP(D*(UVT/100)))
# RED = Davg * TUF

def RED(P, Eff, Flow, UVT, D1Log, NLamps):
    """
    Calculates RED value
    # Selecting appropriate ww coefficients depending on the number of lamps in the module
    # WW6 for 6 lamps, WW11 for 11 lamps.
    """

    if NLamps == 11:
        ww = WW11
    else:
        ww = WW6

    def AvgDose():  # Calculates Davg value
        return ww.A * (((P / 100 * Eff / 100) ** ww.alfa) / (Flow ** ww.beta)) * exp(ww.gama * (UVT / 100))

    def TUF():
        return min(ww.Z * (Flow ** ww.B) * (D1Log ** ww.C) * exp(ww.D * (UVT / 100)), 1)  # TUF<1 always

    return round(AvgDose() * TUF(), 1)


def HeadLoss_gate(Flow, opening=0.1):
    A = 0.00235665626594626
    B = 0.153626033921992
    """
    Calculates the head loss in [cm] on single module
    :param Flow: Flow rate
    :return: dP: Pressure Drop
    """
    return A * (Flow / opening) ** 2 + B * Flow / opening


def Gate_Opening(Channel_Width, Flow):
    """
    Calculates the opening of the sluice in [cm]
    The Flow is in [m^3/h]
    """
    if Channel_Width == 750:
        return Flow * 0.1351 / 10  # [cm]
    elif Channel_Width == 1500:
        return Flow * 0.0683 / 10  # [cm]
    else:
        return 0

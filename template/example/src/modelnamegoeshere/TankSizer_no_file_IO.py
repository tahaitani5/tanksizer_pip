# -*- coding: utf-8 -*-
"""
@author:
Manuel J. Diaz
Aerospace Systems Design Lab
Georgia Institute of Technology
August 2015

This program was originally writte in Fortran 90 and was translated into Python to
remove file I/O for dramatic speed-up. Below is the program's original documentation.

!   PARSEC - Propellant_Tank.f90
!
!*********************************************************************************************
!
!   Program:    Level 1 Propellant Tank Structure Code
!
!   Purpose:    Calculates the Mass of the Fuel/Oxidizer Tanks as an Iso-Grid or Monoque tank.
!
!   Authors:    Eric Staton, Herb Guendal, Scott Thomas, Davey Jones, Rob Chiroux, and
!                   Lisa Johnston
!
!   Start:      July 2004
!
!   Published:  Version 1.0 August 6, 2004
!
!   Revisions:  Version 1.1
!
!   Worked on Last: August 4, 2005
!
!*********************************************************************************************
"""

from math import log10

def Main(inputs):
    """     ----- MAIN CALCULATIONS -----       """
    outputs = {}

    #Calculation for the Barrel Section of the Tank.
    pburst = inputs["Pburst"] * 6894.76 #Converts PSI to Pa

    massf = inputs["Mp"] / inputs["Number_Tanks"]

    Fuel_per_Tank = massf

    R = inputs["Tank_Radius"]

    outputs["New_Radius"] = inputs["Tank_Radius"]

    if (inputs["Toggle"] == 'N'):
        outputs["New_Volume"] = massf / inputs["Fuel_Density"]
        dome_height = inputs["Dome_Height"]
        hf = inputs["Cylinder_Length"] + 2.0 * dome_height
        outputs["New_Length"] = hf
    else:
        outputs["New_Volume"] = massf / inputs["Fuel_Density"]
        outputs["New_Length"] = inputs["AR"] * 2.0 * R + inputs["Cylinder_Length"]
        hf = outputs["New_Length"]
        inputs["Dome_Height"] = inputs["AR"] * R

    alpha = (inputs["Rib_Thickness"] * inputs["Rib_Height"]) / (inputs["Pocket_Thickness"] * inputs["Isogrid_Height"])
    delta = inputs["Rib_Height"] / inputs["Pocket_Thickness"]
    lamda = inputs["Top_Flange_Thickness"] / inputs["Pocket_Thickness"]
    mu = (inputs["Top_Flange_Width"] * inputs["Top_Flange_Thickness"]) / (inputs["Pocket_Thickness"] * inputs["Isogrid_Height"])
    L = inputs["Cylinder_Length"] / inputs["Number_of_Section"]
    beta = ((1 + alpha + mu) * (3.0 * (1 + delta)**2 + 3.0 * mu * (1 + lamda)**2 + 1 + alpha * delta**2 + mu * lamda**2) - 3.0 * ((1 + delta) - mu * (1 + lamda))**2)**0.5

    tstar = inputs["Pocket_Thickness"] * beta / (1 + alpha + mu)
    Estar = inputs["E"] * (1 + alpha + mu)**2 / beta

    tw = inputs["Pocket_Thickness"] * (1 + 3.0 * alpha + 3.0 * mu)
    ta = inputs["Pocket_Thickness"] * (1 + alpha + mu)

    theta = (R / tstar )**0.5 / 16.0

    gammaa = 1 - 0.901 * (1 - 2.718281828459**(-theta))
    gammab = 1 - 0.731 * (1 - 2.718281828459**(-theta))
    gammap = 0.75**2
    gammat = 0.6666667**1.3333333

    Sigma = log10((pburst / inputs["E"]) * (R / tstar)**2)

    ca = 0.005849492
    cb = 0.01939264
    cc = -0.015507073
    cd = -0.074270883
    ce = 0.073557991
    cf = 0.212422975

    deltagamma = ca * Sigma**5 + cb * Sigma**4 + cc * Sigma**3 + cd * Sigma**2 + ce * Sigma + cf

    Ncr1 = gammaa * inputs["E"] * inputs["Pocket_Thickness"]**2 * beta / (R * (3.0 * (1 - inputs["nu"]**2))**0.5)
    Ncr2 = 10.2 * inputs["E"] * inputs["Pocket_Thickness"]**3 * (1 + alpha + mu) / inputs["Isogrid_Height"]**2
    Ncr3 = 0.616 * inputs["E"] * inputs["Pocket_Thickness"] * (1 + alpha + mu) * inputs["Rib_Thickness"]**2 / inputs["Rib_Height"]**2

    Ftu = pburst * R / (inputs["Pocket_Thickness"] * (1 + alpha + mu))

    if (pburst > 0):
        Nacr = (Estar * tstar**2 / R) * (gammaa / ((3.0 * (1 - inputs["nu"]**2))**0.5) + deltagamma) + pburst * R / 2.0
    else:
        Nacr = (Estar * tstar**2 / R) * (gammaa / ((3.0 * (1 - inputs["nu"]**2))**0.5))

    if (pburst > 0):
        Nbcr = (Estar * tstar**2 / R) * (gammab / ((3.0 * (1 - inputs["nu"]**2))**0.5) + deltagamma) + pburst * R / 2.0
    else:
        Nbcr = (Estar * tstar**2 / R) * (gammab / ((3.0 * (1 - inputs["nu"]**2))**0.5))

    Npcr = 0.855 * R**2 * gammap**0.5 * inputs["E"] / (L * (1 - inputs["nu"]**2) * (R / tstar)**2.5)
    Nscr = 0.0885 * gammat**0.75 * 3.14159**2 * Estar * tstar**2.25 / (L**0.5 * (1 - inputs["nu"]**2)**0.625 * R**0.75)
    Nxa = (inputs["Thrust"] + (inputs["Fax"] + (2.0 * 3.14159 * R * tw * L * inputs["rho"] + massf + inputs["AxialMass"]) * (inputs["g"])) * inputs["LFax"]) / (2.0 * 3.14159 * R )
    Nxp = - pburst * R / 2

    if ((Nxa + Nxp) > 0):
        Nxb = inputs["Mbend"] / (3.14159 * R**2)
    else:
        Nxb = -inputs["Mbend"] / (3.14159 * R**2)

    Ncr = Nxa + abs(Nxb) + Nxp
    Nxabp = Nxa + Nxb + Nxp
    Nyp = - pburst * R - ((2.0 * 3.14159 * R * tw * L * inputs["rho"] + massf + inputs["AxialMass"]) * (inputs["g"]) * inputs["LFlat"]) / (2.0 * 3.14159 * R)
    Nxy = ((inputs["Torque"] / R) + inputs["Fsh"]) / (2.0 * 3.14159 * R)

    SigmaX = Nxabp / (ta)
    SigmaY = Nyp / (ta)
    SigmaXY = Nxy / (ta)

    Rib1 = (3.0 * Nyp - Nxabp) / (3.0 * ta)
    Rib2 = 2.0 * (Nxabp + 3**0.5 * Nxy) / (3.0 * ta)
    Rib3 = 2.0 * (Nxabp - 3**0.5 * Nxy) / (3.0 * ta)

    if (Ncr < 0) :
        outputs["MSGenInst"] = 0
        outputs["MSSkinBuck"] = 0
        outputs["MSRibCrip"] = 0
        outputs["MSCPB"] = 0
        outputs["MSIB"] = 0
    else:
        outputs["MSGenInst"] = Ncr1 / (inputs["FSu"] * Ncr) - 1
        outputs["MSSkinBuck"] = Ncr2 / (inputs["FSu"] * Ncr) - 1
        outputs["MSRibCrip"] = Ncr3 / (inputs["FSu"] * Ncr) - 1
        outputs["MSCPB"] = 1 / ((Nxy * inputs["FSu"] / Nscr)**2 + (Nxa + abs(Nxb)) * inputs["FSu"] / Ncr2 + Nyp / Ncr2) -1

        if (((inputs["FSu"] * abs(Nxb) / Nbcr)**3.0 + (inputs["FSu"] * Nxy / Nscr)**3.0 ) < 0):
            temp = (-1) * abs(((inputs["FSu"] * abs(Nxb) / Nbcr)**3.0 + (inputs["FSu"] * Nxy / Nscr)**3.0 ))**(1.0/3.0)
        else:
            temp = abs(((inputs["FSu"] * abs(Nxb) / Nbcr)**3.0 + (inputs["FSu"] * Nxy / Nscr)**3.0 ))**(1.0/3.0)

        if (pburst > 0):
            outputs["MSIB"] = 1 / (inputs["FSu"] * Nxa / Nacr + temp) - 1
        else:
            outputs["MSIB"] = 1 / (inputs["FSu"] * Nxa / Nacr + inputs["FSu"] * Nyp / Npcr + temp) - 1

    outputs["MSPockBurst"] = inputs["Ftenult"] / (inputs["FSu"] * abs(Ftu)) - 1

    if (min(SigmaX, SigmaY, SigmaXY, Rib1, Rib2, Rib3) < 0):
        outputs["MSTF"] = inputs["Ftenult"] / (inputs["FSu"] * abs(min(SigmaX, SigmaY, SigmaXY, Rib1, Rib2, Rib3))) - 1
    else:
        outputs["MSTF"] = 0

    if (inputs["Fshearult"] == 0):
        outputs["MSSF"] = 0
    else:
        outputs["MSSF"] = inputs["Fshearult"] / (inputs["FSu"] * Nxy / ta) - 1

    if (outputs["MSSF"] > 10):
        outputs["MSSF"] = 0

    CylSectWeight = 2.0 * 3.14159 * R * tw * L * inputs["rho"]

    outputs["BarrelWeight"] = CylSectWeight * inputs["Number_of_Section"]

    #Calculation for the Dome Section of the Tank.
    a = R - inputs["Pocket_Thickness"]

    dome_height = inputs["Dome_Height"] - inputs["Dome_Thickness"]

    outputs["Volume"] = 2.0 * 0.5 * 1.33333333 * 3.14159 * a**2 * dome_height + 3.14159 * a**2 * inputs["Cylinder_Length"]

    rhof = massf / outputs["Volume"]

    div = 20.0
    IncSize = a / div
    div = int(div)

    MSyld = [0 for i in range(0,div)]
    MSult = [0 for i in range(0,div)]

    for i in range(0,div):
        x = (i - 1) * IncSize
        y = dome_height / a * (a**2 - x**2)**0.5

        ld = a / dome_height * (a**2 - x**2)**0.5

        r2 = (ld**2 + x**2)**0.5
        r1 = r2**3 * dome_height**2 / a**4

        pind = rhof * inputs["g"] * (inputs["LFax"] * (hf - (dome_height - y)) + inputs["LFlat"] * 2.0 * x)
        pdome = pburst - inputs["pamb"] + pind

        sigma1 = pdome * r2 / (2.0 * inputs["Dome_Thickness"]) + inputs["Fuel_Density"] * (2.0 * y + inputs["Cylinder_Length"]) * inputs["g"] * inputs["LFax"]
        sigma2 = (pdome + inputs["Fuel_Density"] * 2.0 * x * inputs["g"] * inputs["LFlat"]) / inputs["Dome_Thickness"] * (r2 - r2**2 / (2.0 * r1))

        if (a == dome_height):
            taumax = sigma1 / 2.0
        else:
            taumax = (sigma1 - sigma2) / 2.0

        VM = (sigma1**2 + sigma2**2 - (sigma1 * sigma2) + 3.0 * taumax**2)**0.5

        if (inputs["Ftenyield"] == 0):
            MSyld[i] = 0.0
        else:
            MSyld[i] = inputs["Ftenyield"] / (inputs["FSy"] * VM) - 1

        if (inputs["Ftenult"] == 0):
            MSult[i] = 0.0
        else:
            MSult[i] = inputs["Ftenult"] / (inputs["FSu"] * VM) - 1

    dome_vol = 0.5 * 1.33333 * 3.14159 * ((a + inputs["Dome_Thickness"])**2 * (dome_height + inputs["Dome_Thickness"]) - a**2 * dome_height)

    outputs["DomeWeight"] = dome_vol * inputs["rho"]
    outputs["TotalWeight"] = outputs["BarrelWeight"] + 2.0 * outputs["DomeWeight"]
    outputs["Tank_Launch_Mass"] = outputs["TotalWeight"] + Fuel_per_Tank

    outputs["MSyld_min"] = min(MSyld)
    outputs["MSult_min"] = min(MSult)

    outputs["Total_Weight_of_Tanks"] = outputs["TotalWeight"] * inputs["Number_Tanks"]

    return outputs


if __name__ == "__main__":
    import time

    t0 = time.time()

    inputs = {}

    #Tank Geometry
    inputs["Isogrid_Height"] = 0.001 #[m]
    inputs["Rib_Height"] = 0.01 #[m]
    inputs["Rib_Thickness"] = 0.01 #[m]
    inputs["Pocket_Thickness"] = 0.0020 #[m]
    inputs["Top_Flange_Thickness"] = 0.001 #[m]
    inputs["Top_Flange_Width"] = 0.001 #[m]
    inputs["Tank_Radius"] = 8.4 / 2.0 #[m]
    inputs["Cylinder_Length"] = 5.5 / 2.0 #[m]
    inputs["Number_of_Section"] = 1 #[]
    inputs["Dome_Thickness"] = 0.00325 #[m]
    inputs["Dome_Height"] = 2.063968 #[m]
    inputs["AR"] = 0.7071 #[]
    inputs["Toggle"] = "Y" #[]
    inputs["Number_Tanks"] = 1 #[]
#
    #Tank Loads
    inputs["Mp"] = 75000.0 #Propellant Mass [kg]
    inputs["Thrust"] = 4.44e6 #[N]
    inputs["Fax"] = 0.1 #Axial Force [N]
    inputs["AxialMass"] = 10.0 #[kg]
    inputs["Mbend"] = 0.01 #Bending Moment [N-m]
    inputs["Fsh"] = 0.001 #[N]
    inputs["Torque"] = 0.001 #[N]
    inputs["Pburst"] = 35.0 #Burst Pressure [psi]
    inputs["LFax"] = 4. #[N]
    inputs["LFlat"] = 2.5 #[N]
    inputs["g"] = 9.80665 #[m/s^2]
    inputs["pamb"] = 0. #[psi]
    inputs["Fuel_Density"] = 71.0 #[kg/m^3]

    #Material Properties -- Al2219-T851
    inputs["E"] = 7.31E10 #[]
    inputs["Ftenult"] = 4.55E8 #[Pa]
    inputs["Fshearult"] = 2.85E8 #[Pa]
    inputs["rho"] = 2840.00 #[kg/m^3]
    inputs["nu"] = 0.33 #[]
    inputs["FSu"] = 1.4 #[]
    inputs["Ftenyield"] = 3.52E8 #[Pa]
    inputs["FSy"] = 1.25 #[]

    outputs = Main(inputs)

    print(outputs)
    print(f"Time elapsed: {round(time.time() - t0, ndigits=5)}s.")
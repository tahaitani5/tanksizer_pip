import math, time
import numpy as np
import scipy.optimize

import TankSizer_no_file_IO as TS

def Main_Minimize_Weight(x_vec, inputs):
    inputs["Isogrid_Height"] = x_vec[0]
    inputs["Rib_Height"] = x_vec[1]
    inputs["Rib_Thickness"] = x_vec[2]
    inputs["Pocket_Thickness"] = x_vec[3]
    inputs["Top_Flange_Thickness"] = x_vec[4]
    inputs["Top_Flange_Width"] = x_vec[5]
    inputs["Dome_Thickness"] = x_vec[6]
    # scale number of cylinder sections based on SLS 6.7 m/section at 8.4 m tank diameter
    num_of_section = int(math.ceil(inputs["Cylinder_Length"] / (6.7 * (inputs["Tank_Radius"] / 4.2))))
    inputs["Number_of_Section"] = num_of_section if num_of_section > 1 else 1

    out = TS.Main(inputs)

    #Get the constraint vector
    constraints = np.array(Constraints(out))

    #Heavily penalize negative (violated) constraints
    for i in range(0, len(constraints)):
        if constraints[i] < 0:
            constraints[i] *= 1000000.0

    #Evaluate the psuedo-objective (penalty) function of f(x) * (sum(g_i(x)^2) + 0.1)
#    val = (out.get("TotalWeight")) * (np.sum(constraints[:] ** 2) + 0.1)
    val = (out.get("TotalWeight")) + (np.sum(constraints[:]**2))
#   val = out.get("TotalWeight")/4679175.0 * (np.sum(constraints[:] ** 2) + 0.1)

    return val


def Calc_Length(cyl_length, inputs):
    inputs["Cylinder_Length"] = cyl_length #Format the input vector

    # scale number of cylinder sections based on SLS 6.7 m/section at 8.4 m tank diameter
    num_of_section = int(math.ceil(inputs["Cylinder_Length"] / (6.7 * (inputs["Tank_Radius"] / 4.2))))
    inputs["Number_of_Section"] = num_of_section if num_of_section > 1 else 1

    outputs = TS.Main(inputs)

    volume_req = inputs["Mp"] / inputs["Fuel_Density"] #volume required
    volume_calc = outputs["Volume"] #Actual Volume

    residual = volume_req - volume_calc #Difference between Required and Actual
    return residual


def Constraints(outputs):
    cons    = [
        outputs.get("MSGenInst"),
        outputs.get("MSSkinBuck"),
        outputs.get("MSRibCrip"),
        outputs.get("MSPockBurst"),
        outputs.get("MSCPB"),
        outputs.get("MSIB"),
        outputs.get("MSTF"),
        outputs.get("MSSF"),
        outputs.get("MSyld_min"),
        outputs.get("MSult_min")
    ]

    return cons


def Main(thrust, f_density, m_p, dia, axial_mass, opt=True):
    """ Set-up inputs """
    #Format initial vector
    inputs = {}
    inputs["Tank_Radius"] = dia / 2.0
    inputs["Mp"] = m_p
    inputs["Thrust"] = thrust
    inputs["AxialMass"] = 0.
    inputs["Fuel_Density"] = f_density

    #Specify constants
    inputs["LFax"] = 4.
    inputs["LFlat"] = 2.5
    inputs["Dome_Height"] = 0.0 #Initialized, but the program calculates this (toggle ="Y")
    inputs["Number_of_Section"] = 1 #Initialized, but will be recalculated based on length
    inputs["Pburst"] = 40.0
    inputs["Torque"] = 0.001
    inputs["Fsh"] =  0.001
    inputs["Fax"] = 0.0
    inputs["Mbend"] = 0.001
    inputs["g"] = 9.80665*3.5
    inputs["pamb"] = 101325.0
    inputs["AR"] = 0.7071
    inputs["Toggle"] = "Y"
    inputs["Number_Tanks"] = 1
    inputs["Tank_Material"] = 0 #0 -> Al2219

    #Initialize cylinder length
    inputs["Cylinder_Length"] = 0.0

    #Initialize variables to optimize on
    inputs["Isogrid_Height"] = 0.250
    inputs["Rib_Height"] = 0.015
    inputs["Rib_Thickness"] = 0.0025
    inputs["Pocket_Thickness"] = 0.0025
    inputs["Top_Flange_Thickness"] = 0.0125
    inputs["Top_Flange_Width"] = 0.025
    inputs["Dome_Thickness"] = 0.00350

    #Material Properties -- Al2219-T851
    inputs["E"] = 7.31E10 #[]
    inputs["Ftenult"] = 4.55E8 #[Pa]
    inputs["Fshearult"] = 2.85E8 #[Pa]
    inputs["rho"] = 2840.00 #[kg/m^3]
    inputs["nu"] = 0.33 #[]
    inputs["FSu"] = 1.4 #[]
    inputs["Ftenyield"] = 3.52E8 #[Pa]
    inputs["FSy"] = 1.25 #[]

    #Calculate Length
    vol_req = m_p / f_density

    #Calculate minimum volume available (two domes)
    length_dome = dia * inputs["AR"]
    vol_two_domes = 4.0/3.0 * math.pi * (dia/2.0)**2 * (length_dome/2.0) #Volume of an ellipse (two domes)

    #Perform vol req vs. minimum vol check
    min_cyl_length = 0.001 #Minimum cylinder length we'll consider
    max_cyl_length = 100 #Maximum cylinder length we'll consider
    if vol_req < vol_two_domes: #If the prop requested is lower than what two domes can provide, then oversize the tank
        inputs["Cylinder_Length"] = min_cyl_length
    else:
#        inputs["Cylinder_Length"] = scipy.optimize.brentq(Calc_Length, min_cyl_length, max_cyl_length,
#                                            args=(inputs,),
#                                            xtol=1e-5,
#                                            maxiter=50)
        inputs["Cylinder_Length"] = scipy.optimize.newton(Calc_Length, min_cyl_length,
                                            args=(inputs,),
                                            tol=1e-5,
                                            maxiter=50)

    if opt:
        """ Format optimizer """
        #List search region bounds
#        bnds = [(0.1, 0.75), #Isogrid_Height
#                (0.0127, 0.0381), #Rib_Height [0.5", 1.5"]
#                (0.00127, 0.00762), #Rib_Thickness [0.005", 0.3"]
#                (0.001, 0.1), #Pocket_Thickness
#                (0.009525, 0.015875), #Top_Flange_Thickness [0.375", 0.625"]
#                (0.0508, 0.0635), #Top_Flange_Width [2", 2.5"]
#                (0.001, 0.15)] #Dome_Thickness

        bnds = [(0.001, 1.0), #Isogrid_Height
                (0.001, 1.0), #Rib_Height [0.5", 1.5"]
                (0.001, 1.0), #Rib_Thickness [0.005", 0.3"]
                (0.001, 1.0), #Pocket_Thickness
                (0.001, 1.0), #Top_Flange_Thickness [0.375", 0.625"]
                (0.001, 1.0), #Top_Flange_Width [2", 2.5"]
                (0.001, 1.0)] #Dome_Thickness

        out_data = scipy.optimize.differential_evolution(Main_Minimize_Weight, bnds,
                                args = (inputs,),
                                popsize=5,
                                tol=1e-5,
                                polish=True,
                                disp=False)

        """ Set the input vector optimizer converged on """
        inputs["Isogrid_Height"] = out_data["x"][0]
        inputs["Rib_Height"] = out_data["x"][1]
        inputs["Rib_Thickness"] = out_data["x"][2]
        inputs["Pocket_Thickness"] = out_data["x"][3]
        inputs["Top_Flange_Thickness"] = out_data["x"][4]
        inputs["Top_Flange_Width"] = out_data["x"][5]
        inputs["Dome_Thickness"] = out_data["x"][6]

    """ Record results """
    outputs = TS.Main(inputs)

    return outputs


if __name__ == "__main__":
    t0 = time.time()

    inputs = {
        "thrust" : 3.34e5, #[N]
        "f_density" : 70.8, #[kg/m^3], LH2
#       "m_p" : 100, #[kg]
        "m_p" : 73100., #[kg]
        "dia" : 8.4, #[m]
        "axial_mass" : 0. #[kg]
    }

    outputs = Main(opt=True, **inputs)
    print(outputs)
    print(f"Time elapsed: {round(time.time() - t0, ndigits=2)}s.")
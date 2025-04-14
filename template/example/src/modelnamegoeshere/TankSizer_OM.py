# -*- coding: utf-8 -*-
"""
@author:
Manuel J. Diaz

TankSizer_no_file_IO re-implemented in OpenMDAO
"""
import copy
import math
import numpy as np
import openmdao.api as om
import openmdao.utils as om_utils

# from sympy import symbols, exp, simplify, diff, om_utils.cs_safe.abs, log, Min, Max,


class TankSizer(om.ExplicitComponent):
    def setup(self):
        for k, v in tanksizer_inputs.items():
            if "units" in v and v["units"] == "psi":
                # if units of psi, convert to Pa
                v_prime = copy.copy(v)
                v_prime["val"] = om.convert_units(v["val"], "psi", "Pa")
                v_prime["units"] = "Pa"
                self.add_input(k, **v_prime)
            else:
                self.add_input(k, **v)
        for k, v in options.items():
            self.options.declare(k, **v)
        for k, v in tanksizer_outputs.items():
            self.add_output(k, **v)

        # calculate all partials:
        # masses depends on all geometric inputs
        # self.declare_partials(of=["BarrelWeight", "DomeWeight", "tank_dry_mass"], wrt="*", method="fd")
        self.declare_partials(of=["BarrelWeight", "DomeWeight", "tank_dry_mass"], wrt="*", method="cs")

        # every MS depends on the geometric inputs
        self.declare_partials(
            of=[
                # "MSGenInst",
                # "MSSkinBuck",
                # "MSRibCrip",
                # "MSCPB",
                # "MSIB",
                "MSPockBurst",
                "MSTF",
                "MSSF",
                "MSyld",
                "MSult",
            ],
            wrt="*",
            # method="fd",
            method="cs",
        )

    def compute(self, inputs, outputs):
        """TankSizer:
        Evaluate equations
        """

        b = inputs["Rib_Thickness"]
        c = inputs["Top_Flange_Thickness"]
        d = inputs["Rib_Height"]
        h = inputs["Isogrid_Height"]
        w = inputs["Top_Flange_Width"]
        t_b = inputs["Pocket_Thickness"]
        t_d = inputs["Dome_Thickness"]
        pburst = inputs["Pburst"]  # * 6894.76  # Converts PSI to Pa
        R = inputs["Tank_Radius"]
        rho = inputs["Fuel_Density"]

        """----- MAIN CALCULATIONS -----"""
        # Calculation for the Barrel Section of the Tank.
        outputs["Propellant_Volume"] = inputs["Mp"] / rho
        if self.options["Toggle"] == "N":
            dome_height = inputs["Dome_Height"]
            hf = inputs["Cylinder_Length"] + 2.0 * dome_height
            outputs["New_Length"] = hf
        else:
            outputs["New_Length"] = inputs["AR"] * 2.0 * R + inputs["Cylinder_Length"]
            hf = outputs["New_Length"]
            inputs["Dome_Height"] = inputs["AR"] * R

        # Eqs 2.1.2 - 2.1.6
        alpha = (b * d) / (t_b * h)
        delta = d / t_b
        lamda = c / t_b
        mu = (w * c) / (t_b * h)
        L = inputs["Cylinder_Length"] / self.options["Number_of_Section"]
        beta = (
            (1 + alpha + mu) * (3.0 * (1 + delta) ** 2 + 3.0 * mu * (1 + lamda) ** 2 + 1 + alpha * delta**2 + mu * lamda**2)
            - 3.0 * ((1 + delta) - mu * (1 + lamda)) ** 2
        ) ** 0.5

        # Eqs 2.1.7 - 2.1.10
        tstar = t_b * beta / (1 + alpha + mu)
        Estar = inputs["E"] * (1 + alpha + mu) ** 2 / beta
        tw = t_b * (1 + 3.0 * alpha + 3.0 * mu)
        ta = t_b * (1 + alpha + mu)

        # Eqs 2.1.11 - 2.1.15
        theta = (R / tstar) ** 0.5 / 16.0
        gamma_a = 1 - 0.901 * (1 - np.exp(-theta))
        gamma_b = 1 - 0.731 * (1 - np.exp(-theta))
        gamma_p = 0.75**2
        gamma_t = (2 / 3) ** (4 / 3)

        # Eq 2.1.16
        Sigma = np.log10((pburst / inputs["E"]) * (R / tstar[0]) ** 2)

        # Eqs 2.1.17 - 2.1.23
        ca = 0.005849492
        cb = 0.01939264
        cc = -0.015507073
        cd = -0.074270883
        ce = 0.073557991
        cf = 0.212422975
        deltagamma = ca * Sigma**5 + cb * Sigma**4 + cc * Sigma**3 + cd * Sigma**2 + ce * Sigma + cf

        # Eqs 2.1.27 - 2.1.29
        Ncr1 = gamma_a * inputs["E"] * t_b**2 * beta / (R * (3.0 * (1 - inputs["nu"] ** 2)) ** 0.5)
        Ncr2 = 10.2 * inputs["E"] * t_b**3 * (1 + alpha + mu) / h**2
        Ncr3 = 0.616 * inputs["E"] * t_b * (1 + alpha + mu) * b**2 / d**2

        # Eqs 2.1.30 - 2.1.34
        Ftu = pburst * R / (t_b * (1 + alpha + mu))
        if pburst > 0:
            Nacr = (Estar * tstar**2 / R) * (
                gamma_a / ((3.0 * (1 - inputs["nu"] ** 2)) ** 0.5) + deltagamma
            ) + pburst * R / 2.0
        else:
            Nacr = (Estar * tstar**2 / R) * (gamma_a / ((3.0 * (1 - inputs["nu"] ** 2)) ** 0.5))
        if pburst > 0:
            Nbcr = (Estar * tstar**2 / R) * (
                gamma_b / ((3.0 * (1 - inputs["nu"] ** 2)) ** 0.5) + deltagamma
            ) + pburst * R / 2.0
        else:
            Nbcr = (Estar * tstar**2 / R) * (gamma_b / ((3.0 * (1 - inputs["nu"] ** 2)) ** 0.5))
        Npcr = 0.855 * R**2 * gamma_p**0.5 * inputs["E"] / (L * (1 - inputs["nu"] ** 2) * (R / tstar) ** 2.5)
        Nscr = (
            0.0885 * gamma_t**0.75 * math.pi**2 * Estar * tstar**2.25 / (L**0.5 * (1 - inputs["nu"] ** 2) ** 0.625 * R**0.75)
        )

        # Eqs 2.1.35 - 2.1.39
        Nxa = (
            inputs["Thrust"]
            + (
                inputs["Fax"]
                + (2.0 * math.pi * R * tw * L * inputs["rho"] + inputs["Mp"] + inputs["AxialMass"]) * (inputs["g"])
            )
            * inputs["LFax"]
        ) / (
            2.0 * math.pi * R
        )  # Axial line load due to axial applied load
        Nxp = -pburst * R / 2  # Axial line load due to pressure applied load
        if (Nxa + Nxp) > 0:
            Nxb = inputs["Mbend"] / (math.pi * R**2)  # Axial line load due to bending moment applied load
        else:
            Nxb = -inputs["Mbend"] / (math.pi * R**2)

        Ncr = Nxa + om_utils.cs_safe.abs(Nxb) + Nxp  # critical line load
        Nxabp = Nxa + Nxb + Nxp  # total axial line load

        # Eq 2.1.40 - 2.1.41
        Nyp = -pburst * R - (
            (2.0 * math.pi * R * tw * L * inputs["rho"] + inputs["Mp"] + inputs["AxialMass"])
            * (inputs["g"])
            * inputs["LFlat"]
        ) / (2.0 * math.pi * R)
        Nxy = ((inputs["Torque"] / R) + inputs["Fsh"]) / (2.0 * math.pi * R)

        # Eqs 2.1.42 - 2.1.47
        SigmaX = Nxabp / ta
        SigmaY = Nyp / ta
        SigmaXY = Nxy / ta
        Rib1 = (3.0 * Nyp - Nxabp) / (3.0 * ta)
        Rib2 = 2.0 * (Nxabp + 3**0.5 * Nxy) / (3.0 * ta)
        Rib3 = 2.0 * (Nxabp - 3**0.5 * Nxy) / (3.0 * ta)

        if Ncr < 0:
            outputs["MSGenInst"] = 0.0
            outputs["MSSkinBuck"] = 0.0
            outputs["MSRibCrip"] = 0.0
            outputs["MSCPB"] = 0.0
            outputs["MSIB"] = 0.0
        else:
            outputs["MSGenInst"] = Ncr1 / (inputs["Fsu"] * Ncr) - 1
            outputs["MSSkinBuck"] = Ncr2 / (inputs["Fsu"] * Ncr) - 1
            outputs["MSRibCrip"] = Ncr3 / (inputs["Fsu"] * Ncr) - 1
            outputs["MSCPB"] = (
                1
                / ((Nxy * inputs["Fsu"] / Nscr) ** 2 + (Nxa + om_utils.cs_safe.abs(Nxb)) * inputs["Fsu"] / Ncr2 + Nyp / Ncr2)
                - 1
            )

            if ((inputs["Fsu"] * om_utils.cs_safe.abs(Nxb) / Nbcr) ** 3.0 + (inputs["Fsu"] * Nxy / Nscr) ** 3.0) < 0:
                temp = (-1) * om_utils.cs_safe.abs(
                    ((inputs["Fsu"] * om_utils.cs_safe.abs(Nxb) / Nbcr) ** 3.0 + (inputs["Fsu"] * Nxy / Nscr) ** 3.0)
                ) ** (1.0 / 3.0)
            else:
                temp = om_utils.cs_safe.abs(
                    ((inputs["Fsu"] * om_utils.cs_safe.abs(Nxb) / Nbcr) ** 3.0 + (inputs["Fsu"] * Nxy / Nscr) ** 3.0)
                ) ** (1.0 / 3.0)

            if pburst > 0:
                outputs["MSIB"] = 1 / (inputs["Fsu"] * Nxa / Nacr + temp) - 1
            else:
                outputs["MSIB"] = 1 / (inputs["Fsu"] * Nxa / Nacr + inputs["Fsu"] * Nyp / Npcr + temp) - 1

        outputs["MSPockBurst"] = inputs["Ftenult"] / (inputs["Fsu"] * om_utils.cs_safe.abs(Ftu)) - 1

        # TODO: get rid of this Boolean
        # Eq 2.1.56
        if min(SigmaX, SigmaY, SigmaXY, Rib1, Rib2, Rib3) < 0:
            outputs["MSTF"] = (
                inputs["Ftenult"] / (inputs["Fsu"] * om_utils.cs_safe.abs(min(SigmaX, SigmaY, SigmaXY, Rib1, Rib2, Rib3)))
                - 1
            )
        else:
            outputs["MSTF"] = 0

        # Eq 2.1.58
        outputs["MSSF"] = inputs["Fshearult"] / (inputs["Fsu"] * Nxy / ta) - 1

        # Eqs 2.1.60 - 2.1.61
        CylSectWeight = 2.0 * math.pi * R * tw * L * inputs["rho"]
        outputs["BarrelWeight"] = CylSectWeight * self.options["Number_of_Section"]

        # Calculation for the Dome Section of the Tank.
        # Eq 2.2.1
        a = R - t_b

        dome_height = inputs["Dome_Height"] - t_d

        # Eq 2.2.3 - 2.2.4
        outputs["Volume"] = 2.0 * 0.5 * 4 / 3 * math.pi * a**2 * dome_height + math.pi * a**2 * inputs["Cylinder_Length"]
        rhof = inputs["Mp"] / outputs["Volume"]

        # Eqs 2.2.5 - 2.2.6
        # div = 20.0
        div = self.options["Number_of_Divisions"]
        IncSize = a / div
        div = int(div)

        MSyld = [None for i in range(0, div)]
        MSult = [None for i in range(0, div)]

        for i in range(0, div):
            # Eqs 2.2.7 - 2.2.11
            x = (i - 1) * IncSize
            y = dome_height / a * (a**2 - x**2) ** 0.5
            ld = a / dome_height * (a**2 - x**2) ** 0.5
            r2 = (ld**2 + x**2) ** 0.5
            r1 = r2**3 * dome_height**2 / a**4

            # Eqs 2.2.12 - 2.2.13
            pind = rhof * inputs["g"] * (inputs["LFax"] * (hf - (dome_height - y)) + inputs["LFlat"] * 2.0 * x)
            pdome = pburst - inputs["pamb"] + pind

            # Eqs 2.2.14 - 2.2.17
            sigma1 = pdome * r2 / (2.0 * t_d) + rho * (2.0 * y + inputs["Cylinder_Length"]) * inputs["g"] * inputs["LFax"]
            sigma2 = (pdome + rho * 2.0 * x * inputs["g"] * inputs["LFlat"]) / t_d * (r2 - r2**2 / (2.0 * r1))
            if a == dome_height:
                taumax = sigma1 / 2.0
            else:
                taumax = (sigma1 - sigma2) / 2.0
            VM = (sigma1**2 + sigma2**2 - (sigma1 * sigma2) + 3.0 * taumax**2) ** 0.5  # von Mises stress

            # Eq 2.2.18 - 2.2.19
            MSyld[i] = inputs["Ftenyield"] / (inputs["Fsy"] * VM) - 1
            MSult[i] = inputs["Ftenult"] / (inputs["Fsu"] * VM) - 1

        # Eqs 2.2.20 - 2.2.21
        outputs["MSyld"] = MSyld
        outputs["MSult"] = MSult

        # Eqs 2.2.22 - 2.2.24
        dome_vol = 0.5 * 4 / 3 * math.pi * ((a + t_d) ** 2 * (dome_height + t_d) - a**2 * dome_height)
        outputs["DomeWeight"] = dome_vol * inputs["rho"]
        outputs["tank_dry_mass"] = outputs["BarrelWeight"] + 2.0 * outputs["DomeWeight"]

        outputs["Tank_gross_mass"] = outputs["tank_dry_mass"] + inputs["Mp"]
        # outputs["Total_Weight_of_Tanks"] = outputs["tank_dry_mass"] * self.options["Number_Tanks"]

        return outputs


tanksizer_inputs = {}
# Tank Geometry -- design varibles:
tanksizer_inputs["Isogrid_Height"] = {"val": 0.5, "units": "m", "desc": ""}  # h [m]
tanksizer_inputs["Rib_Height"] = {"val": 0.005, "units": "m", "desc": ""}  # d [m]
tanksizer_inputs["Rib_Thickness"] = {"val": 0.005, "units": "m", "desc": ""}  # b [m]
tanksizer_inputs["Pocket_Thickness"] = {"val": 0.005, "units": "m", "desc": ""}  # tb [m]
tanksizer_inputs["Top_Flange_Thickness"] = {"val": 0.005, "units": "m", "desc": ""}  # c [m]
tanksizer_inputs["Top_Flange_Width"] = {"val": 0.005, "units": "m", "desc": ""}  # w [m]
tanksizer_inputs["Dome_Thickness"] = {"val": 0.005, "units": "m", "desc": ""}  # td [m]
# Tank Geometry -- outer mold line geometric parameters:
tanksizer_inputs["Tank_Radius"] = {"val": 4.13, "units": "m", "desc": ""}  # [m]
tanksizer_inputs["Cylinder_Length"] = {"val": 6.0, "units": "m", "desc": ""}  # [m]
tanksizer_inputs["Dome_Height"] = {"val": 2.063968, "units": "m", "desc": ""}  # [m]
tanksizer_inputs["AR"] = {"val": 0.7071, "desc": ""}  # []
# Tank Loads (fixed):
tanksizer_inputs["Mp"] = {"val": 26061.0, "units": "kg", "desc": ""}  # Propellant Mass [kg]
tanksizer_inputs["Thrust"] = {"val": 1000.0, "units": "N", "desc": ""}  # [N]
tanksizer_inputs["Fax"] = {"val": 0.0, "units": "N", "desc": ""}  # Axial Force [N]
tanksizer_inputs["AxialMass"] = {"val": 10.0, "units": "kg", "desc": ""}  # [kg]
tanksizer_inputs["Mbend"] = {"val": 0.01, "units": "N*m", "desc": ""}  # Bending Moment [N-m]
tanksizer_inputs["Fsh"] = {"val": 0.01, "units": "N", "desc": ""}  # [N]
tanksizer_inputs["Torque"] = {"val": 0.01, "units": "N*m", "desc": ""}  # [N]
tanksizer_inputs["Pburst"] = {"val": 35.0, "units": "psi", "desc": ""}  # Burst Pressure [psi]
tanksizer_inputs["LFax"] = {"val": 4.0, "desc": ""}  # axial g's[]
tanksizer_inputs["LFlat"] = {"val": 2.5, "desc": ""}  # lateral g's []
tanksizer_inputs["g"] = {"val": 9.80665, "units": "m/s**2", "desc": ""}  # [m/s^2]
tanksizer_inputs["pamb"] = {"val": 0.0, "units": "psi", "desc": ""}  # [psi]
tanksizer_inputs["Fuel_Density"] = {"val": 71.0, "units": "kg/m**3", "desc": ""}  # [kg/m^3]
# Material Properties (fixed) -- Al2219-T851:
tanksizer_inputs["E"] = {"val": 7.31e10, "units": "Pa", "desc": "Modulus of Elasticity"}  # [Pa]
tanksizer_inputs["Ftenult"] = {"val": 4.55e8, "units": "Pa", "desc": "Ultimate Allowable Limit"}  # [Pa]
tanksizer_inputs["Fshearult"] = {"val": 2.85e8, "units": "Pa", "desc": "Ultimate Shear Limit"}  # [Pa]
tanksizer_inputs["rho"] = {"val": 2840.00, "units": "kg/m**3", "desc": "material density"}  # [kg/m^3]
tanksizer_inputs["nu"] = {"val": 0.33, "desc": "Poisson's Ratio"}  # []
tanksizer_inputs["Fsu"] = {"val": 1.4, "desc": "Ultimate Factor of Safety"}  # []
tanksizer_inputs["Ftenyield"] = {"val": 3.52e8, "units": "Pa", "desc": "Yield Ultimate Limit "}  # [Pa]
tanksizer_inputs["Fsy"] = {"val": 1.25, "desc": "Yield Factor of Safety"}  # []

options = {}
# Tank options (fixed):
options["Toggle"] = {"default": "N", "desc": "", "values": ["Y", "N"]}  # []
options["Number_of_Section"] = {"default": 1, "desc": "Number of barrel sections", "lower": 1}  # []
options["Number_of_Divisions"] = {
    "default": 20,
    "desc": "Number of divisions along the tank's axis to evaluate safety margins",
    "lower": 1,
}  # []
# options["Number_Tanks"] = {'default':1, 'desc':""} #[]

tanksizer_outputs = {}
# new calculations:
tanksizer_outputs["Propellant_Volume"] = {"val": 1.0, "units": "m**3", "desc": ""}
tanksizer_outputs["New_Length"] = {"val": 1.0, "units": "m", "desc": ""}
# margins of safety:
tanksizer_outputs["MSGenInst"] = {"val": 1.0, "desc": ""}
tanksizer_outputs["MSSkinBuck"] = {"val": 1.0, "desc": ""}
tanksizer_outputs["MSRibCrip"] = {"val": 1.0, "desc": ""}
tanksizer_outputs["MSCPB"] = {"val": 1.0, "desc": ""}
tanksizer_outputs["MSIB"] = {"val": 1.0, "desc": ""}
tanksizer_outputs["MSPockBurst"] = {"val": 1.0, "desc": ""}
tanksizer_outputs["MSTF"] = {"val": 1.0, "desc": ""}
tanksizer_outputs["MSSF"] = {"val": 1.0, "desc": ""}
tanksizer_outputs["MSyld"] = {"val": np.ones(options["Number_of_Divisions"]["default"]), "desc": ""}
tanksizer_outputs["MSult"] = {"val": np.ones(options["Number_of_Divisions"]["default"]), "desc": ""}
# mass:
tanksizer_outputs["BarrelWeight"] = {"val": 1.0, "units": "kg", "desc": ""}
tanksizer_outputs["Volume"] = {"val": 1.0, "units": "m**3", "desc": ""}
tanksizer_outputs["DomeWeight"] = {"val": 1.0, "units": "kg", "desc": ""}
tanksizer_outputs["tank_dry_mass"] = {"val": 1.0, "units": "kg", "desc": ""}
tanksizer_outputs["Tank_gross_mass"] = {"val": 1.0, "units": "kg", "desc": ""}
# outputs["Total_Weight_of_Tanks"] = {'val':1.0, 'units':'kg', 'desc':""}


if __name__ == "__main__":
    import time

    t0 = time.time()

    prob = om.Problem()
    prob.model.add_subsystem("tanksizer", TankSizer(), promotes=["*"])

    # prob.driver = om.ScipyOptimizeDriver()
    prob.driver = om.pyOptSparseDriver()
    prob.driver.options["optimizer"] = "SLSQP"
    prob.driver.opt_settings["ACC"] = 1e-6  # TODO: which tolerance is this?

    # add design variables
    prob.model.add_design_var("Isogrid_Height", lower=0.001, scaler=1e3)  # h
    prob.model.add_design_var("Rib_Height", lower=0.0, upper=1.0)  # d
    prob.model.add_design_var("Rib_Thickness", lower=0.0, upper=1.0)  # b
    prob.model.add_design_var("Pocket_Thickness", lower=0.001, upper=0.1, ref0=0.001, ref=0.1)  # t_b
    prob.model.add_design_var("Top_Flange_Thickness", lower=0.0, upper=1.0)  # c
    prob.model.add_design_var("Top_Flange_Width", lower=0.0, upper=1.0)  # w
    prob.model.add_design_var("Dome_Thickness", lower=0.001, upper=0.1, ref0=0.001, ref=0.1)  # t_d

    # add inequality constraints
    # prob.model.add_constraint("MSGenInst", lower=0.0)
    # prob.model.add_constraint("MSSkinBuck", lower=0.0)
    # prob.model.add_constraint("MSRibCrip", lower=0.0)
    # prob.model.add_constraint("MSCPB", lower=0.0)
    # prob.model.add_constraint("MSIB", lower=0.0)
    prob.model.add_constraint("MSPockBurst", lower=0.0, scaler=1e-3)
    prob.model.add_constraint("MSTF", lower=0.0)
    prob.model.add_constraint("MSSF", lower=0.0, scaler=1e-3)
    prob.model.add_constraint("MSyld", lower=0.0)  # , scaler=1e-3)
    prob.model.add_constraint("MSult", lower=0.0)  # , scaler=1e-3)

    # minimize the objective
    # prob.model.add_objective("tanksizer.tank_dry_mass")
    prob.model.add_objective("tank_dry_mass", scaler=1e-3)

    # set-up and solve
    prob.setup()
    prob.run_model()

    # report initial results
    print("----------", "Initial guess", "----------")
    for k in tanksizer_outputs.keys():
        print(k, prob.get_val(f"tanksizer.{k}"), tanksizer_outputs[k]["units"] if "units" in tanksizer_outputs[k] else "")
    print("obj", prob.get_val("tanksizer.tank_dry_mass"))

    print("----------", "Converged results", "----------")
    result = prob.run_driver()
    prob.model.list_inputs(val=True, units=True)
    prob.model.list_outputs(val=True, units=True)
    prob.driver.scaling_report(show_browser=False)
    # jac = prob.compute_totals()
    # print("jacobian", jac)

    print("tank PMF:", 1 - prob.get_val("tanksizer.tank_dry_mass") / prob.get_val("tanksizer.Tank_gross_mass"))

    print(f"Time elapsed: {round(time.time() - t0, ndigits=5)}s.")

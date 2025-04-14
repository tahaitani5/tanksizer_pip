# -*- coding: utf-8 -*-
"""
@author:
Manuel J. Diaz

TankSizer_no_file_IO re-implemented in OpenMDAO
"""
import copy
import jax.numpy as np
import openmdao.api as om
import jax.numpy as jnp
import openmdao.jax as omj


Debug=True
class TankSizer(om.JaxExplicitComponent):
    def initialize(self):
        self.options['default_shape']=()
    def setup(self):
        self.options['use_jit']=not (Debug)
        for k, v in tanksizer_.items():
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
        

    # def compute_partials(self,,partials):
    #     jax_ = {key: jnp.array([key]) for key in }
    #     def compute_outputs():
    #         outputs=self.calculate()
    #         return {key:jnp.array(value) for key,value in outputs.items()}
    #     partials= jacfwd(compute_outputs)(jax_)

    def compute_primal(self,Isogrid_Height, Rib_Height,Rib_Thickness,Pocket_Thickness, Top_Flange_Thickness, Top_Flange_Width, Dome_Thickness, Tank_Radius, Cylinder_Length, Dome_Height, AR, Mp, Thrust, Fax, AxialMass, Mbend, Fsh, Torque, Pburst, LFax, LFlat, g, pamb, Fuel_Density, E, Ftenult, Fshearult, rho, nu, Fsu, Ftenyield, Fsy):
        """TankSizer:
        Evaluate equations
        """

        b = Rib_Thickness
        c = Top_Flange_Thickness
        d = Rib_Height
        h = Isogrid_Height
        w = Top_Flange_Width
        t_b = Pocket_Thickness
        t_d = Dome_Thickness
        pburst = Pburst # * 6894.76  # Converts PSI to Pa
        R = Tank_Radius
        # rho = Fuel_Density
        # outputs={}


        """----- MAIN CALCULATIONS -----"""
        # Calculation for the Barrel Section of the Tank.
        Propellant_Volume = Mp / Fuel_Density
        if self.options["Toggle"] == "N":
            dome_height = Dome_Height
            hf = Cylinder_Length + 2.0 * dome_height
            New_Length= hf
        else:
            New_Length = AR * 2.0 * R + Cylinder_Length
            hf = New_Length
            Dome_Height = AR * R

        # Eqs 2.1.2 - 2.1.6
        alpha = (b * d) / (t_b * h)
        delta = d / t_b
        lamda = c / t_b
        mu = (w * c) / (t_b * h)
        L = Cylinder_Length / self.options["Number_of_Section"]
        beta = (
            (1 + alpha + mu) * (3.0 * (1 + delta) ** 2 + 3.0 * mu * (1 + lamda) ** 2 + 1 + alpha * delta**2 + mu * lamda**2)
            - 3.0 * ((1 + delta) - mu * (1 + lamda)) ** 2
        ) ** 0.5

        # Eqs 2.1.7 - 2.1.10
        tstar = t_b * beta / (1 + alpha + mu)
        Estar = E * (1 + alpha + mu) ** 2 / beta
        tw = t_b * (1 + 3.0 * alpha + 3.0 * mu)
        ta = t_b * (1 + alpha + mu)

        # Eqs 2.1.11 - 2.1.15
        theta = (R / tstar) ** 0.5 / 16.0
        gamma_a =1 - 0.901 * (1 - jnp.exp(-theta))
        gamma_b = 1 - 0.731 * (1 - jnp.exp(-theta))
        gamma_p = 0.75**2
        gamma_t = (2 / 3) ** (4 / 3)

        # Eq 2.1.16
        Sigma = jnp.log10((pburst / E) * (R / tstar) ** 2)


        # Eqs 2.1.17 - 2.1.23
        ca = 0.005849492
        cb = 0.01939264
        cc = -0.015507073
        cd = -0.074270883
        ce = 0.073557991
        cf = 0.212422975
        deltagamma = ca * Sigma**5 + cb * Sigma**4 + cc * Sigma**3 + cd * Sigma**2 + ce * Sigma + cf

        # Eqs 2.1.27 - 2.1.29
        Ncr1 = gamma_a * E * t_b**2 * beta / (R * (3.0 * (1 - nu ** 2)) ** 0.5)
        Ncr2 = 10.2 * E * t_b**3 * (1 + alpha + mu) / h**2
        Ncr3 = 0.616 * E * t_b * (1 + alpha + mu) * b**2 / d**2

        # Eqs 2.1.30 - 2.1.34
        Ftu = pburst * R / (t_b * (1 + alpha + mu))
        Nacr =jnp.where(
            pburst > 0,
            (Estar * tstar**2 / R) * ( gamma_a / ((3.0 * (1 - nu ** 2)) ** 0.5) + deltagamma ) + pburst * R / 2.0,
            (Estar * tstar**2 / R) * (gamma_a / ((3.0 * (1 - nu ** 2)) ** 0.5)))
        
        Nbcr =jnp.where(
            pburst > 0,
            (Estar * tstar**2 / R) * (gamma_b / ((3.0 * (1 - nu ** 2)) ** 0.5) + deltagamma) + pburst * R / 2.0,
            (Estar * tstar**2 / R) * (gamma_b / ((3.0 * (1 - nu ** 2)) ** 0.5)))
        Npcr = 0.855 * R**2 * gamma_p**0.5 * E / (L * (1 - nu ** 2) * (R / tstar) ** 2.5)
        Nscr = (
            0.0885 * gamma_t**0.75 * jnp.pi**2 * Estar * tstar**2.25 / (L**0.5 * (1 - nu ** 2) ** 0.625 * R**0.75)
        )

        # Eqs 2.1.35 - 2.1.39

        Nxa = (
            Thrust+ (Fax+ (2.0 * jnp.pi * R * tw * L * rho + Mp + AxialMass)* g)* LFax
        ) / (
            2.0 * jnp.pi * R
        )  # Axial line load due to axial applied load
        Nxp = -pburst * R / 2  # Axial line load due to pressure applied load
        Nxb=jnp.where(
            (Nxa + Nxp) > 0,
            Mbend / (jnp.pi * R**2) ,# Axial line load due to bending moment applied load
           -(Mbend) / (jnp.pi * R**2))

        Ncr = Nxa + jnp.abs(Nxb) + Nxp  # critical line load


        Nxabp = Nxa + Nxb + Nxp  # total axial line load

        # Eq 2.1.40 - 2.1.41
        Nyp = -pburst * R - (
            (2.0 * jnp.pi * R * tw * L * rho + Mp + AxialMass)
            * (g)
            * LFlat
        ) / (2.0 * jnp.pi * R)
        Nxy = ((Torque/ R) + Fsh) / (2.0 * jnp.pi * R)

        # Eqs 2.1.42 - 2.1.47
        SigmaX = Nxabp / ta
        SigmaY = Nyp / ta
        SigmaXY = Nxy / ta
        Rib1 = (3.0 * Nyp - Nxabp) / (3.0 * ta)
        Rib2 = 2.0 * (Nxabp + 3**0.5 * Nxy) / (3.0 * ta)
        Rib3 = 2.0 * (Nxabp - 3**0.5 * Nxy) / (3.0 * ta)

        MSGenInst = jnp.where(Ncr < 0,0.0,Ncr1 / (Fsu * Ncr) - 1)
        MSSkinBuck = jnp.where(Ncr < 0,0.0,Ncr2 / (Fsu * Ncr) - 1)
        MSRibCrip =jnp.where(Ncr < 0,0.0,Ncr3 / (Fsu * Ncr) - 1)
        MSCPB =jnp.where(Ncr < 0, 0.0,( 1/ ((Nxy * Fsu / Nscr) ** 2 + (Nxa + jnp.abs(Nxb)) * Fsu / Ncr2 + Nyp / Ncr2))- 1)
        temp_exp=(Fsu * jnp.abs(Nxb) / Nbcr) ** 3.0 + (Fsu * Nxy / Nscr) ** 3.0
        temp=jnp.where(Ncr<0.0,0,jnp.where(temp_exp<0,(-1) * jnp.abs(temp_exp) ** (1.0 / 3.0),jnp.abs(temp_exp)** (1.0 / 3.0)))
        MSIB = jnp.where(Ncr<0,0,jnp.where(pburst > 0, 1 / (Fsu * Nxa / Nacr + temp) - 1,1 / (Fsu * Nxa / Nacr + Fsu * Nyp / Npcr + temp) - 1))



                

        MSPockBurst = Ftenult / (Fsu * omj.smooth_abs(Ftu)) - 1


        # TODO: get rid of this Boolean
        # Eq 2.1.56
        min_sigma=omj.ks_min([SigmaX, SigmaY, SigmaXY, Rib1, Rib2, Rib3])
        MSTF = jnp.where(min_sigma < 0,
               Ftenult / (Fsu* omj.smooth_abs(min(SigmaX, SigmaY, SigmaXY, Rib1, Rib2, Rib3),mu=0.1))
                -1,0)

       

        # Eq 2.1.58
        MSSF = Fshearult / (Fsu * Nxy / ta) - 1


        # Eqs 2.1.60 - 2.1.61
        CylSectWeight = 2.0 * jnp.pi * R * tw * L * rho
        BarrelWeight = CylSectWeight *self.options["Number_of_Section"]


        # Calculation for the Dome Section of the Tank.
        # Eq 2.2.1
        a = R - t_b

        dome_height = Dome_Height - t_d

        # Eq 2.2.3 - 2.2.4
        Volume= 2.0 * 0.5 * 4 / 3 * jnp.pi * a**2 * dome_height + jnp.pi * a**2 * Cylinder_Length
        rhof = Mp/ Volume

        # Eqs 2.2.5 - 2.2.6
        # div = 20.0
        div = self.options["Number_of_Divisions"]
        IncSize = a / div
        div = int(div)

        MSyld = jnp.zeros(div)
        MSult =jnp.zeros(div)

        i_val=jnp.arange(0,div)
        # for i in range(0, div):
            # Eqs 2.2.7 - 2.2.11
        x = (i_val - 1) * IncSize
        y = dome_height / a * (a**2 - x**2) ** 0.5
        ld = a / dome_height * (a**2 - x**2) ** 0.5
        r2 = (ld**2 + x**2) ** 0.5
        r1 = r2**3 * dome_height**2 / a**4

        # Eqs 2.2.12 - 2.2.13
        pind = rhof * g* (LFax * (hf - (dome_height - y)) + LFlat * 2.0 * x)
        pdome = pburst - pamb + pind

        # Eqs 2.2.14 - 2.2.17
        sigma1 = pdome * r2 / (2.0 * t_d) + Fuel_Density * (2.0 * y + Cylinder_Length) * g * LFax
        sigma2 = (pdome + Fuel_Density * 2.0 * x * g* LFlat) / t_d * (r2 - r2**2 / (2.0 * r1))
        taumax = jnp.where(a == dome_height,sigma1 / 2.0, (sigma1 - sigma2) / 2.0)
        VM = (sigma1**2 + sigma2**2 - (sigma1 * sigma2) + 3.0 * taumax**2) ** 0.5  # von Mises stress

        # Eq 2.2.18 - 2.2.19
        MSyld = Ftenyield / (Fsy * VM) - 1

        MSult = Ftenult/ (Fsu * VM) - 1

        # # Eqs 2.2.20 - 2.2.21
        # MSyld = MSyld
        # MSult = MSult

        # Eqs 2.2.22 - 2.2.24
        dome_vol = 0.5 * 4 / 3 * jnp.pi * ((a + t_d) ** 2 * (dome_height + t_d) - a**2 * dome_height)

        DomeWeight = dome_vol * rho
        
        tank_dry_mass = BarrelWeight + 2.0 *DomeWeight

        Tank_gross_mass = tank_dry_mass + Mp

        return Propellant_Volume,New_Length,MSGenInst,MSSkinBuck,MSRibCrip,MSCPB,MSIB,MSPockBurst,MSTF,MSSF,MSyld,MSult,BarrelWeight,Volume,DomeWeight,tank_dry_mass,Tank_gross_mass
    
tanksizer_ = {}
# Tank Geometry -- design varibles:
tanksizer_["Isogrid_Height"] = {"val": 0.5, "units": "m", "desc": ""}  # h [m]
tanksizer_["Rib_Height"] = {"val": 0.005, "units": "m", "desc": ""}  # d [m]
tanksizer_["Rib_Thickness"] = {"val": 0.005, "units": "m", "desc": ""}  # b [m]
tanksizer_["Pocket_Thickness"] = {"val": 0.005, "units": "m", "desc": ""}  # tb [m]
tanksizer_["Top_Flange_Thickness"] = {"val": 0.005, "units": "m", "desc": ""}  # c [m]
tanksizer_["Top_Flange_Width"] = {"val": 0.005, "units": "m", "desc": ""}  # w [m]
tanksizer_["Dome_Thickness"] = {"val": 0.005, "units": "m", "desc": ""}  # td [m]
# Tank Geometry -- outer mold line geometric parameters:
tanksizer_["Tank_Radius"] = {"val": 4.13, "units": "m", "desc": ""}  # [m]
tanksizer_["Cylinder_Length"] = {"val": 6.0, "units": "m", "desc": ""}  # [m]
tanksizer_["Dome_Height"] = {"val": 2.063968, "units": "m", "desc": ""}  # [m]
tanksizer_["AR"] = {"val": 0.7071, "desc": ""}  # []
# Tank Loads (fixed):
tanksizer_["Mp"] = {"val": 26061.0, "units": "kg", "desc": ""}  # Propellant Mass [kg]
tanksizer_["Thrust"] = {"val": 1000.0, "units": "N", "desc": ""}  # [N]
tanksizer_["Fax"] = {"val": 0.0, "units": "N", "desc": ""}  # Axial Force [N]
tanksizer_["AxialMass"] = {"val": 10.0, "units": "kg", "desc": ""}  # [kg]
tanksizer_["Mbend"] = {"val": 0.01, "units": "N*m", "desc": ""}  # Bending Moment [N-m]
tanksizer_["Fsh"] = {"val": 0.01, "units": "N", "desc": ""}  # [N]
tanksizer_["Torque"] = {"val": 0.01, "units": "N*m", "desc": ""}  # [N]
tanksizer_["Pburst"] = {"val": 35.0, "units": "psi", "desc": ""}  # Burst Pressure [psi]
tanksizer_["LFax"] = {"val": 4.0, "desc": ""}  # axial g's[]
tanksizer_["LFlat"] = {"val": 2.5, "desc": ""}  # lateral g's []
tanksizer_["g"] = {"val": 9.80665, "units": "m/s**2", "desc": ""}  # [m/s^2]
tanksizer_["pamb"] = {"val": 0.0, "units": "psi", "desc": ""}  # [psi]
tanksizer_["Fuel_Density"] = {"val": 71.0, "units": "kg/m**3", "desc": ""}  # [kg/m^3]
# Material Properties (fixed) -- Al2219-T851:
tanksizer_["E"] = {"val": 7.31e10, "units": "Pa", "desc": "Modulus of Elasticity"}  # [Pa]
tanksizer_["Ftenult"] = {"val": 4.55e8, "units": "Pa", "desc": "Ultimate Allowable Limit"}  # [Pa]
tanksizer_["Fshearult"] = {"val": 2.85e8, "units": "Pa", "desc": "Ultimate Shear Limit"}  # [Pa]
tanksizer_["rho"] = {"val": 2840.00, "units": "kg/m**3", "desc": "material density"}  # [kg/m^3]
tanksizer_["nu"] = {"val": 0.33, "desc": "Poisson's Ratio"}  # []
tanksizer_["Fsu"] = {"val": 1.4, "desc": "Ultimate Factor of Safety"}  # []
tanksizer_["Ftenyield"] = {"val": 3.52e8, "units": "Pa", "desc": "Yield Ultimate Limit "}  # [Pa]
tanksizer_["Fsy"] = {"val": 1.25, "desc": "Yield Factor of Safety"}  # []
# tanksizer_["Toggle"]={"val":"N", "desc":""}
# tanksizer_["Number_of_Section"]={"val":1,"desc":""}
# tanksizer_["Number_of_Divisions"]={"val":20, "desc":""}
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

    # # report initial results
    print("----------", "Initial guess", "----------")
    for k in tanksizer_outputs.keys():
        print(k, prob.get_val(f"tanksizer.{k}"), tanksizer_outputs[k]["units"] if "units" in tanksizer_outputs[k] else "")
    print("obj", prob.get_val("tanksizer.tank_dry_mass"))

    print("----------", "Converged results", "----------")
    result = prob.run_driver()
    prob.model.list_inputs(val=True, units=True)
    prob.model.list_outputs(val=True, units=True)
    prob.driver.scaling_report(show_browser=True)
    # prob.check_partials(compact_print=True)
    # jac = prob.compute_totals()
    # print("jacobian", jac)

    print("tank PMF:", 1 - prob.get_val("tanksizer.tank_dry_mass") / prob.get_val("tanksizer.Tank_gross_mass"))

    print(f"Time elapsed: {round(time.time() - t0, ndigits=5)}s.")

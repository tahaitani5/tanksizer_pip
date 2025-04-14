import unittest
from ..TankSizer_OM import tanksizer_inputs, options, tanksizer_outputs, TankSizer


class Test_TankSizer_OM(unittest.TestCase):
    def test_sanity_check(self):
        """Can things can be imported and initialized?"""
        self.assertEqual(1, 1)

    def test_import_openmdao(self):
        """Can openmdao be imported?"""
        import openmdao.api as om

    def test_import_numpy(self):
        """Can numpy be imported and is it version 1.*?"""
        import numpy as np

        self.assertEqual(np.__version__.split(".")[0], "1")

    def test_known_case(self):
        """Given a known case and result, are they reproduced?"""

        import openmdao.api as om
        import numpy as np

        """ Known case's parameters """
        # tanksizer_inputs = {}
        # Tank Geometry -- design varibles:
        tanksizer_inputs["Isogrid_Height"]["val"] = 0.5  # h [m]
        tanksizer_inputs["Rib_Height"]["val"] = 0.005  # d [m]
        tanksizer_inputs["Rib_Thickness"]["val"] = 0.005  # b [m]
        tanksizer_inputs["Pocket_Thickness"]["val"] = 0.005  # tb [m]
        tanksizer_inputs["Top_Flange_Thickness"]["val"] = 0.005  # c [m]
        tanksizer_inputs["Top_Flange_Width"]["val"] = 0.005  # w [m]
        tanksizer_inputs["Dome_Thickness"]["val"] = 0.005  # td [m]
        # Tank Geometry -- outer mold line geometric parameters:
        tanksizer_inputs["Tank_Radius"]["val"] = 4.13  # [m]
        tanksizer_inputs["Cylinder_Length"]["val"] = 6.0  # [m]
        tanksizer_inputs["Dome_Height"]["val"] = 2.063968  # [m]
        tanksizer_inputs["AR"]["val"] = 0.7071  # []
        # Tank Loads (fixed):
        tanksizer_inputs["Mp"]["val"] = 26061.0  # Propellant Mass [kg]
        tanksizer_inputs["Thrust"]["val"] = 1000.0  # [N]
        tanksizer_inputs["Fax"]["val"] = 0.0  # Axial Force [N]
        tanksizer_inputs["AxialMass"]["val"] = 10.0  # [kg]
        tanksizer_inputs["Mbend"]["val"] = 0.01  # Bending Moment [N-m]
        tanksizer_inputs["Fsh"]["val"] = 0.01  # [N]
        tanksizer_inputs["Torque"]["val"] = 0.01  # [N]
        tanksizer_inputs["Pburst"]["val"] = 35.0  # Burst Pressure [psi]
        tanksizer_inputs["LFax"]["val"] = 4.0  # axial g's[]
        tanksizer_inputs["LFlat"]["val"] = 2.5  # lateral g's []
        tanksizer_inputs["g"]["val"] = 9.80665  # [m/s^2]
        tanksizer_inputs["pamb"]["val"] = 0.0  # [psi]
        tanksizer_inputs["Fuel_Density"]["val"] = 71.0  # [kg/m^3]
        # Material Properties (fixed) -- Al2219-T851:
        tanksizer_inputs["E"]["val"] = 7.31e10  # [Pa]
        tanksizer_inputs["Ftenult"]["val"] = 4.55e8  # [Pa]
        tanksizer_inputs["Fshearult"]["val"] = 2.85e8  # [Pa]
        tanksizer_inputs["rho"]["val"] = 2840.00  # [kg/m^3]
        tanksizer_inputs["nu"]["val"] = 0.33  # []
        tanksizer_inputs["Fsu"]["val"] = 1.4  # []
        tanksizer_inputs["Ftenyield"]["val"] = 3.52e8  # [Pa]
        tanksizer_inputs["Fsy"]["val"] = 1.25  # []

        # options = {}
        # Tank options (fixed):
        options["Toggle"]["default"] = "N"  # []
        options["Number_of_Section"]["default"] = 1  # []
        options["Number_of_Divisions"]["default"] = 20  # []

        # tanksizer_outputs = {}
        # new calculations:
        tanksizer_outputs["Propellant_Volume"]["val"] = 1.0
        tanksizer_outputs["New_Length"]["val"] = 1.0
        # margins of safety:
        tanksizer_outputs["MSGenInst"]["val"] = 1.0
        tanksizer_outputs["MSSkinBuck"]["val"] = 1.0
        tanksizer_outputs["MSRibCrip"]["val"] = 1.0
        tanksizer_outputs["MSCPB"]["val"] = 1.0
        tanksizer_outputs["MSIB"]["val"] = 1.0
        tanksizer_outputs["MSPockBurst"]["val"] = 1.0
        tanksizer_outputs["MSTF"]["val"] = 1.0
        tanksizer_outputs["MSSF"]["val"] = 1.0
        tanksizer_outputs["MSyld"]["val"] = np.ones(options["Number_of_Divisions"]["default"])
        tanksizer_outputs["MSult"]["val"] = np.ones(options["Number_of_Divisions"]["default"])
        # mass:
        tanksizer_outputs["BarrelWeight"]["val"] = 1.0
        tanksizer_outputs["Volume"]["val"] = 1.0
        tanksizer_outputs["DomeWeight"]["val"] = 1.0
        tanksizer_outputs["tank_dry_mass"]["val"] = 1.0
        tanksizer_outputs["Tank_gross_mass"]["val"] = 1.0
        # outputs["Total_Weight_of_Tanks"] = {'val':1.0, 'units':'kg', 'desc':""}

        """ Run the known case """
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
        prob.run_driver()
        prob.model.list_inputs(val=True, units=True)
        prob.model.list_outputs(val=True, units=True)

        self.assertAlmostEqual(prob.get_val("tanksizer.tank_dry_mass")[0], 3356.68578167, places=1)

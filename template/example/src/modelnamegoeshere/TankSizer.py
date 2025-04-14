import os
import subprocess
import platform

def Write_Input_File(cwd, Isogrid_Height, Rib_Height, Rib_Thickness, Skin_Thickness, Flange_Thickness, Flange_Width, Tank_Radius, Cylinder_Length, Number_of_Section, Dome_Thickness, Dome_Height, AR, Toggle, Number_Tanks, Tank_Material, Mp, Thrust, Fax, AxialMass, Mbend, Fsh, Torque, Pburst, LFax, LFlat, g, pamb, Fuel_Density):
# This def writes the input file into the directory
# NOTE: Toggle must be entered as either "Y" or "N" for Propellant_Tank.exe to run
#	try:
#		os.remove(os.path.join(cwd, "Output_Deck.txt"))
#	except OSError:
#		pass

	os.remove(os.path.join(cwd, "Output_Deck.txt"))

	data = []
	data.append("&Tank_Geometry")
	data.append(f"	 Isogrid_Height = {Isogrid_Height}")
	data.append(f"	 Rib_Height = {Rib_Height}")
	data.append(f"	 Rib_Thickness = {Rib_Thickness}")
	data.append(f"	 Pocket_Thickness = {Skin_Thickness}")
	data.append(f"	 Top_Flange_Thickness = {Flange_Thickness}")
	data.append(f"	 Top_Flange_Width = {Flange_Width}")
	data.append(f"	 Tank_Radius = {Tank_Radius}")
	data.append(f"	 Cylinder_Length = {Cylinder_Length}")
	data.append(f"	 Number_of_Section = {Number_of_Section}")
	data.append(f"	 Dome_Thickness = {Dome_Thickness}")
	data.append(f"	 Dome_Height= {Dome_Height}")
	data.append(f"	 Aspect_Ratio = {AR}")
	data.append(f"	 Toggle = \"{Toggle}\"")
	data.append(f"	 Number_of_Tanks = {Number_Tanks}")
	data.append("/")
	data.append("&Tank_Materials")
	data.append(f"	 Tank_Material = {Tank_Material}")
	data.append("/")
	data.append("&Tank_Loads")
	data.append(f"	 Propellant = {Mp}")
	data.append(f"	 Thrust = {Thrust}")
	data.append(f"	 Fax = {Fax}")
	data.append(f"	 AxialMass = {AxialMass}")
	data.append(f"	 Mbend = {Mbend}")
	data.append(f"	 Fsh = {Fsh}")
	data.append(f"	 Torque = {Torque}")
	data.append(f"	 Pburst = {Pburst}")
	data.append(f"	 LFax = {LFax}")
	data.append(f"	 LFlat = {LFlat}")
	data.append(f"	 g = {g}")
	data.append(f"	 pamb = {pamb}")
	data.append(f"	 Fuel_Density = {Fuel_Density}")
	data.append("/")
	data.append("&End")

	#Input_Deck = Header1 + "" + "\t" + Input1 + "" + "\t" + Input2 + "" + "\t" + Input3 + "" + "\t" + Input4 + "" + "\t" + Input5 + "" + "\t" + Input6 + "" + "\t" + Input7 + "" + "\t" + Input8 + "" + "\t" + Input9 + "" + "\t" + Input10 + "" + "\t" + Input11 + "" + "\t" + Input12+ "" + "\t" + Input13 + "" + "\t" + Input14 + "" + "/" + "" + Header2 + "" + "\t" + Input15 + "" + "/" + "" + Header3 + "" + "\t" + Input16 + "" + "\t" + Input17 + "" + "\t" + Input18 + "" + "\t" + Input19 + "" + "\t" + Input20 + "" + "\t" + Input21 + "" + "\t" + Input22 + "" + "\t" + Input23 + "" + "\t" + Input24 + "" + "\t" + Input25 + "" + "\t" + Input26 + "" + "\t" + Input27 + "" + "/" + "" + Header4

	"""Writing input variables into the main directory"""
	with open(os.path.join(cwd,"Input_Deck.txt"), "w") as f:
		for i in data:
			f.write("%s\n" % i)


def Run_PropellantTank(cwd):
	# This def uses the input file to run Propellant_Tank.exe and create an output file
	system = platform.system()

	if system == 'Windows':
		subprocess.check_output([os.path.join(cwd, 'TankSizer.exe')], cwd=os.path.join(cwd))
	else:
		subprocess.check_output([os.path.join(cwd, './TankSizer')], cwd=os.path.join(cwd))


def Read_Output_File (filename):
	with open(filename, 'r') as f:
		#varnames = [HEADER, BarrelWeight,MSGENINST, MSSKINBUCK, MSRIBCRIP, MSPOCKBURST, MSCPB, MSIB, MSTF, MSSF, NEW_LENGTH, NEW_RADIUS, DOMEWEIGHT, TOTALWEIGHT, MSYLD_MIN, MSULT_MIN, NEW_VOLUME, VOLUME, E, FTENULT, FSHEARULT, RHO, NU, FSU, FTENYIELD, FSY, TANK_CYLINDER_LENGTH, FUEL_PER_TANK, TANK_LAUNCH_MASS, TOTAL_WEIGHT_OF_TANKS, DOME_HEIGHT]
		vars = []
		i = 0
		for line in f:
			storevec = []
			numLoc = 0
			for ii in line:
				if ii.isdigit():
					storevec.append(numLoc)
				numLoc += 1

			if len(storevec) > 1:
				vars.append(float(line[min(storevec):max(storevec)+1]))
			i = i + 1

	outputs = {}
	outputs["BarrelWeight"] = vars[0]
	outputs["MSGENINST"] = vars[1]
	outputs["MSSKINBUCK"] = vars[2]
	outputs["MSRIBCRIP"] = vars[3]
	outputs["MSPOCKBURST"] = vars[4]
	outputs["MSCPB"] = vars[5]
	outputs["MSIB"] = vars[6]
	outputs["MSTF"] = vars[7]
	outputs["MSSF"] = vars[8]
	outputs["NEW_LENGTH"] = vars[9]
	outputs["NEW_RADIUS"] = vars[10]
	outputs["DOMEWEIGHT"] = vars[11]
	outputs["TOTALWEIGHT"] = vars[12]
	outputs["MSYLD_MIN"] = vars[13]
	outputs["MSULT_MIN"] = vars[14]
	outputs["NEW_VOLUME"] = vars[15]
	outputs["VOLUME"] = vars[16]
	outputs["E"] = vars[17]
	outputs["FTENULT"] = vars[18]
	outputs["FSHEARULT"] = vars[19]
	outputs["RHO"] = vars[20]
	outputs["NU"] = vars[21]
	outputs["FSU"] = vars[22]
	outputs["FTENYIELD"] = vars[23]
	outputs["FSY"] = vars[24]
	outputs["TANK_CYLINDER_LENGTH"] = vars[25]
	outputs["FUEL_PER_TANK"] = vars[26]
	outputs["TANK_LAUNCH_MASS"] = vars[27]
	outputs["TOTAL_WEIGHT_OF_TANKS"] = vars[28]
	outputs["DOME_HEIGHT"] = vars[29]

	return outputs


def Main(inputs):
	Write_Input_File(**inputs)

	Run_PropellantTank(inputs["cwd"])

	return Read_Output_File(os.path.join(inputs["cwd"], "Output_Deck.txt"))


if __name__ == "__main__":
	import time
	t = time.time()

	cwd = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "Fortran")

	inputs = {}
	inputs["cwd"] = cwd
	inputs["Isogrid_Height"] = 0.01
	inputs["Rib_Height"] = 0.01
	inputs["Rib_Thickness"] = 0.01
	inputs["Skin_Thickness"] = 0.003
	inputs["Flange_Thickness"] = 0.02
	inputs["Flange_Width"] = 0.01
	inputs["Tank_Radius"] = 4.13
	inputs["Cylinder_Length"] = 14.91
	inputs["Number_of_Section"] = 1
	inputs["Dome_Thickness"] = .0018
	inputs["Dome_Height"] = 2.063968
	inputs["AR"] = 0.707
	inputs["Toggle"] = "N"
	inputs["Number_Tanks"] = 1
	inputs["Tank_Material"] = 3
	inputs["Mp"] = 260610.0
	inputs["Thrust"] = 1000.0
	inputs["Fax"] = 0.0
	inputs["AxialMass"] = 10.0
	inputs["Mbend"] = 0.001
	inputs["Fsh"] =  0.001
	inputs["Torque"] = 0.001
	inputs["Pburst"] = 35
	inputs["LFax"] = 4
	inputs["LFlat"] = 2.5
	inputs["g"] = 9.80665
	inputs["pamb"] = 0.0
	inputs["Fuel_Density"] = 71

	outputs = Main(inputs)

	print(f"Time elapsed: {round(time.time() - t, ndigits=5)}s.")
	print("outputs:", outputs)
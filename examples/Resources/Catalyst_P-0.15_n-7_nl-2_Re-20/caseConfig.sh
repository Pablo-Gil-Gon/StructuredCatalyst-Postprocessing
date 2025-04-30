#!/bin/bash
# This script runs the case simulation.
# Necessary variables are defined in this file:

# Geometry (GEOMETRY ALREADY SET, DO NOT CHANGE):
#----------------------------------------------------------
export R="10"
export Lcat="100"
export Lfront="40"
export Lback="40"
export porosity="0.15"
export Rchannels="1.4638501094227998"

# Fluid properties (Can be changed):
#----------------------------------------------------------
# Fluid density [kg/m3]:
export RHO="1.19"
# Fluid visosity [Pa*s]:
export MU="1.5e-5"
# Specific heat [J/(Kg*K)]
export FluidCP="1004.9"
# Prandtl number:
export FluidPr="0.7"
# Molar weight [g/mol ??]:
export FluidMW="29"
# Fluid fusion heat (?):
export FluidHf="0"

# Solid properties (Can be changed):
#----------------------------------------------------------
# Solid density [kg/m3]:
export RHO_s="7800"
# Solid specific heat [J/(Kg*K)]
export SolidCP="510"
# Thermal conductivity [W/(m*K)]
export SolidK="18"
# Molar weight [g/mol ??]:
export SolidMW="56"

# Case parameters (Can be changed):
#----------------------------------------------------------
# Desired porous Reynolds number:
export caseRep="20"
# Outlet pressure [Pa]
export caseOutletp="101325"
# Inlet fluid temperature [K]
export inletTemp="500.0"
# Initial temperature [k]
export initTemp="500.0"
# Exterior wall temperature [k]
export wallTemp="300.0"

# Simulation parameters (Can be changed):
#----------------------------------------------------------
# Desired runtime for the stationary case:
export endTStationary="10"
# Write time step length for the stationary case:
export writeIntervalStationary="1"

# Desired runtime for the flow simulation:
export endTMomentum="0.5"
# Write time step length for the flow simulation:
export writeIntervalMomentum="0.1"

# Desired runtime for the thermal simulation:
export endTThermal="15"
# Write time step length for the thermal simulation:
export writeIntervalThermal="3"

# Mesh parameters (mesh already set, cannot be changed)
#----------------------------------------------------------
# Only for information purposes
#
# Desired size of cells (as the number of cells that 
# fit in the radius of the catalyst). All other number 
# of cells is calculated from this value so that the 
# aspect ratio is close to 1.
# NCellsRadius_fluid="15"
# NCellsRadius_solid="20"

# Section: 1/ of a section

# Point in the solid:
# X_PointInSolid="7.46227733"
# Y_PointInSolid="6.10356456"

# Point in the fluid:
# X_PointInFluid="6.42441870"
# Y_PointInFluid="4.48980547"

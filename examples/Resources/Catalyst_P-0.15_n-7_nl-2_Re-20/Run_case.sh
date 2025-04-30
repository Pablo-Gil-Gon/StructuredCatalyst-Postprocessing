#!/bin/bash

# Source variables
#----------------------------------------------------------
source caseConfig.sh

# Setup OpenFOAM
#----------------------------------------------------------
. /opt/openfoam9/etc/bashrc

# Run stationary solver to get initial conditions
#----------------------------------------------------------
echo "Running stationary case..."
cd MomentumSolution/stationary_solution/
bash Run_stationary.sh
rm -rf "processor"*
echo "Done running stationary case"

# Copy the calculated initial conditions
#----------------------------------------------------------
bash copyInitialConditions.sh

# Run momentum solver to get velocity and pressure fields
#----------------------------------------------------------
echo "Running momentum solver for the case..."
cd ..
bash Run_pimpleFoam.sh
rm -rf "processor"*
echo "Done running momentum solver"
cd ..

# Copy the calculated initial conditions
#----------------------------------------------------------
bash MomentumSolution/setInitialConditions.sh U U
bash MomentumSolution/setInitialConditions.sh "static(p)" p_rgh

# Run solver
#----------------------------------------------------------
decomposePar -allRegions >> "logMeshing"
mpirun -np 16 /home/gilgonza/openfoamCustomSolvers/bin/chtCustomMultiRegion -parallel >> "logMeshing"
reconstructPar -allRegions >> "logMeshing"

rm -rf "processor"*

postProcess -func 'writeCellCentres' -region FluidRegion  -time 0
postProcess -func 'writeCellCentres' -region CatalystRegion  -time 0
postProcess -func 'writeCellVolumes' -region FluidRegion -time 0
postProcess -func 'writeCellVolumes' -region CatalystRegion -time 0

#exit


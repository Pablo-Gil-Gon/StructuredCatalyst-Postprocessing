#!/bin/bash

# Create the mesh
#----------------------------------------------------------
# Use the same mesh as the main case so that the points fit:


# Run solver
#----------------------------------------------------------
decomposePar >> "logMeshing"
mpirun -np 16 pimpleFoam -parallel >> "logMeshing"
reconstructPar >> "logMeshing" #-latestTime

# rm -rf "processor"*

postProcess -func 'writeCellCentres' -time 0
postProcess -func 'writeCellVolumes' -time 0

postProcess -dict system/postProcessDict -fields "(p)"

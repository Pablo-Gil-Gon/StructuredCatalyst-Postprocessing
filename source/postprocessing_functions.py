"""Post-processing functions module

This module defines some functions designed for the post-processing
of the results of simulations of structured catalysts. It is intended
to work with the simulations generated automatically by the
associated program (at time of writing, not yet included as a GitHub
project, but it will be!).

This module requires the module Ofpp (OpenFOAM Post Processing).
It also uses os, subprocess, warnings

"""

#import numpy as np
import Ofpp
import time
import os
import subprocess
import warnings

class CaseParameters:
    """Container class to store the parameters of a simulation.

    Attributes
    ----------
    fluid_rho : float
        Density of the fluid [kg/m3]
    solid_rho : float
        Density of the solid [kg/m3]
    fluid_cp : float
        Specific heat of the fluid [J/(Kg*K)]
    solid_cp : float
        Specific heat of the solid [J/(Kg*K)]
    fluid_Pr : float
        Prandtl number of the fluid [-]
    fluid_k : float
        Heat conductivity of the fluid [W/(m*K)]
    solid_k : float
        Heat conductivity of the fluid [W/(m*K)]
    fluid_mu : float
        Dynamic viscosity of the fluid [Pa*s]
    porosity : float
        Porosity of the reactor [Void volume / Total volume]
    R : float
        Radius of the reactor [m]
    Rchannels : float
        Hydraulic radius of the channels (4*A/P) [m]
        If the channels are circular, it is the radius. If they are 
        square it equals the side of the square.
    Rep : float
        Reynolds number in the channels (rho*vel*2*Rchannels/mu), 
        calculated with the average velocity in the channels [-]
    wallTemp : float
        Temperature at the outer walls of the reactor [K]
    inletTemp : float
        Temperature at the inlet [K]

    Methods
    -------
    __repr__(self) -> str
        Use print(CaseParameters) to check the values of the parameters, 
        with units.

    """

    def __init__(
        self,
        fluid_rho: float,
        solid_rho: float,
        fluid_cp: float,
        solid_cp: float,
        fluid_Pr: float,
        fluid_k: float,
        solid_k: float,
        fluid_mu: float,
        porosity: float,
        R: float,
        Rchannels: float,
        Rep: float,
        wallTemp: float,
        inletTemp: float
    ):
        """
        Initialize a CaseParameters instance with the given values.

        Parameters
        ----------
        fluid_rho : float
            Density of the fluid [kg/m3]
        solid_rho : float
            Density of the solid [kg/m3]
        fluid_cp : float
            Specific heat of the fluid [J/(Kg*K)]
        solid_cp : float
            Specific heat of the solid [J/(Kg*K)]
        fluid_Pr : float
            Prandtl number of the fluid [-]
        fluid_k : float
            Heat conductivity of the fluid [W/(m*K)]
        solid_k : float
            Heat conductivity of the fluid [W/(m*K)]
        fluid_mu : float
            Dynamic viscosity of the fluid [Pa*s]
        porosity : float
            Porosity of the reactor [Void volume / Total volume]
        R : float
            Radius of the reactor [m]
        Rchannels : float
            Hydraulic radius of the channels (4*A/P) [m]
            If the channels are circular, it is the radius. If they are 
            square it equals the side of the square.
        Rep : float
            Reynolds number in the channels (rho*vel*2*Rchannels/mu), 
            calculated with the average velocity in the channels [-]
        wallTemp : float
            Temperature at the outer walls of the reactor [K]
        inletTemp : float
            Temperature at the inlet [K]
        """
        self.fluid_rho = fluid_rho
        self.solid_rho = solid_rho
        self.fluid_cp = fluid_cp
        self.solid_cp = solid_cp
        self.fluid_Pr = fluid_Pr
        self.fluid_k = fluid_k
        self.solid_k = solid_k
        self.fluid_mu = fluid_mu
        self.porosity = porosity
        self.R = R
        self.Rchannels = Rchannels
        self.Rep = Rep
        self.wallTemp = wallTemp
        self.inletTemp = inletTemp

    def __repr__(self) -> str:
        """
        Return a string representation of the CaseParameters instance.

        Returns
        -------
        str
            A string summarizing the parameter values with their 
            units.
            
        """
        return (
            f"{self.__class__.__name__} (\n"
            f"  fluid_rho   = {self.fluid_rho:.5g} [kg/m3]\n"
            f"  solid_rho   = {self.solid_rho:.5g} [kg/m3]\n"
            f"  fluid_cp    = {self.fluid_cp:.5g} [J/(Kg*K)]\n"
            f"  solid_cp    = {self.solid_cp:.5g} [J/(Kg*K)]\n"
            f"  fluid_Pr    = {self.fluid_Pr:.5g} [-]\n"
            f"  fluid_k     = {self.fluid_k:.5g} [W/(m*K)]\n"
            f"  solid_k     = {self.solid_k:.5g} [W/(m*K)]\n"
            f"  fluid_mu    = {self.fluid_mu:.5g} [Pa*s]\n"
            f"  R           = {self.R:.5g} [m]\n"
            f"  Rchannels   = {self.Rchannels:.5g} [m]\n"
            f"  Rep         = {self.Rep:.5g} [-]\n"
            f"  wallTemp    = {self.wallTemp:.5g} [K]\n"
            f"  inletTemp   = {self.inletTemp:.5g} [K]\n)"

        )

    def as_dict(self) -> dict:
        """
        Convert the parameter values to a dictionary.

        Returns
        -------
        dict
            A dictionary of all parameter names and values.
        """
        return {
            "fluid_rho": self.fluid_rho,
            "solid_rho": self.solid_rho,
            "fluid_cp": self.fluid_cp,
            "solid_cp": self.solid_cp,
            "fluid_Pr": self.fluid_Pr,
            "fluid_k": self.fluid_k,
            "fluid_mu": self.fluid_mu,
            "R": self.R,
            "Rchannels": self.Rchannels,
            "Rep": self.Rep,
            "wallTemp": self.wallTemp,
            "inletTemp": self.inletTemp,
        }


def load_case_properties(   case_path: str, 
                            config_file_name: str = 'caseConfig.sh' 
                        ) -> CaseParameters:
    """Function for reading simulation parameters from config file

    This functions reads the parameters of the simulation (including
    material properties, boundary conditions, geometrical properties,
    etc.). Those parameters are saved in the config file for each
    simulation. That file is included in the case folder.

    Parameters
    ----------
    case_path : str
        Relative path to the case folder
    config_file_name : str
        Name of the case config file (default name 'caseConfig.sh')

    Returns
    -------
    params : CaseParameters
        Object of class CaseParameters containing the 

    """

    # The parameters of the simulation are saved in a bash file and 
    # exported as environment variables. It is done this way because
    # OpenFOAM dictionaries can read environment variables directly.

    # To get the values, we source that bash file and get the env 
    # variables.
    command = f'source {os.path.join(case_path, config_file_name)} && env'

    # These are the names of the env variables
    var_names = ['RHO', 'FluidCP', 'RHO_s', 'SolidCP', 'porosity', 'wallTemp', 'R', 'FluidPr', 'SolidK', 'MU', 'inletTemp', 'Rchannels', 'caseRep']
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, executable='/bin/bash', text=True)

    # Parse the output to find only the desired variables
    env_vars = {}
    for line in result.stdout.splitlines():
        key, _, value = line.partition('=')
        if key in var_names:
            env_vars[key] = value

    # The conductivity of the fluid is not declared as a parameter, 
    # must be calculated from the Prandtl number:
    Pr = float(env_vars.get('FluidPr', None))
    mu = float(env_vars.get('MU', None))
    cp_fluid = float(env_vars.get('FluidCP', None))
    fluid_k = cp_fluid*mu/Pr

    params = CaseParameters(
        float(env_vars.get('RHO', None)),
        float(env_vars.get('RHO_s', None)),
        cp_fluid,
        float(env_vars.get('SolidCP', None)),
        Pr,
        fluid_k,
        float(env_vars.get('SolidK', None)),
        mu,
        float(env_vars.get('porosity', None)),
        float(env_vars.get('R', None))*0.001,
        float(env_vars.get('Rchannels', None))*0.001,
        float(env_vars.get('caseRep', None)),
        float(env_vars.get('wallTemp', None)),
        float(env_vars.get('inletTemp', None))
    )

    return params


def get_timestep_folders(case_path: str) -> list[str]:
    """Get the names of timestep folders form simulation directory

    Given a OpenFOAM case directory, this function returns the names 
    of the folders that represent a timestep, INCLUDING THE '0' FOLDER.

    Parameters
    ----------
    case_path : str
        Relative path to the case folder

    Returns
    -------
    timesteps : list[str]
        List of the names of the timestep folders in the directory (as 
        strings)

    Warnings
    --------
    warning
        If there are no timestep folders (folders named as a number)
        in the case directory, function raises a warning.

    """

    timestep_folders = []

    for item in os.listdir(case_path):
        item_path = os.path.join(case_path, item)

        if os.path.isdir(item_path):
            try:
                # Try converting folder name to float
                float(item)
                timestep_folders.append(item)
            except ValueError:
                # Not a timestep folder
                continue

    # Check if the list is empty or if it only contains the '0' 
    # folder:
    if len(timestep_folders) is 0:
        warnmessage = "No timestep folders found in " + case_path + " not even '0' folder"
        warnings.warn(warnmessage)

    elif (len(timestep_folders) is 1) and (float(timestep_folders[0]) == 0.0):
        warnmessage = "No timestep folders found in " + case_path + " just '0' folder"
        warnings.warn(warnmessage)

    # Sort numerically, not lexically
    return sorted(timestep_folders, key=lambda x: float(x))



def read_simulation_data(case_path: str, fluid_region_name: str = 'FluidRegion/', solid_region_name: str = 'CatalystRegion/'):
    """Function for reading the simulation data (mesh and results)


    """

    time1 = time.time()
    # Read the fluid region mesh:
    fluidmesh = Ofpp.FoamMesh(case_path, fluid_region_name)

    time2 = time.time()
    print("Time required for reading the fluidmesh = ", time2-time1)

    time2_1 = time.time()
    # Read the coordinates of the centers of cells and their volumes
    # For this function to work user must have been generated the 'C'
    # and 'V' mesh files for each region. These files are  created by 
    # OpenFOAM's own postprocessing utilities.
    fluidmesh.read_cell_centres(case_path+'0/'+fluid_region_name+'C')
    fluidmesh.read_cell_volumes(case_path+'0/'+fluid_region_name+'V')
    time2_2 = time.time()

    print("Time reading fluidmesh centres and volumes = ", time2_2-time2_1)

    
    # Read the solid region mesh:
    solidmesh = Ofpp.FoamMesh(case_path, solid_region_name)

    time3 = time.time()
    print("Time required for reading the solidmesh = ", time3-time2)

    time3_1 = time.time()
    # Read the coordinates of the centers of cells and their volumes
    solidmesh.read_cell_centres(case_path+'0/'+solid_region_name+'C')
    solidmesh.read_cell_volumes(case_path+'0/'+solid_region_name+'V')
    time3_2 = time.time()

    print("Time reading solidmesh centres and volumes = ", time3_2-time3_1)

    timesteps = get_timestep_folders(case_path)
    print(timesteps)


    return True



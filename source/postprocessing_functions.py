"""Post-processing functions module

This module defines some functions designed for the post-processing
of the results of simulations of structured catalysts. It is intended
to work with the simulations generated automatically by the
associated program (at time of writing, not yet included as a GitHub
project, but it will be!).

This module requires the module Ofpp (OpenFOAM Post Processing).
It also uses os, subprocess, warnings, joblib

"""

#import numpy as np
import Ofpp
import time
import os
import subprocess
import warnings
import joblib

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
    if len(timestep_folders) == 0:
        warnmessage = "No timestep folders found in " + case_path + " not even '0' folder"
        warnings.warn(warnmessage)

    elif (len(timestep_folders) == 1) and (float(timestep_folders[0]) == 0.0):
        warnmessage = "No timestep folders found in " + case_path + " just '0' folder"
        warnings.warn(warnmessage)

    # Sort numerically, not lexically
    return sorted(timestep_folders, key=lambda x: float(x))


def read_simulation_data(   case_path: str, 
                            fluid_region_name: str = 'FluidRegion/', 
                            solid_region_name: str = 'CatalystRegion/', 
                            momentum_simulation_folder: str = 'MomentumSolution/',
                            config_file_name: str = 'caseConfig.sh' 
                        ) -> str:
    """Function for reading the simulation data (mesh and results)

    This function reads the simulation files, saves the 
    information in Python objects and lists and stores in a 
    joblib file in the same simulation directory.

    Parameters
    ----------
    case_path : str
        Relative path to the case folder
    fluid_region_name : str
        Name of the fluid region in the OpenFOAM simulation. By 
        default 'FluidRegion/'
    solid_region_name : str
        Name of the solid region in the OpenFOAM simulation. By 
        default 'CatalystRegion/'
    momentum_simulation_folder : str
        Momentum and heat simulations are decoupled. Name of the 
        direrctory (inside case_path) where the momentum simulation 
        files are. By default 'MomentumSolution/'
    config_file_name : str
        Name of the case config file (default name 'caseConfig.sh')

    Returns Nothing
    ---------------
    datafilename : str
        Name of the file with the data from the results, as a string

    Results
    -------
    joblilb file
        This function creates a joblib file in the case folder 
        containing the data extracted from the simulation. Data in 
        that file is stored in a dictionar. To load it in a script 
        run:
            dict = joblib.load('path_to_the_joblib_file.joblib')
        The dict contains the following items (identified by their 
        key):

        "Parameters" : CaseParameters
            Object of class CaseParameters containing the values 
            of the parameters of this simulaton
        "SolidMesh" : Ofpp.mesh_parser.FoamMesh
            Mesh of the solid region of the catalyst (Ofpp class)
        "FluidMesh" : Ofpp.mesh_parser.FoamMesh
            Mesh of the fluid region of the catalyst (Ofpp class)
        "MomentumTimesteps" : list[str]
            List with the timesteps of the momentum simulation (as 
            strings, the names of the folders containing each 
            timestep. MomentumTimesteps[0]='0' is always the '0' 
            folder of the OpenFOAM simulation.)
        "ThermalTimesteps" : list[str]
            List with the timesteps of the temperature simulation (as
            strings, the names of the folders containing each 
            timestep. MomentumTimesteps[0]='0' is always the '0' 
            folder of the OpenFOAM simulation).
        "FluidTemperature" : list[list[numpy.float64]]
            List "FluidTemperature" contains one list for each 
            timestep in "ThermalTimesteps" in the same order 
            starting for the second time step (the first is the 
            initial condition).
            For each time step, it contains a list with the 
            temperature at the center of every cell in the fluid 
            region. The cells are ordered in the same way as in 
            fluidmesh.cell_centres
        "SolidTemperature" : list[list[numpy.float64]]
            Same as "FluidTemperature" but for the solid region.
        "StaticPressure" : list[list[numpy.float64]]
            Same as "FluidTemperature" but for static pressure instead
            of temperature.
        "VelocityField" list[list[numpy.ndarray]]: 
            Same as "FluidTemperature" but for velocity pressure 
            instead of temperature. Since velocity is a vector, for 
            every cell center instead of a float we have a 
            numpy.ndarray with three elements.

    """

    # Read the fluid region mesh:
    time1 = time.time()
    fluidmesh = Ofpp.FoamMesh(case_path, fluid_region_name)

    time2 = time.time()
    print("Time required for reading the fluidmesh = ", time2-time1)

    # Read the coordinates of the centers of cells and their volumes
    # For this function to work user must have been generated the 'C'
    # and 'V' mesh files for each region. These files are  created by 
    # OpenFOAM's own postprocessing utilities.
    fluidmesh.read_cell_centres(case_path+'0/'+fluid_region_name+'C')
    fluidmesh.read_cell_volumes(case_path+'0/'+fluid_region_name+'V')

    # Read the solid region mesh:
    time3 = time.time()
    solidmesh = Ofpp.FoamMesh(case_path, solid_region_name)

    time4 = time.time()
    print("Time required for reading the solidmesh = ", time4-time3)

    # Read the coordinates of the centers of cells and their volumes
    solidmesh.read_cell_centres(case_path+'0/'+solid_region_name+'C')
    solidmesh.read_cell_volumes(case_path+'0/'+solid_region_name+'V')

    # Since the simulations for momentum and temperature are decoupled,
    # we have different timesteps for each of the simulations:
    timesteps_momentum = get_timestep_folders(case_path + 'MomentumSolution/')
    timesteps_thermal = get_timestep_folders(case_path)
    print("Timesteps momentum simulation: ",timesteps_momentum)
    print("Timesteps thermal simulation: ",timesteps_thermal)

    # Read the magnitudes for each timestep:
    # TODO  Write the option to read just some of the timesteps and 
    #       some of the magnitudes.

    # Timestep [0] is the '0' folder, skip that one.
    timesteps_to_read_thermal = timesteps_thermal[1:]
    timesteps_to_read_momentum = timesteps_momentum[1:]

    # Parse each field for each timestep and store them in a list.
    #  Each element of the list contains the value of the field in 
    # the timestep that is in the same position in the 
    # 'timesteps_to_read_*' list.
    T_fluid = []
    T_solid = []
    for ts in timesteps_to_read_thermal:
        T_fluid.append(Ofpp.parse_internal_field(case_path + ts + '/' + fluid_region_name + 'T'))
        T_solid.append(Ofpp.parse_internal_field(case_path + ts + '/' + solid_region_name + 'T'))

    static_p = []
    vel_field = []
    for ts in timesteps_to_read_momentum:
        static_p.append(Ofpp.parse_internal_field(case_path + momentum_simulation_folder + ts + '/' + 'static(p)'))
        vel_field.append(Ofpp.parse_internal_field(case_path + momentum_simulation_folder + ts + '/' + 'U'))

    # Save the data in a joblib file. The rationale behind this is 
    # that reading and parsing data from the OpenFOAM files can take 
    # quite a long time, up to a couple minutes. If we save all 
    # those files in one of these fast formats I can read the data 
    # from openfoam once and then use them as I want (may not sound 
    # very convincing, but trust me I've spent a lot of very 
    # frustating time waiting for these data to load). 

    # Include the case parameters too:
    params = load_case_properties(case_path,  config_file_name)
    # Save the variables as a dict:
    sim_data = {"Parameters": params,
                "SolidMesh": solidmesh, 
                "FluidMesh": fluidmesh, 
                "MomentumTimesteps": timesteps_momentum,
                "ThermalTimesteps": timesteps_thermal,
                "FluidTemperature": T_fluid,
                "SolidTemperature": T_solid,
                "StaticPressure": static_p,
                "VelocityField": vel_field}

    datafilename = case_path + "Case_P" + str(params.porosity) + "_Re" + str(params.Rep) + "_DATA.joblib"

    joblib.dump(sim_data, datafilename)

    return datafilename






"""Post-processing functions module

This module defines some functions designed for the post-processing
of the results of simulations of structured catalysts. It uses the 
data from simulations that have already been processed by the 
functions defined in data_handling_functions.py module.

"""
import numpy as np

def getAvg_p_rgh(   data: dict,
                    num_zdots: int
                ):
    """Function for getting the average pressure in the cross section

    This function calcullates the average pressure in the cross 
    section of the system (that is, both in the range where there 
    is both solid and fluid as the regions where there is just fluid, 
    the "buffer zones").

    This function divides the lenght of the reactor in num_zdots-1 
    segments of equal size. The average is calcullated for each of 
    the num_zdots points that separate the segments by averaging the 
    pressure at every cell whose center falls between the midpoint of 
    the segment that falls to the left and the midpoint of the 
    segment to the right. For the averaging, the pressure of each cell 
    is weighted to its volume divided by the total volume of all the 
    cells involved.

    If the dict data contains more than one momentum timestep, the 
    average pressure along the axis for each of them is returned.

    z_dots, avg_p = getAvg_p_rgh( data, num_zdots )

    Parameters
    ----------
    data : dict
        dictionary with the results from the simulation
    num_zdots : int
        Number of points to divide the lenght of the reactor in.

    Returns
    -------
    z_dots : list[numpy.float64]
        z-coordinate of the num_zdots points for which the average 
        pressure is calcullated. length of z_dots is num_zdots

    avg_p : list[list[numpy.float64]]
        Average pressure arround the section at each of the z_dots 
        for each of the momentum timesteps.
    """

    # Centres of the cells in the fluid region:
    fluidmesh = data["FluidMesh"]
    z_centres = [centre[2] for centre in fluidmesh.cell_centres]


    # Minimum and maximum z-coordinate of all the cells:
    min_z = min(z_centres)
    max_z = max(z_centres)
    print(z_centres[1])

    # Z points to calcullate the average arround:
    z_dots = np.linspace(min_z, max_z, num_zdots)

    # Half size of the segments:
    half_segsize = (z_dots[1] - z_dots[0])/2.0
    
    # Save index of cells in each of the samnple sections:
    indexes = [[] for _ in range(0, num_zdots)]

    for i in range(0, fluidmesh.num_cell):
        for j in range(0,num_zdots):
            if (z_centres[i] >= z_dots[j]-half_segsize) and (z_centres[i]<=z_dots[j]+half_segsize):
                indexes[j].append(i)

    # Calcullate the average pressure in each section for each timestep.
    num_timesteps = len(data["MomentumTimesteps"])
    print(num_timesteps)
    print(data["MomentumTimesteps"])
    p_data = data["StaticPressure"]
    avg_p =  []

    for ts in range(0, num_timesteps):
        print(ts)
        print(p_data[ts][1])
        p_rgh_ts = []
        for j in range(0,num_zdots):
            total_cell_vol = np.sum([fluidmesh.cell_volumes[i] for i in indexes[j]])
            p_rgh_ts_zi = np.sum([p_data[ts][i]*fluidmesh.cell_volumes[i]/total_cell_vol for i in indexes[j]])

            p_rgh_ts.append(p_rgh_ts_zi)

        avg_p.append(p_rgh_ts)

    return z_dots, avg_p



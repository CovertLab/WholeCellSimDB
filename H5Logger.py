import h5py
import scipy.io 
import glob
import argparse
import re

def __state_properties(directory):
    """ 
    Returns a dict with the state names as keys, and a list of the
    paths to property files.
    """
    prop_files = glob.glob(directory+"/state-[a-zA-Z]*-[a-zA-Z]*.mat")
    state_properties = {}
    for prop in prop_files:
        state = prop.split("-")[-2]
        state_properties.setdefault(state, []).append(prop)
    return state_properties

def __create_groups(hdf_file, state_list):
    """
    Creates a group in the hdf_file for each key value in the 
    state_properties dict.
    """
    # For each state in list
    #   Create new group in hdf_file
    pass

def __insert_state_datasets(hdf_file, state, properties):
    """
    Creates a dataset in the /group_nmae of hdf_file for each property
    in the property_list.
    """
    # For each property:
    #   try to load property.mat
    #   Convert "__data__" from numpy.ndarray to a list.
    #   Insert list into the group named state
    pass

def main():
    parser = argparse.ArgumentParser(description='Stuff')
    parser.add_argument('-d', '--directory',
                        help='Directory of WCS output files.',
                        required=True)
    parser.add_argument('-o', '--output',
                        help='HDF5 output filename.',
                        required=True)
    args = parser.parse_args()
    
    # Directory of WholeCell Simulation output files.
    directory = args.directory

    # Name of HDF5 file.
    filename = args.output
    filename = re.search('.*\.hdf5$', filename) and \
               filename or filename + ".hdf5"

    # Open HDF5 file.
    hdf_file = h5py.File(args.output, 'w')

    # Get list of all state-STATE-PROPERTY.mat files.
    state_properties = __state_properties(directory)

    # Create a group in the hdf_file for each state.
    __create_groups(hdf_file, state_properties.keys())

    for properties, state in state_properties.items():
        __insert_state_dataset(hdf_file, state, properties) 




if __name__=="__main__":
    main()

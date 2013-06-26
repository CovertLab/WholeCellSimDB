import h5py
import os
import scipy.io 
import glob
import argparse
import re

def get_state_properties(directory): # 1
    """ 
    Returns a dict with the state names as keys, and a list of the
    paths to property files as values.
    """
    prop_files = glob.glob(directory+"/state-[a-zA-Z]*-[a-zA-Z]*.mat")
    state_properties = {}
    for prop in prop_files:
        state = prop.split("-")[-2]
        state_properties.setdefault(state, []).append(prop)
    return state_properties

def create_state_groups(hdf_file, state_list): #1
    """
    Creates an HDF5 group for each state in the list.
    Returns a list of pre-existing groups.
    """
    pre_existing_groups = []
    for state in state_list:
        try:
            hdf_file.create_group(state)
        except ValueError:
            pre_existing_groups.append(state)
    return pre_existing_groups

def insert_state_data(hdf_file, state, properties):
    """
    Creates a dataset in the /group_name of hdf_file for each property
    in the property_list.
    """
    not_loaded = []
    for prop in properties:
        prop_dict = None
        prop_name = prop.split("-")[-1].split(".")[0]
        try:
            prop_dict = scipy.io.loadmat(prop)
        except SystemError:
            not_loaded.append(prop + " SystemError")
        except MemoryError:
            not_loaded.append(prop + " MemoryError")
        if prop_dict:
            if 'data' in prop_dict:
                prop_data = prop_dict['data'].tolist()
                hdf_file[state].create_dataset(prop_name, data=prop_data)
            else:
                not_loaded.append(prop) 
    return not_loaded

def log_dir(directory, hdf_filename):
    """
    Logs simulation states found in 'directory' to
    the hdf5 file 'hdf_filename'
    """
    hdf_filename = re.search('.*\.hdf5$', hdf_filename) and \
               hdf_filename or hdf_filename + ".hdf5"
    hdf_file = h5py.File(hdf_filename, 'w')

    if (os.path.exists(directory)):
        state_properties = get_state_properties(directory)
        

        create_state_groups(hdf_file, state_properties.keys())

        for state, properties in state_properties.items():
            print insert_state_data(hdf_file, state, properties) 
    else:
        return 1
    return 0

    print "Done"



if __name__=="__main__":
    main()

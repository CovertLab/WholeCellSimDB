import glob
import numpy
import re
import scipy.io

from wcdb.models import *



def save_simulation_from_mat(simulation_dir, batch, batch_index):
    """Keys: ['processes', 'verbosity', 'macromoleculeStateInitialization', 'stepSizeSec', 'states', 'lengthSec', 'seed'] """
    options = loadmat(simulation_dir + '/options.mat')
    parameters = loadmat(simulation_dir + '/parameters.mat')
    processes = parameters['processes'].keys() 
    states = parameters['states'].keys()
    #length = options['lengthSec']
    
    property_files = glob.glob(simulation_dir + "/state-[a-zA-Z]*-[a-zA-Z]*.mat")

    state_properties = {}    

    for prop_file in property_files:
        state = prop_file.split("-")[1]  # State name
        prop = prop_file.replace(".", "-").split("-")[2]  # Property name
        try:
            mat_dict = scipy.io.loadmat(prop_file)
            if "data" in mat_dict.keys():
                data = mat_dict['data']
                label_sets = [""] 
                d_list = [data.dtype, data.shape, label_sets]
                # Weird syntax. Just constructing the state_property dict.
                state_properties.setdefault(state, {}).setdefault(prop, d_list)
                
        except SystemError: #TODO: handle errors
            pass
        except MemoryError: #TODO: handle errors
            pass
    
    # Save simulation
    simulation = Simulation.objects.create_simulation( 
        batch=batch,
        batch_index=batch_index,
        processes=processes,
        state_properties=state_properties,
        options=options,
        #length=length,
        parameters=parameters)

    ###############
    # Saving Data #
    ###############
                                               
    #save property values data
    for prop_file in property_files:
        state_name = prop_file.split("-")[1]
        prop_name = prop_file.replace(".", "-").split("-")[2]

        print prop_file
        try:
            property_mat_dict = scipy.io.loadmat(prop_file)
            
            if "data" in mat_dict.keys():
                # Get the property. 
                state_obj = simulation.states.get(name=state_name)
                try:
                    property_obj = state_obj.properties.get(name=prop_name)

                    # Get the data.
                    data = property_mat_dict['data']

                    # Add teh data to the property.
                    property_obj.add_data(data)
                except:
                    pass
        except:
            pass


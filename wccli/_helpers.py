import glob
import numpy
import re
import scipy.io

from wcdb.models import SimulationBatch, Simulation

def save_simulation_batch(organism_name,
                          organism_version,
                          name,
                          description,
                          investigator_first, 
                          investigator_last,
                          investigator_affiliation,
                          investigator_email,
                          ip,
                          batch_dir):
    
    batch_obj = SimulationBatch.objects.create_simulation_batch(
        organism_name = organism_name,
        organism_version = organism_version,
        name = name, 
        description = description, 
        investigator_first = investigator_first,
        investigator_last = investigator_last,
        investigator_affiliation = investigator_affiliation,
        investigator_email = investigator_email,
        ip = ip)

    first_sim_dir = batch_dir + '/1'
    save_simulation_from_mat(first_sim_dir, batch_obj, 1)

#    sim_dirs = glob.glob(batch_dir + "/[0-9]*")
#    for sim_dir in sim_dirs:
#        batch_index = int(float(re.split("/", sim_dir).pop()))
#        
#        print "Saving simulation %d of %d ... " % (batch_index, len(sim_dirs))
#        save_simulation(organism_name, name, batch_index, sim_dir)

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
        state = prop_file.split("-")[1] # State name
        prop = prop_file.replace(".", "-").split("-")[2] # Property name
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

def loadmat(filename, throw_error_on_unknown_data_format=True):
    data = scipy.io.loadmat(filename, struct_as_record=False)
    dict = {}
    for key in data:
        if isinstance(data[key], numpy.ndarray): 
            # If 2 layers deep is the matlab struct
            if len(data[key]) == 1 \
            and isinstance(data[key][0], numpy.ndarray) \
            and len(data[key][0]) == 1 \
            and isinstance(data[key][0][0], 
                           scipy.io.matlab.mio5_params.mat_struct):
                # Normalize the matlab struct.
                dict[key] = _normalize(data[key][0][0], 
                                       throw_error_on_unknown_data_format)
            # Else if it's one dimension and the value is a unicode.
            elif data[key].ndim == 1 \
            and isinstance(data[key][0], numpy.unicode_):
                # Make it a list
                dict[key] = data[key].tolist()[0]
            # This appears to be the third way this can be things.
            elif data[key].ndim == 2 \
            and data[key].shape[0] == 1 \
            and data[key].shape[1] == 1:
                dict[key] = data[key].tolist()[0][0]
    return dict

def _normalize(matobj, throw_error_on_unknown_data_format):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, numpy.ndarray) and len(elem) == 1 and \
           isinstance(elem[0], numpy.ndarray) and len(elem[0]) == 1 and \
           isinstance(elem[0][0], scipy.io.matlab.mio5_params.mat_struct):
            dict[strg] = _normalize(elem[0][0], throw_error_on_unknown_data_format)
        else:
            if elem.ndim == 1 and isinstance(elem[0], numpy.unicode_):
                dict[strg] = elem.tolist()[0]
            elif elem.ndim == 2 and elem.shape[0] == 1 and elem.shape[1] == 1:
                dict[strg] = elem.tolist()[0][0]
            elif elem.ndim == 2 and elem.shape[0] == 1:
                dict[strg] = elem.tolist()[0]               
            elif elem.ndim == 2 and elem.shape[1] == 1:
                dict[strg] = [x[0] for x in elem.tolist()]
            elif elem.ndim == 2 and elem.shape[0] == 0 and elem.shape[1] == 0:
                dict[strg] = None
            elif throw_error_on_unknown_data_format:
                raise Exception('Invalid data')
            else:
                dict[strg] = elem
            
    return dict

import glob
import numpy
import re
import scipy.io

from wcdb.models import SimulationBatch, Simulation

def save_simulation_batch(
    organism_name, organism_version,
    name, description,
    investigator_first, investigator_last, investigator_affiliation, investigator_email,
    ip, batch_dir
    ):
            
    #load options, parameters, states, processes
    first_sim_dir = batch_dir + '/1'
    options = loadmat(first_sim_dir + '/options.mat')
    parameters = loadmat(first_sim_dir + '/parameters.mat')
    
    processes = parameters['processes'].keys()
    states = parameters['states'].keys()
    
    state_properties = {}
    for state_name, state in loadmat(first_sim_dir + '/state-0.mat', False).iteritems():
        state_properties[state_name] = [prop_name for prop_name, prop_value in state.iteritems()]
    
    #save batch
    SimulationBatch.objects.create_simulation_batch( 
        organism_name = organism_name,
        organism_version = organism_version,
        name = name, 
        description = description, 
        investigator_first = investigator_first,
        investigator_last = investigator_last,
        investigator_affiliation = investigator_affiliation,
        investigator_email = investigator_email,
        ip = ip,
        processes = processes,
        states = states,
        state_properties = state_properties,
        options = options,
        parameters = parameters)
        
    #save simulations
    sim_dirs = glob.glob(batch_dir + "/[0-9]*")
    for sim_dir in sim_dirs:
        batch_index = int(float(re.split("/", sim_dir).pop()))
        
        print "Saving simulation %d of %d ... " % (batch_index, len(sim_dirs))
        save_simulation(organism_name, name, batch_index, sim_dir)
    
def save_simulation(organism_name, batch_name, batch_index, sim_dir):
    # get simulation batch
    batch = SimulationBatch.objects.get(organism__name = organism_name, name = batch_name)
    
    # Get a list of all the paths to the .mat files to be loaded.
    property_files = glob.glob(sim_dir + "/state-[a-zA-Z]*-[a-zA-Z]*.mat")
    
    #collect names of state properties
    state_properties = {}    
    for prop_file in property_files:
        state = prop_file.split("-")[-2] # State name
        prop = prop_file.replace(".", "-").split("-")[-2] # Property name

        try:
            # This is the .mat file loaded into python
            mat_dict = scipy.io.loadmat(prop_file)

            # This is the actual generated data.
            if "data" in mat_dict.keys():
                data = mat_dict['data']
                d_list = (data.shape, data.dtype)
                # Weird syntax. Just constructing the state_property dict.
                state_properties.setdefault(state, {}).setdefault(prop, d_list)
                
        except SystemError: #TODO: handle errors
            pass
        except MemoryError: #TODO: handle errors
            pass
        
    #create simulation
    sim = Simulation.objects.create_simulation(
        batch = batch,
        batch_index = batch_index,
        state_properties=state_properties)
    sim.save()
                                               
    #save property values data
    for prop_file in property_files:
        state_name = prop_file.split("-")[-2]
        prop_name = prop_file.replace(".", "-").split("-")[-2]

        #try:
        mat_dict = scipy.io.loadmat(prop_file)
            
        if "data" in mat_dict.keys():
            data = mat_dict['data']
            p_obj = sim.property_values.get(property__state__name = state_name, property__name = prop_name)
            p_obj.add_data(data)

        #except SystemError: #TODO: handle errors
        #    pass
        #except MemoryError: #TODO: handle errors
        #    pass

def loadmat(filename, throw_error_on_unknown_data_format=True):
    data = scipy.io.loadmat(filename, struct_as_record=False)
    dict = {}
    for key in data:
        if isinstance(data[key], numpy.ndarray):
            if len(data[key]) == 1 and \
               isinstance(data[key][0], numpy.ndarray) and len(data[key][0]) == 1 and \
               isinstance(data[key][0][0], scipy.io.matlab.mio5_params.mat_struct):
                dict[key] = _normalize(data[key][0][0], throw_error_on_unknown_data_format)
            elif data[key].ndim == 1 and isinstance(data[key][0], numpy.unicode_):
                dict[key] = data[key].tolist()[0]
            elif data[key].ndim == 2 and data[key].shape[0] == 1 and data[key].shape[1] == 1:
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
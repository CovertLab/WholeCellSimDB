import dateutil.parser
import glob
import numpy
import os
import pytz
import re
import scipy.io
from wcdb.models import SimulationBatch, Simulation

def save_simulation_batch(organism_name, batch_dir):   
    #load metadata
    first_sim_dir = os.path.join(batch_dir, '1')
    md = scipy.io.loadmat(os.path.join(first_sim_dir, 'metadata.mat'))
    organism_version = md['revision'][0][0]
    name = md['shortDescription'][0]
    description = md['longDescription'][0]
    investigator_first = md['firstName'][0]
    investigator_last = md['lastName'][0]
    investigator_affiliation = md['affiliation'][0]
    investigator_email = md['email'][0]
    ip = md['ipAddress'][0]
    date = dateutil.parser.parse(md['startTime'][0]).replace(tzinfo=pytz.timezone('Africa/Abidjan')) 
        
    #load options, parameters
    options = load_options(batch_dir)
    parameters = load_parameters(batch_dir)    
    processes = parameters['processes'].keys()
    states = load_states(batch_dir)
    
    for state_name in options['states'].keys() + parameters['states'].keys():
        if state_name not in states:
            states[state_name] = {}
                
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
        date = date,
        processes = processes,
        states = states,
        options = options,
        parameters = parameters)
        
    #save simulations
    sim_dirs = glob.glob(os.path.join(batch_dir, "[0-9]*"))
    for sim_dir in sim_dirs:    
        batch_index = int(float(re.split(os.sep, sim_dir).pop()))
        
        print "Saving simulation %d of %d ... " % (batch_index, len(sim_dirs))
        save_simulation(organism_name, batch_dir, batch_index)
    
def save_simulation(organism_name, batch_dir, batch_index):
    sim_dir = os.path.join(batch_dir, str(batch_index))

    #get batch name, length
    md = scipy.io.loadmat(os.path.join(sim_dir, 'metadata.mat'))
    batch_name = md['shortDescription'][0]
    length = md['lengthSec'][0][0]
    
    # get simulation batch
    batch = SimulationBatch.objects.get(organism__name = organism_name, name = batch_name)
    
    # Get a list of all the paths to the .mat files to be loaded.
    property_files = glob.glob(os.path.join(sim_dir, "state-[a-zA-Z]*-[a-zA-Z]*.mat"))
    
    #collect names of state properties
    states = {}    
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
                states.setdefault(state, {}).setdefault(prop, d_list)
                
        except SystemError: #TODO: handle errors
            pass
        except MemoryError: #TODO: handle errors
            pass
        
    #create simulation
    sim = Simulation.objects.create_simulation(
        batch = batch,
        batch_index = batch_index,
        length = length,
        states = states)
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
        
def load_options(batch_dir):
    units_labels = loadmat(os.path.join(batch_dir, 'units_labels.mat'))
    
    first_sim_dir = os.path.join(batch_dir, '1')
    option_vals = loadmat(os.path.join(first_sim_dir, 'options.mat'))
    
    options = {}
    for prop_name, value in option_vals.iteritems():
        if re.match(r"^__.+?__$", prop_name) or prop_name == 'processes' or prop_name == 'states':
            continue
        options[prop_name] = {
            'units': units_labels[prop_name]['units'] if prop_name in units_labels and 'units' in units_labels[prop_name] else None, 
            'value': value
            }
    options['processes'] = {}
    for process_name, props in option_vals['processes'].iteritems():        
        options['processes'][process_name] = {}
        for prop_name, value in props.iteritems():
            options['processes'][process_name][prop_name] = {
                'units': units_labels['processes'][process_name][prop_name]['units'] if process_name in units_labels['processes'] and prop_name in units_labels['processes'][process_name] and 'units' in units_labels['processes'][process_name][prop_name] else None, 
                'value': value
                }
    options['states'] = {}
    for state_name, props in option_vals['states'].iteritems():
        options['states'][state_name] = {}
        for prop_name, value in props.iteritems():
            options['states'][state_name][prop_name] = {
                'units': units_labels['states'][state_name][prop_name]['units'] if state_name in units_labels['states'] and prop_name in units_labels['states'][state_name] and 'units' in units_labels['states'][state_name][prop_name] else None, 
                'value': value
                }
    
    return options
        
def load_parameters(batch_dir):
    units_labels = loadmat(os.path.join(batch_dir, 'units_labels.mat'))
    
    first_sim_dir = os.path.join(batch_dir, '1')
    parameter_vals = loadmat(os.path.join(first_sim_dir,  'parameters.mat'))    
    
    parameters = {}
    for prop_name, value in parameter_vals.iteritems():
        if re.match(r"^__.+?__$", prop_name) or prop_name == 'processes' or prop_name == 'states':
            continue
            
        parameters[prop_name] = {
            'units': units_labels[prop_name]['units'] if prop_name in units_labels and 'units' in units_labels[prop_name] else None, 
            'value': value
            }
    parameters['processes'] = {}
    for process_name, props in parameter_vals['processes'].iteritems():
        parameters['processes'][process_name] = {}
        for prop_name, value in props.iteritems():
            parameters['processes'][process_name][prop_name] = {
                'units': units_labels['processes'][process_name][prop_name]['units'] if process_name in units_labels['processes'] and prop_name in units_labels['processes'][process_name] and 'units' in units_labels['processes'][process_name][prop_name] else None, 
                'value': value
                }
    parameters['states'] = {}
    for state_name, props in parameter_vals['states'].iteritems():
        parameters['states'][state_name] = {}
        for prop_name, value in props.iteritems():
            parameters['states'][state_name][prop_name] = {
                'units': units_labels['states'][state_name][prop_name]['units'] if state_name in units_labels['states'] and prop_name in units_labels['states'][state_name] and 'units' in units_labels['states'][state_name][prop_name] else None, 
                'value': value
                }
    
    return parameters
    
def load_states(batch_dir):
    units_labels = loadmat(os.path.join(batch_dir, 'units_labels.mat'))
    first_sim_dir = os.path.join(batch_dir, '1')
    
    states = {}
    for state_name, state in loadmat(os.path.join(first_sim_dir, 'state-0.mat'), False).iteritems():
        states[state_name] = {}
        for prop_name, prop_value in state.iteritems():
            if state_name in units_labels['states'] and \
                prop_name in units_labels['states'][state_name] and \
                'units' in units_labels['states'][state_name][prop_name]:
                units = units_labels['states'][state_name][prop_name]['units']
            else:
                units = None
            if state_name in units_labels['states'] and \
                prop_name in units_labels['states'][state_name] and \
                'labels' in units_labels['states'][state_name][prop_name]:
                labels = []
                for dim_labels in units_labels['states'][state_name][prop_name]['labels']:
                    if dim_labels.size > 0:
                        labels.append([x[0] for x in dim_labels[0].tolist()])
                    else:
                        labels.append([])
            else:
                labels = None
            states[state_name][prop_name] = {'units': units, 'labels': labels}
            
    return states    

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
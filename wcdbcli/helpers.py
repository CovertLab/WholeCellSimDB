import dateutil.parser
import glob
import h5py
import numpy
import os
import pytz
import re
import scipy.io
import tempfile
from subprocess import call
from wcdb.models import SimulationBatch, Simulation
from WholeCellDB import settings

def save_simulation_batch(organism_name, batch_name, batch_dir, first_sim_idx = None, max_num_simulations = None, expand_sparse_mat=True):
    if first_sim_idx is None:
        first_sim_idx = 1
    
    #load metadata
    first_sim_dir = os.path.join(batch_dir, str(first_sim_idx))
    md = scipy.io.loadmat(os.path.join(first_sim_dir, 'metadata.mat'))
    organism_version = md['revision'][0][0]
    name = md['shortDescription'][0]
    description = md['longDescription'][0]
    investigator_first = md['firstName'][0]
    investigator_last = md['lastName'][0]
    investigator_affiliation = md['affiliation'][0]
    investigator_email = md['email'][0]
    ip = md['ipAddress'][0]
    date = dateutil.parser.parse(md['startTime'][0]).replace(tzinfo=pytz.timezone('America/Los_Angeles')) 
    
    #load options, parameters
    options = load_options(batch_dir, first_sim_dir)
    parameters = load_parameters(batch_dir, first_sim_dir)
    processes = parameters['processes'].keys()
    states = load_states(batch_dir, first_sim_dir)
    
    for state_name in options['states'].keys() + parameters['states'].keys():
        if state_name not in states:
            states[state_name] = {}
    
    #save batch
    SimulationBatch.objects.create_simulation_batch( 
        organism_name = organism_name,
        organism_version = organism_version,
        name = batch_name, 
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
    sim_dirs = sim_dirs[first_sim_idx-1:]
    if max_num_simulations is not None:
        sim_dirs = sim_dirs[:max_num_simulations]
    
    for sim_idx, sim_dir in enumerate(sim_dirs):
        print "Saving simulation %d of %d ... " % (sim_idx+1, len(sim_dirs))
        save_simulation(organism_name, batch_name, sim_dir, sim_idx+1, expand_sparse_mat)

def save_simulation(organism_name, batch_name, sim_dir, batch_index, expand_sparse_mat=True):
    #get batch name, length
    md = scipy.io.loadmat(os.path.join(sim_dir, 'metadata.mat'))
    length = md['lengthSec'][0][0]
    
    # get simulation batch
    batch = SimulationBatch.objects.get(organism__name = organism_name, name = batch_name)
    
    #create simulation
    sim = Simulation.objects.create_simulation(batch = batch, batch_index = batch_index, length = length)
    sim.save()
    
    #save property values data
    for state in batch.states.all():
        for property in state.properties.all():
            filename = os.path.join(sim_dir, 'state-%s-%s.mat' % (state.name, property.name))
            data = scipy.io.loadmat(filename)
            if 'data' in data:
                sim.property_values \
                    .get(property = property) \
                    .set_data(data['data'])
            elif 'None' in data and expand_sparse_mat and \
                isinstance(data['None'], scipy.io.matlab.mio5_params.MatlabOpaque) and \
                data['None'].tolist()[0][2] == 'edu.stanford.covert.util.SparseMat':
                
                tmp_filedescriptor, tmp_filename = tempfile.mkstemp(dir=settings.TMP_DIR, suffix='.mat')
                tmp_file = os.fdopen(tmp_filedescriptor, 'w')
                tmp_file.close()
                os.remove(tmp_filename)
                tmp_filename_h5 = tmp_filename.replace('.mat', '.h5')
                
                matlab_cmd = "setWarnings(); setPath(); warning('on', 'MATLAB:save:sizeTooBigForMATFile'); in_filename='%s'; out_filename='%s'; out_filename_h5='%s'; try; in = load(in_filename); out.data = full(in.data); save(out_filename, '-struct', 'out'); [~, id] = lastwarn(); if strcmp(id, 'MATLAB:save:sizeTooBigForMATFile'); delete(out_filename); save(out_filename_h5, '-struct', 'out', '-v7.3'); end; end; exit;" % (filename, tmp_filename, tmp_filename_h5)
                
                call('ssh covertlab-cluster "cd /home/projects/WholeCell/simulation; matlab -nodesktop -nosplash -r \\"%s\\" > /dev/null 2>&1"' % matlab_cmd, shell=True)
                
                try:
                    if os.path.isfile(tmp_filename):
                        data = scipy.io.loadmat(tmp_filename)
                        if 'data' in data:
                            sim.property_values \
                                .get(property = property) \
                                .set_data(data['data'])
                        data = None
                    elif os.path.isfile(tmp_filename_h5):
                        f = h5py.File(tmp_filename_h5, 'r')
                        if 'data' in f.keys():
                            sim.property_values \
                                .get(property = property) \
                                .set_data(f['data'])
                        f.close()
                        f = None
                    else:
                        print '  Unable to load %s.%s.%s.%s' % (batch.name, sim.batch_index, state.name, property.name)
                except:
                    print '  Unable to load %s.%s.%s.%s' % (batch.name, sim.batch_index, state.name, property.name)
                    
                if os.path.isfile(tmp_filename):
                    os.remove(tmp_filename)
                if os.path.isfile(tmp_filename_h5):
                    os.remove(tmp_filename_h5)
                    
    sim.lock_file()
    sim.save()
            
def load_options(batch_dir, first_sim_dir):
    units_labels = loadmat(os.path.join(batch_dir, 'units_labels.mat'))
    
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

def load_parameters(batch_dir, first_sim_dir):
    units_labels = loadmat(os.path.join(batch_dir, 'units_labels.mat'))
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

def load_states(batch_dir, first_sim_dir):
    units_labels = loadmat(os.path.join(batch_dir, 'units_labels.mat'))
    
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
                        tmp = dim_labels[0].tolist()
                        labels.append([x[0] if x.size > 0 else '' for x in tmp])
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

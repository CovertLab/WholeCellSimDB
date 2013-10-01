from collections import OrderedDict
from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext
from haystack.models import SearchResult
from WholeCellDB import settings
import datetime
import os


def get_option_dict(batch):
    """
    Returns an OrderedDict of options. 

    Things I'm not sure of:
        1) Is this returning the values, or just the names of the options
           as well as which State/Processes they are for.
        2) Should all SimulationRuns associated with a Batch of Simulatios
           have the same Option/Parameter values?
        3) Are Options/Paramters ever not associated with either a Process
           nor a State?

    """

    # An ordered dict remembers the order that keys were inserted into 
    # the dictionary. 
    options = OrderedDict()

    # It looks like this is getting all the options associated with a batch
    # of simulation runs that aren't associated with either a process
    # or a state. 

    for opt in batch.options.filter(process=None, state=None).order_by('name').values('name').annotate(Count('name')):
        tmp2 = [x[0] for x in batch.options.filter(process=None, state=None, name=opt['name']).order_by('index').values_list('value')] 
        if len(tmp2) == 1:
            tmp2 = tmp2[0]
        options[opt['name']] = tmp2

    # The options OrderedDict contains two keys ["processes", "states"] which
    # which point to other OrderedDicts
    options['processes'] = OrderedDict()
    for p in batch.processes.order_by('name'):
        tmp = OrderedDict()
        for opt in p.options.order_by('name').values('name').annotate(Count('name')):
            tmp2 = [x[0] for x in p.options.filter(name=opt['name']).order_by('index').values_list('value')]
            if len(tmp2) == 1:
                tmp2 = tmp2[0]
            tmp[opt['name']] = tmp2
        if len(tmp) > 0:
            options['processes'][p.name] = tmp
    
    options['states'] = OrderedDict()
    for s in batch.states.order_by('name'):
        tmp = OrderedDict()
        for opt in s.options.order_by('name').values('name').annotate(Count('name')):
            tmp2 = [x[0] for x in s.options.filter(name=opt['name']).order_by('index').values_list('value')]
            if len(tmp2) == 1:
                tmp2 = tmp2[0]
            tmp[opt['name']] = tmp2
            
        if len(tmp) > 0:
            options['states'][s.name] = tmp
    
    return options
    
def get_parameter_dict(batch):
    parameters = OrderedDict()
        
    for opt in batch.parameters.filter(process=None, state=None).order_by('name').values('name').annotate(Count('name')):
        tmp2 = [x[0] for x in batch.parameters.filter(process=None, state=None, name=opt['name']).order_by('index').values_list('value')] 
        if len(tmp2) == 1:
            tmp2 = tmp2[0]
        parameters[opt['name']] = tmp2
    
    parameters['processes'] = OrderedDict()
    for p in batch.processes.order_by('name'):
        tmp = OrderedDict()
        for opt in p.parameters.order_by('name').values('name').annotate(Count('name')):
            tmp2 = [x[0] for x in p.parameters.filter(name=opt['name']).order_by('index').values_list('value')]
            if len(tmp2) == 1:
                tmp2 = tmp2[0]
            tmp[opt['name']] = tmp2
        if len(tmp) > 0:
            parameters['processes'][p.name] = tmp
    
    parameters['states'] = OrderedDict()
    for s in batch.states.order_by('name'):
        tmp = OrderedDict()
        for opt in s.parameters.order_by('name').values('name').annotate(Count('name')):
            tmp2 = [x[0] for x in s.parameters.filter(name=opt['name']).order_by('index').values_list('value')]
            if len(tmp2) == 1:
                tmp2 = tmp2[0]
            tmp[opt['name']] = tmp2
            
        if len(tmp) > 0:
            parameters['states'][s.name] = tmp
    
    return parameters





def render_template(templateFile, request, data = {}):
    #add data
    data['last_updated_date'] = datetime.datetime.fromtimestamp(os.path.getmtime(settings.TEMPLATE_DIRS[0] + '/' + templateFile))

    #render
    return render_to_response(templateFile, data, context_instance = RequestContext(request))
        
def get_organism_list_with_stats(qs):
    organisms = []
    for organism in qs:
        if isinstance(organism, SearchResult):
            organism = organism.object
        batches = organism.simulation_batches.all()
        
        organisms.append({
            'id': organism.id,
            'name': organism.name,
            'n_version': batches.values('organism_version').annotate(Count('organism_version')).count(),
            'n_investigator': batches.values('investigator').annotate(Count('investigator')).count(),
            'n_simulation_batch': batches.count(),
            'n_simulation': sum([batch.simulations.count() for batch in batches]),
        })
    return organisms




def truncate_fields(obj):
    for key, val in obj.iteritems():
        if isinstance(val, dict):
            obj[key] = truncate_fields(val)
        elif isinstance(val, (list, tuple, )):
            idx = -1
            for subval in val:
                idx += 1
                obj[key][idx] = truncate_fields(subval)
        elif isinstance(val, (str, unicode)) and key not in ['content', 'text']:
            obj[key] = val[:225]
    return obj

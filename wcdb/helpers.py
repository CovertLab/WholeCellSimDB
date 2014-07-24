from ordereddict import OrderedDict
from django.db.models import Count
from itertools import tee, izip

def get_option_dict(batch):
    options = OrderedDict()

    for opt in batch.options.filter(process=None, state=None).order_by('name').values('name').annotate(Count('name')):
        tmp2 = list(batch.options.filter(process=None, state=None, name=opt['name']).order_by('index').values('value', 'units'))
        if len(tmp2) == 1:
            tmp2 = tmp2[0]
        options[opt['name']] = tmp2

    options['processes'] = OrderedDict()
    for p in batch.processes.order_by('name'):
        tmp = OrderedDict()
        for opt in p.options.order_by('name').values('name').annotate(Count('name')):
            tmp2 =list(p.options.filter(name=opt['name']).order_by('index').values('value', 'units'))
            if len(tmp2) == 1:
                tmp2 = tmp2[0]
            tmp[opt['name']] = tmp2
        if len(tmp) > 0:
            options['processes'][p.name] = tmp
    
    options['states'] = OrderedDict()
    for s in batch.states.order_by('name'):
        tmp = OrderedDict()
        for opt in s.options.order_by('name').values('name').annotate(Count('name')):
            tmp2 = list(s.options.filter(name=opt['name']).order_by('index').values('value', 'units'))
            if len(tmp2) == 1:
                tmp2 = tmp2[0]
            tmp[opt['name']] = tmp2
            
        if len(tmp) > 0:
            options['states'][s.name] = tmp
    
    return options
    
def get_parameter_dict(batch):
    parameters = OrderedDict()
        
    for opt in batch.parameters.filter(process=None, state=None).order_by('name').values('name').annotate(Count('name')):
        tmp2 = list(batch.parameters.filter(process=None, state=None, name=opt['name']).order_by('index').values('value', 'units'))
        if len(tmp2) == 1:
            tmp2 = tmp2[0]
        parameters[opt['name']] = tmp2
    
    parameters['processes'] = OrderedDict()
    for p in batch.processes.order_by('name'):
        tmp = OrderedDict()
        for opt in p.parameters.order_by('name').values('name').annotate(Count('name')):
            tmp2 = list(p.parameters.filter(name=opt['name']).order_by('index').values('value', 'units'))
            if len(tmp2) == 1:
                tmp2 = tmp2[0]
            tmp[opt['name']] = tmp2
        if len(tmp) > 0:
            parameters['processes'][p.name] = tmp
    
    parameters['states'] = OrderedDict()
    for s in batch.states.order_by('name'):
        tmp = OrderedDict()
        for opt in s.parameters.order_by('name').values('name').annotate(Count('name')):
            tmp2 = list(s.parameters.filter(name=opt['name']).order_by('index').values('value', 'units'))
            if len(tmp2) == 1:
                tmp2 = tmp2[0]
            tmp[opt['name']] = tmp2
            
        if len(tmp) > 0:
            parameters['states'][s.name] = tmp
    
    return parameters
    
def get_timestep(sim):
    time_propval = sim.property_values.get(property__state__name='Time', property__name='values')
    time_units = time_propval.property.units
    times = time_propval.get_dataset_slice()
    diff = times[0][0][1] - times[0][0][0]
    
    if time_units == 'h':
        diff *= 3600
    elif time_units == 'min':
        diff *= 60
    
    return float(diff)

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def is_sorted(iterable, key=None):
    if key is None:
        key = lambda a, b: a <= b
    return all(key(a, b) for a, b in pairwise(iterable))

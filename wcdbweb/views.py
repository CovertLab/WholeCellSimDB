from django.core.servers.basehttp import FileWrapper
from django.db.models import Avg, Count, Min, Max
from django.http import HttpResponse
from haystack.query import SearchQuerySet
from helpers import render_template
from wcdb import models
from wcdb.helpers import get_option_dict, get_parameter_dict
from WholeCellDB import settings
import copy
import forms
import helpers

###################
### landing page
###################
def index(request):
    summary = {
        'n_in_silico_organism': models.Organism.objects.all().count(),
        'n_simulation_batch': models.SimulationBatch.objects.all().count(), 
        'n_simulation': models.Simulation.objects.all().count(), 
        'n_process': models.Process.objects.values('name').annotate(count=Count('name')).count(),
        'n_state': models.State.objects.values('name').annotate(count=Count('name')).count(),
        'n_property': models.Property.objects
            .values('name', 'state__name')
            .annotate(Count('name'), Count('state__name'))
            .count(),
        'n_parameter': models.Parameter.objects
            .values('name', 'process__name', 'state__name')
            .annotate(Count('name'), Count('process__name'), Count('state__name'))
            .count(),
        'n_option': models.Option.objects
            .values('name', 'process__name', 'state__name')
            .annotate(Count('name'), Count('process__name'), Count('state__name'))
            .count(),
        'n_investigator': models.Investigator.objects.all().count(),
    }
    return render_template('index.html', request, data = {
            'summary': summary
        })
        
###################
### slicing
###################
def list_investigators(request):
    investigators = helpers.get_investigator_list_with_stats(models.Investigator.objects.all())

    return render_template('list_investigators.html', request, data = {
        'investigators': investigators
        })
    
def investigator(request, id):
    investigator = models.Investigator.objects.get(id=id)
        
    #organisms = models.Organism.objects.all().filter(simulation_batches__investigator__id=id)
    tmp = {}
    for batch in investigator.simulation_batches.all().annotate(n_simulations = Count('simulations')):
        if not tmp.has_key(batch.organism.id):
            tmp[batch.organism.id] = {'id': batch.organism.id, 'name': batch.organism.name, 'versions': [], 'n_simulation_batches': 0, 'n_simulatons': 0}
        tmp[batch.organism.id]['versions'].append(batch.organism_version)
        tmp[batch.organism.id]['n_simulation_batches'] += 1
        tmp[batch.organism.id]['n_simulatons'] += batch.n_simulations
        
    organisms = []
    for id, tmp2 in tmp.iteritems():
        organisms.append({
            'id': tmp2['id'],
            'name': tmp2['name'],
            'n_versions': len(set(tmp2['versions'])),
            'n_simulation_batches': tmp2['n_simulation_batches'],
            'n_simulatons': tmp2['n_simulatons']
            })
    
    return render_template('investigator.html', request, data = {
        'investigator': investigator,
        'organisms': organisms
        })
    
def list_organisms(request):
    organisms = helpers.get_organism_list_with_stats(models.Organism.objects.all())
            
    return render_template('list_organisms.html', request, data = {
        'organisms': organisms
        })
    
def organism(request, id):
    organism = models.Organism.objects.get(id=id)
    investigators = {}
    for batch in organism.simulation_batches.all():
        if not investigators.has_key(batch.investigator.id):
            investigators[batch.investigator.id] = {
                'id': batch.investigator.id,
                'full_name': batch.investigator.user.get_full_name(),
                'affiliation': batch.investigator.affiliation,
                'n_simulation_batch': 0,
                'n_simulation': 0
                }
        investigators[batch.investigator.id]['n_simulation_batch'] += 1
        investigators[batch.investigator.id]['n_simulation'] += batch.simulations.count()            
    
    return render_template('organism.html', request, data = {
        'organism': organism,
        'investigators': investigators,
        })
    
def list_simulation_batches(request):    
    batches = helpers.get_simulation_batch_list_with_stats(models.SimulationBatch.objects.all())
    
    return render_template('list_simulation_batches.html', request, data = {
        'batches': batches
    })
    
def simulation_batch(request, id):
    batch = models.SimulationBatch.objects.get(id=id)    
    return render_template('simulation_batch.html', request, data = {
        'batch': batch,
        'processes': batch.processes.order_by('name'),
        'states': batch.states.order_by('name'),
        'options': get_option_dict(batch),
        'parameters': get_parameter_dict(batch),
    })
    
def list_simulations(request):    
    simulations = models.Simulation.objects.all()
    return render_template('list_simulations.html', request, data = {
        'simulations': simulations
    })
    
#TODO
def simulation(request, id):
    simulation = models.Simulation.objects.get(id=id)    
    batch = simulation.batch
    return render_template('simulation.html', request, data = {
        'simulation': simulation,
        'batch': batch,
    })
    
def list_options(request):
    options = models.Option.objects.all()
    
    organisms = models.Organism.objects.all()
    simulation_batches = models.SimulationBatch.objects.order_by('organism__name', 'name')    
    simulation_batch_ids = [x[0] for x in simulation_batches.values_list('id')]
    
    options = {
        'Global': models.Option.objects
            .filter(process__isnull=True, state__isnull=True)
            .values('name', 'units', 'value', 'index', 'simulation_batch__id', 'simulation_batch__name')
            .order_by('name', 'simulation_batch__name', 'index'),
        'Processes': models.Option.objects
            .filter(process__isnull=False)
            .values('process__name', 'name', 'units', 'value', 'index', 'simulation_batch__id', 'simulation_batch__name')
            .order_by('process__name', 'name', 'simulation_batch__name', 'index'),
        'States': models.Option.objects
            .filter(state__isnull=False)
            .values('state__name', 'name', 'units', 'value', 'index', 'simulation_batch__id', 'simulation_batch__name')
            .order_by('state__name', 'name', 'simulation_batch__name', 'index'),
        }
    
    return render_template('list_options.html', request, data = {
        'organisms': organisms,
        'simulation_batches': simulation_batches,
        'simulation_batch_ids': simulation_batch_ids,
        'options': options
    })
    
def option(request, option_name, process_name=None, state_name=None):
    options = models.Option.objects \
        .filter(name=option_name, process__name=process_name, state__name=state_name) \
        .values('name', 'process__name', 'state__name', 'simulation_batch__organism__id', 'simulation_batch__organism__name', 'simulation_batch__id', 'simulation_batch__name', 'value', 'units') \
        .order_by('simulation_batch__organism__name', 'simulation_batch__name')
    return render_template('option.html', request, data = {
        'option_name': option_name,
        'process_name': process_name,
        'state_name': state_name,
        'options': options
    })
    
def list_parameters(request):
    organisms = models.Organism.objects.all()
    simulation_batches = models.SimulationBatch.objects.order_by('organism__name', 'name')    
    simulation_batch_ids = [x[0] for x in simulation_batches.values_list('id')]
    
    parameters = {
        'Global': models.Parameter.objects
            .filter(process__isnull=True, state__isnull=True)
            .values('name', 'units', 'value', 'index', 'simulation_batch__id', 'simulation_batch__name')
            .order_by('name', 'simulation_batch__name', 'index'),
        'Processes': models.Parameter.objects
            .filter(process__isnull=False)
            .values('process__name', 'name', 'units', 'value', 'index', 'simulation_batch__id', 'simulation_batch__name')
            .order_by('process__name', 'name', 'simulation_batch__name', 'index'),
        'States': models.Parameter.objects
            .filter(state__isnull=False)
            .values('state__name', 'name', 'units', 'value', 'index', 'simulation_batch__id', 'simulation_batch__name')
            .order_by('state__name', 'name', 'simulation_batch__name', 'index'),
        }
    
    return render_template('list_parameters.html', request, data = {
        'organisms': organisms,
        'simulation_batches': simulation_batches,
        'simulation_batch_ids': simulation_batch_ids,
        'parameters': parameters
    })
    
def parameter(request, parameter_name, process_name=None, state_name=None):
    parameters = models.Parameter.objects \
        .filter(name=parameter_name, process__name=process_name, state__name=state_name) \
        .values('name', 'process__name', 'state__name', 'simulation_batch__organism__id', 'simulation_batch__organism__name', 'simulation_batch__id', 'simulation_batch__name', 'value', 'units') \
        .order_by('simulation_batch__organism__name', 'simulation_batch__name')
    return render_template('parameter.html', request, data = {
        'parameter_name': parameter_name,
        'process_name': process_name,
        'state_name': state_name,
        'parameters': parameters
    })
    
def list_processes(request):
    organisms = models.Organism.objects.all()
    simulation_batches = models.SimulationBatch.objects.order_by('organism__name', 'name')
    simulation_batch_ids = [x[0] for x in simulation_batches.values_list('id')]
    processes =  models.Process.objects \
        .values('name', 'simulation_batch__id', 'simulation_batch__name') \
        .order_by('name', 'simulation_batch__name')
    
    return render_template('list_processes.html', request, data = {
        'organisms': organisms,
        'simulation_batches': simulation_batches,
        'simulation_batch_ids': simulation_batch_ids,
        'processes': processes
    })
    
#TODO
def process(request, process_name):
    process = models.Process.objects.filter(name=process_name)
    return render_template('process.html', request, data = {
        'process': process
    })
    
def list_states(request):
    organisms = models.Organism.objects.all()
    simulation_batches = models.SimulationBatch.objects.order_by('organism__name', 'name')
    simulation_batch_ids = [x[0] for x in simulation_batches.values_list('id')]
    state_properties =  models.Property.objects \
        .values('name', 'state__name', 'state__simulation_batch__id', 'state__simulation_batch__name') \
        .order_by('state__name', 'name', 'state__simulation_batch__name')
    
    return render_template('list_states.html', request, data = {
        'organisms': organisms,
        'simulation_batches': simulation_batches,
        'simulation_batch_ids': simulation_batch_ids,
        'state_properties': state_properties
    })
    
#TODO
def state(request, state_name):
    state = models.State.objects.filter(name=state_name)
    return render_template('state.html', request, data = {
        'state': state
    })
    
#TODO
def state_property(request, state_name, property_name):
    property = models.Property.objects.filter(name=property_name, state__name=state_name)
    return render_template('property.html', request, data = {
        'property': property
    })

#TODO    
def state_property_row(request, state_name, property_name, row_name):
    row = models.Label.objects.filter(dimension=1, name=property_name, property__name=property_name, property__state__name=state_name)
    return render_template('state_property_row.html', request, data = {
        'row': row
    })

#TODO    
def state_property_row_batch(request, state_name, property_name, row_name, batch_id):
    row = models.Label.objects.get(dimension=1, name=property_name, property__name=property_name, property__state__name=state_name, property__state__simulation_batch__id=batch_id)
    return render_template('state_property_row_batch.html', request, data = {
        'row': row
    })
    
###################
### downloading
###################
def download(request):
    form = forms.DownloadForm(request.POST)
    if not form.is_valid():        
        return render_template(
            request = request,
            templateFile = 'download.html', 
            data = {
                'form': form,
                'organisms': models.Organism.objects.all()
                }
            )
    else:
        batches = models.SimulationBatches.objects.filter(id__in=form.cleaned_data['simulation_batches'])
        return helpers.download_batches(batches, 'WholeCellDB')        

def organism_download(request, id):
    organism = models.Organism.objects.get(id=id)    
    return helpers.download_batches(organism.simulation_batches.all(), organism.name)   
    
def simulation_batch_download(request, id):
    batch = models.SimulationBatch.objects.get(id=id)    
    return helpers.download_batches([batch], batch.name)    
    
def simulation_download(request, id):
    simulation = models.Simulation.objects.get(id=id)
    file = open(simulation.file_path, 'rb')
    file.seek(0,2)
    fileWrapper = FileWrapper(file)
    response = HttpResponse(
        fileWrapper,
        mimetype = "application/x-hdf",
        content_type = "application/x-hdf"
        )
    response['Content-Disposition'] = ("attachment; filename=simulation-%d.h5" % simulation.id)
    response['Content-Length'] = file.tell()
    file.seek(0)
    return response
    
def investigator_download(request, id):
    investigator = models.Investigator.objects.get(id=id)    
    return helpers.download_batches(investigator.simulation_batches.all(), investigator.user.get_full_name())
    
###################
### searching
###################
def search_basic(request):
    query = request.GET.get('query', '')
    format = request.GET.get('format', 'html')
    engine = request.GET.get('engine', 'haystack')
    
    if engine == 'google':
        return search_basic_google(request, query)
    return search_basic_haystack(request, query, format)
    
def search_basic_haystack(request, query, format='html'):
    batches = SearchQuerySet().models(models.SimulationBatch).filter(text=query).order_by('organism__name', 'name')
    organisms = SearchQuerySet().models(models.Organism).filter(text=query).order_by('name')
    investigators = SearchQuerySet().models(models.Investigator).filter(text=query).order_by('last_name', 'first_name', 'affiliation')
    
    if format == 'hdf5':
        batches = [batch.object for batch in batches] 
        for organism in organisms:
            batches = batches + list(organism.object.simulation_batches.all())
        for investigator in investigators:
            batches = batches + list(investigator.object.simulation_batches.all())
            
        batches = set(batches)
        
        return helpers.download_batches(batches, 'WholeCellDB-search-basic')

    return render_template('search_basic_haystack.html', request, data = {
        'organisms': helpers.get_organism_list_with_stats(organisms),
        'batches': helpers.get_simulation_batch_list_with_stats(batches),
        'investigators': helpers.get_investigator_list_with_stats(investigators),
        'query': query,
        'engine': 'haystack',
        })

def search_basic_google(request, query):
    return render_template('search_basic_google.html', request, data = {
        'query': query,
        'engine': 'google',
        })

def search_advanced(request):
    valid = request.method == "POST"
    
    #form
    form = forms.AdvancedSearchForm(request.POST or {'result_format': 'html', 'n_option_filters': 3, 'n_parameter_filters': 3, 'n_process_filters': 3, 'n_state_filters': 3})
    valid = form.is_valid() and valid
    
    if valid:
        n_option_filters = form.cleaned_data['n_option_filters']
        n_parameter_filters = form.cleaned_data['n_parameter_filters']
        n_process_filters = form.cleaned_data['n_process_filters']
        n_state_filters = form.cleaned_data['n_state_filters']
    else:
        n_option_filters = 3
        n_parameter_filters = 3
        n_process_filters = 3
        n_state_filters = 3
    
    #options
    tmp = {('option-%d-operator' % i): 'eq' for i in range(n_option_filters)}
    tmp = dict(tmp.items() + request.POST.items())
    option_form = forms.AdvancedSearchOptionForm(tmp)
    option_forms = []
    for i in range(n_option_filters):
        option_form_i = copy.deepcopy(option_form)
        option_form_i.prefix = 'option-%d' % i
        option_form_i._errors = None
        option_form_i._changed_data = None
        option_forms.append(option_form_i)
        valid = option_form_i.is_valid() and valid
    
    #parameters
    tmp = {('parameter-%d-operator' % i): 'eq' for i in range(n_parameter_filters)}
    tmp = dict(tmp.items() + request.POST.items())
    parameter_forms = []
    parameter_form = forms.AdvancedSearchParameterForm(tmp)
    for i in range(n_parameter_filters):
        parameter_form_i = copy.deepcopy(parameter_form)
        parameter_form_i.prefix = 'parameter-%d' % i
        parameter_form_i._errors = None
        parameter_form_i._changed_data = None
        parameter_forms.append(parameter_form_i)
        valid = parameter_form_i.is_valid() and valid
        
    #processes
    tmp = {('process-%d-modeled' % i): '1' for i in range(n_process_filters)}
    tmp = dict(tmp.items() + request.POST.items())
    process_forms = []
    process_form = forms.AdvancedSearchProcessForm(tmp)
    for i in range(n_process_filters):
        process_form_i = copy.deepcopy(process_form)
        process_form_i.prefix = 'process-%d' % i
        process_form_i._errors = None
        process_form_i._changed_data = None
        process_forms.append(process_form_i)
        valid = process_form_i.is_valid() and valid
        
    #states
    tmp = {('state-%d-modeled' % i): '1' for i in range(n_state_filters)}
    tmp = dict(tmp.items() + request.POST.items())
    state_forms = []
    state_form = forms.AdvancedSearchStateForm(tmp)
    for i in range(n_state_filters):
        state_form_i = copy.deepcopy(state_form)
        state_form_i.prefix = 'state-%d' % i
        state_form_i._errors = None
        state_form_i._changed_data = None
        state_forms.append(state_form_i)
        valid = state_form_i.is_valid() and valid
         
    #filter batches
    if valid:
        batches = models.SimulationBatch.objects.all()
        
        #investigator
        if form.cleaned_data['investigator_name_first']:
            batches = batches.filter(investigator__user__first_name__icontains=form.cleaned_data['investigator_name_first'])
        if form.cleaned_data['investigator_name_last']:
            batches = batches.filter(investigator__user__last_name__icontains=form.cleaned_data['investigator_name_last'])
        if form.cleaned_data['investigator_affiliation']:
            batches = batches.filter(investigator__affiliation__icontains=form.cleaned_data['investigator_affiliation'])
        
        #organism
        if form.cleaned_data['organism_name']:
            batches = batches.filter(organism__name__icontains=form.cleaned_data['organism_name'])
        if form.cleaned_data['organism_version']:
            batches = batches.filter(organism_version__icontains=form.cleaned_data['organism_version'])
        
        #batch metadata
        if form.cleaned_data['simulation_batch_name']:
            batches = batches.filter(name__icontains=form.cleaned_data['simulation_batch_name'])
        if form.cleaned_data['simulation_batch_ip']:
            batches = batches.filter(ip__icontains=form.cleaned_data['simulation_batch_ip'])
        if form.cleaned_data['simulation_batch_date']: 
            date = form.cleaned_data['simulation_batch_date']            
            batches = batches.filter(date__year = date.year, date__month = date.month, date__day = date.day)
            
        #options, parameters, processes, states
        batches = search_advanced_options(batches, option_forms)
        batches = search_advanced_parameters(batches, parameter_forms)
        batches = search_advanced_processes(batches, process_forms)
        batches = search_advanced_states(batches, state_forms)
        
        #exit if data requested in hdf5 format
        if form.cleaned_data['result_format'] == 'hdf5':
            return helpers.download_batches(batches, 'WholeCellDB-advanced-search')
            
        #get related organisms and investigators
        organisms = models.Organism.objects.filter(simulation_batches__id__in=batches.values_list('id'))
        investigators = models.Investigator.objects.filter(simulation_batches__id__in=batches.values_list('id'))
    
        #calculate stats for results table
        organisms = helpers.get_organism_list_with_stats(organisms)
        batches = helpers.get_simulation_batch_list_with_stats(batches)
        investigators = helpers.get_investigator_list_with_stats(investigators)
    else:
        organisms = None
        batches = None
        investigators = None
    
    return render_template('search_advanced.html', request, data = {
        'valid': valid,
        'form': form,
        'option_forms': option_forms,
        'parameter_forms': parameter_forms,
        'process_forms': process_forms,
        'state_forms': state_forms,
        'organisms': organisms,
        'batches': batches,
        'investigators': investigators,
        })
        
def search_advanced_options(batches, forms):
    for form in forms:
        if hasattr(form, 'cleaned_data') and form.cleaned_data['option']:
            filter = {}
                
            #state/process
            option = form.cleaned_data['option']
            if ':' in option:
                is_state_process, option = option.split(':')
                state_process_name, option = option.split('.')
                if is_state_process is 'state':
                    filter['options__state__name'] = state_process_name
                else:
                    filter['options__process__name'] = state_process_name
            else:
                filter['options__process'] = None
                filter['options__state'] = None
                
            #index
            if '[' in option:
                option, index = option[:-1].split('[')
                filter['options__index'] = int(float(index))
            else:
                filter['options__index'] = 0

            #option
            filter['options__name'] = option
                
            #operator, value                  
            operator = form.cleaned_data['operator']
            if operator == 'eq':
                operator = ''
            else:
                operator = '__' + operator
                
            value = form.cleaned_data['value']
            filter['options__value' + operator] = value
            
            #filter
            batches = batches.filter(**filter)
            
    return batches
    
def search_advanced_parameters(batches, forms):
    for form in forms:
        if hasattr(form, 'cleaned_data') and form.cleaned_data['parameter']:
            filter = {}
                
            #state/process
            parameter = form.cleaned_data['parameter']
            if ':' in parameter:
                is_state_process, parameter = parameter.split(':')
                state_process_name, parameter = parameter.split('.')
                if is_state_process is 'state':
                    filter['parameters__state__name'] = state_process_name
                else:
                    filter['parameters__process__name'] = state_process_name
            else:
                filter['parameters__process'] = None
                filter['parameters__state'] = None
                
            #index
            if '[' in parameter:
                parameter, index = parameter[:-1].split('[')
                filter['parameters__index'] = int(float(index))
            else:
                filter['parameters__index'] = 0

            #parameter
            filter['parameters__name'] = parameter
                
            #operator, value                  
            operator = form.cleaned_data['operator']
            if operator == 'eq':
                operator = ''
            else:
                operator = '__' + operator
                
            value = form.cleaned_data['value']
            filter['parameters__value' + operator] = value
            
            #filter
            batches = batches.filter(**filter)
            
    return batches

def search_advanced_processes(batches, forms):
    for form in forms:
        if hasattr(form, 'cleaned_data') and form.cleaned_data['process']:
            if form.cleaned_data['modeled'] == '1':
                batches = batches.filter(processes__name = form.cleaned_data['process'])
            else:
                batches = batches.exclude(processes__name = form.cleaned_data['process'])
    
    return batches
    
def search_advanced_states(batches, forms):
    for form in forms:
        if hasattr(form, 'cleaned_data') and form.cleaned_data['state_property']:
            state, property = form.cleaned_data['state_property'].split('.')            
            if form.cleaned_data['modeled'] == '1':
                batches = batches.filter(states__name = state, states__properties__name=property)
            else:
                batches = batches.exclude(states__name = state, states__properties__name=property)
    
    return batches

def sitemap(request):
    return render_template('sitemap.xml', request, data = {
        'ROOT_URL': settings.ROOT_URL,
        'simulation_batches': models.SimulationBatch.objects.all(),
        })
        
def sitemap_top_level(request):
    return render_template('sitemap_top_level.xml', request, data = {
        'ROOT_URL': settings.ROOT_URL,
        'organisms': models.Organism.objects.all(),
        'simulation_batches': models.SimulationBatch.objects.all(),
        'simulations': models.Simulation.objects.all(),
        'investigators': models.Investigator.objects.all(),
        'options': models.Option.objects
            .values('name', 'state__name', 'process__name', 'simulation_batch__date')
            .annotate(Count('name'), Count('state__name'), Count('process__name'), date=Max('simulation_batch__date'))
            .order_by('process__name', 'state__name', 'name'),
        'parameters': models.Parameter.objects
            .values('name', 'state__name', 'process__name', 'simulation_batch__date')
            .annotate(Count('name'), Count('state__name'), Count('process__name'), date=Max('simulation_batch__date'))
            .order_by('process__name', 'state__name', 'name'),
        'processes': models.Process.objects
            .values('name', 'simulation_batch__date')
            .annotate(Count('name'), date=Max('simulation_batch__date'))
            .order_by('name'),
        'states': models.State.objects
            .values('name', 'simulation_batch__date')
            .annotate(Count('name'), date=Max('simulation_batch__date'))
            .order_by('name'),
        'state_properties': models.Property.objects
            .values('name', 'state__name', 'state__simulation_batch__date')
            .annotate(Count('name'), Count('state__name'), date=Max('state__simulation_batch__date'))
            .order_by('state__name', 'name')
        })
        
def sitemap_simulation_batch(request):
    id = request.GET.get('id', None)
    return render_template('sitemap_simulation_batch.xml', request, data = {
        'ROOT_URL': settings.ROOT_URL,
        'batch': models.SimulationBatch.objects.get(id=id),
        })
        
###################
### documentation
###################
def tutorial(request):
    return render_template('tutorial.html', request)
    
def help(request):
    return render_template('help.html', request)
    
def about(request):
    return render_template('about.html', request)
    
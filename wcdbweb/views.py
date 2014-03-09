from django.core.servers.basehttp import FileWrapper
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from haystack.query import SearchQuerySet
from helpers import render_template
from wcdb import models
from wcdb.helpers import get_option_dict, get_parameter_dict
from WholeCellDB import settings
import copy
import forms
import helpers
import os
import re
import tempfile
import time
import zipfile

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
    
def simulation(request, id):
    simulation = models.Simulation.objects.get(id=id)    
    batch = simulation.batch
    return render_template('simulation.html', request, data = {
        'simulation': simulation,
        'batch': batch,
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
        if not os.path.isdir(settings.ROOT_DIR):
            os.mkdir(settings.TMP_DIR)
        
        file = tempfile.TemporaryFile(dir=settings.TMP_DIR)
        zip = zipfile.ZipFile(file, 'w')

        for batch_id in form.cleaned_data['simulation_batches']:
            batch = models.SimulationBatch.objects.get(id=batch_id)
            for simulation in batch.simulations.all():
                zip.write(simulation.file_path, '%s/%s/%d.h5' % (slugify(batch.organism.name), slugify(batch.name), simulation.batch_index))
        zip.close()
        fileWrapper = FileWrapper(file)
        response = HttpResponse(
            fileWrapper,
            mimetype = "application/x-zip",
            content_type = "application/x-zip"
            )
        response['Content-Disposition'] = "attachment; filename=WholeCellDB.zip"
        response['Content-Length'] = file.tell()
        file.seek(0)
        return response

def organism_download(request, id):
    organism = models.Organism.objects.get(id=id)
    
    if not os.path.isdir(settings.ROOT_DIR):
        os.mkdir(settings.TMP_DIR)
    
    file = tempfile.TemporaryFile(dir=settings.TMP_DIR)
    zip = zipfile.ZipFile(file, 'w')
    for batch in organism.simulation_batches.all():
        for simulation in batch.simulations.all():
            zip.write(simulation.file_path, '%s/%s/%d.h5' % (slugify(organism.name), slugify(batch.name), simulation.batch_index))
    zip.close()
    fileWrapper = FileWrapper(file)
    response = HttpResponse(
        fileWrapper,
        mimetype = "application/x-zip",
        content_type = "application/x-zip"
        )
    response['Content-Disposition'] = ("attachment; filename=%s.zip" % slugify(organism.name))
    response['Content-Length'] = file.tell()
    file.seek(0)
    return response
    
def simulation_batch_download(request, id):
    batch = models.SimulationBatch.objects.get(id=id)
    
    if not os.path.isdir(settings.ROOT_DIR):
        os.mkdir(settings.TMP_DIR)
    
    file = tempfile.TemporaryFile(dir=settings.TMP_DIR)
    zip = zipfile.ZipFile(file, 'w')
    for simulation in batch.simulations.all():
        zip.write(simulation.file_path, '%s/%s/%d.h5' % (slugify(batch.organism.name), slugify(batch.name), simulation.batch_index))
    zip.close()
    fileWrapper = FileWrapper(file)
    response = HttpResponse(
        fileWrapper,
        mimetype = "application/x-zip",
        content_type = "application/x-zip"
        )
    response['Content-Disposition'] = ("attachment; filename=%s.zip" % slugify(batch.name))
    response['Content-Length'] = file.tell()
    file.seek(0)
    return response
    
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
    
    if not os.path.isdir(settings.ROOT_DIR):
        os.mkdir(settings.TMP_DIR)
    
    file = tempfile.TemporaryFile(dir=settings.TMP_DIR)
    zip = zipfile.ZipFile(file, 'w')
    for batch in investigator.simulation_batches.all():
        for simulation in batch.simulations.all():
            zip.write(simulation.file_path, '%s/%s/%d.h5' % (slugify(batch.organism.name), slugify(batch.name), simulation.batch_index))
    zip.close()
    fileWrapper = FileWrapper(file)
    response = HttpResponse(
        fileWrapper,
        mimetype = "application/x-zip",
        content_type = "application/x-zip"
        )
    response['Content-Disposition'] = ("attachment; filename=%s.zip" % slugify(investigator.user.get_full_name()))
    response['Content-Length'] = file.tell()
    file.seek(0)
    return response
    
###################
### searching
###################
def search_basic(request):
    query = request.GET.get('q', '')
    engine = request.GET.get('engine', 'haystack')
    
    if engine == 'google':
        return search_basic_google(request, query)
    return search_basic_haystack(request, query)
    
def search_basic_haystack(request, query):
    organisms = helpers.get_organism_list_with_stats(SearchQuerySet().models(models.Organism).filter(text=query).order_by('name'))
    batches = helpers.get_simulation_batch_list_with_stats(SearchQuerySet().models(models.SimulationBatch).filter(text=query).order_by('organism__name', 'name'))
    investigators = helpers.get_investigator_list_with_stats(SearchQuerySet().models(models.Investigator).filter(text=query).order_by('last_name', 'first_name', 'affiliation'))

    return render_template('search_basic_haystack.html', request, data = {
        'organisms': organisms,
        'batches': batches,
        'investigators': investigators,
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
    form = forms.AdvancedSearchForm(request.POST or {'n_option_filters': 3, 'n_parameter_filters': 3, 'n_process_filters': 3})
    valid = form.is_valid() and valid
    
    if valid:
        n_option_filters = form.cleaned_data['n_option_filters']
        n_parameter_filters = form.cleaned_data['n_parameter_filters']
        n_process_filters = form.cleaned_data['n_process_filters']
    else:
        n_option_filters = 3
        n_parameter_filters = 3
        n_process_filters = 3
    
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

def sitemap(request):
    return render_template('sitemap.xml', request, data = {
        'ROOT_URL': settings.ROOT_URL,
        'organisms': models.Organism.objects.all(),
        'investigators': models.Investigator.objects.all(),
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
    
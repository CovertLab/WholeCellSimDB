from django.core.servers.basehttp import FileWrapper
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from django.views.decorators.csrf import csrf_exempt
from haystack.query import SearchQuerySet
from helpers import render_template
from wcdb import models
from wcdb.helpers import get_option_dict, get_parameter_dict
from WholeCellDB import settings
import forms
import helpers
import os
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
    investigators = []
    for investigator in models.Investigator.objects.all():
        batches = investigator.simulation_batches.all()
                
        investigators.append({
            'id': investigator.id,
            'full_name': investigator.user.get_full_name,
            'affiliation': investigator.affiliation,
            'n_organism': batches.values('organism').annotate(Count('organism')).count(),
            'n_simulation_batches': batches.count(),
            'n_simulation': sum([batch.simulations.count() for batch in batches]),
            })

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
    batches = models.SimulationBatch.objects.all()
    batches = batches.annotate(length_avg=Avg('simulations__length'))
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
    batches = SearchQuerySet().models(models.SimulationBatch).filter(text=query).order_by('organism__name', 'name')

    return render_template('search_basic_haystack.html', request, data = {
        'organisms': organisms,
        'batches': batches,
        'query': query,
        'engine': 'haystack',
        })

def search_basic_google(request, query):
    return render_template('search_basic_google.html', request, data = {
        'query': query,
        'engine': 'google',
        })
    
@csrf_exempt
def search_advanced(request):
    if request.method == "POST":
        form = forms.AdvancedSearchForm(data=request.POST)
        if form.is_valid():
            organisms = models.Organism.objects.all()
            batches = models.SimulationBatch.objects.all()
            
            searchIsEmpty = True
            
            #investigator
            if not form.cleaned_data['investigator_name_first'] == '':
                searchIsEmpty = False
                organisms = organisms.filter(simulation_batches__investigator__user__first_name__icontains=form.cleaned_data['investigator_name_first'])
                batches = batches.filter(investigator__user__first_name__icontains=form.cleaned_data['investigator_name_first'])
            if not form.cleaned_data['investigator_name_last'] == '':
                searchIsEmpty = False
                organisms = organisms.filter(simulation_batches__investigator__user__last_name__icontains=form.cleaned_data['investigator_name_last'])
                batches = batches.filter(investigator__user__last_name__icontains=form.cleaned_data['investigator_name_last'])
            if not form.cleaned_data['investigator_affiliation'] == '':
                searchIsEmpty = False
                organisms = organisms.filter(simulation_batches__investigator__affiliation__icontains=form.cleaned_data['investigator_affiliation'])
                batches = batches.filter(investigator__affiliation__icontains=form.cleaned_data['investigator_affiliation'])
            
            #organism
            if not form.cleaned_data['organism_name'] == '':
                searchIsEmpty = False
                organisms = organisms.filter(simulation_batches__organism__name__icontains=form.cleaned_data['organism_name'])
                batches = batches.filter(organism__name__icontains=form.cleaned_data['organism_name'])
            if not form.cleaned_data['organism_version'] == '':
                searchIsEmpty = False
                organisms = organisms.filter(simulation_batches__organism_version__icontains=form.cleaned_data['organism_version'])
                batches = batches.filter(organism_version__icontains=form.cleaned_data['organism_version'])
            
            #batch meta data
            if not form.cleaned_data['simulation_batch_name'] == '':
                searchIsEmpty = False
                organisms = organisms.filter(simulation_batches__name__icontains=form.cleaned_data['simulation_batch_name'])
                batches = batches.filter(name__icontains=form.cleaned_data['simulation_batch_name'])
            if not form.cleaned_data['simulation_batch_ip'] == '':
                searchIsEmpty = False
                organisms = organisms.filter(simulation_batches__ip__icontains=form.cleaned_data['simulation_batch_ip'])
                batches = batches.filter(ip__icontains=form.cleaned_data['simulation_batch_ip'])
            if not form.cleaned_data['simulation_batch_date'] == '':                
                try:                  
                    date = time.strptime(form.cleaned_data['simulation_batch_date'], '%m/%d/%Y')
                    
                    searchIsEmpty = False
                    organisms = organisms.filter(
                        simulation_batches__date__year=date.tm_year, 
                        simulation_batches__date__month=date.tm_mon,
                        simulation_batches__date__day=date.tm_mday)
                    batches = batches.filter(
                        date__year=date.tm_year,
                        date__month=date.tm_mon,
                        date__day=date.tm_mday)
                except:
                    pass
            if not form.cleaned_data['simulation_batch_options'] == '':
                pass #TODO
            if not form.cleaned_data['simulation_batch_parameters'] == '':
                pass #TODO
            
            #values
            if not form.cleaned_data['simulation_states'] == '':
                pass #TODO
            
            if not searchIsEmpty:            
                organisms = helpers.get_organism_list_with_stats(organisms)
                return render_template('search_advanced_results.html', request, data = {
                    'form': form,
                    'organisms': organisms,
                    'batches': batches,
                    })
    
    form = forms.AdvancedSearchForm(request)
    return render_template('search_advanced_form.html', request, data = {
        'form': form 
        })

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
    
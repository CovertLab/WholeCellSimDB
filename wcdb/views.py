from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from haystack.query import SearchQuerySet
from helpers import render_template
from wcdb.models import * 
from wcdb.helpers import get_option_dict, get_parameter_dict
from WholeCellDB import settings
import forms
import helpers
import time

def index(request):
    summary = {
        'n_organism': Organism.objects.count(),
        'n_simulation_batch': SimulationBatch.objects.count(), 
        'n_simulation': Simulation.objects.count(), 
        'n_process': Process.objects.values('name').annotate(count=Count('name')).count(),
        'n_state': State.objects.values('name').annotate(count=Count('name')).count(),
        'n_property': Property.objects.values('name', 'state__name').annotate(Count('name'), Count('state__name')).count(),
        'n_parameter': Parameter.objects.values('name', 'target__name').annotate(Count('name'), Count('target__name')).count(),
        'n_option': Option.objects.values('name', 'target__name').annotate(Count('name'), Count('target__name')).count(),
        'n_investigator': Investigator.objects.all().count(),
    }
    return render_template('index.html', request, data = {
            'summary': summary
        })
        
def list_investigators(request):
    investigators = []
    for investigator in Investigator.objects.all():
        batches = investigator.simulation_batches.all()
                
        investigators.append({
            'id': investigator.id,
            'full_name': investigator.get_full_name,
            'affiliation': investigator.affiliation,
            'n_simulation_batches': batches.count(),
            'n_simulation': sum([batch.simulations.count() for batch in batches]),
            })

    return render_template('list_investigators.html', request, data = {
        'investigators': investigators
        })
    
def investigator(request, id):
    return render_template('investigator.html', request, data = {
        'investigator': Investigator.objects.get(id=id)
        })
    
# Organism
def list_organisms(request):
    organisms = helpers.get_organism_list_with_stats(Organism.objects.all())
            
    return render_template('list_organisms.html', request, data = {
        'organisms': organisms
        })
    
def organism(request, id):
    organism = Organism.objects.get(id=id)

    return render_template('organism.html', request, data = {
        'organism': organism,
        })
    
# Batches
def list_simulation_batches(request):    
    batches = models.SimulationBatch.objects.all()
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
    
# Simulation
def simulation(request, id):
    pass
    
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
    
def tutorial(request):
    return render_template('tutorial.html', request)
    
def about(request):
    return render_template('about.html', request)
    
def sitemap(request):
	return render_template('sitemap.xml', request, data = {
        'ROOT_URL': settings.ROOT_URL,
        'organisms': models.Organism.objects.all(),
        'investigators': models.Investigator.objects.all(),
        })
    
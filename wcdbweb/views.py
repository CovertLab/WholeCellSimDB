from django.contrib.auth import login as auth_login, logout as auth_logout        
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.servers.basehttp import FileWrapper
from django.db.models import Avg, Count, Min, Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils import simplejson
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from haystack.query import SearchQuerySet
from helpers import render_template
from odict import odict
from wcdb import models
from wcdb.helpers import get_option_dict, get_parameter_dict, get_timestep
from WholeCellDB import settings
import copy
import forms
import h5py
import helpers
import math
import numpy
import os
import tempfile

###################
### landing page
###################
def index(request):
    summary = {
        'n_in_silico_organism': models.Organism.objects.count(),
        'n_simulation_batch': models.SimulationBatch.objects.count(), 
        'n_simulation': models.Simulation.objects.count(), 
        'n_process': models.Process.objects.values('name').distinct().count(),
        'n_state': models.State.objects.values('name').distinct().count(),
        'n_property': models.Property.objects
            .values('name', 'state__name')
            .distinct()
            .count(),
        'n_parameter': models.Parameter.objects
            .values('name', 'process__name', 'state__name')
            .distinct()
            .count(),
        'n_option': models.Option.objects
            .values('name', 'process__name', 'state__name')
            .distinct()
            .count(),
        'n_investigator': models.Investigator.objects.count(),        
    }
    
    default_data_series = models.PropertyValue.objects \
        .filter(property__state__simulation_batch__id=1, property__state__name='MetabolicReaction', property__name='growth', simulation__batch_index__lte=5) \
        .values('property__id', 'property__state__id', 'property__state__simulation_batch__id', 'property__state__simulation_batch__organism__id', 'simulation__id') \
        .order_by('simulation__batch_index')
    
    return render_template('index.html', request, data = {
            'summary': summary,
            'default_data_series': default_data_series,
            'x_axis': {
                'max': models.Simulation.objects.filter(batch__id=1, batch_index__lte=5).aggregate(Max('length'))['length__max'],
                },
            'y_axis': {
                'label': 'Value',
                'title': 'Value',
                'units': None,
                },
        })
        
###################
### slicing
###################
def list_investigators(request):
    investigators = helpers.get_investigator_list_with_stats(models.Investigator.objects.all().order_by('user__last_name', 'user__first_name'))

    return render_template('list_investigators.html', request, data = {
        'investigators': investigators
        })
    
def investigator(request, id):
    investigator = models.Investigator.objects.get(id=id)
    
    tmp = {}
    for batch in investigator.simulation_batches.all().annotate(n_simulation = Count('simulations')):
        if not tmp.has_key(batch.organism.id):
            tmp[batch.organism.id] = {'id': batch.organism.id, 'name': batch.organism.name, 'versions': [], 'n_simulation_batch': 0, 'n_simulation': 0}
        tmp[batch.organism.id]['versions'].append(batch.organism_version)
        tmp[batch.organism.id]['n_simulation_batch'] += 1
        tmp[batch.organism.id]['n_simulation'] += batch.n_simulation
        
    organisms = []
    for id, tmp2 in tmp.iteritems():
        organisms.append({
            'id': tmp2['id'],
            'name': tmp2['name'],
            'n_versions': len(set(tmp2['versions'])),
            'n_simulation_batch': tmp2['n_simulation_batch'],
            'n_simulation': tmp2['n_simulation']
            })
            
    organisms = sorted(organisms, key=lambda organism: organism['name'])
    
    return render_template('investigator.html', request, data = {
        'investigator': investigator,
        'organisms': organisms,
        'simulation_batches': investigator.simulation_batches.order_by('organism__name', 'organism_version', 'name')
        })
    
def list_organisms(request):
    organisms = helpers.get_organism_list_with_stats(models.Organism.objects.all().order_by('name'))
            
    return render_template('list_organisms.html', request, data = {
        'organisms': organisms
        })
    
def organism(request, id):
    organism = models.Organism.objects.get(id=id)
    investigators = models.Investigator.objects.filter(simulation_batches__organism__id=id).order_by('user__last_name', 'user__first_name').distinct()
     
    return render_template('organism.html', request, data = {
        'organism': organism,
        'simulation_batches': organism.simulation_batches.order_by('organism_version', 'name'),
        'investigators': helpers.get_investigator_list_with_stats(investigators),
        })
    
def list_simulation_batches(request):    
    batches = helpers.get_simulation_batch_list_with_stats(models.SimulationBatch.objects.all())
    batches = sorted(batches, key=lambda batch: (batch.organism.name, len(batch.name) < 9 or 'Wild-type' != batch.name[0:9], batch.name, ))
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
    simulations = models.Simulation.objects.all().select_related('simulation_batch', 'simulation_batch__organism', 'simulation_batch__investigator', 'simulation_batch__investigator__user')
    simulations = sorted(simulations, key=lambda sim: (sim.batch.organism.name, len(sim.batch.name) < 9 or 'Wild-type' != sim.batch.name[0:9], sim.batch.name, sim.batch_index))
	
    return render_template('list_simulations.html', request, data = {
        'simulations': simulations
    })
    
def simulation(request, id):
    simulation = models.Simulation.objects.get(id=id)
    batch = simulation.batch
    
    state = batch.states.filter(name__in=['MetabolicReaction', 'Reaction'])
    if state.count() > 0:
        state = state[0]
    elif batch.states.count() > 0:
        state = batch.states.all()[0]
    else:
        state = None
    
    if state is not None:
        prop = state.properties.filter(name__in=['growth', 'Growth'])
        if prop.count() > 0:
            prop = prop[0]
        elif state.properties.count() > 0:
            prop = state.properties.all()[0]
        else:
            prop = None
        
    if prop is not None:
        default_data_series = {'state': state, 'property': prop, 'row': None, 'col': None}
    else:
        default_data_series = None
           
    x_axis = {
        'max': simulation.length,
        }

    y_axis = {
        'label': 'Value',
        'title': 'Value',
        'units': None,
        }
        
    return render_template('simulation.html', request, data = {
        'simulation': simulation,
        'batch': batch,
        'default_data_series': default_data_series,
        'x_axis': x_axis,
        'y_axis': y_axis,
    })

def list_options(request):
    tmp = models.Organism.objects.all() \
        .annotate(n_batches=Count('simulation_batches__id')) \
        .order_by('name')
    organism_ids = [x.id for x in tmp]
#    organisms = {x.id: x for x in tmp}
    organisms = odict([(x.id, x) for x in tmp])
    
    options = {
        'Global': models.Option.objects
            .filter(process__isnull=True, state__isnull=True)
            .values('name', 'units', 'value', 'index', 'simulation_batch__organism__id')
            .annotate(Count('name'), Count('index'), Count('value'), n_batches=Count('simulation_batch__organism__id'))
            .order_by('name', 'simulation_batch__name', 'index'),
        'Processes': models.Option.objects
            .filter(process__isnull=False)
            .values('process__name', 'name', 'units', 'value', 'index', 'simulation_batch__organism__id')
            .annotate(Count('process__name'), Count('name'), Count('index'), Count('value'), n_batches=Count('simulation_batch__organism__id'))
            .order_by('process__name', 'name', 'simulation_batch__name', 'index'),
        'States': models.Option.objects
            .filter(state__isnull=False)
            .values('state__name', 'name', 'units', 'value', 'index', 'simulation_batch__organism__id')
            .annotate(Count('state__name'), Count('name'), Count('index'), Count('value'), n_batches=Count('simulation_batch__organism__id'))
            .order_by('state__name', 'name', 'simulation_batch__name', 'index'),
        }
    
    return render_template('list_options.html', request, data = {
        'organisms': organisms,
        'organism_ids': organism_ids,
        'options': options
    })
    
def option(request, option_name, process_name=None, state_name=None):
    options = models.Option.objects \
        .filter(name=option_name, process__name=process_name, state__name=state_name) \
        .values('name', 'index', 'process__name', 'state__name', 'simulation_batch__organism__id', 'simulation_batch__organism__name', 'simulation_batch__id', 'simulation_batch__name', 'value', 'units') \
        .order_by('simulation_batch__organism__name', 'simulation_batch__name', 'index')
    return render_template('option.html', request, data = {
        'option_name': option_name,
        'process_name': process_name,
        'state_name': state_name,
        'options': options
    })
    
def list_parameters(request):
    tmp = models.Organism.objects.all() \
        .annotate(n_batches=Count('simulation_batches__id')) \
        .order_by('name')
    organism_ids = [x.id for x in tmp]
#    organisms = {x.id: x for x in tmp}
    organisms = odict([(x.id, x) for x in tmp])
    
    parameters = {
        'Global': models.Parameter.objects
            .filter(process__isnull=True, state__isnull=True)
            .values('name', 'units', 'value', 'index', 'simulation_batch__organism__id')
            .annotate(Count('name'), Count('index'), Count('value'), n_batches=Count('simulation_batch__organism__id'))
            .order_by('name', 'simulation_batch__name', 'index'),
        'Processes': models.Parameter.objects
            .filter(process__isnull=False)
            .values('process__name', 'name', 'units', 'value', 'index', 'simulation_batch__organism__id')
            .annotate(Count('process__name'), Count('name'), Count('index'), Count('value'), n_batches=Count('simulation_batch__organism__id'))
            .order_by('process__name', 'name', 'simulation_batch__name', 'index'),
        'States': models.Parameter.objects
            .filter(state__isnull=False)
            .values('state__name', 'name', 'units', 'value', 'index', 'simulation_batch__organism__id')
            .annotate(Count('state__name'), Count('name'), Count('index'), Count('value'), n_batches=Count('simulation_batch__organism__id'))
            .order_by('state__name', 'name', 'simulation_batch__name', 'index'),
        }
    
    return render_template('list_parameters.html', request, data = {
        'organisms': organisms,
        'organism_ids': organism_ids,
        'parameters': parameters
    })
    
def parameter(request, parameter_name, process_name=None, state_name=None):
    parameters = models.Parameter.objects \
        .filter(name=parameter_name, process__name=process_name, state__name=state_name) \
        .values('name', 'index', 'process__name', 'state__name', 'simulation_batch__organism__id', 'simulation_batch__organism__name', 'simulation_batch__id', 'simulation_batch__name', 'value', 'units') \
        .order_by('simulation_batch__organism__name', 'simulation_batch__name', 'index')
    return render_template('parameter.html', request, data = {
        'parameter_name': parameter_name,
        'process_name': process_name,
        'state_name': state_name,
        'parameters': parameters
    })
    
def list_processes(request):
    tmp = models.Organism.objects.all() \
        .annotate(n_batches=Count('simulation_batches__id')) \
        .order_by('name')    
    organism_ids = [x.id for x in tmp]
#    organisms = {x.id: x for x in tmp}
    organisms = odict([(x.id, x) for x in tmp])
    
    processes =  models.Process.objects \
        .values('name', 'simulation_batch__organism__id') \
        .annotate(Count('name'), n_batches=Count('simulation_batch__organism__id')) \
        .order_by('name')
    
    return render_template('list_processes.html', request, data = {
        'organisms': organisms,
        'organism_ids': organism_ids,
        'processes': processes,
    })
    
def process(request, process_name):
    tmp = models.Organism.objects.all() \
        .annotate(n_batches=Count('simulation_batches__id')) \
        .order_by('name')    
    organism_ids = [x.id for x in tmp]
#    organisms = {x.id: x for x in tmp}
    organisms = odict([(x.id, x) for x in tmp])
    
    options = models.Option.objects \
        .filter(process__name=process_name) \
        .values('name', 'units', 'value', 'index', 'simulation_batch__organism__id') \
        .annotate(Count('name'), Count('value'), Count('index'), n_batches=Count('simulation_batch__organism__id')) \
        .order_by('name', 'index')
    parameters = models.Parameter.objects \
        .filter(process__name=process_name) \
        .values('name', 'units', 'value', 'index', 'simulation_batch__organism__id') \
        .annotate(Count('name'), Count('value'), Count('index'), n_batches=Count('simulation_batch__organism__id')) \
        .order_by('name', 'index')
        
    return render_template('process.html', request, data = {
        'process_name': process_name,
        'organisms': organisms,
        'organism_ids': organism_ids,
        'options': options, 
        'parameters': parameters
    })
    
def list_states(request):
    tmp = models.Organism.objects.all() \
        .annotate(n_batches=Count('simulation_batches__id')) \
        .order_by('name')
    organism_ids = [x.id for x in tmp]
#    organisms = {x.id: x for x in tmp}
    organisms = odict([(x.id, x) for x in tmp])
        
    state_properties = models.Property.objects \
        .values('id', 'name', 'state__name', 'state__simulation_batch__organism__id') \
        .annotate(Count('name'), Count('state__name'), n_batches=Count('state__simulation_batch__organism__id')) \
        .order_by('state__name', 'name')
		
    return render_template('list_states.html', request, data = {
        'organisms': organisms,
        'organism_ids': organism_ids,
        'state_properties': state_properties,
    })
    
def state(request, state_name):
    tmp = models.Organism.objects.all() \
        .annotate(n_batches=Count('simulation_batches__id')) \
        .order_by('name')    
    organism_ids = [x.id for x in tmp]
#    organisms = {x.id: x for x in tmp}
    organisms = odict([(x.id, x) for x in tmp])
    
    options = models.Option.objects \
        .filter(state__name=state_name) \
        .values('name', 'units', 'value', 'index', 'simulation_batch__organism__id') \
        .annotate(Count('name'), Count('value'), Count('index'), n_batches=Count('simulation_batch__organism__id')) \
        .order_by('name', 'index')
    parameters = models.Parameter.objects \
        .filter(state__name=state_name) \
        .values('name', 'units', 'value', 'index', 'simulation_batch__organism__id') \
        .annotate(Count('name'), Count('value'), Count('index'), n_batches=Count('simulation_batch__organism__id')) \
        .order_by('name', 'index')
    properties = models.Property.objects \
        .filter(state__name=state_name) \
        .values('name', 'units', 'state__simulation_batch__organism__id', 'labels__dimension') \
        .annotate(Count('name'), n_batches=Count('state__simulation_batch__organism__id')) \
        .order_by('name')
        
    return render_template('state.html', request, data = {
        'state_name': state_name,
        'organisms': organisms,
        'organism_ids': organism_ids,
        'options': options, 
        'parameters': parameters,
        'properties': properties,
		
    })
    
def state_property(request, state_name, property_name):
    tmp = models.Organism.objects.all() \
        .annotate(n_batches=Count('simulation_batches__id')) \
        .order_by('name')    
    organism_ids = [x.id for x in tmp]
#    organisms = {x.id: x for x in tmp}
    organisms = odict([(x.id, x) for x in tmp])
    
    labels = models.PropertyLabel.objects \
        .filter(property__name=property_name, property__state__name=state_name)
    dimension_values = set([x['dimension'] for x in labels.values('dimension')])
    
    is_labeled = labels.exclude(name='').count() > 0
    show_slice_links = 0 in dimension_values and 1 in dimension_values
    
    label_values = labels \
        .values('dimension', 'name', 'property__state__simulation_batch__organism__id') \
        .annotate(Count('dimension'), Count('name'), n_batches=Count('property__state__simulation_batch__organism__id')) \
        .order_by('dimension', 'name')
        
    return render_template('state_property.html', request, data = {
        'state_name': state_name,
        'property_name': property_name,
        'organisms': organisms,
        'organism_ids': organism_ids,
        'is_labeled': is_labeled,
        'show_slice_links': show_slice_links,
        'labels': label_values,
    })

def state_property_row(request, state_name, property_name, row_name):
    cols = models.PropertyLabel.objects \
        .filter(dimension=1, property__name=property_name, property__state__name=state_name, property__labels__name=row_name, property__labels__dimension=0) \
        .values('name') \
        .distinct() \
        .order_by('name')
    col_names = [col['name'] for col in cols]
        
    cols_batches_organisms = models.PropertyLabel.objects \
        .filter(dimension=1, property__name=property_name, property__state__name=state_name, property__labels__name=row_name, property__labels__dimension=0) \
        .values('name', 'property__state__simulation_batch__organism__id', 'property__state__simulation_batch__organism__name', 'property__state__simulation_batch__id', 'property__state__simulation_batch__name') \
        .order_by('property__state__simulation_batch__organism__name', 'property__state__simulation_batch__name', 'name')
        
    tmp = models.PropertyValue.objects \
        .filter(property__name=property_name, property__state__name=state_name, dtype__isnull=False) \
        .values('simulation__batch__id', 'simulation__batch__name') \
        .distinct()
    property_value_batches = [x['simulation__batch__id'] for x in tmp]
    
    return render_template('state_property_row.html', request, data = {
        'state_name': state_name, 
        'property_name': property_name, 
        'row_name': row_name,
        'col_names': col_names,
        'cols_batches_organisms': cols_batches_organisms,
        'property_value_batches': property_value_batches,
    })

def state_property_row_col_batch(request, state_name, property_name, batch_id, row_name = '', col_name = ''):
    if row_name is None:
        row_name = ''
    if col_name is None:
        col_name = ''

    batch = models.SimulationBatch.objects.get(id=batch_id)
    state = batch.states.get(name=state_name)
    property = state.properties.get(name=property_name)
    
    x_axis = {
        'max': batch.simulations.aggregate(Max('length'))['length__max'],
        }

    if property.units:
        y_axis = {
            'label': property_name,
            'title': '%s (%s)'  % (property_name, property.units),
            'units': property.units,
            }
    else:
        y_axis = {
            'label': property_name,
            'title': property_name,
            'units': None,
            }
    
    return render_template('state_property_row_col_batch.html', request, data = {
        'state_name': state_name, 
        'property_name': property_name, 
        'row_name': row_name,
        'col_name': col_name,
        'batch': batch, 
        'x_axis': x_axis,
        'y_axis': y_axis
    })
    
########################
### list/get data series
########################
def list_data_series(request):
    organism_id = request.GET.get('organism', '')
    if organism_id == '':
        data = []
        for organism in models.Organism.objects.all():
            data.append({
                'id':'%d' % organism.id, 
                'parentid': '0', 
                'organism': organism.id,
                'isleaf': False,
                'label': organism.name, 
                'units': '',
                })
        return helpers.render_json_response(data)
    organism = models.Organism.objects.get(id=int(float(organism_id)))
        
    simulation_batch_id = request.GET.get('simulation_batch', '')
    if simulation_batch_id == '':
        data = []
        for simulation_batch in organism.simulation_batches.all():
            data.append({
                'id':'%d.%d' % (organism.id, simulation_batch.id), 
                'parentid': '%d' % organism.id, 
                'organism': organism.id,
                'simulation_batch': simulation_batch.id,
                'isleaf': False,
                'label': simulation_batch.name, 
                'units': '', 
                })
        return helpers.render_json_response(data)
    simulation_batch = models.SimulationBatch.objects.get(id=int(float(simulation_batch_id)))
        
    simulation_id = request.GET.get('simulation', '')
    if simulation_id == '':
        data = []
        for simulation in simulation_batch.simulations.all():
            data.append({
                'id':'%d.%d.%d' % (organism.id, simulation_batch.id, simulation.id), 
                'parentid': '%d.%d' % (organism.id, simulation_batch.id), 
                'organism': organism.id,
                'simulation_batch': simulation_batch.id,
                'simulation': simulation.id,
                'isleaf': False,
                'label': simulation.batch_index, 
                'units': ''
                })
        return helpers.render_json_response(data)
    simulation = models.Simulation.objects.get(id=int(float(simulation_id)))
        
    state_id = request.GET.get('state', '')
    if state_id == '':
        data = []
        for state in simulation_batch.states.all():
            data.append({
                'id':'%d.%d.%d.%d' % (organism.id, simulation_batch.id, simulation.id, state.id), 
                'parentid': '%d.%d.%d' % (organism.id, simulation_batch.id, simulation.id), 
                'organism': organism.id,
                'simulation_batch': simulation_batch.id,
                'simulation': simulation.id,
                'state': state.id,
                'isleaf': False,
                'label': state.name, 
                'units': ''
                })
        return helpers.render_json_response(data)
    state = models.State.objects.get(id=int(float(state_id)))
        
    property_id = request.GET.get('property', '')
    if property_id == '':
        data = []
        for property in state.properties.all():
            data.append({
                'id':'%d.%d.%d.%d.%d' % (organism.id, simulation_batch.id, simulation.id, state.id, property.id), 
                'parentid': '%d.%d.%d.%d' % (organism.id, simulation_batch.id, simulation.id, state.id), 
                'organism': organism.id,
                'simulation_batch': simulation_batch.id,
                'simulation': simulation.id,
                'state': state.id,
                'property': property.id,
                'isleaf': property.labels.filter(name__isnull=False).exclude(name='').count() == 0,
                'label': property.name, 
                'units': property.units if property.units is not None else '',
                'data_valid': \
                    property.values.get(simulation__id=simulation.id).dtype is not None and \
                    property.labels.filter(dimension=0, name__isnull=False).count() > 0 and \
                    property.labels.filter(dimension=1, name__isnull=False).count() > 0,
                })
        return helpers.render_json_response(data)
    property = models.Property.objects.select_related('labels').get(id=int(float(property_id)))
    
    data_valid = \
        property.values.get(simulation__id=simulation.id).dtype is not None and \
        property.labels.filter(dimension=0, name__isnull=False).count() > 0 and \
        property.labels.filter(dimension=1, name__isnull=False).count() > 0
        
    row_id = request.GET.get('row', '')
    col_id = request.GET.get('col', '')
    if row_id == '' and col_id == '':
        if property.labels.filter(dimension=0).exclude(name='').count() > 0:
            
            data = []
            isleaf = property.labels.filter(dimension=1, name__isnull=False).exclude(name='').count() == 0
            for row in property.labels.filter(dimension=0).exclude(name='').all():
                data.append({
                    'id':'%d.%d.%d.%d.%d.%d' % (organism.id, simulation_batch.id, simulation.id, state.id, property.id, row.id), 
                    'parentid': '%d.%d.%d.%d.%d' % (organism.id, simulation_batch.id, simulation.id, state.id, property.id), 
                    'organism': organism.id,
                    'simulation_batch': simulation_batch.id,
                    'simulation': simulation.id,
                    'state': state.id,
                    'property': property.id,
                    'row': row.id,
                    'isleaf': isleaf,
                    'label': row.name, 
                    'units': property.units if property.units is not None else '',
                    'data_valid': data_valid,
                    })
            return helpers.render_json_response(data) 

    if row_id == '':
        rows = property.labels.filter(dimension=0)
        if rows.count() > 0:
            row_id = '%d' % rows[0].id
    
    if col_id == '':
        data = []
        for col in property.labels.filter(dimension=1).exclude(name='').all():
            data.append({
                'id':'%d.%d.%d.%d.%d.%s.%d' % (organism.id, simulation_batch.id, simulation.id, state.id, property.id, row_id, col.id), 
                'parentid': '%d.%d.%d.%d.%d.%s' % (organism.id, simulation_batch.id, simulation.id, state.id, property.id, row_id), 
                'organism': organism.id,
                'simulation_batch': simulation_batch.id,
                'simulation': simulation.id,
                'state': state.id,
                'property': property.id,
                'row': row_id,
                'isleaf': True,
                'label': col.name, 
                'units': property.units if property.units is not None else '',
                'data_valid': data_valid,
                })
        return helpers.render_json_response(data)
        
    col = models.PropertyLabel.objects.get(id=int(float(col_id)))
    raise Exception('Cannot dig deeper into hierarchy')
    
def get_data_series(request):
    format = request.GET.get('format') or request.POST.get('format') or 'hdf5'
    if format not in ['hdf5', 'json', 'bson', 'msgpack', 'numl']:
        raise Exception('Invalid format')
    
    data_series_requests = simplejson.loads(request.GET.get('data_series') or request.POST.get('data_series'))
    if len(data_series_requests) > 100:
        raise Exception('Queries are limited to 100 data series')
        
    if format == 'hdf5':
        data_series = helpers.create_temp_hdf5_file()        
        data_series_filename = data_series.filename
    else:
        data_series = []
            
    for data_series_request in data_series_requests:
        property_value = models.PropertyValue.objects.get(simulation__id=data_series_request['simulation'], property__id=data_series_request['property'])
        if property_value.shape is None:
            continue
        
        property = property_value.property
        state = property.state
        batch = state.simulation_batch
        organism = batch.organism
        simulation = property_value.simulation
        
        if 'row' in data_series_request and data_series_request['row']:
            row = models.PropertyLabel.objects.get(id=data_series_request['row'])
        else:
            row = None
            
        if 'col' in data_series_request and data_series_request['col']:
            col = models.PropertyLabel.objects.get(id=data_series_request['col'])
        else:
            col = None
            
        data = property_value.get_dataset_slice(row, col)
        
        downsample_step = get_timestep(simulation)
        
        if format == 'hdf5':
            dset = data_series.create_dataset('%s/%s/%d/%s/%s%s%s/data' % (organism.name, batch.name, simulation.batch_index, state.name, property.name, '/%s' % row.name if row is not None else '', '/%s' % col.name if col is not None else ''),
                data = data,
                compression = "gzip",
                compression_opts = 4,
                chunks = True)
            dset.attrs['simulation_length'] = simulation.length
            dset.attrs['data_units'] = property.units
            dset.attrs['time_units'] = 's'
            dset.attrs['downsample_step'] = downsample_step
            
            data_series.flush()
        else:
            attrs = {
                'organism': organism.name,
                'simulation_batch': batch.name,
                'simulation_batch_index': simulation.batch_index,
                'simulation_length': simulation.length,
                'state': state.name,
                'property': property.name,
                'data_units': property.units,
                'time_units': 's',
                'downsample_step': downsample_step,
                }
            
            if row is not None:
                attrs['row'] = row.name
            if col is not None:
                attrs['col'] = col.name
            
            data_series.append({
                'data': numpy.transpose(data, (2, 0, 1)).squeeze().tolist(),
                'attrs': attrs
                })
   
    if format == 'hdf5':
        data_series.close()
        return helpers.render_tempfile_response(data_series_filename, 'WholeCellDB', 'h5', 'application/x-hdf')
    elif format == 'json':
        return helpers.render_json_response(data_series)
    elif format == 'bson':
        return helpers.render_bson_response(data_series)
    elif format == 'msgpack':
        return helpers.render_msgpack_response(data_series)
    elif format == 'numl':
        return helpers.render_numl_response(data_series)
   
###################
### downloading
###################
@csrf_protect
def download(request):
    form = forms.DownloadForm(request.POST)
    if not form.is_valid():        
        response = render_template(
            request = request,
            templateFile = 'download.html', 
            data = {
                'form': form,
                'batches': models.SimulationBatch.objects.annotate(n_simulations=Count('simulations')).values('organism__id', 'organism__name', 'name', 'id', 'n_simulations').order_by('organism__name', 'name')
                }
            )
    else:
        batch_ids = form.cleaned_data['simulation_batches']    
        batches = models.SimulationBatch.objects.filter(id__in=form.cleaned_data['simulation_batches'])
        response = helpers.download_batches(batches, 'WholeCellDB')
        
    response['X-Robots-Tag'] = 'noindex'
    return response

@login_required
def organism_download(request, id):
    organism = models.Organism.objects.get(id=id)    
    response = helpers.download_batches(organism.simulation_batches.all(), organism.name)
    response['X-Robots-Tag'] = 'noindex'
    return response
    
def simulation_batch_download(request, id):
    batch = models.SimulationBatch.objects.get(id=id)    
    response = helpers.download_batches([batch], batch.name)
    response['X-Robots-Tag'] = 'noindex'
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
    response['X-Robots-Tag'] = 'noindex'
    file.seek(0)
    return response

@login_required
def state_download(request, state_name):
    tmp_file = helpers.create_temp_hdf5_file()
    tmp_filename = tmp_file.filename
    
    batches = models.SimulationBatch.objects.filter(states__name=state_name)
    for batch in batches:
        state = batch.states.get(name=state_name)
        for prop in state.properties.all():
            for pv in prop.values.all():
                if pv.shape is None:
                    continue
                    
                dset = tmp_file.create_dataset('%s/%s/%d/%s/%s/data' % (batch.organism.name, batch.name, pv.simulation.batch_index, state.name, prop.name),
                    data = pv.dataset.data,
                    compression = "gzip",
                    compression_opts = 4,
                    chunks = True)
            
                dset.attrs['simulation_length'] = pv.simulation.length
                dset.attrs['data_units'] = prop.units
                dset.attrs['time_units'] = 's'
                dset.attrs['downsample_step'] = get_timestep(pv.simulation)
                
                tmp_file.flush()
    
    tmp_file.close()
    
    response = helpers.render_tempfile_response(tmp_filename, state_name, 'h5', 'application/x-hdf')
    response['X-Robots-Tag'] = 'noindex'
    return response

@login_required
def state_property_download(request, state_name, property_name):
    tmp_file = helpers.create_temp_hdf5_file()
    tmp_filename = tmp_file.filename
    
    batches = models.SimulationBatch.objects.filter(states__name=state_name, states__properties__name=property_name)
    for batch in batches:
        prop = models.Property.objects.filter(state__name=state_name, name=property_name, state__simulation_batch__id=batch.id)[0]
        for pv in prop.values.all():
            if pv.shape is None:
                continue
                
            dset = tmp_file.create_dataset('%s/%s/%d/%s/%s/data' % (batch.organism.name, batch.name, pv.simulation.batch_index, state_name, prop.name),
                data = pv.dataset.data,
                compression = "gzip",
                compression_opts = 4,
                chunks = True)
        
            dset.attrs['simulation_length'] = pv.simulation.length
            dset.attrs['data_units'] = prop.units
            dset.attrs['time_units'] = 's'
            dset.attrs['downsample_step'] = get_timestep(pv.simulation)
            
            tmp_file.flush()
    
    tmp_file.close()
    
    response = helpers.render_tempfile_response(tmp_filename, '%s-%s' % (state_name, property_name), 'h5', 'application/x-hdf')
    response['X-Robots-Tag'] = 'noindex'
    return response

@login_required
def state_property_row_download(request, state_name, property_name, row_name):
    tmp_file = helpers.create_temp_hdf5_file()
    tmp_filename = tmp_file.filename
    
    batches = models.SimulationBatch.objects.filter(states__name=state_name, states__properties__name=property_name)
    for batch in batches:
        prop = models.Property.objects.filter(state__name=state_name, name=property_name, state__simulation_batch__id=batch.id)[0]
        row = prop.labels.filter(name=row_name)[0]
        for pv in prop.values.all():
            if pv.shape is None:
                continue
                    
            shape = list(pv.shape)
            shape[0] = 1
            
            dset = tmp_file.create_dataset('%s/%s/%d/%s/%s%s/data' % (batch.organism.name, batch.name, pv.simulation.batch_index, state_name, property_name, '/%s' % row_name if row_name else ''),
                data = pv.dataset[row.index, ...],
                shape = shape,
                compression = "gzip",
                compression_opts = 4,
                chunks = True)
        
            dset.attrs['simulation_length'] = pv.simulation.length
            dset.attrs['data_units'] = prop.units
            dset.attrs['time_units'] = 's'
            dset.attrs['downsample_step'] = get_timestep(pv.simulation)
            
            tmp_file.flush()
    
    tmp_file.close()
    
    response = helpers.render_tempfile_response(tmp_filename, '%s-%s-%s' % (state_name, property_name, row_name), 'h5', 'application/x-hdf')
    response['X-Robots-Tag'] = 'noindex'
    return response
    
def state_property_row_col_batch_download(request, state_name, property_name, row_name, col_name, batch_id):
    if row_name is None:
        row_name = ''
    if col_name is None:
        col_name = ''
        
    format = request.GET.get('format', 'hdf5')
           
    batch = models.SimulationBatch.objects.get(id=batch_id)
    prop = models.Property.objects.get(name=property_name, state__name=state_name, state__simulation_batch__id=batch_id)
    row = models.PropertyLabel.objects.filter(dimension=0, name=row_name, property__name=property_name, property__state__name=state_name, property__state__simulation_batch__id=batch_id)[0]
    col = models.PropertyLabel.objects.filter(dimension=1, name=col_name, property__name=property_name, property__state__name=state_name, property__state__simulation_batch__id=batch_id)[0]
    
    if format == 'hdf5':
        tmp_file = helpers.create_temp_hdf5_file()
        tmp_filename = tmp_file.filename
        
        for pv in prop.values.all():
            if pv.shape is None:
                continue
         
            sim = pv.simulation
            pathname = '%s/%s/%d/%s/%s%s%s/data' % (batch.organism.name, batch.name, sim.batch_index, state_name, property_name, '/%s' % row_name if row_name else '', '/%s' % col_name if col_name else '', )
            dset = tmp_file.create_dataset(pathname, 
                data = pv.get_dataset_slice(row, col),
                compression = "gzip",
                compression_opts = 4,
                chunks = True)
                
            dset.attrs['simulation_length'] = sim.length
            dset.attrs['data_units'] = prop.units
            dset.attrs['time_units'] = 's'
            dset.attrs['downsample_step'] = get_timestep(sim)
            
            tmp_file.flush()
            
        tmp_file.close()
        
        filename = '%s-%s-%s-%s%s%s' % (batch.organism.name, batch.name, state_name, property_name, '-%s' % row_name if row_name else '', '-%s' % col_name if col_name else '')
        response = helpers.render_tempfile_response(tmp_filename, filename, 'h5', 'application/x-hdf')
        response['X-Robots-Tag'] = 'noindex'
        return response
    elif format in ['json', 'bson', 'msgpack', 'numl']:        
        max_datapoints = 5e5
        n_datapoints = batch.simulations.count() * batch.simulations.aggregate(Max('length'))['length__max']        
        if n_datapoints <= max_datapoints:
            downsample_step = 1
        else:
            tmp = n_datapoints / max_datapoints
            downsample_step_10 = math.pow(10, math.ceil(math.log10(tmp)))
            downsample_step_5 = 5 * math.pow(10, math.ceil(math.log10(tmp/5)))
            downsample_step_2 = 2 * math.pow(10, math.ceil(math.log10(tmp/2)))
        
            if math.fabs(downsample_step_10 - tmp) < math.fabs(downsample_step_5 - tmp) and math.fabs(downsample_step_10 - tmp) < math.fabs(downsample_step_2 - tmp):
                downsample_step = downsample_step_10
            elif math.fabs(downsample_step_5 - tmp) < math.fabs(downsample_step_2 - tmp):
                downsample_step = downsample_step_5
            else:
                downsample_step = downsample_step_2
            
            downsample_step = int(downsample_step)
            
        data = []
        for pv in prop.values.all():
            if pv.shape is None:
                continue
                
            sim = pv.simulation

            tmp = numpy.transpose(pv.get_dataset_slice(row, col)[:,:,::downsample_step], (2, 0, 1)).squeeze()
            data.append({
                'data': tmp.tolist(),
                'attrs': {
                    'organism': batch.organism.name,
                    'simulation_batch': batch.name,
                    'simulation_batch_index': sim.batch_index,
                    'state': state_name,
                    'property': property_name,
                    'row': row_name,
                    'col': col_name,                    
                    'simulation_length': sim.length,
                    'data_units': prop.units,
                    'time_units': 's',
                    'downsample_step': get_timestep(batch.simulations.all()[0]) * float(downsample_step)
                    },
                })        
        if format == 'json':
            response = helpers.render_json_response(data)
        elif format == 'bson':
            response = helpers.render_bson_response(data)
        elif format == 'msgpack':
            response = helpers.render_msgpack_response(data)
        elif format == 'numl':
            response = helpers.render_numl_response(data)
        response['X-Robots-Tag'] = 'noindex'
        return response
    else:
        raise ValidationError('Invalid format: %s' % format)

@login_required        
def investigator_download(request, id):
    investigator = models.Investigator.objects.get(id=id)    
    response = helpers.download_batches(investigator.simulation_batches.all(), investigator.user.get_full_name())
    response['X-Robots-Tag'] = 'noindex'
    return response
    
### SED-ML    
def simulation_batch_sedml(request, id):
    batch = models.SimulationBatch.objects.get(id=id)
    
    timestep = get_timestep(batch.simulations.all()[0])
    length = batch.simulations.all().values().annotate(max_length=Max('length'))[0]['max_length']
    
    response = render_to_response('sedml.xml',
        {
            'batch': batch,
            'output_end_time': length,
            'number_of_points': length / timestep + 1, 
            'batch__options__seeds': batch.options.filter(name='seed'),
            'simulation': None,
            'model': {
                'language': 'urn:sedml:language:matlab',
                'source': 'http://covertlab.stanford.edu/svn/WholeCell/simulation/?p=%s' % batch.organism_version
                },
        }, context_instance = RequestContext(request), mimetype = 'application/xml')
    response['Content-Disposition'] = ("attachment; filename=simulation_batch-%d.sed-ml.xml" % batch.id)
    response['X-Robots-Tag'] = 'noindex'
    return response
   
def simulation_sedml(request, id):
    simulation = models.Simulation.objects.get(id=id)
    batch = simulation.batch
    
    length = simulation.length
    timestep = get_timestep(simulation)
    
    response = render_to_response('sedml.xml',
        {
            'batch': batch,
            'output_end_time': length,
            'number_of_points': length / timestep + 1,
            'batch__options__seeds': batch.options.filter(name='seed'),
            'simulation': simulation,
            'model': {
                'language': 'urn:sedml:language:matlab',
                'source': 'http://covertlab.stanford.edu/svn/WholeCell/simulation/?p=%s' % batch.organism_version
                },
        }, context_instance = RequestContext(request), mimetype = 'application/xml')
    response['Content-Disposition'] = ("attachment; filename=simulation-%d.sed-ml.xml" % simulation.id)
    response['X-Robots-Tag'] = 'noindex'
    return response
    
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

@csrf_protect
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
#    tmp = {('option-%d-operator' % i): 'eq' for i in range(n_option_filters)}
    tmp = dict([(('option-%d-operator' % i), 'eq') for i in range(n_option_filters)])
    tmp = dict(tmp.items() + request.POST.items())    
    option_forms = []
    option_form = forms.AdvancedSearchOptionForm(tmp)
    for i in range(n_option_filters):
        option_form_i = copy.deepcopy(option_form)
        option_form_i.prefix = 'option-%d' % i
        option_form_i._errors = None
        option_form_i._changed_data = None
        option_forms.append(option_form_i)
        valid = option_form_i.is_valid() and valid
    
    #parameters
#    tmp = {('parameter-%d-operator' % i): 'eq' for i in range(n_parameter_filters)}
    tmp = dict([(('parameter-%d-operator' % i), 'eq') for i in range(n_parameter_filters)])
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
#    tmp = {('process-%d-modeled' % i): '1' for i in range(n_process_filters)}
    tmp = dict([(('process-%d-modeled' % i), '1') for i in range(n_process_filters)])
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
#    tmp = {('state-%d-modeled' % i): '1' for i in range(n_state_filters)}
    tmp = dict([(('state-%d-modeled' % i), '1') for i in range(n_state_filters)])
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
        
        #take unique
        batches = batches.distinct().order_by('organism__name', 'organism_version', 'name')
        
        #exit if data requested in hdf5 format
        if form.cleaned_data['result_format'] == 'hdf5':
            return helpers.download_batches(batches, 'WholeCellDB-advanced-search')
            
        #get related organisms and investigators
        organisms = models.Organism.objects.filter(simulation_batches__id__in=batches.values_list('id')).distinct().order_by('name')        
        investigators = models.Investigator.objects.filter(simulation_batches__id__in=batches.values_list('id')).distinct().order_by('user__last_name', 'user__first_name')
    
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
    
def robots(request):
    return render_template('robots.txt', request, data = {
        'ROOT_URL': settings.ROOT_URL,
        'ROOT_DOMAIN': settings.ROOT_URL.replace('http://', ''),
        'organisms': models.Organism.objects.values('id'),
        'simulation_batches': models.SimulationBatch.objects.values('id'),
        'simulations': models.Simulation.objects.values('id'),
        'states': models.State.objects.values('name').distinct(),
        'state_properties': models.Property.objects.values('name', 'state__name').distinct(),
        'investigators': models.Investigator.objects.values('id'),
        }, mimetype = 'text/plain')

def sitemap(request):
    return render_template('sitemap.xml', request, data = {
        'ROOT_URL': settings.ROOT_URL,
        'simulation_batches': models.SimulationBatch.objects.all(),
        })
        
def sitemap_top_level(request):
    return render_template('sitemap_top_level.xml', request, data = {
        'ROOT_URL': settings.ROOT_URL,
        'organisms': models.Organism.objects.all(),
        'simulation_batches': models.SimulationBatch.objects,
        'simulations': models.Simulation.objects,
        'investigators': models.Investigator.objects.all(),
        'options': models.Option.objects
            .values('name', 'state__name', 'process__name')
            .annotate(Count('name'), Count('state__name'), Count('process__name'), date=Max('simulation_batch__date'))
            .order_by('process__name', 'state__name', 'name'),
        'parameters': models.Parameter.objects
            .values('name', 'state__name', 'process__name')
            .annotate(Count('name'), Count('state__name'), Count('process__name'), date=Max('simulation_batch__date'))
            .order_by('process__name', 'state__name', 'name'),
        'processes': models.Process.objects
            .values('name')
            .annotate(Count('name'), date=Max('simulation_batch__date'))
            .order_by('name'),
        'states': models.State.objects
            .values('name')
            .annotate(Count('name'), date=Max('simulation_batch__date'))
            .order_by('name'),
        'state_properties': models.Property.objects
            .values('name', 'state__name')
            .annotate(Count('name'), Count('state__name'), date=Max('state__simulation_batch__date'))
            .order_by('state__name', 'name')
        })
        
def sitemap_simulation_batch(request):
    id = request.GET.get('id', None)
    return render_template('sitemap_simulation_batch.xml', request, data = {
        'ROOT_URL': settings.ROOT_URL,
        'batch': models.SimulationBatch.objects.get(id=id),
        })
        
@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request):
    next = request.REQUEST.get('next', '')
    
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            if next:
                return HttpResponseRedirect(next)
            else:
                return render_template('login_success.html', request)
    else:
        form = AuthenticationForm(request)

    request.session.set_test_cookie()

    return render_template('login.html', request, data = {
        'form': form,
        'next': next,
        })
        
def login_sucess(request):
    return render_template('login_sucess.html', request)
    
def logout(request):
    auth_logout(request)
    return render_template('logout.html', request)
        
###################
### documentation
###################
def tutorial(request):
    return render_template('tutorial.html', request)
    
def advanced_analysis_gallery(request):
	return render_template('advanced_analysis_gallery.html', request)
	
def help(request):
    return render_template('help.html', request, data = {
        'growth_property': models.Property.objects.get(name='growth', state__name='MetabolicReaction', state__simulation_batch__id=1),
    })
    
def about(request):
    return render_template('about.html', request)
    

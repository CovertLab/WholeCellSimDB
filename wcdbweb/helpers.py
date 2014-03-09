from django.core.servers.basehttp import FileWrapper
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from haystack.models import SearchResult
from WholeCellDB import settings
import datetime
import os
import tempfile
import zipfile

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

def get_simulation_batch_list_with_stats(qs):
    batches = []
    for batch in qs:
        if isinstance(batch, SearchResult):
            batch = batch.object
        batches.append({
            'id': batch.id,
            'name': batch.name,
            'date': batch.date,
            'investigator': batch.investigator,
            'organism': batch.organism,
            'simulations': batch.simulations,
            'length_avg': batch.simulations.all().aggregate(Avg('length'))['length__avg']
            })
    return batches
    
def get_investigator_list_with_stats(qs):
    investigators = []
    for investigator in qs:
        if isinstance(investigator, SearchResult):
            investigator = investigator.object
        batches = investigator.simulation_batches.all()
                
        investigators.append({
            'id': investigator.id,
            'full_name': investigator.user.get_full_name,
            'affiliation': investigator.affiliation,
            'n_organism': batches.values('organism').annotate(Count('organism')).count(),
            'n_simulation_batches': batches.count(),
            'n_simulation': sum([batch.simulations.count() for batch in batches]),
            })
            
    return investigators
    
def download_batches(batches, filename):
    if not os.path.isdir(settings.ROOT_DIR):
        os.mkdir(settings.TMP_DIR)
    
    file = tempfile.TemporaryFile(dir=settings.TMP_DIR)
    zip = zipfile.ZipFile(file, 'w')
    for batch in batches:
        for simulation in batch.simulations.all():
            zip.write(simulation.file_path, '%s/%s/%d.h5' % (slugify(batch.organism.name), slugify(batch.name), simulation.batch_index))
    zip.close()
    fileWrapper = FileWrapper(file)
    response = HttpResponse(
        fileWrapper,
        mimetype = "application/x-zip",
        content_type = "application/x-zip"
        )
    response['Content-Disposition'] = "attachment; filename=%s.zip" % slugify(filename)
    response['Content-Length'] = file.tell()
    file.seek(0)
    return response
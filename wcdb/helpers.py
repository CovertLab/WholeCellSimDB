from collections import OrderedDict
from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext
from haystack.models import SearchResult
from WholeCellDB import settings

import datetime
import os
import glob
import scipy.io

def render_template(templateFile, request, data={}):
    data['last_updated_date'] = datetime.datetime.fromtimestamp(
            os.path.getmtime(settings.TEMPLATE_DIRS[0] + '/' + templateFile))

    return render_to_response(templateFile, data, 
                              context_instance = RequestContext(request))


def get_organism_list_with_stats(qs):
    organisms = []
    for organism in qs:
        if isinstance(organism, SearchResult):
            organism = organism.object
        organisms.append({
            'id': organism.id,
            'name': organism.name,
            'n_version': organism.versions.all().count(),
            'n_simulation_batch': 0,
            'n_simulation': 0
        })
    return organisms


def truncate_fields(obj):
    for key, val in obj.iteritems():
        if isinstance(val, dict):
            obj[key] = truncate_fields(val)
        elif isinstance(val, (list, tuple, )):
            idx = 0
            for subval in val:
                obj[key][idx] = truncate_fields(subval)
                idx += 1
        elif isinstance(val, (str, unicode)) and key not in ['content', 'text']:
            obj[key] = val[:225]
    return obj

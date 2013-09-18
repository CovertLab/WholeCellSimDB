from django.shortcuts import render_to_response
from django.template import RequestContext
from WholeCellDB import settings
import datetime
import os

def render_template(templateFile, request, data = {}):
    #add data
    data['last_updated_date'] = datetime.datetime.fromtimestamp(os.path.getmtime(settings.TEMPLATE_DIRS[0] + '/' + templateFile))

    #render
    return render_to_response(templateFile, data, context_instance = RequestContext(request))

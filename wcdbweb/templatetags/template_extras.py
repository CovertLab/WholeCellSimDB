from collections import OrderedDict
from dateutil.tz import tzlocal
from django import template
from WholeCellDB import settings
import datetime
import math
import os

register = template.Library()

@register.filter
def columns(arr, n_cols):    
    n_cols = int(float(n_cols))
    
    col_arr = []
    idx = 0
    for i in range(n_cols):
        idx2 = int(math.ceil((i + 1.) * (len(arr) + 0.) / (n_cols + 0.)))
        col_arr.append(arr[idx:idx2])
        idx = idx2
        
    return col_arr

@register.filter
def order_by(qs, field):
    return qs.order_by(field)
    
@register.filter
def is_dict(obj):
    return isinstance(obj, (dict, OrderedDict))
    
@register.filter
def is_list(obj):
    return isinstance(obj, list)
    
@register.filter
def get_template_last_updated(templateFile):
	return datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(settings.TEMPLATE_DIRS[0], templateFile)), tzlocal())
    
@register.filter
def set_time_zone(datetime):
	return datetime.replace(tzinfo=tzlocal())
    
@register.assignment_tag
def regroup_by(all_objects, by, field, values):
    tmp = {}    
    for object in all_objects:
        if object[field] not in tmp:
            tmp[object[field]] = []
        tmp[object[field]].append(object)
        
    returnVal = []
    for value in values:
        returnVal.append({'grouper': value, 'list': tmp[value] if value in tmp else []})
        
    return returnVal
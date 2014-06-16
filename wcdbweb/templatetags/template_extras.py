import ordereddict
from dateutil.tz import tzlocal
from django import template
from django.utils.functional import allow_lazy
from django.utils.encoding import force_unicode
from WholeCellDB import settings
import datetime
import os
import re

register = template.Library()

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
    
@register.filter    
def get_organisms_n_batches(organisms, id):
    return organisms[id].n_batches
    
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
    
def strip_empty_lines(value):
    """Return the given HTML with empty and all-whitespace lines removed."""
    return re.sub(r'\n+', '\n', force_unicode(value))
strip_empty_lines = allow_lazy(strip_empty_lines, unicode)

class GaplessNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return strip_empty_lines(self.nodelist.render(context).strip())

def gapless(parser, token):
    """
    Remove empty and whitespace-only lines.  Useful for getting rid of those
    empty lines caused by template lines with only template tags and possibly
    whitespace.

    Example usage::

        <p>{% gapless %}
          {% if yepp %}
            <a href="foo/">Foo</a>
          {% endif %}
        {% endgapless %}</p>

    This example would return this HTML::

        <p>
            <a href="foo/">Foo</a>
        </p>

    """
    nodelist = parser.parse(('endgapless',))
    parser.delete_first_token()
    return GaplessNode(nodelist)
gapless = register.tag(gapless)
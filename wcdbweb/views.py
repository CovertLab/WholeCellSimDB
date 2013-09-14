from django.db.models import Count
from helpers import render_template
from wcdb import models

def index(request):
    summary = {
        'n_in_silico_organism': models.Simulation.objects.values('organism').annotate(count=Count('organism')).count(),
        'n_simulation': models.Simulation.objects.all().count(), 
        'n_process': models.Process.objects.all().count(),
        'n_state': models.State.objects.all().count(),
        'n_property': models.Property.objects.all().count(),
        'n_parameter': models.Parameter.objects.all().count(),
        'n_option': models.Option.objects.all().count(),
        'n_investigators': [], #TODO
    }
    return render_template('index.html', request, data = {
            'summary': summary
        })
    
def list_batches(request):
    return render_template('list_batches.html', request)
    
def tutorial(request):
    return render_template('tutorial.html', request)
    
def about(request):
    return render_template('about.html', request)
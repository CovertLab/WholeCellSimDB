from django import forms
from wcdb import models

class AdvancedSearchForm(forms.Form):
    #investigator
    investigator_name_first     = forms.CharField(required = False, widget = forms.TextInput, label='Investigator first name', help_text='Enter investigator first name')
    investigator_name_last      = forms.CharField(required = False, widget = forms.TextInput, label='Investigator last name', help_text='Enter investigator last name')
    investigator_affiliation    = forms.CharField(required = False, widget = forms.TextInput, label='Investigator affiliaton', help_text='Enter investigator affiliation')

    #organism
    organism_name               = forms.CharField(required = False, widget = forms.TextInput, label='Organism name', help_text='Enter organism name')
    organism_version            = forms.CharField(required = False, widget = forms.TextInput, label='Organism version', help_text='Enter organism version')

    #batch meta data
    simulation_batch_name       = forms.CharField(required = False, widget = forms.TextInput, label='Simulation batch name', help_text='Enter simulation batch name')
    simulation_batch_ip         = forms.CharField(required = False, widget = forms.TextInput, label='Simulation batch IP address', help_text='Enter simulation batch IP address')
    simulation_batch_date       = forms.CharField(required = False, widget = forms.TextInput, label='Simulation batch date', help_text='Enter simulation batch date')
    simulation_batch_options    = forms.CharField(required = False, widget = forms.Textarea, label='Option values', help_text='Enter option values')
    simulation_batch_parameters = forms.CharField(required = False, widget = forms.Textarea, label='Parameter values', help_text='Enter parameter values')

    #values 
    simulation_states           = forms.CharField(required = False, widget = forms.Textarea, label='State values', help_text='Enter state values')    
    
class DownloadForm(forms.Form):
    simulation_batches          = forms.MultipleChoiceField(required = True, widget = forms.CheckboxSelectMultiple, label = 'Simulation batches', help_text = 'Select simulation batches')
    
    def __init__(self, *args, **kwargs):
        super(DownloadForm, self).__init__(*args, **kwargs)
        
        choices = []
        for organism in models.Organism.objects.all():
            for batch in organism.simulation_batches.all():
                choices.append((batch.id, batch.name, ))
        self.fields['simulation_batches'].choices = choices
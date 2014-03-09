from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Count
from wcdb import models

RESULT_FORMAT_CHOICES = (
    ('hdf5', 'hdf5'),
    ('html', 'html'),
)

OPERATOR_CHOICES = (
    ('eq', '='),
    ('gt', '>'),
    ('gte', '>='),
    ('lt', '<'),
    ('lte', '<='),
    #('exact', 'Exact match'),
    #('iexact', 'Exact match (case insensitive)'),
    #('contains', 'Contains'),
    #('icontains', 'Contains (case insensitive)'),
    #('startswith', 'Starts with'),
    #('istartswith', 'Starts with (case insensitive)'),
    #('endswith', 'Ends with'),
    #('iendswith', 'Ends with (case insensitive)'),
    #('regex', 'Regular expression match'),
    #('iregex', 'Regular expression match (case insensitive)'),
)

MODELED_CHOICES = (
    ('1', 'Modeled'),
    ('0', 'Not modeled'),
)

class AdvancedSearchForm(forms.Form):
    #investigator
    result_format               = forms.ChoiceField(required = True, widget = forms.TextInput, label='Result format', help_text='Select format', choices = RESULT_FORMAT_CHOICES, initial='html')
    
    #investigator
    investigator_name_first     = forms.CharField(required = False, widget = forms.TextInput, label='Investigator first name', help_text='Enter investigator first name', initial='')
    investigator_name_last      = forms.CharField(required = False, widget = forms.TextInput, label='Investigator last name', help_text='Enter investigator last name', initial='')
    investigator_affiliation    = forms.CharField(required = False, widget = forms.TextInput, label='Investigator affiliaton', help_text='Enter investigator affiliation', initial='')

    #organism
    organism_name               = forms.CharField(required = False, widget = forms.TextInput, label='Organism name', help_text='Enter organism name', initial='')
    organism_version            = forms.CharField(required = False, widget = forms.TextInput, label='Organism version', help_text='Enter organism version', initial='')

    #batch meta data
    simulation_batch_name       = forms.CharField(required = False, widget = forms.TextInput, label='Simulation batch name', help_text='Enter simulation batch name', initial='')
    simulation_batch_ip         = forms.IPAddressField(required = False, widget = forms.TextInput, label='Simulation batch IP address', help_text='Enter simulation batch IP address', initial=None)
    simulation_batch_date       = forms.DateField(required = False, widget = forms.DateInput, label='Simulation batch date', help_text='Enter simulation batch date', initial=None)
    
    #options, parameters, processes, states
    n_option_filters            = forms.IntegerField(required = True, widget = forms.TextInput, min_value = 0, initial=3)
    n_parameter_filters         = forms.IntegerField(required = True, widget = forms.TextInput, min_value = 0, initial=3)
    n_process_filters           = forms.IntegerField(required = True, widget = forms.TextInput, min_value = 0, initial=3)
    n_state_filters             = forms.IntegerField(required = True, widget = forms.TextInput, min_value = 0, initial=3)
    
class AdvancedSearchOptionForm(forms.Form):
    option   = forms.ChoiceField(required = False, widget = forms.Select, label='Option', help_text='Select an option', initial=None)
    operator = forms.ChoiceField(required = True, widget = forms.Select, label='Operator', help_text='Select an operator', choices = OPERATOR_CHOICES, initial='eq')
    value    = forms.CharField(required = False, widget = forms.TextInput, label='Value', help_text='Enter the desired value', initial='')
       
    def __init__(self, *args, **kwargs):
        super(AdvancedSearchOptionForm, self).__init__(*args, **kwargs)
        
        global_choices = []
        options = models.Option.objects.filter(process__isnull=True, state__isnull=True).values('name', 'index').order_by('name', 'index').annotate(Count('name'), Count('index'))
        for i in range(options.count()):
            option = options[i]
            if option['index'] > 0 or (i + 1 < options.count() and option['name'] == options[i+1]['name']):
                tmp = '%s[%d]' % (option['name'], option['index'])
            else:
                tmp = '%s' % (option['name'])
            global_choices.append((tmp, tmp))
            
        process_choices = []
        options = models.Option.objects.filter(process__isnull=False).values('process__name', 'name', 'index').order_by('process__name', 'name', 'index').annotate(Count('process__name'), Count('name'), Count('index'))
        for i in range(options.count()):
            option = options[i]
            if option['index'] > 0 or (i + 1 < options.count() and option['process__name'] == options[i+1]['process__name'] and option['name'] == options[i+1]['name']):
                tmp = '%s.%s[%d]' % (option['process__name'], option['name'], option['index'])
            else:
                tmp = '%s.%s' % (option['process__name'], option['name'])
            process_choices.append(('process:' + tmp, tmp))
            
        state_choices = []
        options = models.Option.objects.filter(state__isnull=False).values('state__name', 'name', 'index').order_by('state__name', 'name', 'index').annotate(Count('state__name'), Count('name'), Count('index'))
        for i in range(options.count()):
            option = options[i]
            if option['index'] > 0 or (i + 1 < options.count() and option['state__name'] == options[i+1]['state__name'] and option['name'] == options[i+1]['name']):
                tmp = '%s.%s[%d]' % (option['state__name'], option['name'], option['index'])
            else:
                tmp = '%s.%s' % (option['state__name'], option['name'])
            state_choices.append(('state:' + tmp, tmp))
            
        self.fields['option'].choices = (
            ('Global', global_choices),
            ('Process', process_choices),
            ('States', state_choices),
            )
            
    def clean_value(self):
        if self.cleaned_data['option'] == '' and not self.cleaned_data['value'] == '':
            raise ValidationError('Value must be empty if option not selected')
        return self.cleaned_data['value']
        
class AdvancedSearchParameterForm(forms.Form):
    parameter = forms.ChoiceField(required = False, widget = forms.Select, label='Parameter', help_text='Select a parameter')
    operator  = forms.ChoiceField(required = True, widget = forms.Select, label='Operator', help_text='Select an operator', choices = OPERATOR_CHOICES)
    value     = forms.CharField(required = False, widget = forms.TextInput, label='Value', help_text='Enter the desired value')
       
    def __init__(self, *args, **kwargs):
        super(AdvancedSearchParameterForm, self).__init__(*args, **kwargs)
        
        global_choices = []
        parameters = models.Parameter.objects.filter(process__isnull=True, state__isnull=True).values('name', 'index').order_by('name', 'index').annotate(Count('name'), Count('index'))
        for i in range(parameters.count()):
            parameter = parameters[i]
            if parameter['index'] > 0 or (i + 1 < parameters.count() and parameter['name'] == parameters[i+1]['name']):
                tmp = '%s[%d]' % (parameter['name'], parameter['index'])
            else:
                tmp = '%s' % (parameter['name'])
            global_choices.append((tmp, tmp))
            
        process_choices = []
        parameters = models.Parameter.objects.filter(process__isnull=False).values('process__name', 'name', 'index').order_by('process__name', 'name', 'index').annotate(Count('process__name'), Count('name'), Count('index'))
        for i in range(parameters.count()):
            parameter = parameters[i]
            if parameter['index'] > 0 or (i + 1 < parameters.count() and parameter['process__name'] == parameters[i+1]['process__name'] and parameter['name'] == parameters[i+1]['name']):
                tmp = '%s.%s[%d]' % (parameter['process__name'], parameter['name'], parameter['index'])
            else:
                tmp = '%s.%s' % (parameter['process__name'], parameter['name'])
            process_choices.append(('process:' + tmp, tmp))
            
        state_choices = []
        parameters = models.Parameter.objects.filter(state__isnull=False).values('state__name', 'name', 'index').order_by('state__name', 'name', 'index').annotate(Count('state__name'), Count('name'), Count('index'))
        for i in range(parameters.count()):
            parameter = parameters[i]
            if parameter['index'] > 0 or (i + 1 < parameters.count() and parameter['state__name'] == parameters[i+1]['state__name'] and parameter['name'] == parameters[i+1]['name']):
                tmp = '%s.%s[%d]' % (parameter['state__name'], parameter['name'], parameter['index'])
            else:
                tmp = '%s.%s' % (parameter['state__name'], parameter['name'])
            state_choices.append(('state:' + tmp, tmp))
            
        self.fields['parameter'].choices = (
            ('Global', global_choices),
            ('Process', process_choices),
            ('States', state_choices),
            )
            
    def clean_value(self):
        if self.cleaned_data['parameter'] == '' and not self.cleaned_data['value'] == '':
            raise ValidationError('Value must be empty if parameter not selected')
        return self.cleaned_data['value']
        
class AdvancedSearchProcessForm(forms.Form):
    process = forms.ChoiceField(required = False, widget = forms.Select, label='Process', help_text='Select a process')
    modeled = forms.ChoiceField(required = True, widget = forms.Select, label='Modeled', help_text='Select a value', choices = MODELED_CHOICES)
       
    def __init__(self, *args, **kwargs):
        super(AdvancedSearchProcessForm, self).__init__(*args, **kwargs)        
        self.fields['process'].choices = [(p['name'], p['name']) for p in models.Process.objects.values('name').order_by('name').annotate(Count('name'))]
        
class AdvancedSearchStateForm(forms.Form):
    state_property = forms.ChoiceField(required = False, widget = forms.Select, label='State/property', help_text='Select a state/property')
    modeled        = forms.ChoiceField(required = True, widget = forms.Select, label='Modeled', help_text='Select a value', choices = MODELED_CHOICES)
       
    def __init__(self, *args, **kwargs):
        super(AdvancedSearchStateForm, self).__init__(*args, **kwargs)
        choices = []
        for s in models.State.objects.values('name').order_by('name').annotate(Count('name')):
            state_choices = []
            for p in models.Property.objects.filter(state__name=s['name']).values('name').order_by('name').annotate(Count('name')):
                val = '%s.%s' % (s['name'], p['name'])
                state_choices.append((val, p['name']))
            choices.append((s['name'], state_choices))
        self.fields['state_property'].choices = choices
    
class DownloadForm(forms.Form):
    simulation_batches = forms.MultipleChoiceField(required = True, widget = forms.CheckboxSelectMultiple, label = 'Simulation batches', help_text = 'Select simulation batches')
    
    def __init__(self, *args, **kwargs):
        super(DownloadForm, self).__init__(*args, **kwargs)
        
        choices = []
        for organism in models.Organism.objects.all():
            for batch in organism.simulation_batches.all():
                choices.append((batch.id, batch.name, ))
        self.fields['simulation_batches'].choices = choices
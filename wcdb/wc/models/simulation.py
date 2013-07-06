from django.db import models
from wc.models.models import UserProfile, StateProperty
from wc.models.wcmodel import WCModel


""" Simulation """
class Simulation(models.Model):
    name            = models.CharField(max_length=255)
    batch           = models.CharField(max_length=255)
    description     = models.TextField()
    replicate_index = models.PositiveIntegerField()

    ip     = models.IPAddressField()
    length = models.FloatField()
    date = models.DateTimeField(auto_now=True, auto_now_add=True)
    user = models.ForeignKey(UserProfile, editable=False)

    wcmodel = models.ForeignKey('WCModel')

    parameter_values = models.ManyToManyField('ParameterValue')
    option_values    = models.ManyToManyField('OptionValue')

    class Meta:
        get_latest_by = 'date'
        app_label='wc'

    
    def __unicode__(self):
        return self.name

""" StatePropertyValue """
class StatePropertyValue(models.Model):
    state_property  = models.ForeignKey(StateProperty)
    simulation      = models.ForeignKey(Simulation)

    def __unicode__(self):
        return 


    class Meta:
        app_label='wc'


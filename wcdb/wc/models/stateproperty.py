from django.db import models
from wc.models.simulation import Simulation

""" Property """
class StateProperty(models.Model):
    state_name = models.CharField(max_length=255)
    property_name = models.CharField(max_length=255)

    def __unicode__(self):
        return " - ".join([self.state_name, self.property_name])
    
    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        app_label='wc'


""" StatePropertyValue """
class StatePropertyValue(models.Model):
    state = models.ForeignKey(StateProperty)
    simulation      = models.ForeignKey(Simulation)
    

    def __unicode__(self):
        return 

    def get_path(self):
        return "/".join(['/states', 
                        this.stateproperty__state_name,
                        this.stateproperty__property_name])

    def file_name(self):
        return ".".join([self.simulation__name, "h5"])


    """
    This method runs the h5py code necessary to fetch the dataset
    as a numpy array
    """
    def dataset(self):
        f = h5py.File(self.file_name(), 'r')
        return f[self.get_path()]


    class Meta:
        app_label='wc'


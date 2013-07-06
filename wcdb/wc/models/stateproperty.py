from django.db import models

import numpy
import h5py


""" Property """
class StateProperty(models.Model):
    state_name = models.CharField(max_length=255)
    property_name = models.CharField(max_length=255)

    def __unicode__(self):
        return "-".join([self.state_name, self.property_name])
    
    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        app_label='wc'


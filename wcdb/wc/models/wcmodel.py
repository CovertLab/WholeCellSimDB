from django.db import models
from wc.models.models import StateProperty

""" Models """
class WCModel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    organism = models.CharField(max_length=255, default=name)

    parameters  = models.ManyToManyField('Parameter')
    options     = models.ManyToManyField('Option')
    processes   = models.ManyToManyField('Process')
    state_properties = models.ManyToManyField('StateProperty')

    def __unicode__(self):
        return ", ".join([self.name, self.organism])


    class Meta:
        verbose_name = 'Model'
        verbose_name_plural = 'Models'
        app_label='wc'

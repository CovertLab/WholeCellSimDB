from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

import numpy
import h5py

HDF5_ROOT = "/home/nolan/wcdb/hdf5"

       

""" User """
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    affiliation = models.CharField(max_length=255, 
                                   blank=True, default='')

    
    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        get_latest_by = 'user__date_joined'


""" Parameter """ 
class Parameter(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class ParameterValue(models.Model):
    parameter = models.ForeignKey('Parameter')
    value = models.FloatField()

    def __unicode__(self):
        return str(self.value)


""" Option """
class Option(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class OptionValue(models.Model):
    option = models.ForeignKey('Option')
    value = models.TextField()

    def __unicode__(self):
        return self.value


""" Process """
class Process(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'Processes'

    def __unicode__(self):
        return self.name


""" Models """
class WCModel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    organism = models.CharField(max_length=255, default=name)

    parameters  = models.ManyToManyField('Parameter')
    options     = models.ManyToManyField('Option')
    processes   = models.ManyToManyField('Process')

    def save(self, *args, **kwargs):
        print("Saving WCModel to database.")
        if not self.pk: # Create a new hdf5 model file.
            file_name = "_".join(['model', ".".join([self.name,'h5'])])
            file_path = "/".join([HDF5_ROOT, file_name]).replace(" ", "_")
            print("Ceating new hdf5 file for WCModel.")
            print("File path: " + file_path)
            try:
                f = h5py.File(file_path, "w-")
                f.create_group("states")
                f.create_dataset("processes",   (1,1), maxshape=(1, None))
                f.create_dataset("options",     (1,1), maxshape=(1, None))
                f.create_dataset("parameter",   (1,1), maxshape=(1, None))
                f.create_dataset("metadat",     (1,1), maxshape=(1, None))
                f.close()
                print("File has been created.")
            except(IOError):
                print "ERROR: File specified already exists."

        super(WCModel, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Model'
        verbose_name_plural = 'Models'

""" Simulation """
class Simulation(models.Model):
    name            = models.CharField(max_length=255)
    batch           = models.CharField(max_length=255)
    description     = models.TextField()
    replicate_index = models.PositiveIntegerField()

    ip     = models.IPAddressField()
    length = models.FloatField()
    date = models.DateTimeField(auto_now=True, auto_now_add=True)
    user = models.ForeignKey(User, editable=False)

    parameter_values = models.ManyToManyField('ParameterValue')
    option_values    = models.ManyToManyField('OptionValue')


    class Meta:
        get_latest_by = 'date'




""" Labels """
class LabelTableManager(models.Manager):
    def create_label_table(self, table_name, table_dictionary):
        label_table_name = self.create(name=table_name)
        # Use raw SQL to create a new table. 


class LabelTable(models.Model):
    name = models.CharField(max_length=255)

    objects = LabelTableManager()


""" Property """
class StateProperty(models.Model):
    state_name = models.CharField(max_length=255)
    property_name = models.CharField(max_length=255)

    wc_model = models.ForeignKey("WCModel")
   
    row_label_ids = models.ForeignKey("LabelTable", related_name="row") 
    col_label_ids = models.ForeignKey("LabelTable", related_name="col")


    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'


class StatePropertyValue(models.Model):
    state_property  = models.ForeignKey(StateProperty)
    simulation      = models.ForeignKey(Simulation)



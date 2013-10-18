#!/usr/bin/env python
from django.db import models

import h5py
from django.contrib.auth.models import User
from WholeCellDB.settings import HDF5_ROOT
from wcdb.managers import *

property_tag = property


# Option Related Classes
# Option, Target, Group, SimulationsOptions
class OptionTarget(models.Model):
    class Meta:
        app_label='wcdb'


class Option(models.Model):
    name = models.CharField(max_length=255, null=False, default="")
    target = models.ForeignKey('OptionTarget', related_name='options')

    def __unicode__(self):
        # If target is an organism version
        #   /options/%s
        # elif target is a state
        #   "/options/states/%s/%s" % (self.target.name, self.name)
        # elif target is a process
        #   "/options/processes/%s/%s" % (self.target.name, self.name)
        # else
        #   "%s/%s" % (self.target.__unicode__(), self.name)
        return '%s/%s' % (self.target.__unicode__(), self.name)

    class Meta:
        app_label = 'wcdb'


class OptionGroup(OptionTarget):
    name = models.CharField(max_length=255, null=False, default="")
    target = models.ForeignKey('OptionTarget', related_name='option_groups')

    def __unicode__(self):
        return '%s/%s' % (self.target.__unicode__(), self.name)

    class Meta:
        app_label = 'wcdb'


class SimulationsOptions(models.Model):
    simulation = models.ForeignKey('Simulation')
    option = models.ForeignKey('Option')
    value = models.CharField(max_length=255, default="", null=True)
    index = models.IntegerField(default=1)

    class Meta:
        app_label = 'wcdb'


# Parameter Related Classes
# Parameter, Target, Group, Simulation Options
class ParameterTarget(models.Model):
    class Meta:
        app_label = 'wcdb'


class Parameter(models.Model):
    name = models.CharField(max_length=255, null=False, default="")
    target = models.ForeignKey('ParameterTarget', related_name='parameters')

    def __unicode__(self):# If target is an organism version
        #   /options/%s
        # elif target is a state
        #   "/options/states/%s/%s" % (self.target.name, self.name)
        # elif target is a process
        #   "/options/processes/%s/%s" % (self.target.name, self.name)
        # else
        #   "%s/%s" % (self.target.__unicode__(), self.name)
        return '%s/%s' % (self.target.__unicode__(), self.name)

    class Meta:
        app_label='wcdb'


class ParameterGroup(ParameterTarget):
    name = models.CharField(max_length=255, null=False, default="")
    target = models.ForeignKey('ParameterTarget', related_name='parameter_groups')

    def __unicode__(self):
        return '%s/%s' % (self.target.__unicode__(), self.name)

    class Meta:
        app_label = 'wcdb'


class SimulationsParameters(models.Model):
    simulation = models.ForeignKey('Simulation')
    parameter = models.ForeignKey('Parameter')
    value = models.CharField(max_length=255, default="", null=True)
    index = models.IntegerField(default=1)

    class Meta:
        app_label = 'wcdb'


# Property Related Models
# Property, SimulationsProperties
class Property(models.Model):
    name = models.CharField(max_length=255, null=False, default='')
    state = models.ForeignKey('State', related_name='properties')
    shape = models.CharField(max_length=255, null=False, default='[0]')
    dtype = models.CharField(max_length=5, null=False, default='f8')
    labels = models.ManyToManyField('LabelSet', through='PropertyLabelSets')

    def __unicode__(self):
        return " - ".join([
            self.state.__unicode__(),
            self.name
            ])

    @property_tag
    def path(self):
        """The path to the dataset within the simulation h5 file """
        return "%s/%s" % (self.state.path, self.name)

    class Meta:
        verbose_name_plural = 'Properties'
        unique_together = ['name', 'state']
        ordering = ['state', 'name']
        app_label = 'wcdb'


class PropertyValue(models.Model):
    property = models.ForeignKey('Property')
    simulation = models.ForeignKey('Simulation')

    # Number of indices filled in in the time dimension.
    _filled = models.IntegerField(default=0)

    objects = PropertyValuesManager()

    def __unicode__(self):
        return self.path

    @property_tag
    def path(self):
        return "%s/%s" % (self.simulation.path, self.property.path)

    @property_tag
    def h5file(self):
        return self.simulation.h5file

    @property_tag
    def dataset(self):
        """ The H5Py Dataset object for this property. """
        f = self.h5file
        return f[self.path]

    def add_data(self, ts):
        """
        This method is for adding new time slices to the data.

        Arguments
            name        type
            ----------------------
            ts      | numpy.array


        This method requires that ts.shape be the same lengh as the
        shape as self.dataset.shape, and the last dimension of ts is less than
        the number indices available in self.dataset.

        That is, len(ts.shape) == len(self.dataset.shape)

        For example:
            If self.dataset.shape is (2,3,4), you must pass in a tuple of
            shape (2,3,x).

            If ts == {{0, 1}, {2, 3}, {4, 5}} then it will fail.

            Instead, it should be ts == {{[0], [1]}, {[2], [3]}, {[4], [5]}}
        """
        # If all dimensions, except the time dimension, are equal.
        """ I'm not sure if I should be doing this if statement, or if I
            should just let it throw the exception."""
        if ts.shape[:-1] == self.dataset.shape[:-1]:
            lts = ts.shape[-1] # Length of the new slice.

            # If there isn't enough room for the time timeslice then
            # we'll expand the dataset so there is room.
            if lts > (self.dataset.shape[-1] - self._filled):
                new_length = self._filled + lts
                # The new shape is the old one, but with the new
                # length replacing the old length.
                new_shape = self.dataset.shape[:-1] + (new_length,)
                self.dataset.resize(new_shape)
                self.simulation.length = new_length
            # Put the new time slice(s) in the dataset starting
            # at the first empty slot.
            self.dataset[..., self._filled:self._filled+lts] = ts
            self.state.simulation.h5file.flush()
            self._filled += lts
        else:
            return False  # Can this be made pretty?


# Processes
class Process(OptionTarget, ParameterTarget):
    name = models.CharField(max_length=255, null=False, default="")
    organism_version= models.ForeignKey("OrganismVersion", related_name='processes')

    def __unicode__(self):
        return "%s - %s" % (self.organism_version.__unicode__(), self.name)

    class Meta:
        unique_together = ['name', 'organism_version']
        verbose_name_plural = 'Processes'
        app_label = 'wcdb'

    """
    I need to create a process manager so that I can store 
    this information in the HDF5 file as well.  
    """


# States
class State(OptionTarget, ParameterTarget):
    name = models.CharField(max_length=255, null=False, default="")
    organism_version = models.ForeignKey('OrganismVersion', related_name='states')
    units = models.CharField(max_length=10)
 
    def __unicode__(self):
        return " - ".join([self.organism_version.__unicode__(), self.name])

    @property_tag
    def path(self):
        return "/states/%s" % self.name

    class Meta:
        app_label = 'wcdb'
    

# Simulations
class Simulation(models.Model):
    """

    - JSON DESCRIPTION -
    simulation_run = {
        "organism name": string,
        "version": string,
        "options": {
            "__simulation_parameter_name__": value,
            "target_type": {
                "target_name": {
                    "option_name": [value0, value1, ..., valueN],
                },
            },
        },
        "parameters": {
            "__name_of_parameter_for_simulation__": value,
            "target_type": {
                "target_name": {
                    "parameters_name": [value0, value1, ..., valueN],
                },
            },
        },
        "processes": [
            "Process_1",
            "Process_2",
            ...,
        ],
        "states_properties": {
            "state_name": {
                "units": "unit type",
                "properties": {
                    "property_name": {
                        "dimensions": [d0, d1, ..., dn],
                        "dtype": "dtype",
                        "labels": [
                            "labelset_name_for_dim0",
                            "labelset_name_for_dim1",
                            ...
                        ]
                    },
                },
            },
        }
    }
        
    """ 
    # Metadata
    organism_version = models.ForeignKey('OrganismVersion', related_name='simulations')
    batch = models.ForeignKey('SimulationBatch', related_name='simulations')
    batch_index = models.PositiveIntegerField(default=1)
    length = models.IntegerField(default=1)

    properties = models.ManyToManyField('Property', through='PropertyValue')
    options = models.ManyToManyField('Option', through='SimulationsOptions')
    parameters = models.ManyToManyField('Parameter', through='SimulationsParameters')

    # Internal
    _file_permissions = models.CharField(max_length=3, default="a")

    objects = SimulationManager()

    @property_tag
    def path(self):
        return "/simulations/%s" % self.batch_index

    @property_tag
    def h5file(self):
        """ The H5Py File object for the Simulation HDF5 file """        
        return self.batch.h5file

    def __unicode__(self):
        return '%s - /simulations/%s/ ' % (self.batch.name, self.batch_index)

    class Meta:
        unique_together = (('batch', 'batch_index'), )
        get_latest_by = 'batch__date'
        app_label = 'wcdb'


# SimulationBatches
class SimulationBatch(models.Model):
    """
    batch_description = {
        "name": string,
        "description": string,
        "organism_version": string,
        "ip":"string",
        "investigator": {
            "first name": string,
            "last name": string,
            "affiliation: string,
            "email": string
        },

    }
        
    """
    name = models.CharField(max_length=255, default='')
    description = models.TextField(default="")
    organism_version = models.ForeignKey('OrganismVersion', related_name='simulation_batches')
    investigator = models.ForeignKey('Investigator', related_name='simulation_batches')
    ip = models.IPAddressField(default="0.0.0.0")
    date = models.DateTimeField(auto_now=True, auto_now_add=True)
    
    objects = SimulationBatchManager()

    @property_tag
    def file_path(self):
        """ The path to the HDF5 file for the SimulationBatch """
        return '%s/%s.h5' % (HDF5_ROOT, self.name)

    def h5file(self):
        return h5py.File(self.file_path)

    def __unicode__(self):
        return "%s - %s" % (self.organism_version.__unicode__(), self.name)


    class Meta:
        verbose_name = 'Simulation batch'
        verbose_name_plural = 'Simulation batches'
        get_latest_by = 'date'
        app_label = 'wcdb'


# In-Silico Organisms and their different versions of code.
class Organism(models.Model):
    """
    This table represents an in-silico organism.

    organism_description = {
        "name": string,
    }

    """
    name = models.CharField(max_length=255, default="", unique=True)
    ## Possible Fields ##
    # programming language used
    # programming language version
    # domain, kingdom, phylum, class, order, family, genus, species

    def __unicode__(self):
        return self.name
    

    class Meta:
        ordering = ['name']
        app_label = 'wcdb'


class OrganismVersion(OptionTarget, ParameterTarget):
    """ 
    This table represents a specific code version of an in-silico version of an
    organisms.

    - JSON Description -

    organism_version = {
        "organism name": string,
        "version": string,
        "options": {
            "simulation_options": [
                "__simulation_parameter_1_name",
                "__simulation_parameter_2_name":{
                    "suboption_name":
                },
                ...,
            ],
            "target_type": {
                "target_name": [
                    "option_1_name",
                    "option_2_name",
                    ...
                ],
            },
        },
        "parameters": {
            "__name_of_parameter_for_simulation__": value,
            "target_type": {
                "target_name": [
                    "parameter_1_name",
                    "parameter_2_name",
                    ...
                ],
            },
        },
        "processes": [
            "Process 1",
            "Process B",
            ...
        ],
        "states_properties": {
            "state_name": {
                "units": "unit type",
                "properties": {
                    "property_name": {
                        "dimensions": [d0, d1, ..., dn],
                        "dtype": "dtype",
                        "labels": [
                            "labelset_name_for_dim0",
                            "labelset_name_for_dim1",
                            ...
                        ]
                    },
            },
        },
        "label_sets": {
            "label_set": [
                "label_1",
                "label_2",
                ...
            ],
        }
    }
    """
    version = models.CharField(max_length=255)
    organism = models.ForeignKey('Organism', related_name='versions')

    objects = OrganismVersionManager()

    def option_dict(self):
        pass

    def parameter_dict(self):
        pass

    def state_property_dict(self):
        pass

    def process_list(self):
        pass

    def __unicode__(self):
        return "%s %s" % (self.organism.__unicode__(), self.version)

    class Meta:
        ordering = ['version']
        app_label = 'wcdb'


# People
class Investigator(User):
    affiliation = models.CharField(max_length=255, default="")
    
    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

    class Meta:
        ordering = ['last_name', 'first_name']
        get_latest_by = 'date_joined'


# The Labelsets associated with OrganismVersions, the Labels they contain,
# and the relationships they have with Properties
class PropertyLabelSets(models.Model):
    """
    Model for representing the ManyToMany relationship between
    Properties and LabelSets.

    It has a field for indicating which dimension of the
    property the LabelSet it is associated with.
    """
    property = models.ForeignKey('Property')
    label_set = models.ForeignKey('LabelSet')
    dimension = models.PositiveIntegerField()


    class Meta:
        app_label = 'wcdb'


class LabelSet(models.Model):
    """
    A set of labels that describe the dimensions of Properties.

    Example Names:
        'Compartments'
        'Gene'
        'ProteinComplex-Mature

    - JSON Description -
    labelset_description = {
        "name": ["label 1", "label 2", ... , "label n"],
    }
    """
    name = models.CharField(max_length=255)
    labels = models.ManyToManyField('Label', through='LabelSetsLabels')
    organism_version = models.ForeignKey('OrganismVersion', related_name='labelsets')

    def __unicode__(self):
        return name

    class Meta:
        app_label = 'wcdb'


class LabelSetsLabels(models.Model):
    """
    Model for representing the ManyToMany relationship between
    Labels and LabelSets.

    It has a field for indicating which index the Label is
    associated with in the LabelSet.
    """
    label_set = models.ForeignKey('LabelSet')
    label = models.ForeignKey('Label')
    index = models.PositiveIntegerField()

    class Meta:
        app_label = 'wcdb'


class Label(models.Model):
    """
    A label for dimension index in a property.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __unicode__(self):
        return "%s - %s" % (self.name, self.description)

    class Meta:
        app_label = 'wcdb'

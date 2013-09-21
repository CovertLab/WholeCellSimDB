#!/usr/bin/env python
from django.db import models
from django.contrib.auth.models import User

import h5py
import re
import sys
from WholeCellDB.settings import HDF5_ROOT

property_tag = property

# This serves as the base class for the Option and Parameter tables.
class OPBase(models.Model):
    target  = models.ForeignKey('OPTarget', related_name='%(class)s')
    name    = models.CharField(max_length=255)
    value   = models.CharField(max_length=255, null=True, blank=True)
    index   = models.IntegerField(default=0) # This will probably have to be stored in HDF5 file.

    def __unicode__(self):
        return ' - '.join([
                self.target.__unicode__(),
                self.name,
                self.value
            ])


    class Meta:
        abstract = True # Need to do something about the indexes. Store in HDF5?


class Option(OPBase):  
    target = models.ForeignKey('OPTarget', related_name='options')


    class Meta:
        app_label = 'wcdb'


class Parameter(OPBase):
    target = models.ForeignKey('OPTarget', related_name='parameters')


    class Meta:
        app_label='wcdb'


# This is the base class for the State and Process tables, which contain
# mostly the same relations, just in a different context.
class OPTarget(models.Model):
    name = models.CharField(max_length=255)
    simulation = models.ForeignKey('Simulation', related_name='OPParent')

    def __unicode__(self):
        return ' - '.join([
            self.simulation.__unicode__(),
            self.name
            ])


    class Meta:
        abstract = True


class Process(OPTarget):
    simulation = models.ForeignKey("Simulation", related_name='processes')


    class Meta:
        verbose_name_plural = 'Processes'
        app_label = 'wcdb'

 
class State(OPTarget):
    simulation = models.ForeignKey('Simulation', related_name='states')   
     

    class Meta:
        app_label = 'wcdb'
    

""" Properties """
class PropertyManager(models.Manager):
    def create_property_value(self, state, name, shape, dtype):
        """ 
        Creates a new StatePropertyValue and the associated dataset. 

        Arguments
            name            | type
            ----------------------------------
            simulation      | wcdb.models.Simulation
            property        | wcdb.models.Property 
            shape           | Tuple of Ints
            dtype           | Numpy.dtype
        """
        p_obj = self.create(state=state, name=name)

        maxshape = shape[:-1] + (None,)

        f = simulation.h5file  # Get the simulation h5 file

        # Create the datset in the simulation h5 file
        f.create_dataset(p_obj.path, 
                         shape = shape, 
                         dtype = dtype,
                         maxshape = maxshape)

        # Make sure it's saved and closed.
        f.flush()
        f.close()

        return p_obj


class Property(models.Model):
    name   = models.CharField(max_length='255', default='')    
    state  = models.ForeignKey('State', related_name='properties')
    labels = models.ManyToManyField('LabelSet', through='PropertyLabel')

    # Number of indices filled in in the time dimension.
    _filled = models.IntegerField(default=0) 

    objects = PropertyManager()
    
    @property_tag
    def path_to_dataset(self):
        """ The path to the dataset within the simulation h5 file """
        return "/".join([self.state.name,
                         self.name])

    @property_tag
    def shape_of_dataset(self):
        """ The shape of the property's dataset """
        return self.dataset.shape

    @property_tag
    def length_of_dataset(self):
        return self.shape[-1]

    @property_tag
    def num_dimensions(self):
        return (len(self.shape) - 1)

    @property_tag
    def dataset(self):
        """ The H5Py Dataset object for this property. """
        f = self.simulation.h5file
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
                new_shape = self.dataset.shape[:-1] + (new_length,)
                self.dataset.resize(new_shape)
                self.simulation.length = new_length

            self.dataset[...,self._filled:self._filled+lts] = ts
            self.simulation.h5file.flush()
            self._filled += lts
        else:
            return False # Can this be made pretty?

    # Unicode
    def __unicode__(self):
        return " - ".join([
            self.state.__unicode__(),
            self.property.name
            ])

    class Meta:
        verbose_name_plural = 'Properties'
        ordering = ['state', 'name']
        app_label = 'wcdb'


class PropertyLabel(models.Model):
    property  = models.ForeignKey('Property', related_name='label_sets')
    label_set = models.ForeignKey('LabelSet', related_name='properties')
    dimension = models.PositiveIntegerField()


    class Meta:
        app_label = 'wcdb'


class SimulationManager(models.Manager):
    def create_simulation(self, 
                          batch,    
                          batch_index = 1,
                          state_properties = {},
                          length = 0.0):
        
        # Associated the Simulation with the batch. 
        simulation = batch.simulations.create(                                 
                                 batch_index = batch_index,
                                 length = length,
                                 )

        f = simulation.h5file 

        for state_name, pd in state_properties.iteritems():
            state = batch.states.get(name = state_name)
            
            g = f.create_group('/states/' + state_name) # This should maybe happen in a StateManager?
            f.flush()
            
            for prop_name, d in pd.iteritems():
                property = state.properties.get(name=prop_name)
                PropertyValue.objects.create_property_value(
                                                simulation, 
                                                property,
                                                d[0], # Shape
                                                d[1]) # dType

        f.flush()
        f.close() 

        return simulation


class Simulation(models.Model):
    # Metadata
    batch       = models.ForeignKey('SimulationBatch', related_name='simulations')  
    batch_index = models.PositiveIntegerField(default=1)
    length      = models.FloatField(default=0.0)  

    # Internal
    _file_permissions = models.CharField(max_length=3, default="a")

    objects = SimulationManager()

    """""""""""""""""""""""""""""""""""""""#
    # Methods for dealing with the H5 file.#
    """""""""""""""""""""""""""""""""""""""#
    @property_tag
    def file_path(self):
        """ The path to the HDF5 file for the Simulation """
        return '%s/%d.h5' % (HDF5_ROOT, self.id)

    @property_tag
    def h5file(self):
        """ The H5Py File object for the Simulation HDF5 file """        
        return h5py.File(self.file_path, self._file_permissions)

    def lock_file(self):
        """
        Makes the file read only (when accessing through these models)
        """
        self._file_permissions = "r"

    # Other classes/methods
    def __unicode__(self):
        return ' - '.join([
            self.batch.__unicode__(),
            self.batch.name, 
            '%d' % self.batch_index
            ])

    class Meta:
        unique_together = (('batch', 'batch_index'), )
        get_latest_by = 'batch__date'
        app_label = 'wcdb'

        
class SimulationBatchManager(models.Manager):
    def create_simulation_batch(self, 
                          organism_name,
                          organism_version,
                          name="", 
                          description="", 
                          investigator_first="",
                          investigator_last="",
                          investigator_affiliation="",
                          investigator_email="",
                          ip='0.0.0.0',
                          processes = [],
                          states = [], 
                          state_properties = {},
                          options = {},
                          parameters = {}):

        organism = OrganismVersion.objects.get_or_create(name=organism_version, organism__name=organism)[0]
        organism.save()
        
        investigator = Investigator.objects.get_or_create(
            first_name=investigator_first,
            last_name=investigator_last,
            email=investigator_email,
            affiliation=investigator_affiliation)[0]
        
        batch = organism.simulation_batches.create(
            name = name,
            description = description,
            organism_version = organism_version,
            investigator = investigator,
            ip = ip)
        batch.save()
        
        #processes
        for name in processes:
            process = batch.processes.create(name=name)
            process.save()
        
        #states
        for name in states:
            state = batch.states.create(name=name)
            state.save()
            
        #state properties
        for state_name, props in state_properties.iteritems():
            state = batch.states.get(name=state_name)
            for prop_name in props:
                property = state.properties.create(name=prop_name)
                property.save()
        
        #options
        for prop_name, value in options.iteritems():
            if re.match(r"^__.+?__$", prop_name) or prop_name == 'processes' or prop_name == 'states':
                continue
            if isinstance(value, list):
                for index in range(len(value)):
                    option = batch.options.create(name = prop_name, value = value[index], index = index)
            else:
                option = batch.options.create(name = prop_name, value = value)
            option.save()
        
        for process_name, props in options['processes'].iteritems():
            process = batch.processes.get(name = process_name)
            
            for prop_name, value in props.iteritems():
                if isinstance(value, list):
                    for index in range(len(value)):
                        option = batch.options.create(process = process, name = prop_name, value = value[index], index = index)
                else:
                    option = batch.options.create(process = process, name = prop_name, value = value)
                option.save()
        
        for state_name, props in options['states'].iteritems():
            state = batch.states.get(name = state_name)
            
            for prop_name, value in props.iteritems():
                if isinstance(value, list):
                    for index in range(len(value)):
                        option = batch.options.create(state = state, name = prop_name, value = value[index], index = index)
                else:
                    option = batch.options.create(state = state, name = prop_name, value = value)
                option.save()
        
        #parameters
        for prop_name, value in parameters.iteritems():
            if re.match(r"^__.+?__$", prop_name) or prop_name == 'processes' or prop_name == 'states':
                continue
            if isinstance(value, list):
                for index in range(len(value)):
                    parameter = batch.parameters.create(name = prop_name, value = value[index], index = index)
            else:
                parameter = batch.parameters.create(name = prop_name, value = value)
            parameter.save()
        
        for process_name, props in parameters['processes'].iteritems():
            process = batch.processes.get(name = process_name)
            
            for prop_name, value in props.iteritems():
                if isinstance(value, list):
                    for index in range(len(value)):
                        parameter = batch.parameters.create(process = process, name = prop_name, value = value[index], index = index)
                else:
                    parameter = batch.parameters.create(process = process, name = prop_name, value = value)
                parameter.save()
        
        for state_name, props in parameters['states'].iteritems():
            state = batch.states.get(name = state_name)
            
            for prop_name, value in props.iteritems():
                if isinstance(value, list):
                    for index in range(len(value)):
                        parameter = batch.parameters.create(state = state, name = prop_name, value = value[index], index = index)
                else:
                    parameter = batch.parameters.create(state = state, name = prop_name, value = value)
                parameter.save()
        
        return batch # Do some cleanup

        
class SimulationBatch(models.Model):
    name             = models.CharField(max_length=255, default='')
    description      = models.TextField(default="")    
    organism_version = models.ForeignKey('OrganismVersion', related_name='simulation_batches')
    investigator     = models.ForeignKey('Investigator', related_name='simulation_batches')
    ip               = models.IPAddressField(default="0.0.0.0")
    date             = models.DateTimeField(auto_now=True, auto_now_add=True)
    
    objects = SimulationBatchManager()
    
    def __unicode__(self):
        return " - ".join([
                self.organism_version.__unicode__(),
                self.name
            ])


    class Meta:
        verbose_name = 'Simulation batch'
        verbose_name_plural = 'Simulation batches'
        get_latest_by = 'date'
        app_label = 'wcdb'
 

class LabelSet(models.Model):
    name = models.CharField(max_length=255)
    organism_version = models.ForeignKey('OrganismVersion', related_name='label_sets')
    dimensions = models.IntegerField()

    def __unicode__(self):
        return name


    class Meta:
        app_label = 'wcdb'


class LabelSetLabel(models.Model):
    """This crazily named table just stores extra names for the m2m relation between Labels and their Sets."""
    label = models.ForeignKey('Label')
    label_set = models.ForeignKey('LabelSet')
    index = models.PositiveIntegerField()

    class Meta:
       app_label = 'wcdb'


class Label(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __unicode__(self):
        return ("%i. %s" % (self.index, self.name)).strip()


    class Meta:
        app_label = 'wcdb'


class Organism(models.Model):
    """ This table represents an in-silico organism. """
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


class OrganismVersion(models.Model):
    """ 
    This table represents a specific code version of an in-silico version of an
    organisms.
    """
    version_number = models.CharField(max_length=255)
    organism = models.ForeignKey('Organism', related_name='versions')

    def __unicode__(self):
        return " - ".join([
                self.organism.__unicode__(),
                self.version_number
            ])


    class Meta:
        ordering = ['version_number']
        app_label = 'wcdb'
        unique_together = ('version_number', 'organism__name')


class Investigator(User):
    affiliation = models.CharField(max_length=255, default="")
    
    def __unicode__(self):
        return ('%s %s' % (self.first_name, self.last_name)).strip()       
    

    class Meta:
        ordering = ['last_name', 'first_name']
        get_latest_by = 'date_joined'

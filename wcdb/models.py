#!/usr/bin/env python
from django.db import models
from django.contrib.auth.models import User

import h5py
import os
import re
import sys
from WholeCellDB.settings import HDF5_ROOT

property_tag = property

""" OPP """
class Option(models.Model):
    """ 
    Option 

    Creating Options
        Options.objects.create(name, value, simulation)
    """     
    process          = models.ForeignKey('Process', null=True, blank=True, related_name = 'options')
    state            = models.ForeignKey('State', null=True, blank=True, related_name = 'options')
    name             = models.CharField(max_length=255, db_index=True)
    value            = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    units            = models.CharField(max_length=255, null=True, blank=True)
    index            = models.IntegerField(default=0, db_index=True)
    simulation_batch = models.ForeignKey("SimulationBatch", related_name = 'options')

    def __unicode__(self):
        names = [
            self.simulation_batch.organism.name,
            self.simulation_batch.name,
            ]
        if self.state is not None:
            names.append(self.state.name)
        if self.state is not None:
            names.append(self.state.name)
        names.append(self.name)
        return ' - '.join(names)

    class Meta:
        app_label = 'wcdb'
        ordering = ['name', 'index']
        get_latest_by = 'simulation_batch__date'

class Parameter(models.Model):
    """ 
    Parameter

    Creating Parameter
        Parameter.objects.create(name, value, simulation)
    """     
    process          = models.ForeignKey('Process', null=True, blank=True, related_name='parameters')
    state            = models.ForeignKey('State', null=True, blank=True, related_name='parameters')
    name             = models.CharField(max_length=255, db_index=True)
    value            = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    units            = models.CharField(max_length=255, null=True, blank=True)
    index            = models.IntegerField(default=0, db_index=True)
    simulation_batch = models.ForeignKey("SimulationBatch", related_name='parameters')

    def __unicode__(self):
        names = [
            simulation_batch.organism.name,
            simulation_batch.name,
            ]
        if self.state is not None:
            names.append(self.state.name)
        if self.state is not None:
            names.append(self.state.name)
        names.append(self.name)
        return ' - '.join(names)

    class Meta:
        app_label='wcdb'
        ordering = ['name', 'index']
        get_latest_by = 'simulation_batch__date'


""" Process """      
class Process(models.Model):
    """ 
    Process 

    Creating Processes
        Process.objects.create(name, simulation_batch)
    """ 
    name             = models.CharField(max_length=255, db_index=True)
    simulation_batch = models.ForeignKey("SimulationBatch", related_name = 'processes')

    def __unicode__(self):
        return ' - '.join([
            self.simulation_batch.organism.name,
            self.simulation_batch.name,
            self.name
            ])
    
    class Meta:
        verbose_name_plural = 'Processes'
        app_label='wcdb'
        ordering = ['name']
        get_latest_by = 'simulation_batch__date'

""" States """   
class State(models.Model):
    """
    State

    State.objects.create(name, simulation)
        name        |   type
        --------------------------------------
        name        |   String
        simulation  |   wcdb.models.Simulation
    """
    name             = models.CharField(max_length=255, db_index=True)
    simulation_batch = models.ForeignKey('SimulationBatch', related_name='states')   
        
    # Unicode
    def __unicode__(self):
        return ' - '.join([
            self.simulation_batch.organism.name,
            self.simulation_batch.name,
            self.name
            ])
            
    class Meta:
        app_label='wcdb'
        ordering = ['name']
        get_latest_by = 'simulation_batch__date'


""" Properties """
class Property(models.Model):
    state = models.ForeignKey('State', related_name='properties')   
    name  = models.CharField(max_length=255, db_index=True)
    units = models.CharField(max_length=255, null=True, blank=True)
    
    def __unicode__(self):
        return ' - '.join([
            self.state.simulation_batch.organism.name,
            self.state.simulation_batch.name,
            self.state.name,
            self.name
            ])
            
    class Meta:
        app_label='wcdb'
        ordering = ['name']
        get_latest_by = 'state__simulation_batch__date'

""" Properties """
class PropertyValueManager(models.Manager):
    def create_property_value(self, simulation, property, shape, dtype):
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
        p_obj = self.create(simulation=simulation, property=property)

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


class PropertyValue(models.Model):
    """
    Property value
    """
    simulation = models.ForeignKey('Simulation', related_name='property_values')
    property   = models.ForeignKey('Property', related_name = 'values')

    # Number of indices filled in in the time dimension.
    _filled = models.IntegerField(default=0) 

    objects = PropertyValueManager()
    
    @property_tag
    def path(self):
        """ The path to the dataset within the simulation h5 file """
        return "/".join([self.property.state.name,
                         self.property.name])

    @property_tag
    def shape(self):
        """ The shape of the property's dataset """
        return self.dataset.shape

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
            return False

    # Unicode
    def __unicode__(self):
        return " - ".join([
            self.simulation.batch.organism.name, 
            self.simulation.batch.name, 
            '%d' % self.simulation.batch_index,
            self.property.state.name, 
            self.property.name
            ])

    class Meta:
        verbose_name_plural = 'Properties'
        app_label='wcdb'
        ordering = ['simulation__batch_index']
        get_latest_by = 'simulation__batch__date'
        
class PropertyLabel(models.Model):
    property  = models.ForeignKey('Property', related_name='labels')  
    name      = models.CharField(max_length=255, null=True, blank=True, default=None, db_index=True)
    dimension = models.PositiveIntegerField(db_index=True)
    index     = models.PositiveIntegerField(db_index=True)
    
    def get_dataset(self, batch_indices = None):
        sims = self.property.state.simulation_batch.simulations
        
        if batch_indices is None:
            batch_indices = [x[0] for x in sims.values_list('batch_index')]
        
        return_val = []
        for batch_index in batch_indices:
            prop_val = property.values.get(simulation__batch_index = batch_index)
            return_val.append(prop_val.dataset.take(self.index, self.dimension))
            
        return return_val
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        app_label = 'wcdb'
        ordering = ['dimension', 'index']
        get_latest_by = 'property__simulation__batch__date'


class SimulationManager(models.Manager):
    def create_simulation(self, 
                          batch,    
                          batch_index = 1,
                          length = None,
                          state_properties = {}):
        
        simulation = batch.simulations.create(                                 
                                 batch_index = batch_index,
                                 length = length)

        f = simulation.h5file 

        for state_name, pd in state_properties.iteritems():
            state = batch.states.get(name = state_name)
            
            g = f.create_group('/states/' + state_name)
            f.flush()
            
            for prop_name, d in pd.iteritems():
                property = state.properties.get(name=prop_name)
                PropertyValue.objects.create_property_value(simulation, 
                                                 property,
                                                 d[0], # Shape
                                                 d[1]) # dType

        f.flush()
        f.close() 

        return simulation

class Simulation(models.Model):
    """ 
    Simulation 

    Creation Arguments
        name                | type
        ----------------------------
        batch               | SimulationBatch
        batch_index         | Positive Integer
        state_properties    | Dict String:Dict {"State name": PropertyDict,}
        length              | Float

        State Dict Format:
            {"State Name": 
                {"Property name": 
                    (
                      (k0, k1, ..., kn, t), 
                      dtype
                    )
                }
            }

        Where k0, ..., kn are Integers describing the shape of the property,
        and t is an Integer indicating how many time slices there will be.
    """
    # Metadata
    batch       = models.ForeignKey('SimulationBatch', related_name='simulations')  
    batch_index = models.PositiveIntegerField(default=1, db_index=True)
    length      = models.FloatField(null=True, blank=True, default=None)

    # Internal
    _file_permissions = models.CharField(max_length=3, default="a")

    objects = SimulationManager()

    """""""""""""""""""""""""""""""""""""""#
    # Methods for dealing with the H5 file.#
    """""""""""""""""""""""""""""""""""""""#
    @property_tag
    def file_path(self):
        """ The path to the HDF5 file for the Simulation """
        return os.path.join(HDF5_ROOT, '%d.h5' % self.id)

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
            self.batch.organism.name, 
            self.batch.name, 
            '%d' % self.batch_index
            ])

    class Meta:
        unique_together = (('batch', 'batch_index'), )
        ordering = ['batch_index']
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
                          date=None,
                          processes = [],
                          states = [], 
                          state_properties = {},
                          options = {},
                          parameters = {}):

        organism = Organism.objects.get_or_create(name = organism_name)[0]
        organism.save()
        
        user = User.objects.get_or_create(
                first_name = investigator_first,
                last_name = investigator_last,
                email = investigator_email
                )[0]
        user.save()
        try:
            investigator = user.investigator
            investigator.affiliation = investigator_affiliation
        except Investigator.DoesNotExist:
            investigator = Investigator(
               user = user, 
               affiliation = investigator_affiliation
               )
        investigator.save()
        
        batch = organism.simulation_batches.create(
            name = name,
            description = description,
            organism_version = organism_version,
            investigator = investigator,
            ip = ip,
            date = date)
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
            for prop_name, units_labels in props.iteritems():
                property = state.properties.create(name=prop_name, units=units_labels['units'])
                property.save()
                
                for dimension, dimension_labels in enumerate(units_labels['labels'] or []):
                    for index, name in enumerate(dimension_labels):
                        label = property.labels.create(name=name, dimension=dimension, index=index)
                        label.save()
                
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
        
        return batch
        
class SimulationBatch(models.Model):
    organism         = models.ForeignKey('Organism', related_name = 'simulation_batches')
    organism_version = models.CharField(max_length=255, default="")
    name             = models.CharField(max_length=255, default="", db_index=True)
    description      = models.TextField(default="")
    investigator     = models.ForeignKey('Investigator', related_name = 'simulation_batches')
    ip               = models.IPAddressField(default="0.0.0.0")
    date             = models.DateTimeField(null=True, blank=True, db_index=True)
    date_added       = models.DateTimeField(auto_now=True, auto_now_add=True)
    
    objects = SimulationBatchManager()
    
    class Meta:
        verbose_name = 'Simulation batch'
        verbose_name_plural = 'Simulation batches'
        ordering = ['name']
        get_latest_by = 'date'
        app_label = 'wcdb'
        unique_together = (('organism', 'name'), )
        
class Organism(models.Model):
    name = models.CharField(max_length=255, default="", unique=True, db_index=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        app_label = 'wcdb'
        ordering = ['name']
        get_latest_by = 'simulation_batches__date'

class Investigator(models.Model):
    user        = models.OneToOneField(User)
    affiliation = models.CharField(max_length=255, default="")
    
    def __unicode__(self):
        return ('%s %s' % (self.first_name, self.last_name)).strip()       
    
    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        get_latest_by = 'simulation_batches__date'
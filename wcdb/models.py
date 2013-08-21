#!/usr/bin/env python
from django.db import models
from django.contrib.auth.models import User
import h5py
import sys

HDF5_ROOT = "/home/nolan/hdf5"


class Parameter(models.Model):
    """ 
    Parameter

    Each Whole Cell Model (WCM) will have a set of Parameters. Because the 
    number of parameters may change depending on the WCM, they are stored
    internally in their own as Django models.
    """ 
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


    class Meta:
        app_label='wcdb'


class Option(models.Model):
    """ 
    Option 

    Each Whole Cell Model (WCM) will have a set of Options. Because the 
    number of options may change depending on the WCM, they are stored
    internally in their own as Django models.
    """ 

    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


    class Meta:
        app_label='wcdb'


""" Process """
class Process(models.Model):
    """ 
    Process 

    Each Whole Cell Model (WCM) will have a set of Process. Because the 
    number of processes may change depending on the WCM, they are stored
    internally in their own as Django models.
    """ 
    name = models.CharField(max_length=255, primary_key=True, unique=True)

    class Meta:
        verbose_name_plural = 'Processes'
        app_label='wcdb'

    def __unicode__(self):
        return self.name


class State(models.Model):
    """
    State

    States are groups of paramters. 
    """
    name = models.CharField(max_length=255)
    simulation = models.ForeignKey('Simulation')
     
    @property
    def path(self):
        """ The path to the dataset within the simulation h5 file """
        return "/".join(['/states', self.name]).replace(" ", "_")

    # Unicode
    def __unicode__(self):
        return " - ".join([self.simulation.name, 
                           self.name])

class PropertyManager(models.Manager):
    def create_property(self, simulation, state_name, property_name,
                        shape, dtype):
        """ 
        Creates a new StatePropertyValue and the associated dataset. 

        Arguments
            name            | type
            ----------------------------------
            simulation      | wcdb.Simulation
            state_name      | String
            property_name   | String
            dimensions      | Tuple of Ints
            dtype           | Numpy.dtype
        """
        s_obj = State.objects.get_or_create(name=state_name, 
                                            simulation=simulation)[0]
        p_obj = self.create(name=property_name, state=s_obj)

        maxshape = shape[:-1] + (None,)

        f = simulation.h5file  # Get the simulation h5 file

        # Create the datset in the simulation h5 file
        f.create_dataset(p_obj.path, shape=shape, dtype=dtype,
                         maxshape=maxshape)

        # Make sure it's saved and closed.
        f.flush()
        f.close()

        return p_obj


class Property(models.Model):
    """
    Property

    """
    name  = models.CharField(max_length=255)
    state = models.ForeignKey('State')

    # Number of indices filled in in the time dimension.
    filled = models.IntegerField(default=0) 

    objects = PropertyManager()
                         
    # Generates the path to the dataset in the h5 file.
    @property
    def path(self):
        """ The path to the dataset within the simulation h5 file """
        return "/".join([self.state.path,
                         self.name]).replace(" ", "_")

    @property
    def shape(self):
        """ The shape of the property's dataset """
        return self.dataset.shape

    # Access the H5Py dataset object for this property.
    @property
    def dataset(self):
        """ The H5Py Dataset object for this property. """
        f = self.state.simulation.h5file
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
        if ts.shape[:-1] == self.dataset.shape[:-1]:
            lts = ts.shape[-1] # Length of the time dimension.

            # If there isn't enough room for the time timeslice then
            # we'll expand the dataset so there is room.
            if lts > (self.dataset.shape[-1] - self.filled):
                new_shape = self.dataset.shape[:-1] + (self.filled + lts,)
                self.dataset.resize(new_shape)

            self.dataset[...,self.filled:self.filled+lts] = ts
            self.state.simulation.h5file.flush()
            self.filled += lts
        else:
            return False

    # Unicode
    def __unicode__(self):
        return " - ".join([self.state.simulation.name, 
                           self.state.name, 
                           self.name])

    class Meta:
        app_label='wcdb'


class SimulationManager(models.Manager):
    def create_simulation(self, name, organism, replicate_index=1, t=1,
                          description="", ip='0.0.0.0', batch="", length=1.0,
                          options={},     parameters={}, processes=[], 
                          state_properties={}):

        simulation = self.create(name=name, batch=batch, length=length, 
                                 ip=ip, t=t, description=description,
                                 replicate_index=replicate_index)

        f = simulation.h5file 

        for s, pd in state_properties.iteritems():
            for p, d in pd.iteritems():
                dim = d[0] + (t,)
                simulation.add_property(s, p, dim, d[1])

        for name, value in options.iteritems():
                simulation.add_option(name=name, value=value)

        for name, value in parameters.iteritems():
            simulation.add_parameter(name=name, value=value)

        for name in processes:
            simulation.add_process(name=name)

        f.flush()
        f.close() 

        return simulation

class Simulation(models.Model):
    """ 
    Simulation 

    """
    # Metadata
    name            = models.CharField(max_length=255, unique=True)
    organism        = models.CharField(max_length=255, default="")
    batch           = models.CharField(max_length=255, default="")
    description     = models.TextField(default="")
    length          = models.FloatField(default=1.0)
    replicate_index = models.PositiveIntegerField(default=1)
    ip              = models.IPAddressField(default="0.0.0.0")
    date            = models.DateTimeField(auto_now=True, auto_now_add=True)
    t               = models.PositiveIntegerField()

    # M2M Fields
    options     = models.ManyToManyField('Option', 
                                 through='SimulationsOptions')
    parameters  = models.ManyToManyField('Parameter', 
                                 through='SimulationsParameters')
    processes   = models.ManyToManyField('Process')

    # Internal
    _file_permissions = models.CharField(max_length=3, default="a")

    objects = SimulationManager()

    
    # Methods for dealing with State-Properties
    # States
    def get_state(self, state_name):
        return self.state_set.get(name=state_name)

    def add_state(self, state_name):
        """ 
        NOTE: This stuff should be in a State Manager. 
        """
        State.objects.create(name=state_name, simulation=self)
        if self._file_permissions == 'a':
            f = self.h5file
            g = f.create_group('/states/' + state_name) 
            f.flush()
            return g

    # Properties
    def add_property(self, state_name, property_name, shape, dtype):
        """ 
        Adds and returns a property to this Simulation.

        I have provided this method because it works from the perspective of
        adding a property to a Simulation, instead of the perspective of
        creating a property, and then specifying the Simulation you're
        relating it too.

        Arguments
            name            |   type 
            ----------------------------------
            state_name      |   String 
            property_name   |   String
            shape           |   Tuple of Ints
            dtype           |   numpy.dtype
    
        """
        return Property.objects.create_property(self, state_name, 
                                                 property_name, shape, dtype)


    def get_property(self, state_name, property_name):
        """ 
        Returns the Property with the specified name.

        Arguments
            name            |   type
            ------------------------------------
            state_name      |   String
            property_name   |   String
        """
        s = self.state_set.get(name=state_name)
        return s.property_set.get(name=property_name)

    #########################################
    # OPP                                   #
    def add_op(self, cls, name, value):
        obj = cls.objects.get_or_create(name=name)[0]
        m2m = getattr(sys.modules[__name__], 
                      "Simulations" + cls._meta.verbose_name_plural.title())
        return m2m.objects.create(simulation=self, obj=obj, value=value)

    def add_option(self, name, value):
        return self.add_op(Option, name, value)

    def add_parameter(self, name, value):
        return self.add_op(Parameter, name, value)

    def add_process(self, name):
        p = Process.objects.get_or_create(name=name)
        return self.processes.add(p)


    ########################################
    # Methods for dealing with the H5 file.#
    @property
    def file_path(self):
        """ The path to the HDF5 file for the Simulation """
        return HDF5_ROOT + "/" + self.name.replace(" ","_") + ".h5"

    @property
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
        return self.name


    class Meta:
        get_latest_by = 'date'
        app_label='wcdb'


class SimulationsOptions(models.Model):
    simulation  = models.ForeignKey(Simulation)
    obj         = models.ForeignKey(Option)
    value       = models.TextField()

    @property
    def option(self):
        return self.obj

    class Meta:
        app_label='wcdb'


class SimulationsParameters(models.Model):
    simulation  = models.ForeignKey(Simulation)
    obj         = models.ForeignKey(Parameter)
    value       = models.FloatField()

    @property
    def parameter(self):
        return self.obj

    class Meta:
        app_label='wcdb'

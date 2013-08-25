#!/usr/bin/env python
from django.db import models
from django.contrib.auth.models import User
import h5py
import sys

HDF5_ROOT = "/home/nolan/hdf5"

### OPP ###
class Option(models.Model):
    """ 
    Option 

    Each Whole Cell Model (WCM) will have a set of Options. Because the 
    number of options may change depending on the WCM, they are stored
    internally in their own as Django models.
    """ 
    name        = models.CharField(max_length=255)
    value       = models.CharField(max_length=255)
    simulation  = models.ForeignKey("Simulation")

    def __unicode__(self):
        return self.name


    class Meta:
        app_label='wcdb'


class Parameter(models.Model):
    """ 
    Parameter

    Each Whole Cell Model (WCM) will have a set of Parameters. Because the 
    number of parameters may change depending on the WCM, they are stored
    internally in their own as Django models.
    """ 
    name        = models.CharField(max_length=255)
    value       = models.PositiveIntegerField()
    simulation  = models.ForeignKey("Simulation")

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
    name       = models.CharField(max_length=255)
    simulation = models.ForeignKey("Simulation")

    class Meta:
        verbose_name_plural = 'Processes'
        app_label='wcdb'

    def __unicode__(self):
        return self.name

### States ###
class StateManager(models.Manager):
    def create_state(self, name, simulation):
        state = self.create(name=name, simulation=simulation)
        f = simulation.h5file
        g = f.create_group('/states/' + name)
        f.flush()
        return state
    
class State(models.Model):
    """
    State

    States are groups of paramters. 

    Creation Arguments
        name        |   type
        --------------------------------------
        name        |   String
        simulation  |   wcdb.models.Simulation
    """
    name = models.CharField(max_length=255)
    simulation = models.ForeignKey('Simulation')

    objects = StateManager()
     
    @property
    def path(self):
        """ The path to the dataset within the simulation h5 file """
        return "/".join(['/states', self.name]).replace(" ", "_")

    # Unicode
    def __unicode__(self):
        return " - ".join([self.simulation.name, 
                           self.name])


### Properties ###
class PropertyManager(models.Manager):
    def create_property(self, simulation, state, name, shape, dtype):
        """ 
        Creates a new StatePropertyValue and the associated dataset. 

        Arguments
            name            | type
            ----------------------------------
            simulation      | wcdb.Simulation
            state           | wcdb.State 
            name            | String
            dimensions      | Tuple of Ints
            dtype           | Numpy.dtype
        """
        p_obj = self.create(name=name, state=state)

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
                         
    @property
    def path(self):
        """ The path to the dataset within the simulation h5 file """
        return "/".join([self.state.path,
                         self.name]).replace(" ", "_")

    @property
    def shape(self):
        """ The shape of the property's dataset """
        return self.dataset.shape

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
                new_length = self.filled + lts
                new_shape = self.dataset.shape[:-1] + (new_length,)
                self.dataset.resize(new_shape)
                self.state.simulation.t = new_length

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
    def create_simulation(self, 
                          name, 
                          organism,
                          batch="", 
                          description="", 
                          length=1.0,
                          replicate_index=1,
                          ip='0.0.0.0', 
                          t=1, 
                          options={},
                          parameters={},
                          processes=[], 
                          state_properties={}):

        simulation = self.create(name=name, 
                                 organism=organism,
                                 batch=batch, 
                                 description=description,
                                 length=length, 
                                 replicate_index=replicate_index,
                                 ip=ip,
                                 t=t)

        f = simulation.h5file 

        for state_name, pd in state_properties.iteritems():
            state = State.objects.create_state(state_name, simulation)
            for prop_name, d in pd.iteritems():
                Property.objects.create_property(simulation,
                                                 state, 
                                                 prop_name,
                                                 d[0], # Shape
                                                 d[1]) # dType

        for name, value in options.iteritems():
            Option.objects.create(name=name, value=value,
                                   simulation=simulation)

        for name, value in parameters.iteritems():
            Parameter.objects.create(name=name, value=value,
                                     simulation=simulation)

        for name in processes:
            Process.objects.create(name=name, simulation=simulation)

        f.flush()
        f.close() 

        return simulation

class Simulation(models.Model):
    """ 
    Simulation 

    Creation Arguments
        name                | type
        ----------------------------
        name                | String
        organism            | String
        batch               | String
        description         | String 
        length              | Float 
        replicate_index     | Positive Integer
        ip                  | IP Address
        t                   | Integer
        options             | Dict String:String {"Option name": "Option val",}
        parameters          | Dict String:Float  {"Parameter name": 0.0,}
        processes           | Tuple of Strings of Process names.
        state_properties    | Dict String:Dict {"State name": PropertyDict,}

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
    name            = models.CharField(max_length=255, unique=True)
    organism        = models.CharField(max_length=255, default="")
    batch           = models.CharField(max_length=255, default="")
    description     = models.TextField(default="")
    length          = models.FloatField(default=1.0)
    replicate_index = models.PositiveIntegerField(default=1)
    ip              = models.IPAddressField(default="0.0.0.0")
    date            = models.DateTimeField(auto_now=True, auto_now_add=True)
    t               = models.PositiveIntegerField()

    # Internal
    _file_permissions = models.CharField(max_length=3, default="a")

    objects = SimulationManager()

    ########################################
    # Methods for dealing with the H5 file.#
    ########################################
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

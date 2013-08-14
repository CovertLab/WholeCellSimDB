#!/usr/bin/env python
"""
This is the models module for the Whole Cell DB. 
"""
from django.db import models
from django.contrib.auth.models import User
import h5py

HDF5_ROOT = "/home/nolan/hdf5"

__author__ = "Nolan Phillips"
__credits__ = ["Nolan Phillips", "Yingwei Wang", "Jonathan Karr"]
__version__ = "1.0.1"
__maintainer__ = "Nolan Phillips"
__email__ = "ncphillips@upei.ca"
__status__ = "Development"
__date__ = "Tue Aug 13 22:22:18 ADT 2013"

""" User """
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    affiliation = models.CharField(max_length=255, 
                                   blank=True, default='')

    def __unicode__(self):
        if (self.affiliation == ""):
            return self.user.__unicode__()
        else:
            return " - ".join([self.user.__unicode__(), self.affiliation])
    
    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        get_latest_by = 'user__date_joined'
        app_label='wcdb'


""" Parameter """ 
class Parameter(models.Model):
    name = models.CharField(max_length=255)
    value = models.FloatField()

    def __unicode__(self):
        return " = ".join([self.name, str(self.value)])


    class Meta:
        app_label='wcdb'


""" Option """
class Option(models.Model):
    name = models.CharField(max_length=255)
    value = models.TextField()

    def __unicode__(self):
        return " = ".join([self.name, self.value])


    class Meta:
        app_label='wcdb'


""" Process """
class Process(models.Model):
    name = models.CharField(max_length=255, primary_key=True, unique=True)

    class Meta:
        verbose_name_plural = 'Processes'
        app_label='wcdb'

    def __unicode__(self):
        return self.name


class State(models.Model):
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

""" StateProperty """
class PropertyManager(models.Manager):
    def create_property(self, simulation, state_name, property_name,
                        dimensions, dtype):
        """ 
        Creates a new StatePropertyValue and the associated dataset. 

        Arguments
            name            type
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

        maxshape = dimensions[:-1] + (None,)

        f = simulation.h5file  # Get the simulation h5 file

        # Create the datset in the simulation h5 file
        f.create_dataset(p_obj.path, shape=dimensions, dtype=dtype,
                         maxshape=maxshape)

        # Make sure it's saved and closed.
        f.flush()
        f.close()

        return p_obj


class Property(models.Model):
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
    def create_simulation(self, name, organism, model, replicate_index=1, t=1,
                          description="", ip='0.0.0.0', batch="", length=1.0,
                          options={},     parameters={}, processes=[], 
                          state_properties={}):

        simulation = self.create(name=name, batch=batch,   model=model, 
                                 length=length, ip=ip, t=t,
                                 description=description,
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

""" Simulation """
class Simulation(models.Model):
    # Metadata
    name            = models.CharField(max_length=255, unique=True)
    model           = models.CharField(max_length=255, default="")
    organism        = models.CharField(max_length=255, default="")
    batch           = models.CharField(max_length=255, default="")
    description     = models.TextField(default="")
    length          = models.FloatField(default=1.0)
    #user            = models.ForeignKey('UserProfile')
    replicate_index = models.PositiveIntegerField(default=1)
    ip              = models.IPAddressField(default="0.0.0.0")
    date            = models.DateTimeField(auto_now=True, auto_now_add=True)
    t               = models.PositiveIntegerField()

    # M2M Fields
    options     = models.ManyToManyField('Option')
    parameters  = models.ManyToManyField('Parameter')
    processes   = models.ManyToManyField('Process')

    # Internal
    _file_permissions = models.CharField(max_length=3, default="a")

    objects = SimulationManager()

    
    # Methods for dealing with State-Properties
    # States
    def get_state(self, state_name):
        """ Returns a Queryset of properties from the specified state """
        return self.state_set.get(state_name=state_name)

    def add_state(self, state_name):
        State.objects.create(name=state_name, simulation=self)
        if self._file_permissions == 'a':
            f = self.h5file
            g = f.create_group('/states/' + state_name) 
            f.flush()
            return g

    # Properties
    def add_property(self, s, p, dim, dtype):
        """ Adds a property to the wcmodel. """
        p_obj = Property.objects.create_property(self, s, p, dim, dtype)


    def get_property(self, state_name, property_name):
        """ Returns the StatePropertyValue specified """
        s = self.state_set.get(name=state_name)
        return s.property_set.get(name=property_name)

    ########################################################################
    # General methods for dealing with Options, Parameters, and Processes. #
    def add_opp(self, cls, field, name, value=''):
        """ 
        If the opp is added to the simulation that object is returned,
        however, if the opp already exists then nothing is returned.  

        Arguments
            name    |   type
            -------------------------------------------------
            cls     |   Class
            field   |   django.db.models.ForeignKeyField
            name    |   String
            value   |   OPTIONAL: String OR Float 

        """
        try: 
            o = cls.objects.get_or_create(name=name, value=value)[0]
        except:
            o = cls.objects.get_or_create(name=name)[0]
        
        if o not in field.filter(name=name):
            field.add(o)
            return o

    def set_opp(self, cls, field, name, value):
        """ 
        Updates the value of the OPP with the given name.

        Arguments
            name    |   type
            ----------------------------------
            cls     |   Class
            field   |   models.ForeignKeyField
            name    |   String
            value   |   String OR Float 


        NOTE:   This method accomplishes it's task by removing
                the previous object-relation and adding a new one.

        """
        try:
            new = cls.objects.get_or_create(name=name, value=value)[0]
            current = field.filter(name=name)[0]
            if new.value != current.value:
                field.remove(current)
                field.add(new)
                return new
        except: pass

    # Methods for dealing with Options 
    def add_option(self, name, value=""):
        """ 
        Adds an Option with the specified name and value to the Simulation.

        Argument
            name    |   type
            ----------------------
            name    |   String
            value   |   String
        """
        if type(value) == str:
            self.add_opp(Option, self.options, name, value)

    def get_option(self, name):
        """ 
        Returns the Option with the specified name.

        Arguments
            name    |   type
            ------------------
            name    |   String
        """ 
        return self.options.filter(name=name)[0]

    def set_option(self, name, value):
        """ 
        Set the value of the Option with the specified name to the 
        specified value. 

        Arguments
            name    |   type
            ----------------
            name    |   String
            value   |   String

        """
        if type(value) == str:
            self.set_opp(Option, self.options, name, value)

    # Methods for dealing with Paramters
    def add_parameter(self, name, value=0):
        """
        Adds a parameter to the Simulation with the
        specified name and value.

        Arguments
            name    |   type
            ---------------------------
            name    |   String
            value   |   Float
        """
        if type(value) == float:
            self.add_opp(Parameter, self.parameters, name, value)

    def get_parameter(self, name):
        """ 
        Returns the parameter with the specified name. 

        Arguments
            name    |   type
            --------------------
            name    |   String

        """
        return self.parameters.filter(name=name)[0]

    def set_parameter(self, name, value):
        """
        Sets the value of the Parameter with the specified name,
        to the specified value. 

        Arguments
            name    |   type
            ---------------------
            name    |   String
            value   |   float
        """
        if type(value) == float:
            self.set_opp(Parameter, self.parameters, name, value)

    # Methods for dealing with Process 
    def add_process(self, name):
        """
        Adds a process to this Simulation simulation with
        the specified name. 

        Arguments
            name    |   type
            ----------------
            name    |   String
    
        """
        self.add_opp(Process, self.processes, name)

    def get_process(self, name):
        """
        Returns the process associated with this Simulation with
        the specified name.


        Arguments
            name    |   type
            -----------------
            name    |   String
        """
        return self.processes.filter(name=name)[0]

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

HDF5_ROOT = "/home/nolan/hdf5"
from django.db import models
from django.contrib.auth.models import User
import h5py


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
        app_label='wc'


""" Parameter """ 
class Parameter(models.Model):
    name = models.CharField(max_length=255, primary_key=True, unique=True)
    value = models.FloatField()

    def __unicode__(self):
        return " = ".join([self.parameter.__unicode__(), str(self.value)])


    class Meta:
        app_label='wc'


""" Option """
class Option(models.Model):
    name = models.CharField(max_length=255, primary_key=True, unique=True)
    value = models.TextField()

    def __unicode__(self):
        return " = ".join([self.option.__unicode__(), self.value])


    class Meta:
        app_label='wc'


""" Process """
class Process(models.Model):
    name = models.CharField(max_length=255, primary_key=True, unique=True)

    class Meta:
        verbose_name_plural = 'Processes'
        app_label='wc'

    def __unicode__(self):
        return self.name
   app_label='wc'


""" Models """
class WCModel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    organism = models.CharField(max_length=255, default=name)


    class Meta:
        verbose_name = 'Model'
        verbose_name_plural = 'Models'
        app_label='wc'


class StatePropertyManager(models.Manager):
    def create_property(self, simulation, state_property):
        """ Creates a new StatePropertyValue and the associated dataset """
        spv = StatePropertyValue.objects.create(
                state_property=state_property,
                simulation=simulation)

        spv_path = spv.get_path()  # Get the path to the dataset
        f = simulation.get_file()  # Get the simulation h5 file

        # Create the datset in the simulation h5 file
        f.create_dataset(spv_path, (1,1), 'f8', maxshape=(None,None))

        # Make sure it's saved and closed.
        f.flush()
        f.close()

        return spv


""" StateProperty """
class StateProperty(models.Model):
    simulation      = models.ForeignKey('Simulation')
    state_name      = models.CharField(max_length=255)
    property_name   = models.CharField(max_length=255)

    objects = StatePropertyManager()
                         
    # Generates the path to the dataset in the h5 file.
    def get_path(self):
        """ Get the path to the dataset within the simulation h5 file """
        return "/".join(['/states', 
                        self.state_name,
                        self.property_name]).replace(" ", "_")

    # Access the H5Py dataset object for this property.
    def dataset(self):
        """ Returns the H5Py Dataset object for this property. """
        if self.simulation.__editable == True:
            f = h5py.File(self.file_name())
        else:
            f = h5py.File(self.file_name(), 'r')
        return f[self.get_path()]

    # Unicode
    def __unicode__(self):
        return self.simulation.__unicode__() + "| " + \
               self.state_name + " " + self.property_name


    class Meta:
        app_label='wc'


class SimulationManager(models.Manager):
    def create_simulation(self, name, wcmodel, user, batch="", description="",
                          replicate_index=1,   ip='0.0.0.0',   length=1.0,
                          option_values={}, parameter_values={}):

        simulation = self.create(name=name, batch=batch,   wcmodel=wcmodel, 
                                 user=user, length=length, ip=ip,
                                 description=description,
                                 replicate_index=replicate_index)

        # For each state property in the model, create a new value.
        for sp in wcmodel.state_properties.all():
            StatePropertyValue.objects.create_property(simulation, sp)

        # Autocreate all OptionValues
        for option in wcmodel.options.all():
            # If the value was given in the Simulation creation call, 
            # then set the value to the given one. Otherwise just use
            # an empty string as the value.
            if option.name in option_values:
                option_value = option_values[option.name]
            else:
                option_value = ""
            
            o = OptionValue.objects.get_or_create(option=option, 
                                                  value=option_value)[0]
            simulation.options.add(o)

        # Autocreate all ParameterValues
        for parameter in wcmodel.parameters.all():
            # If the value was given in the Simulation creation call, 
            # then set the value to the given one. Otherwise just use
            # 0 as the value.
            if parameter.name in parameter_values:
                parameter_value = parameter_values[parameter.name]
            else:
                parameter_value = 0
            
            p = ParameterValue.objects.get_or_create(parameter=parameter, 
                                                     value=parameter_value)[0]
            simulation.parameters.add(p)
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
    user            = models.ForeignKey('UserProfile')
    replicate_index = models.PositiveIntegerField(default=1)
    ip              = models.IPAddressField(default="0.0.0.0")
    date            = models.DateTimeField(auto_now=True, auto_now_add=True)

    # M2M Fields
    options     = models.ManyToManyField('Option')
    parameters  = models.ManyToManyField('Parameter')
    processes   = models.ManyToManyField('Process')

    # Internal
    __editable = models.BooleanField(default=True)

    objects = SimulationManager()

    
    # Methods for dealing with Properties
    def add_property(self, state_name, property_name):
        """ Adds a property to the wcmodel. """
        state_property = StateProperty.objects.get_or_create(
            state_name=state_name,
            property_name=property_name)[0]
        self.state_properties.add(state_property)


    def get_state(self, state_name):
        """ Returns a Queryset of properties from the specified state """
        return self.state_properties.filter(state_name=state_name)

    def get_property(self, state_name, property_name):
        """ Returns the StatePropertyValue specified """
        return self.stateproperty_set.filter(state_name=state_name,
                                             property_name=property_name)[0]

    def get_property(self, state_name, property_name):
        """ Returns the StatePropertyValue specified """
        return self.state_properties.filter(state_name=state_name, 
                                            property_name=property_name)[0]

    # Methods for dealing with Options 
    def add_option(self, name, value=""):
        """ Adds an option to the wcmodel. Returns true if it was successfully
            added to the Simulation. """
        option = Option.objects.get_or_create(name=name, value=value)[0]
        if option not in self.options.all():
            self.options.add(option)
            return True
        else return False

    def get_option(self, name):
        return self.options.filter(name=name)

    def set_option(self, name, value):
        """ Set the options value. """
        current= self.options.filter(name=name)[0]  # Current value?
        if current.value != value: # Actually changing the value?
            new_value = Option.objects.get_or_create(name=name, value=value)[0]
            self.options.remove(current_value)
            self.options.add(new_value)

    # Methods for dealing with Paramters
    def add_parameter(self, name, value=0):
        """ Adds a parameter to the wcmodel. """
        parameter = Parameter.objects.get_or_create(name=name, value=value)[0]
        if parameter not in self.options.all():
            self.options.add(parameter)
        self.parameters.add(parameter_added)

    def set_parameter(self, name, value):
        """ Set the parameters value. """

        parameter = Parameter.objects.get(name=name)  # Which parameter?
        current_value = self.parameters.filter(parameter=parameter)[0]
        new_value = ParameterValue.objects.get_or_create(parameter=parameter,
                                                      value=value)[0]
        if current_value is not new_value:
            self.parameters.remove(current_value)
            self.parameters.add(new_value)

    # Methods for dealing with the H5 file.
    def get_path(self):
        """ Returns the path to the HDF5 file for the Simulation """
        return HDF5_ROOT + "/" + self.name.replace(" ","_") + ".h5"

    def get_file(self):
        """ Returns the H5Py File object for the Simulation HDF5 file """
        if self.__editable == True:
            return h5py.File(self.get_path())
        else:
            return h5py.File(self.get_path(), 'r')

    # Other classes/methods
    def __unicode__(self):
        return self.name  

    def __unicode__(self):
        return ", ".join([self.name, self.organism])

       def add_process(self, name):
        """ Adds a process to the wcmodel. """
        process_added = Process.objects.get_or_create(name=name)[0]
        self.processes.add(process_added)

    
    class Meta:
        get_latest_by = 'date'
        app_label='wc'

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

    def __unicode__(self):
        return self.name


    class Meta:
        app_label='wc'


class ParameterValue(models.Model):
    parameter = models.ForeignKey('Parameter')
    value = models.FloatField()

    def __unicode__(self):
        return " = ".join([self.parameter.__unicode__(), str(self.value)])


    class Meta:
        app_label='wc'


""" Option """
class Option(models.Model):
    name = models.CharField(max_length=255, primary_key=True, unique=True)

    def __unicode__(self):
        return self.name


    class Meta:
        app_label='wc'


class OptionValue(models.Model):
    option = models.ForeignKey('Option')
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


""" StateProperty """
class StateProperty(models.Model):
    state_name = models.CharField(max_length=255)
    property_name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.state_name + " - " + self.property_name
    
    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        app_label='wc'


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

    def get_state(self, state_name):
        """ Returns a Queryset of properties from the specified state """
        return self.state_properties.filter(state_name=state_name)

    def get_property(self, state_name, property_name):
        """ Returns the StatePropertyValue specified """
        return self.state_properties.filter(state_name=state_name, 
                                            property_name=property_name)[0]

    def add_parameter(self, name):
        parameter_added = Parameter.objects.get_or_create(name=name)[0]
        self.parameters.add(parameter_added)

    def add_option(self, name):
        option_added = Option.objects.get_or_create(name=name)[0]
        self.options.add(option_added)

    def add_process(self, name):
        process_added = Process.objects.get_or_create(name=name)[0]
        self.processes.add(process_added)

    def add_property(self, state_name, property_name):
        state_property = StateProperty.objects.get_or_create(
            state_name=state_name,
            property_name=property_name)[0]
        self.state_properties.add(state_property)


    class Meta:
        verbose_name = 'Model'
        verbose_name_plural = 'Models'
        app_label='wc'


""" StatePropertyValue """
class StatePropertyValue(models.Model):
    state_property = models.ForeignKey(StateProperty)
    simulation     = models.ForeignKey('Simulation')
    

    def __unicode__(self):
        return "| ".join([self.simulation.__unicode__(),
                          self.state_property.__unicode__()])

    def get_path(self):
        return "/".join(['/states', 
                        self.state_property.state_name,
                        self.state_property.property_name]).replace(" ", "_")

    def file_name(self):
        return ".".join([self.simulation__name, "h5"])

    def file_path(self):
        return HDF5_ROOT + "/" + self.file_name()


    """
    This method runs the h5py code necessary to fetch the dataset
    as a numpy array
    """
    def dataset(self):
        f = h5py.File(self.file_name(), 'r')
        return f[self.get_path()]


    class Meta:
        app_label='wc'



class SimulationManager(models.Manager):
    def create_simulation(self, name, wcmodel, user, batch="", description="",
                          replicate_index=1,   ip='0.0.0.0',   length=1.0):

        simulation = self.create(name=name, batch=batch,   wcmodel=wcmodel, 
                                 user=user, length=length, ip=ip,
                                 description=description,
                                 replicate_index=replicate_index)

        file_path = HDF5_ROOT + "/" + name.replace(" ", "_") + ".h5" 
        hdf5_file = h5py.File(file_path) 

        # Auocreate states in both Django and HDF5
        self.__create_states(hdf5_file, simulation, 
                           wcmodel.state_properties.all())

        # Autocreate all OptionValues
        for option in wcmodel.options.all():
            option_value = OptionValue.objects.get_or_create(
                                option=option, value="")

        # Autocreate all ParameterValues
        for parameter in wcmodel.parameters.all():
            parameter_value = ParameterValue.objects.get_or_create(
                                    parameter=parameter, value=0)

        hdf5_file.flush()
        hdf5_file.close()
        return simulation

    def __create_states(self, hdf5_file, simulation, state_properties):
        for sp in state_properties:
            StatePropertyValue.objects.create(
                state_property=sp,
                simulation=simulation)

            # This should be done by the StatePropertyValueManager
            sp_path = "/".join(["/states", 
                                sp.state_name,
                                sp.property_name]).replace(" ", "_")

            hdf5_file.create_dataset(sp_path, (1,1), 'f8', 
                                     maxshape=(None,None))


""" Simulation """
class Simulation(models.Model):
    name            = models.CharField(max_length=255, unique=True)
    batch           = models.CharField(max_length=255, default="")
    description     = models.TextField(default="")
    replicate_index = models.PositiveIntegerField(default=1)

    ip     = models.IPAddressField(default="0.0.0.0")
    length = models.FloatField(default=1.0)
    date = models.DateTimeField(auto_now=True, auto_now_add=True)
    user = models.ForeignKey('UserProfile')

    wcmodel = models.ForeignKey('WCModel')

    parameters = models.ManyToManyField('ParameterValue')
    options = models.ManyToManyField('OptionValue')

    objects = SimulationManager()

    def get_path(self):
        return HDF5_ROOT + "/" + self.name.replace(" ","_") + ".h5"

    def get_state(self, state_name):
        """ Returns a Queryset of properties from the specified state """
        return self.statepropertyvalue_set.filter(
                                        state_property__state_name=state_name)

    def get_property(self, state_name, property_name):
        """ Returns the StatePropertyValue specified """
        state_property = StateProperty.objects.filter(state_name=state_name,
                                                    property_name=property_name)
        return self.statepropertyvalue_set.filter(
                                            state_property=state_property)[0]

    def get_file(self):
        pass

    def __unicode__(self):
        return self.name  


    class Meta:
        get_latest_by = 'date'
        app_label='wc'

    
   

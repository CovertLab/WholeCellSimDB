from django.db import models

""" StateProperty """
class StateProperty(models.Model):
    state_name = models.CharField(max_length=255)
    property_name = models.CharField(max_length=255)

    def __unicode__(self):
        return " - ".join([self.state_name, self.property_name])
    
    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        app_label='wc'


""" StatePropertyValue """
class StatePropertyValue(models.Model):
    state = models.ForeignKey(StateProperty)
    simulation      = models.ForeignKey('Simulation')
    

    def __unicode__(self):
        return 

    def get_path(self):
        return "/".join(['/states', 
                        this.stateproperty__state_name,
                        this.stateproperty__property_name])

    def file_name(self):
        return ".".join([self.simulation__name, "h5"])


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
            replicate_index=0, ip='0.0.0.0', length=0.0):
        simulation = self.create(name=name, batch=batch, wcmodel=wcmodel, 
                                user=user, length=length, ip=ip,
                                description=description,
                                replicate_index=replicate_index)
        for state_property in wcmodel.state_properties.all():
            StatePropertyValue.objects.create(
                    state_property=state_property,
                    simulation=simulation)


""" Simulation """
class Simulation(models.Model):
    name            = models.CharField(max_length=255)
    batch           = models.CharField(max_length=255)
    description     = models.TextField()
    replicate_index = models.PositiveIntegerField()

    ip     = models.IPAddressField()
    length = models.FloatField()
    date = models.DateTimeField(auto_now=True, auto_now_add=True)
    user = models.ForeignKey('UserProfile', editable=False)

    wcmodel = models.ForeignKey('WCModel')

    parameter_values = models.ManyToManyField('ParameterValue')
    option_values    = models.ManyToManyField('OptionValue')

    objects = SimulationManager()

    class Meta:
        get_latest_by = 'date'
        app_label='wc'

    
    def __unicode__(self):
        return self.name

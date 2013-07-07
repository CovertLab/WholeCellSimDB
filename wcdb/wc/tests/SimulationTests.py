from django.test import TestCase
from django.contrib.auth.models import User
#from wc.models.models import *
#from wc.models.simulation import Simulation
#from wc.models.stateproperty import StateProperty
#from wc.models.wcmodel import WCModel
from wc.models import *


class SimulationTests(TestCase):
    def setUp(self):
        test_user = User.objects.create_user(
                'john', 'lennon@thebeatles.com', 'johnpassword')
        WCModel.objects.create(name="Test WCModel", organism="Test organism")
        test_model = WCModel.objects.get(pk=1)
        test_model.parameters.add(
                Parameter.objects.create(name="Parameter A"))
        test_model.options.add(
                Option.objects.create(name="Test Option"))
        test_model.processes.add(
                Process.objects.create(name="Test Process"))
        test_model.state_properties.add(
                StateProperty.objects.create(
                    state_name="State A",
                    property_name="Property a"))
        test_model.state_properties.add(
                StateProperty.objects.create(
                    state_name="State A",
                    property_name="Property b"))

        Simulation.objects.create_simulation(
            name="Test Simulation 1",
            wcmodel=test_model,
            user=UserProfile.objects.create(user=test_user),
            batch="Batch 1",
            description="This is a test.",
            replicate_index=3,
            ip="123.14.3.0",
            length=3.0)

    def test_create_simulation(self):
        self.assertQuerysetEqual(
            Simulation.objects.all(),
            ['<Simulation: Test Simulation 1>'])

    def test_statepropertyvalues_autocreated(self):
        simulation = Simulation.objects.get(pk=1)
        self.assertQuerysetEqual(
            StatePropertyValue.objects.all(),
            ['<StatePropertyValue: Test Simulation 1| State A - Property a>',
             '<StatePropertyValue: Test Simulation 1| State A - Property b>'])

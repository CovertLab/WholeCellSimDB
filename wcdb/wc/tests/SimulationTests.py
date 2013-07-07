from django.test import TestCase
from django.contrib.auth.models import User
from wc.models.models import *
from wc.models.simulation import Simulation
from wc.models.stateproperty import StateProperty
from wc.models.wcmodel import WCModel


class SimulationTests(TestCase):
    def test_create_simulation_without_stateproperties(self):
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

        Simulation.objects.create(
            name="Test Simulation 1",
            batch="Batch 1",
            description="This is a test.",
            replicate_index=3,
            ip="123.14.3.0",
            length=3.0,
            user=UserProfile.objects.create(user=test_user),
            wcmodel=test_model)

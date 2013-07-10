HDF5_ROOT = "/home/nolan/hdf5"
import os 
from django.test import TestCase
from django.contrib.auth.models import User
#from wc.models.models import *
#from wc.models.simulation import Simulation
#from wc.models.stateproperty import StateProperty
#from wc.models.wcmodel import WCModel
from wc.models import *


class SimulationTests(TestCase):
    def create_simulation(self):
        test_user = User.objects.create_user(
                'john', 'lennon@thebeatles.com', 'johnpassword')
        WCModel.objects.create(name="Test WCModel", organism="Test organism")
        test_model = WCModel.objects.get(pk=1)
        test_model.parameters.add(
                Parameter.objects.create(name="Parameter A"))
        test_model.options.add(
                Option.objects.create(name="Option A"))
        test_model.processes.add(
                Process.objects.create(name="Process A"))
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

        simulation = Simulation.objects.get(pk=1)

        file_path = HDF5_ROOT + "/" + simulation.name.replace(" ", "_") + ".h5"
        return file_path


    def test_create_simulation(self):
        file_path = self.create_simulation()
        self.assertQuerysetEqual(
            Simulation.objects.all(),
            ['<Simulation: Test Simulation 1>'])
        os.remove(file_path)


    def test_statepropertyvalues_autocreated(self):
        file_path = self.create_simulation()
        self.assertQuerysetEqual(
            StatePropertyValue.objects.all(),
            ['<StatePropertyValue: Test Simulation 1| State A - Property a>',
             '<StatePropertyValue: Test Simulation 1| State A - Property b>'])
        os.remove(file_path)

    def test_parametervalues_autocreated(self):
        file_path = self.create_simulation()
        simulation = Simulation.objects.get(pk=1)
        self.assertQuerysetEqual(
            ParameterValue.objects.all(),
            ['<ParameterValue: Parameter A = 0.0>'])
        os.remove(file_path)

    def test_optionvalues_autocreated(self):
        file_path = self.create_simulation()
        simulation = Simulation.objects.get(pk=1)
        self.assertQuerysetEqual(
            OptionValue.objects.all(),
            ['<OptionValue: Option A = >'])
        os.remove(file_path)

    def test_hdf5_file_created(self):
        file_path = self.create_simulation()
        file_exists = True
        if os.path.exists(file_path):
            os.remove(file_path)
        else: 
            file_exists = False
        self.assertEqual(file_exists, True)



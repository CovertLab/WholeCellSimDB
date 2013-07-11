HDF5_ROOT = "/home/nolan/hdf5"

import os 
from django.test import TestCase
from django.contrib.auth.models import User
from wc.models import *


class SimulationTests(TestCase):
    def create_simulation(self):
        test_user = User.objects.create_user(
                'john', 'lennon@thebeatles.com', 'johnpassword')
        WCModel.objects.create(name="Test WCModel", organism="Test organism")
        test_model = WCModel.objects.get(pk=1)
        test_model.add_parameter("Parameter A")
        test_model.add_option("Option A")
        test_model.add_process("Process A")
        test_model.add_property("State A", "Property a")
        test_model.add_property("State A", "Property b")

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

    def test_get_state(self):
        file_path = self.create_simulation()
        simulation = Simulation.objects.all()[0]
        self.assertQuerysetEqual(
            simulation.get_state("State A"),
            ['<StatePropertyValue: Test Simulation 1| State A - Property a>',
             '<StatePropertyValue: Test Simulation 1| State A - Property b>'])
        os.remove(file_path)

    def test_get_property(self):
        file_path = self.create_simulation()
        simulation = Simulation.objects.all()[0]
        self.assertEqual(
            simulation.get_property("State A", "Property a").__unicode__(),
            'Test Simulation 1| State A - Property a'),
        os.remove(file_path)

    def test_hdf5_file_created(self):
        file_path = self.create_simulation()
        file_exists = True
        if os.path.exists(file_path):
            os.remove(file_path)
        else: 
            file_exists = False
        self.assertEqual(file_exists, True)



from django.test import TestCase
from django.contrib.auth.models import User

import os
import h5py

import wc.models as wcm

HDF5_ROOT = "/home/nolan/wcdb/hdf5"

class GreatBigTest(TestCase):
    # I'm not trying to be super thorough with this yet, I just want to 
    # automate the process of making a model and a couple things to each of it's
    # many to many fields. Then, I have to create a simulation and attach values
    # for the options, parameters, and processes. 
    def test_fully_create_model_and_make_simulation(self):

        user = User.objects.create_user(
                'john', 'lennon@thebeatles.com', 'johnpassword')

        # Parameter
        wcm.Parameter.objects.create(name="Param 1")
        wcm.Parameter.objects.create(name="Param 2")
        self.assertQuerysetEqual(
                wcm.Parameter.objects.all(),
                ['<Parameter: Param 1>', '<Parameter: Param 2>'])

        # ParameterValue
        wcm.ParameterValue.objects.create(
                parameter=wcm.Parameter.objects.get(pk=1), 
                value=1.0)
        wcm.ParameterValue.objects.create(
                parameter=wcm.Parameter.objects.get(pk=2),
                value=2.0)
        self.assertQuerysetEqual(
                wcm.ParameterValue.objects.all(),
                [   '<ParameterValue: 1.0>', 
                    '<ParameterValue: 2.0>'])

        # Option
        wcm.Option.objects.create(name="Option 1")
        wcm.Option.objects.create(name="Option 2")
        self.assertQuerysetEqual(
                wcm.Option.objects.all(),
                ['<Option: Option 1>', '<Option: Option 2>'])
       
        # Option Value
        wcm.OptionValue.objects.create(
                option=wcm.Option.objects.get(pk=1),
                value="OptionValue 1")
        wcm.OptionValue.objects.create(
                option=wcm.Option.objects.get(pk=2),
                value="OptionValue 2")
        self.assertQuerysetEqual(
                wcm.OptionValue.objects.all(),
                [   '<OptionValue: OptionValue 1>', 
                    '<OptionValue: OptionValue 2>'])

        # Process
        wcm.Process.objects.create(name="Process 1")
        wcm.Process.objects.create(name="Process 2")
        self.assertQuerysetEqual(
                wcm.Process.objects.all(),
                ['<Process: Process 1>', '<Process: Process 2>'])

        # Create Model

        wcm.WCModel.objects.create(name="gbt", organism="G. Big Test")
        self.assertQuerysetEqual(
                wcm.WCModel.objects.all(),
                ['<WCModel: gbt>']) 

        # Add parameters to Model
        testmodel = wcm.WCModel.objects.get(pk=1)
        testmodel.parameters.add(wcm.Parameter.objects.get(pk=1))
        self.assertQuerysetEqual(
                testmodel.parameters.all(),
                ['<Parameter: Param 1>'])

        testmodel.parameters.add(wcm.Parameter.objects.get(pk=2))
        self.assertQuerysetEqual(
                testmodel.parameters.all(),
                ['<Parameter: Param 1>', '<Parameter: Param 2>'])

        # Add options to model
        testmodel.options.add(wcm.Option.objects.get(pk=1))
        self.assertQuerysetEqual(
                testmodel.options.all(),
                ['<Option: Option 1>'])

        testmodel.options.add(wcm.Option.objects.get(pk=2))
        self.assertQuerysetEqual(
                testmodel.options.all(),
                ['<Option: Option 1>', '<Option: Option 2>'])

        # Add processes to model
        testmodel.processes.add(wcm.Process.objects.get(pk=1))
        self.assertQuerysetEqual(
                testmodel.processes.all(),
                ['<Process: Process 1>'])

        testmodel.processes.add(wcm.Process.objects.get(pk=2))
        self.assertQuerysetEqual(
                testmodel.processes.all(),
                ['<Process: Process 1>', '<Process: Process 2>'])

        # Create simulation
        wcm.Simulation.objects.create( 
                name="Test Sim",
                batch="Test batch.",
                user=User.objects.get(pk=1),
                length=1.0,
                description="Test description",
                replicate_index=1,
                ip="13.155.12.4",
                wcmodel=wcm.WCModel.objects.get(pk=1))
        self.assertQuerysetEqual(
                wcm.Simulation.objects.all(),
                ['<Simulation: Test Sim>'])

        # Add Parameter and Option values to the simulation.
        testsim= wcm.Simulation.objects.get(pk=1)
        testsim.parameter_values.add(wcm.ParameterValue.objects.get(pk=1))
        testsim.parameter_values.add(wcm.ParameterValue.objects.get(pk=2))
        testsim.option_values.add(wcm.OptionValue.objects.get(pk=1))
        testsim.option_values.add(wcm.OptionValue.objects.get(pk=1))


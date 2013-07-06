from django.test import TestCase
from django.contrib.auth.models import User

import os
import h5py

import wc.models.models as wcm

class GreatBigTest(TestCase):
    # I'm not trying to be super thorough with this yet, I just want to 
    # automate the process of making a model and a couple things to each of it's
    # many to many fields. Then, I have to create a simulation and attach values
    # for the options, parameters, and processes. 
    #def test_fully_create_model_and_make_simulation(self):
    def setUp(self):

        user = User.objects.create_user(
                'john', 'lennon@thebeatles.com', 'johnpassword')

        # Parameter
        wcm.Parameter.objects.create(name="Param 1")
        wcm.Parameter.objects.create(name="Param 2")
        # Parameter Values
        wcm.ParameterValue.objects.create(
                parameter=wcm.Parameter.objects.get(pk=1), 
                value=1.0)
        wcm.ParameterValue.objects.create(
                parameter=wcm.Parameter.objects.get(pk=2),
                value=2.0)
        # Option
        wcm.Option.objects.create(name="Option 1")
        wcm.Option.objects.create(name="Option 2")

        # Option Value
        wcm.OptionValue.objects.create(
                option=wcm.Option.objects.get(pk=1),
                value="OptionValue 1")
        wcm.OptionValue.objects.create(
                option=wcm.Option.objects.get(pk=2),
                value="OptionValue 2")

        # Process
        wcm.Process.objects.create(name="Process 1")
        wcm.Process.objects.create(name="Process 2")

        # StateProperties
        wcm.StateProperty.objects.create(
                state_name="Chromosome", property_name="damagedBasePairs")
        wcm.StateProperty.objects.create(
                state_name="Mass", property_name="dnaWt")
        wcm.StateProperty.objects.create(
                state_name="Mass", property_name="total")

        # Create Model
        wcm.WCModel.objects.create(name="gbt", organism="G. Big Test")

    def test_parameters_created(self):
        self.assertQuerysetEqual(
                wcm.Parameter.objects.all(),
                ['<Parameter: Param 1>', '<Parameter: Param 2>'])

    def test_parametervalues_created(self):
        self.assertQuerysetEqual(
                wcm.ParameterValue.objects.all(),
                [   '<ParameterValue: 1.0>', 
                    '<ParameterValue: 2.0>'])
    def test_options_created(self):
        self.assertQuerysetEqual(
                wcm.Option.objects.all(),
                ['<Option: Option 1>', '<Option: Option 2>'])
        
    def test_optionvalues_created(self): 
        self.assertQuerysetEqual(
                wcm.OptionValue.objects.all(),
                [   '<OptionValue: OptionValue 1>', 
                    '<OptionValue: OptionValue 2>'])
    def test_process_created(self):
        self.assertQuerysetEqual(
                wcm.Process.objects.all(),
                ['<Process: Process 1>', '<Process: Process 2>'])

    def test_stateproperty_created(self):
        self.assertQuerysetEqual(
            wcm.StateProperty.objects.all(),
            [   '<StateProperty: Chromosome-damagedBasePairs>', 
                '<StateProperty: Mass-dnaWt>',
                '<StateProperty: Mass-total>'])

    def test_wcmodel_created(self):
        self.assertQuerysetEqual(
                wcm.WCModel.objects.all(),
                ['<WCModel: gbt>']) 

    def test_add_parameters_to_wcmodel(self):
        testmodel = wcm.WCModel.objects.get(pk=1)
        testmodel.parameters.add(wcm.Parameter.objects.get(pk=1))
        self.assertQuerysetEqual(
                testmodel.parameters.all(),
                ['<Parameter: Param 1>'])

    def test_add_second_parameter_to_wcmodel(self):
        testmodel = wcm.WCModel.objects.get(pk=1)
        testmodel.parameters.add(wcm.Parameter.objects.get(pk=2))
        self.assertQuerysetEqual(
                testmodel.parameters.all(),
                ['<Parameter: Param 1>', '<Parameter: Param 2>'])

    def test_add_option_to_wcmodel(self):
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
        
        testsim= wcm.Simulation.objects.get(pk=1)

        # Add parameter values to simulation
        testsim.parameter_values.add(wcm.ParameterValue.objects.get(pk=1))
        testsim.parameter_values.add(wcm.ParameterValue.objects.get(pk=2))

        # Add option values to simulation
        testsim.option_values.add(wcm.OptionValue.objects.get(pk=1))
        testsim.option_values.add(wcm.OptionValue.objects.get(pk=2))

        # Create StatePropertyValue objects.
        wcm.StatePropertyValue.objects.create(
                state_property=wcm.StateProperty.objects.get(pk=1),
                simulation=testsim)
        wcm.StatePropertyValue.objects.create(
                state_property=wcm.StateProperty.objects.get(pk=2),
                simulation=testsim)
        wcm.StatePropertyValue.objects.create(
                state_property=wcm.StateProperty.objects.get(pk=3),
                simulation=testsim)

        self.assertQuerysetEqual(
                wcm.Simulation.objects.all(),
                ['<Simulation: Test Sim>'])


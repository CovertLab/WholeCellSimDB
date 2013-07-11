from django.test import TestCase

from wc.models import *
#from wc.models.models import Parameter, Option, Process
#from wc.models.stateproperty import StateProperty
#from wc.models.wcmodel import WCModel



class WCModelTests(TestCase):
    def test_create_empty_model(self):
        WCModel.objects.create(name="Test WCModel", organism="Test organism")
        self.assertQuerysetEqual(
                WCModel.objects.all(),
                ['<WCModel: Test WCModel, Test organism>'])

    # Add things through the methods.
    def test_add_parameter_method(self):
        WCModel.objects.create(name="Test WCModel", organism="Test organism")
        test_model = WCModel.objects.get(pk=1)
        test_model.add_parameter("Parameter A")
        self.assertQuerysetEqual(
            Parameter.objects.all(),
            ['<Parameter: Parameter A>'])

    def test_add_option_method(self):
        WCModel.objects.create(name="Test WCModel", organism="Test organism")
        test_model = WCModel.objects.get(pk=1)
        test_model.add_option("Option A")
        self.assertQuerysetEqual(
            Option.objects.all(),
            ['<Option: Option A>'])

    def test_add_process_method(self):
        WCModel.objects.create(name="Test WCModel", organism="Test organism")
        test_model = WCModel.objects.get(pk=1)
        test_model.add_process("Process A")
        self.assertQuerysetEqual(
            Process.objects.all(),
            ['<Process: Process A>'])

    def test_add_stateproperty_method(self):
        WCModel.objects.create(name="Test WCModel", organism="Test organism")
        test_model = WCModel.objects.get(pk=1)
        test_model.state_properties.add(
                StateProperty.objects.create(
                    state_name="State A",
                    property_name="Property a"))

    def test_get_state_method(self):
        WCModel.objects.create(name="Test WCModel", organism="Test organism")
        test_model = WCModel.objects.get(pk=1)
        test_model.add_property("State A", "Property a")
        test_model.add_property("State B", "Property b")
        self.assertQuerysetEqual(
                test_model.get_state('State A'),
                ['<StateProperty: State A - Property a>'])

    def test_get_property_method(self):
        WCModel.objects.create(name="Test WCModel", organism="Test organism")
        test_model = WCModel.objects.get(pk=1)
        test_model.state_properties.add(
            StateProperty.objects.create(
                state_name="State A",
                property_name="Property a"),
            StateProperty.objects.create(
                state_name="State A",
                property_name="Property b"))
        self.assertEqual(
                test_model.get_property("State A", "Property a").__unicode__(),
                'State A - Property a')

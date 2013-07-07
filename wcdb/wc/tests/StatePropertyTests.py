from django.test import TestCase
from django.contrib.auth.models import User
#from wc.models.models import *
#from wc.models.stateproperty import StateProperty
#from wc.models.wcmodel import WCModel
from wc.models import *


class StatePropertyModelTests(TestCase):
    def test_create_state_property(self):
        StateProperty.objects.create(
                state_name="State A", 
                property_name="Property a")
        self.assertQuerysetEqual(
                StateProperty.objects.all(),
                ['<StateProperty: State A - Property a>',])
    def test_create_two_properties_from_same_state(self):
        # Create two properties from the same state.
        StateProperty.objects.create(
                state_name="State A",
                property_name="Property a")
        StateProperty.objects.create(
                state_name="State A",
                property_name="Property b")
        # All in the 
        self.assertQuerysetEqual(
                StateProperty.objects.all(),
                ['<StateProperty: State A - Property a>',
                 '<StateProperty: State A - Property b>'])
        self.assertQuerysetEqual(
                StateProperty.objects.filter(state_name="State A"),
                ['<StateProperty: State A - Property a>',
                 '<StateProperty: State A - Property b>'])

    def test_create_two_properties_from_different_states(self):
        #Create two properties in two different states.
        StateProperty.objects.create(
                state_name="State A",
                property_name="Property a")
        StateProperty.objects.create(
                state_name="State B",
                property_name="Property b")
        # Al    l StateProperies
        self.assertQuerysetEqual(
                StateProperty.objects.all(),
                ['<StateProperty: State A - Property a>',
                 '<StateProperty: State B - Property b>'])
        # Just those from State A
        self.assertQuerysetEqual(
                StateProperty.objects.filter(state_name="State A"),
                ['<StateProperty: State A - Property a>'])
        # Just those from State B
        self.assertQuerysetEqual(
                StateProperty.objects.filter(state_name="State B"),
                ['<StateProperty: State B - Property b>'])


class StatePropertyValueTests(TestCase):
    def test_value(self):
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



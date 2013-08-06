from django.test import TestCase
from django.contrib.auth.models import User
from wc.models import *

import os

#
#class StatePropertyModelTests(TestCase):
#    def test_create_state_property(self):
#        StateProperty.objects.create(
#                state_name="State A", 
#                property_name="Property a")
#        self.assertQuerysetEqual(
#                StateProperty.objects.all(),
#                ['<StateProperty: State A - Property a>',])
#
#    def test_create_two_properties_from_same_state(self):
#        # Create two properties from the same state.
#        StateProperty.objects.create(
#                state_name="State A",
#                property_name="Property a")
#        StateProperty.objects.create(
#                state_name="State A",
#                property_name="Property b")
#        # All in the 
#        self.assertQuerysetEqual(
#                StateProperty.objects.all(),
#                ['<StateProperty: State A - Property a>',
#                 '<StateProperty: State A - Property b>'])
#        self.assertQuerysetEqual(
#                StateProperty.objects.filter(state_name="State A"),
#                ['<StateProperty: State A - Property a>',
#                 '<StateProperty: State A - Property b>'])
#
#    def test_create_two_properties_from_different_states(self):
#        #Create two properties in two different states.
#        StateProperty.objects.create(
#                state_name="State A",
#                property_name="Property a")
#        StateProperty.objects.create(
#                state_name="State B",
#                property_name="Property b")
#        # Al    l StateProperies
#        self.assertQuerysetEqual(
#                StateProperty.objects.all(),
#                ['<StateProperty: State A - Property a>',
#                 '<StateProperty: State B - Property b>'])
#        # Just those from State A
#        self.assertQuerysetEqual(
#                StateProperty.objects.filter(state_name="State A"),
#                ['<StateProperty: State A - Property a>'])
#        # Just those from State B
#        self.assertQuerysetEqual(
#                StateProperty.objects.filter(state_name="State B"),
#                ['<StateProperty: State B - Property b>'])
#
#
#
#
#
#class StatePropertyValueTests(TestCase):
#    def create_simulation(self):
#        test_user = User.objects.create_user(
#                'john', 'lennon@thebeatles.com', 'johnpassword')
#        WCModel.objects.create(name="Test WCModel", organism="Test organism")
#        test_model = WCModel.objects.get(pk=1)
#        test_model.add_option("Test option")
#        test_model.add_parameter("Test parameter")
#        test_model.add_process("Test process")
#        test_model.add_property("State A", "Property a")
#        test_model.add_property("State A", "Property b")
#
#        simulation = Simulation.objects.create_simulation(
#            "test_prop",
#            test_model,
#            UserProfile.objects.create(user=test_user))
#
#        return simulation   
#
#    def test_hdf5_state_created(self):
#        simulation = self.create_simulation()
#        f = h5py.File(simulation.get_path())
#
#        for p in simulation.statepropertyvalue_set.all():
#            print p.get_path()
#            self.assertEquals(p.get_path() in f, True)
#
#        f.flush()
#        f.close() 
#        os.remove(simulation.get_path())

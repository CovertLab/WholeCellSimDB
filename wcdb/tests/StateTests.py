from django.test import TestCase
from wcdb.models import *


import os
import h5py


class StateModelTests(TestCase):
    def sample_simulation(self, name="Sim", options={}, parameters={},
                          processes=[], state_properties={}):
        return Simulation.objects.create_simulation(
                    name=name,
                    organism = "E. coli",
                    batch = "First batch.",
                    description = "Description of the Simulation.",
                    replicate_index=1000,
                    ip="127.0.0.1",
                    length=10000.00,
                    options=options,
                    parameters=parameters,
                    processes=processes,
                    state_properties=state_properties)

    def test_objects_createstate(self):
        simulation = self.sample_simulation()
        state = State.objects.create_state("Test State", simulation)
        self.assertQuerysetEqual(
            State.objects.all(),
            ['<State: Sim - Test State>'])
        os.remove(simulation.file_path)

    def test_path(self):
        simulation = self.sample_simulation()
        state = State.objects.create_state("Test State", simulation)
        self.assertEqual(state.path, "/states/Test State")
        os.remove(simulation.file_path)

    def test_h5py_group_created(self):
        simulation = self.sample_simulation()
        state = State.objects.create_state("Test State", simulation)
        self.assertEqual(
            ("Test State" in simulation.h5file["states"]),
            True)
        os.remove(simulation.file_path)
 

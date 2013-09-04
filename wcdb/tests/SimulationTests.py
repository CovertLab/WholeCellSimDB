import os 
import numpy as np
from django.test import TestCase
from django.contrib.auth.models import User
from wcdb.models import *


class SimulationTests(TestCase):
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
        
    def test_create_simulation(self):
        sim = self.sample_simulation()
        self.assertQuerysetEqual(
            Simulation.objects.all(),
            ['<Simulation: Sim>'])
        os.remove(sim.file_path)

    # Check opp autocreated
    def test_opp_autocreated_and_dont_conflict_during_creation(self):
        sim = self.sample_simulation(
            parameters={"Parameter A": 0.0, "Parameter B":1.0},
            options={"Option A": "value a", "Option B": "value b"},
            processes=["Process 1", "Process 2"])

        self.assertQuerysetEqual(
            Parameter.objects.all(),
            ['<Parameter: Parameter B>',
             '<Parameter: Parameter A>'])

        self.assertQuerysetEqual(
             Option.objects.all(),
             ['<Option: Option B>', 
              '<Option: Option A>'])

        self.assertQuerysetEqual(
            Process.objects.all(),
            ['<Process: Process 1>', '<Process: Process 2>'])

        os.remove(sim.file_path)

    ##############################################################
    # State Properties
    ##############################################################
    # Autocreated?
    def test_1_state_1_property_autocreated(self):
        sim = self.sample_simulation(
            state_properties={"State A": { "Prop a": ((1,1,100),"=f8")}})
        self.assertQuerysetEqual(
            Property.objects.all(),
            ['<Property: Sim - State A - Prop a>'])
        os.remove(sim.file_path)

    def test_1_state_multi_property_autocreated(self):
        sim = self.sample_simulation(
            state_properties={"State A": { "Prop a": ((1,1,100), "=f8"),
                                           "Prop b": ((1,100), "=f8") }})
        self.assertQuerysetEqual(
            Property.objects.all(),
            ['<Property: Sim - State A - Prop a>',
            '<Property: Sim - State A - Prop b>'])
        os.remove(sim.file_path)
 
    def test_multi_state_multi_property_autocreated(self):
        sim = self.sample_simulation(
            state_properties={"State A": { "Prop a": ((1,1,100),"=f8"),
                                           "Prop b": ((1,100),"=f8") },
                              "State B": { "Prop c": ((4,5,100),"=f8")}})
        self.assertQuerysetEqual(
            Property.objects.all(),
            ['<Property: Sim - State A - Prop a>',
            '<Property: Sim - State A - Prop b>',
            '<Property: Sim - State B - Prop c>'])
        os.remove(sim.file_path)

    #### Methods ####
    def test_hdf5_file_created(self):
        sim = self.sample_simulation(
            state_properties={"State A": { "Prop a": ((1,1,100),"=f8"),
                                           "Prop b": ((1,100),"=f8") },
                              "State B": { "Prop c": ((4,5,100),"=f8")}})
        file_exists = True
        if os.path.exists(sim.file_path):
            os.remove(sim.file_path)
        else: 
            file_exists = False
        self.assertEqual(file_exists, True)

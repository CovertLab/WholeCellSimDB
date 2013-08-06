HDF5_ROOT = "/home/nolan/hdf5"

import os 
import numpy
from django.test import TestCase
from django.contrib.auth.models import User
from wc.models import *


class SimulationTests(TestCase):
     def test_create_simulation(self):
         sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1")
         self.assertQuerysetEqual(
             Simulation.objects.all(),
             ['<Simulation: Sim 1>'])
         os.remove(sim._get_file_path())
 
     # Check opp autocreated.
     def test_parameter_autocreated(self):
          sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1",
             parameters={"Parameter A": 0.0, "Parameter B":1.0})
          self.assertQuerysetEqual(
              Parameter.objects.all(),
              [ '<Parameter: Parameter B = 1.0>',
              '<Parameter: Parameter A = 0.0>'])
          os.remove(sim._get_file_path())
 
     def test_option_autocreated(self):
         sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1",
             options={"Option A": "value a", "Option B": "value b"})
         self.assertQuerysetEqual(
              Option.objects.all(),
              ['<Option: Option B = value b>', 
               '<Option: Option A = value a>'])
         os.remove(sim._get_file_path())
 
     def test_processes_autocreated(self):
         sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1",
             processes=["Process 1", "Process 2"])
         self.assertQuerysetEqual(
             Process.objects.all(),
             ['<Process: Process 1>', '<Process: Process 2>'])
         os.remove(sim._get_file_path())
  
     # Set OPP
     def test_set_option(self):
          sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1",
             options={'Option A': 'first'})
          self.assertQuerysetEqual(
             Option.objects.all(),
             ['<Option: Option A = first>'])
          sim.set_option("Option A", "second")
          self.assertQuerysetEqual(
             Option.objects.all(),
             ['<Option: Option A = first>',
              '<Option: Option A = second>'])
          self.assertQuerysetEqual(
             sim.options.all(),
             ['<Option: Option A = second>'])
          os.remove(sim._get_file_path())
 
     def test_set_option_that_doesnt_exist(self):
          sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1")
          self.assertQuerysetEqual(Option.objects.all(), [])
          sim.set_option("Option A", "first")
          self.assertQuerysetEqual(sim.options.all(), [])
          self.assertQuerysetEqual(
             Option.objects.all(),
             ['<Option: Option A = first>'])
          os.remove(sim._get_file_path())
  
     def test_set_parameter(self):
         sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1",
          parameters={'Parameter A': 1.0})
         self.assertQuerysetEqual(
          Parameter.objects.all(),
          ['<Parameter: Parameter A = 1.0>'])
 
         sim.set_parameter("Parameter A", 2.0)
 
         self.assertQuerysetEqual(
           Parameter.objects.all(),
           ['<Parameter: Parameter A = 1.0>',
            '<Parameter: Parameter A = 2.0>'])
         self.assertQuerysetEqual(
           sim.parameters.all(),
           ['<Parameter: Parameter A = 2.0>'])
         os.remove(sim._get_file_path())
  
     def test_set_parameter_that_doesnt_exist(self):
         sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1")
         self.assertQuerysetEqual(Parameter.objects.all(), [])
         sim.set_parameter("Parameter A", 1.0)
         self.assertQuerysetEqual(sim.parameters.all(), [])
         self.assertQuerysetEqual(
          Parameter.objects.all(),
          ['<Parameter: Parameter A = 1.0>'])
         os.remove(sim._get_file_path())
 
     # get_opp()
     def test_get_option(self):
         sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1",
             options={'Option A': 'first'})
         o = Option.objects.all()[0]
         self.assertEqual(o, sim.get_option("Option A"))
         os.remove(sim._get_file_path())
 
     def test_get_option_after_changing_value(self):
         sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1",
             options={'Option A': 'first'})
         sim.set_option("Option A", "second")
         o = Option.objects.filter(name="Option A", value="second")[0]
         self.assertEqual(o, sim.get_option("Option A"))
         os.remove(sim._get_file_path())
 
     def test_get_parameter(self):
         sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1",
             parameters={'Parameter A': 1.0})
         o = Parameter.objects.all()[0]
         self.assertEqual(o, sim.get_parameter('Parameter A'))
         os.remove(sim._get_file_path())
 
     def test_get_parameter_after_changing_value(self):
         sim = Simulation.objects.create_simulation('Sim 1', 'Mg', 'Mg1',
             parameters={'Parameter A': 1.0})
         sim.set_parameter('Parameter A', 2.0)
         o = Parameter.objects.filter(name='Parameter A', value=2.0)[0]
         self.assertEqual(o, sim.get_parameter('Parameter A'))
         os.remove(sim._get_file_path())
 
     def test_get_process(self):
         sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1",
             processes=['Process A'])
         o = Process.objects.all()[0]
         self.assertEqual(o, sim.get_process('Process A'))
         os.remove(sim._get_file_path())
 
     ##############################################################
     # State Properties
     ##############################################################
     # Autocreated?
     def test_1_state_1_property_autocreated(self):
         sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1",
             state_properties={"State A": { "Prop a": ("=f8", (1,1,100))}})
         self.assertQuerysetEqual(
             StateProperty.objects.all(),
             ['<StateProperty: Sim 1 - State A - Prop a>'])
         os.remove(sim._get_file_path())
 
     def test_1_state_multi_property_autocreated(self):
         sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1",
             state_properties={"State A": { "Prop a": ("=f8", (1,1,100)),
                                            "Prop b": ("=f8", (1,100)) }})
         self.assertQuerysetEqual(
             StateProperty.objects.all(),
             ['<StateProperty: Sim 1 - State A - Prop a>',
             '<StateProperty: Sim 1 - State A - Prop b>'])
         os.remove(sim._get_file_path())
  
     def test_multi_state_multi_property_autocreated(self):
         sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1",
             state_properties={"State A": { "Prop a": ("=f8", (1,1,100)),
                                            "Prop b": ("=f8", (1,100)) },
                               "State B": { "Prop c": ("=f8", (4,5,100))}})
         self.assertQuerysetEqual(
             StateProperty.objects.all(),
             ['<StateProperty: Sim 1 - State A - Prop a>',
             '<StateProperty: Sim 1 - State A - Prop b>',
             '<StateProperty: Sim 1 - State B - Prop c>'])
         os.remove(sim._get_file_path())
 
     #### Methods ####
     def test_get_state(self):
         sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1",
             state_properties={"State A": { "Prop a": ("=f8", (1,1,100)),
                                            "Prop b": ("=f8", (1,100)) },
                               "State B": { "Prop c": ("=f8", (4,5,100))}})
         self.assertQuerysetEqual(
             sim.get_state("State A"),
             ['<StateProperty: Sim 1 - State A - Prop a>',
             '<StateProperty: Sim 1 - State A - Prop b>'])
         os.remove(sim._get_file_path())
 
     def test_add_state(self):
         sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1")
         # Finish this later. 
         os.remove(sim._get_file_path())
 
     def test_get_state(self):
         sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1",
             state_properties={"State A": { "Prop a": ("=f8", (1,1,100)),
                                            "Prop b": ("=f8", (1,100)) },
                               "State B": { "Prop c": ("=f8", (4,5,100))}})
         self.assertEqual(
             sim.get_property("State A", "Prop a"), 
             StateProperty.objects.get(state_name="State A", 
                                         property_name="Prop a"))
         os.remove(sim._get_file_path())
 
     
     def test_hdf5_file_created(self):
         sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1",
             state_properties={"State A": { "Prop a": ("=f8", (1,1,100)),
                                            "Prop b": ("=f8", (1,100)) },
                               "State B": { "Prop c": ("=f8", (4,5,100))}})
         file_exists = True
         if os.path.exists(sim._get_file_path()):
             os.remove(sim._get_file_path())
         else: 
             file_exists = False
         self.assertEqual(file_exists, True)
 
    # Adding to Datasets
#    def test_get_state(self):
#        sim = Simulation.objects.create_simulation("Sim 1", "Mg", "Mg1",
#            state_properties={"State A": { "Prop a": ("=f8", (2,4,100))}})
#       
#        _WIN_ = 10 
#
#        for t in [ x*_WIN_ + _WIN_ for x in range(10)]:
#          data = numpy.random.randint(2,4,_WIN_-1)
#          sim.get_property('State A', 'Prop a').dataset()[2,4,t-_WIN_:t] = data
#          sim.get_file().flush()           


            

        

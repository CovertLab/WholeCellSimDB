from wcdb.wcloaders import WCMatLoader
from wcdb.models import *
import re
import numpy


class PropertyValuesManager(models.Manager):
    def create_property_value(self, simulation, property):
        """
        Creates a new relationship between a Simulation
        and a Property. It also creates the HDF5 dataset
        in the simulations file.
        """
        sps = self.create(simulation=simulation, property=property)
        print "%s shape %s" % (sps.property.name, property.shape)
        shape_l = tuple(int(v) for v in re.findall("[0-9]+", property.shape))
        maxshape = shape_l[:-1] + (None,)
        print maxshape

        f = sps.h5file()  # Get the simulation h5 file

        f.create_dataset(sps.path,
                         shape=shape_l,
                         maxshape=maxshape)

        # Make sure it's saved and closed.
        f.flush()
        f.close()

        return sps 


class SimulationManager(models.Manager):
    def create_simulation_from_mat(self, sim_dir, batch, index, length=30000):
        from wcdb.models import Property, PropertyValue, Process, State
        sim = self.create(batch=batch, batch_index=index, length=length,
                          organism_version=batch.organism_version)
        ov = sim.organism_version
        properties = Property.objects.filter(state__organism_version=ov)
        options_dict = WCMatLoader.options(sim_dir)
        parameters_dict = WCMatLoader.parameters(sim_dir)

        for property in properties:
            PropertyValue.objects.create_property_value(property=property,
                                                        simulation=sim)

        # Option Relations
        for tn, to in options_dict.iteritems():
            if tn == "processes":
                for pn, po in to.iteritems():
                    p = Process.objects.get(name=pn, organism_version=ov)
                    self.create_simulation_options_relations(sim, p, po)
            elif tn == "state":
                for pn, po in to.iteritems():
                    s = State.objects.get(name=pn, organism_version=ov)
                    self.create_simulation_options_relations(sim, s, po)
            elif re.match(r"^__.+?__$", tn):
                simulation_options = to
                self.create_simulation_options_relations(sim, sim,
                                                         simulation_options)

        #Parameter Relations
        for tn, to in parameters_dict.iteritems():
            if tn == "processes":
                for pn, po in to.iteritems():
                    p = Process.objects.get(name=pn, organism_version=ov)
                    self.create_simulation_parameters_relations(sim, p, po)
            elif tn == "state":
                for pn, po in to.iteritems():
                    s = State.objects.get(name=pn, organism_version=ov)
                    self.create_simulation_parameters_relations(sim, s, po)
            elif re.match(r"^__.+?__$", tn):
                simulation_options = to
                self.create_simulation_parameters_relations(sim, sim,
                                                            simulation_options)

        # Properties Values

    def create_simulation_from_json(self):
        pass

    @staticmethod
    def create_simulation_options_relations(sim, target, d):
        from wcdb.models import Option, OptionGroup, SimulationsOptions
        for k, v in d.iteritems():
            # If the targets value is a dict then the target must be
            # an option group (see OrganismVersionManager)
            if type(v) == dict:
                # Find the organism version with the name k
                # pointing to the previous target and parse it.
                og = OptionGroup.objects.get(name=k, target=target)
                SimulationManager.create_simulation_options_relations(sim, og, v)
            # If the targets value is a list then the target is an
            # option with multiple indices, so loop through and add them.
            elif type(v) == list:
                o = Option.objects.get(name=k, target=target)
                for index in range(len(v)):
                    SimulationsOptions.objects.create(option=o,
                                                      simulation=sim,
                                                      index=index+1,
                                                      value=v[index])
            # If the targets value is not a dict, list, or tuple,
            # the target is an option with a single value
            else:
                o = Option.objects.get(name=k, target=target)
                SimulationsOptions.objects.create(option=o,
                                                  simulation=sim,
                                                  value=v)

    @staticmethod
    def create_simulation_parameters_relations(sim, target, d):
        from wcdb.models import Parameter, ParameterGroup, SimulationsParameters
        for k, v in d.iteritems():
            # If the targets value is a dict then the target must be
            # an option group (see OrganismVersionManager)
            if type(v) == dict:
                # Find the organism version with the name k
                # pointing to the previous target and parse it.
                pg = ParameterGroup.objects.get(name=k, target=target)
                SimulationManager.create_simulation_parameters_relations(sim, pg, v)
            # If the targets value is a list then the target is an
            # option with multiple indices, so loop through and add them.
            elif type(v) == list:
                p = Parameter.objects.get(name=k, target=target)
                for index in range(len(v)):
                    SimulationsParameters.objects.create(parameter=p,
                                                         simulation=sim,
                                                         index=index+1,
                                                         value=v[index])
            # If the targets value is not a dict, list, or tuple,
            # the target is an option with a single value
            else:
                print "VALUE = %s" % v
                p = Parameter.objects.get(name=k, target=target)
                SimulationsParameters.objects.create(parameter=p,
                                                     simulation=sim,
                                                     value=v)


class SimulationBatchManager(models.Manager):
    def create_simulation_batch_from_mat(self, name, description,
                                         organism_version, investigator,
                                         ip, batch_dir):
        b = self.create(name=name, description=description,
                        organism_version=organism_version,
                        investigator=investigator,
                        ip=ip)

        first_sim_dir = batch_dir + '/1'
        from wcdb.models import Simulation
        Simulation.objects.create_simulation_from_mat(first_sim_dir, b, 1)

        #    sim_dirs = glob.glob(batch_dir + "/[0-9]*")
        #    for sim_dir in sim_dirs:
        #        batch_index = int(float(re.split("/", sim_dir).pop()))
        #
        #        print "Saving simulation %d of %d ... " % (batch_index, len(sim_dirs))
        #        save_simulation(organism_name, name, batch_index, sim_dir)

    def create_simulation_batch_from_json(self):
        pass


class OrganismVersionManager(models.Manager):
    def create_organism_version(self, organism_name, version, options,
                                parameters, processes, state_properties):
        from wcdb.models import Organism, OrganismVersion, State, Process
        o = Organism.objects.get_or_create(name=organism_name)[0]
        ov = OrganismVersion.objects.create(organism=o, version=version)
        OrganismVersionManager.create_state_properties_from_dict(ov, state_properties)
        OrganismVersionManager.create_processes_from_list(ov, processes)

        # Options
        for tn, to in options.iteritems():
            if tn == "processes":
                for pn, po in to.iteritems():
                    if pn in processes:
                        p = Process.objects.get(name=pn, organism_version=ov)
                        self.create_options_from_dict(p, po)
            elif tn == "state":
                for pn, po in to.iteritems():
                    state = State.objects.get(name=pn, organism_version=ov)
                    self.create_options_from_dict(state, po)
            elif re.match(r"^__.+?__$", tn):
                simulation_options = to
                self.create_options_from_dict(ov, simulation_options)

        for tn, to in parameters.iteritems():
            if tn == "processes":
                for pn, po in to.iteritems():
                    if pn in processes:
                        p = Process.objects.get(name=pn, organism_version=ov)
                        self.create_parameters_from_dict(p, po)
            elif tn == "state":
                for pn, po in to.iteritems():
                    state = State.objects.get(name=pn, organism_version=ov)
                    self.create_parameters_from_dict(state, po)
            elif re.match(r"^__.+?__$", tn):
                simulation_options = to
                self.create_parameters_from_dict(ov, simulation_options)

    def create_organism_version_from_mat(self, organism_name,
                                         organism_version, dir):
        options = WCMatLoader.options(dir)
        parameters = WCMatLoader.parameters(dir)
        processes = WCMatLoader.processes(dir)
        state_properties = WCMatLoader.state_properties(dir)
        self.create_organism_version(organism_name, organism_version, options, parameters, processes, state_properties)

    def create_organism_version_from_json(self, json_description):
        pass

    @staticmethod
    def create_state_properties_from_dict(ov, state_properties):
        """
        "states_properties": {
            "state_name": {
                "units": "unit type",
                "properties": {
                    "property_name": {
                        "dimensions": [d0, d1, ..., dn],
                        "dtype": "dtype",
                        "labels": [
                            "labelset_name_for_dim0",
                            "labelset_name_for_dim1",
                            ...
                        ]
                    },
            },
        },
        """

        # First keys are state names, with the values
        # being the state descriptions.
        from wcdb.models import State, Property, LabelSet, PropertyLabelSets
        for state_name, state_description in state_properties.iteritems():
#           THE WAY IT SHOULD BE
#            state = State.objects.create(name=state_name,
#                                         units=state_description['units'],
#                                         organism_version=ov)
#            print "\tCreated state: %s" % state
#
#            for p_name, p_description in sate_description['properties']:

            # This is just because the mat files don't work have the units.
            state = State.objects.get_or_create(name=state_name,
                                                units="",
                                                organism_version=ov)[0]
            for p_name, p_description in state_description.iteritems():
                #shape = p_description['shape']
                shape = p_description[1]
                #dtype = p_description['dtype']
                dtype = p_description[0]
                #labelsets = p_description['labelsets']
                labelsets = ['']
                prop = Property.objects.get_or_create(state=state,
                                                      name=p_name,
                                                      shape=shape,
                                                      dtype=dtype)[0]
#                for dim in range(len(labelsets)):
#                    name = labelsets[dim]
#                    ls = LabelSet.objects.get(name=name, organism_version=ov)
#                    PropertyLabelSets.objects.create(label_set=ls, property=prop, dimension=dim)
#                    print "\tProperty %s has labelset %s at index %i" % (prop, ls, dim)

    @staticmethod
    def create_processes_from_list(organism_version, process_list):
        for process_name in process_list:
            from wcdb.models import Process
            Process.objects.create(name=process_name, organism_version=organism_version)
        

    @staticmethod
    def create_options_from_dict(target, d):
        from wcdb.models import OptionGroup, Option
        for k, v in d.iteritems():
            if type(v) == dict:
                og = OptionGroup.objects.create(name=k, target=target)
                OrganismVersionManager.create_options_from_dict(og, v)
            else:
                Option.objects.create(name=k, target=target)

    @staticmethod
    def create_parameters_from_dict(target, d):
        from wcdb.models import ParameterGroup, Parameter
        for k, v in d.iteritems():
            if type(v) == dict:
                og = ParameterGroup.objects.create(name=k, target=target)
                OrganismVersionManager.create_parameters_from_dict(og, v)
            else:
                Parameter.objects.create(name=k, target=target)





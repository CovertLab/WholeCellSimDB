from wcdb.models import *
from wcdb.wcloaders import WCMatLoader


class PropertyValuesManager(models.Manager):
    def create_property_value(self, simulation, property):
        """
        Creates a new relationship between a Simulation
        and a Property. It also creates the HDF5 dataset
        in the simulations file.
        """

        sps = self.create(simulation=simulation, property=property)
        maxshape = property.shape[:-1] + (None,)

        f = sps.h5file  # Get the simulation h5 file

        # Create the dataset in the simulation h5 file
        f.create_dataset(sps.path,
                         shape=property.shape,
                         dtype=property.dtype,
                         maxshape=maxshape)

        # Make sure it's saved and closed.
        f.flush()
        f.close()

        return p_obj


class SimulationManager(models.Manager):
    def create_simulation_from_mat(self, sim_dir, batch, index, length=30000):
        sim = self.create(batch=batch, index=index, length=length,
                          organism_version=batch.organism_version)
        ov = sim.organism_version
        properties = Property.objects.filter(organism_version=ov)
        options_dict = WCMatLoader.options(sim_dir)
        parameters_dict = WCMatLoader.parameters(sim_dir)

        for property in properties:
            PropertyValue.objects.create_property_value(property=property,
                                                        simulation=sim)

        # Option Relations
        for tn, to in options_dict.iteritems():
            if tn == "processes":
                for pn, po in to:
                    p = Process.objects.get(name=pn, organism_version=ov)
                    self.create_simulation_options_relations(sim, p, po)
            elif tn == "state":
                for pn, po in to:
                    s = State.objects.get(name=pn, organism_version=ov)
                    self.create_simulation_options_relations(sim, s, po)
            elif re.match(r"^__.+?__$", tn):
                simulation_options = to
                self.create_simulation_options_relations(sim, sim,
                                                         simulation_options)

        #Parameter Relations
        for tn, to in parameters_dict.iteritems():
            if tn == "processes":
                for pn, po in to:
                    p = Process.objects.get(name=pn, organism_version=ov)
                    self.create_simulation_parameters_relations(sim, p, po)
            elif tn == "state":
                for pn, po in to:
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
                                                      index=index,
                                                      value=v[index])
            # If the targets value is not a dict, list, or tuple,
            # the target is an option with a single value
            else:
                o = Option.objects.get(name=k, target=target)
                SimulationsOptions.objects.create(option=o,
                                                  simulation=sim,
                                                  index=0,
                                                  value=v)

    @staticmethod
    def create_simulation_parameters_relations(sim, target, d):
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
                                                         index=index,
                                                         value=v[index])
            # If the targets value is not a dict, list, or tuple,
            # the target is an option with a single value
            else:
                p = Parameter.objects.get(name=k, target=target)
                SimulationsParameters.objects.create(parameter=p,
                                                     simulation=sim,
                                                     index=0,
                                                     value=v)


class SimulationBatchManager(models.Manager):
    def create_simulation_batch_from_mat(self, name, description,
                                         organism_version, investigator,
                                         ip, batch_dir):
        self.create(name=name, description=description,
                    organism_version=organism_version,
                    investigator=investigator,
                    ip=ip)

        first_sim_dir = batch_dir + '/1'
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
        # Organism
        from wcdb.models import Organism
        o = Organism.objects.get_or_create(name=organism_name)

        # Organism Version
        ov = self.create(o, version=version)

        # State Properties
        OrganismVersionManager.create_state_properties_from_dict(ov, state_properties)

        # Processes
        OrganismVersionManager.create_processes_from_dict(ov, processes)

        # Options
        for tn, to in options.iteritems():
            if tn == "processes":
                for pn, po in to:
                    p = Process.objects.get(name=pn, organism_version=ov)
                    self.create_options_from_dict(p, po)
            elif tn == "state":
                for pn, po in to:
                    state = State.objects.get(name=pn, organism_version=ov)
                    self.create_options_from_dict(state, po)
            elif re.match(r"^__.+?__$", tn):
                simulation_options = to
                self.create_options_from_dict(ov, simulation_options)

        for tn, to in parameters.iteritems():
            if tn == "processes":
                for pn, po in to:
                    p = Process.objects.get(name=pn, organism_version=ov)
                    self.create_parameters_from_dict(p, po)
            elif tn == "state":
                for pn, po in to:
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
    def create_state_properties_from_dict(self, ov, state_properties):
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
        for state_name, state_description in state_properties.iteritems():
            state = State.objects.create(name=state_name,
                                         units=state_description['units'],
                                         organism_version=ov)

            for p_name, p_description in sate_description['properties']:
                shape = p_description['shape']
                dtype = p_description['dtype']
                labelsets = p_description['labelsets']

                prop = Property.objects.create(state=state,
                                               name=p_name,
                                               shape=shape,
                                               dtype=dtype)

                for name in labelsets:
                    ls = LabelSet.objects.get(name=name, organism_version=ov)
                    PropertyLabelSets.objects.create(labelset=ls, property=prop)

    @staticmethod
    def create_processes_from_dict(self, organism, dict):
        pass

    @staticmethod
    def create_options_from_dict(target, d):
        for k, v in d.iteritems():
            if type(v) == dict:
                og = OptionGroup.objects.create(name=k, target=target)
                OrganismVersionManager.create_options_from_dict(og, v)
            else:
                Option.objects.create(name=k, target=target)

    @staticmethod
    def create_parameters_from_dict(target, d):
        for k, v in d.iteritems():
            if type(v) == dict:
                og = ParameterGroup.objects.create(name=k, target=target)
                OrganismVersionManager.create_parameters_from_dict(og, v)
            else:
                Parameter.objects.create(name=k, target=target)





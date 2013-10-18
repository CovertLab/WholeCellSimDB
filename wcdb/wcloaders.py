from wcdb.models import *
import glob
import scipy.io
import numpy

class WCMatLoader:
    @staticmethod
    def complete_property_data(simulation, simulation_dir):
        """
        WCMatLoader.complete_property_data(simulation, simulation_dir)

        This method finds all state-property files in simulation_dir and
        loads their data into the database. It is intended to be used to
        load simulation data that is complete.
        """
        property_files = glob.glob(simulation_dir + \
                                   "/state-[a-zA-Z]*-[a-zA-Z]*.mat")

        #save property values data
        for prop_file in property_files:
            state_name = prop_file.split("-")[1]
            prop_name = prop_file.replace(".", "-").split("-")[2]

            try:
                property_mat_dict = scipy.io.loadmat(prop_file)

                if "data" in mat_dict.keys():
                    # Get the property.
                    s_obj = simulation.organism_version.states.get(
                                                        name=state_name)
                    try:
                        # Try to find that property.
                        p_obj = s_obj.properties.get(name=prop_name)

                        # Create the property value.
                        sims_prop = PropertyValue.objects.get_or_create(
                            property=p_obj,
                            simulation=simulation
                        )

                        # Get the data.
                        data = property_mat_dict['data']

                        # Add teh data to the property.
                        sims_prop.add_data(data)
                    except:
                        pass
            except:
                pass

    @staticmethod
    def state_properties(sample_dir):
        print "Class: WCMatLoader\tMethod: state_properties"
        property_files = glob.glob(sample_dir + \
                                   "/state-[a-zA-Z]*-[a-zA-Z]*.mat")

        state_properties = {}
        print "\tBegin..."
        for prop_file in property_files:
            state = prop_file.split("-")[1]  # State name
            print "\tState: %s" % state
            prop = prop_file.replace(".", "-").split("-")[2]  # Property name
            print "\tState: %s" % prop
            try:
                print "\t\tLoading mat..."
                mat_dict = scipy.io.loadmat(prop_file)
                print "\t\tdone."
                if "data" in mat_dict.keys():
                    data = mat_dict['data']
                    label_sets = [""]
                    d_list = [data.dtype, data.shape, label_sets]
                    # Weird syntax. Just constructing the state_property dict.
                    state_properties.setdefault(state, {}).setdefault(prop,
                                                                      d_list)

            except SystemError: #TODO: handle errors
                pass
            except MemoryError: #TODO: handle errors
                pass

        return state_properties

    @staticmethod
    def options(sample_dir):
        """
        Returns a nested dictionary containing options
        groups and their options.
        """
        return WCMatLoader._load_dict(sample_dir + "/options.mat")

    @staticmethod
    def parameters(sample_dir):
        """
        Returns a nested dictionary containing parameter
        groups and their parameters
        """
        return WCMatLoader._load_dict(sample_dir + "/parameters.mat")

    @staticmethod
    def processes(sample_dir):
        """
        Returns a list of processes names.
        """
        return WCMatLoader.options(sample_dir)['processes'].keys()

    @staticmethod
    def _load_dict(filename, throw_error_on_unknown_data_format=True):
        data = scipy.io.loadmat(filename, struct_as_record=False)
        dict = {}
        for key in data:
            if isinstance(data[key], numpy.ndarray):
                # If 2 layers deep is the matlab struct
                if len(data[key]) == 1 \
                and isinstance(data[key][0], numpy.ndarray) \
                and len(data[key][0]) == 1 \
                and isinstance(data[key][0][0],
                               scipy.io.matlab.mio5_params.mat_struct):
                    # Normalize the matlab struct.
                    dict[key] = WCMatLoader._normalize(data[key][0][0],
                                           throw_error_on_unknown_data_format)
                # Else if it's one dimension and the value is a unicode.
                elif data[key].ndim == 1 \
                and isinstance(data[key][0], numpy.unicode_):
                    # Make it a list
                    dict[key] = data[key].tolist()[0]
                # This appears to be the third way this can be things.
                elif data[key].ndim == 2 \
                and data[key].shape[0] == 1 \
                and data[key].shape[1] == 1:
                    dict[key] = data[key].tolist()[0][0]
        return dict

    @staticmethod
    def _normalize(mat_obj, throw_error_on_unknown_data_format):
        '''
        A recursive function which constructs nested
        dictionary from matobject.
        '''
        dict = {}
        for strg in mat_obj._fieldnames:
            elem = mat_obj.__dict__[strg]
            if isinstance(elem, numpy.ndarray) and len(elem) == 1 and \
               isinstance(elem[0], numpy.ndarray) and len(elem[0]) == 1 and \
               isinstance(elem[0][0], scipy.io.matlab.mio5_params.mat_struct):
                dict[strg] = WCMatLoader._normalize(elem[0][0], throw_error_on_unknown_data_format)
            else:
                if elem.ndim == 1 and isinstance(elem[0], numpy.unicode_):
                    dict[strg] = elem.tolist()[0]
                elif elem.ndim == 2 and elem.shape[0] == 1 and elem.shape[1] == 1:
                    dict[strg] = elem.tolist()[0][0]
                elif elem.ndim == 2 and elem.shape[0] == 1:
                    dict[strg] = elem.tolist()[0]
                elif elem.ndim == 2 and elem.shape[1] == 1:
                    dict[strg] = [x[0] for x in elem.tolist()]
                elif elem.ndim == 2 and elem.shape[0] == 0 and elem.shape[1] == 0:
                    dict[strg] = None
                elif throw_error_on_unknown_data_format:
                    raise Exception('Invalid data')
                else:
                    dict[strg] = elem

        return dict


class WCJsonLoader():
    """
    NOT IMPLEMENTED

    This class will have the same public methods as WCMatloader, and
    each of these methods will return data in the same structure.

    They should probably be inheriting from the same class.
    Maybe that class should be an Abstract Base Class.
    """
    pass

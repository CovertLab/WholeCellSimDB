from django.test import TestCase

import os
import h5py

import wc.models as wcm

HDF5_ROOT = "/home/nolan/wcdb/hdf5"

class WCModelTests(TestCase):
    def test_creating_a_wcmodel(self):
        # Create a test model.
        wcmodel = wcm.WCModel.objects.create(name="test")
        self.assertQuerysetEqual(
                wcm.WCModel.objects.all(),
                ['<WCModel: test>'])
        # Check to see if an HDF5 has been created.
        file_path = "/".join([HDF5_ROOT, "model_test.h5"])
        file_exists = True
        try:
            with open(file_path): pass
        except IOError:
            file_exists = False 

        self.assertEqual(file_exists, True)
        # Delete the file if it was created.
        os.remove(file_path)
    
    def test_adding_a_process(self):
        wcmodel = wcm.WCModel.objects.create(name="test model")
        process = wcm.Process.objects.create(name="test process")
        wcmodel.processes.add(process)

        file_path = "/".join([HDF5_ROOT, "test_model.h5"])
        os.remove(file_path)


        

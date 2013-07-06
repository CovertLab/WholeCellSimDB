from django.test import TestCase

from wc.models.models import Parameter, Option, Process, StateProperty
from wc.models.wcmodel import WCModel



class WCModelTests(TestCase):
    def test_create_empty_model(self):
        WCModel.objects.create(name="Test WCModel", organism="Test organism")
        self.assertQuerysetEqual(
                WCModel.objects.all(),
                ['<WCModel: Test WCModel, Test organism>'])

    def test_add_parameter(self):
        WCModel.objects.create(name="Test WCModel", organism="Test organism")
        test_model = WCModel.objects.get(pk=1)
        test_model.parameters.add(name="Test Parameter")

    def test_add_option(self):
        WCModel.objects.create(name="Test WCModel", organism="Test organism")
        test_model = WCModel.objects.get(pk=1)
        test_model.options.add(name="Test Option")

    def test_add_process(self):
        WCModel.objects.create(name="Test WCModel", organism="Test organism")
        test_model = WCModel.objects.get(pk=1)
        test_model.processes.add(name="Test Process")

    def test_add_state_property(self):
        WCModel.objects.create(name="Test WCModel", organism="Test organism")
        test_model = WCModel.objects.get(pk=1)
        test_model.state_properties.add(name="Test StateProperty")



from django.test import TestCase
from wcdb.models import Parameter


class ParameterModelTests(TestCase):
    def test_create_parameter(self):
        Parameter.objects.create(name="Test Parameter", value=1)
        self.assertQuerysetEqual(
                Parameter.objects.all(),
                ['<Parameter: Test Parameter = 1.0>'])

    def test_create_two_different_parameters(self):
        Parameter.objects.create(name="Test Parameter", value=1.0)
        Parameter.objects.create(name="Test Parameter", value=2)
        self.assertQuerysetEqual(
                Parameter.objects.all(),
                ['<Parameter: Test Parameter = 1.0>', 
                 '<Parameter: Test Parameter = 2.0>'])

    def test_create_two_identical_parameters(self):
        Parameter.objects.create(name="Test 1.0", value=1.0)
        Parameter.objects.get_or_create(name="Test 1.0", value = 1.0)
        self.assertQuerysetEqual(
                Parameter.objects.all(),
                ['<Parameter: Test 1.0 = 1.0>'])

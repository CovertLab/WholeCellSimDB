from django.test import TestCase
from wcdb.models import Parameter


class ParameterModelTests(TestCase):
    def test_create_parameter(self):
        Parameter.objects.create(name="Test Parameter")
        self.assertQuerysetEqual(
                Parameter.objects.all(),
                ['<Parameter: Test Parameter>'])

    def test_create_two_different_parameters(self):
        Parameter.objects.create(name="Test Parameter")
        Parameter.objects.create(name="Test Parameter")
        self.assertQuerysetEqual(
                Parameter.objects.all(),
                ['<Parameter: Test Parameter>',
                 '<Parameter: Test Parameter>'])

    def test_create_two_identical_parameters(self):
        Parameter.objects.create(name="Test 1.0")
        Parameter.objects.get_or_create(name="Test 1.0")
        self.assertQuerysetEqual(
                Parameter.objects.all(),
                ['<Parameter: Test 1.0>'])

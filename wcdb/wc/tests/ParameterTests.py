from django.test import TestCase
from wc.models.models import Parameter


class ParameterModelTests(TestCase):
    def test_create_parameter(self):
        Parameter.objects.create(name="Test 1")
        self.assertQuerysetEqual(
                Parameter.objects.all(),
                ['<Parameter: Test 1>'])

    def test_create_two_different_parameters(self):
        Parameter.objects.create(name="Test 1")
        Parameter.objects.create(name="Test 2")
        self.assertQuerysetEqual(
                Parameter.objects.all(),
                ['<Parameter: Test 1>', '<Parameter: Test 2>'])

    def test_create_two_identical_parameters(self):
        Parameter.objects.create(name="Test 1")
        Parameter.objects.get_or_create(name="Test 1")
        self.assertQuerysetEqual(
                Parameter.objects.all(),
                ['<Parameter: Test 1>'])

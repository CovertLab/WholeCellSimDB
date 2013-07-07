from django.test import TestCase
from wc.models.models import Parameter, ParameterValue


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



class ParameterValueModelTests(TestCase):
    def test_create_parametervalue(self):
        test_param = Parameter.objects.create(name="Parameter 1")
        ParameterValue.objects.create(parameter=test_param, value=1.0)
        self.assertQuerysetEqual(
                ParameterValue.objects.all(),
                ['<ParameterValue: Parameter 1 = 1.0>'])

    def test_create_two_values_for_same_parameter(self):
        test_param = Parameter.objects.create(name="Parameter 1")
        ParameterValue.objects.create(parameter=test_param, value=1.0)
        ParameterValue.objects.create(parameter=test_param, value=2.0)
        self.assertQuerysetEqual(
                ParameterValue.objects.all(),
                ['<ParameterValue: Parameter 1 = 1.0>',
                '<ParameterValue: Parameter 1 = 2.0>'])
   

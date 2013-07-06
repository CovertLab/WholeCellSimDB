from django.test import TestCase
from wc.models.models import Parameter, ParameterValue


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
   

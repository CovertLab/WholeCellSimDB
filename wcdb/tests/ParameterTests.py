from django.test import TestCase
from wcdb.models import Parameter, OPTarget, State, Process


class ParameterModelTests(TestCase):
   
    def test_create_option_with_OPTarget(self):
        target = OPTarget.objects.create(name="Test Target")
        Parameter.objects.create(name="Test 1", value="Value 1", index=1, target=target)
        self.assertQuerysetEqual(
                Parameter.objects.all(),
                ['<Parameter: Test Target - Test 1 = Value 1>'])

    def test_create_option_with_State(self):
        target = State.objects.create(name="Test Target")
        Parameter.objects.create(name="Test 1", value="Value 1", index=1, target=target)
        self.assertQuerysetEqual(
                Parameter.objects.all(),
                ['<Parameter: Test 1 - Value 1>'])

    def test_create_option_with_Process(self):
        target = Process.objects.create(name="Test Target")
        Parameter.objects.create(name="Test 1", value="Value 1", index=1, target=target)
        self.assertQuerysetEqual(
                Parameter.objects.all(),
                ['<Parameter: Test 1 - Value 1>'])


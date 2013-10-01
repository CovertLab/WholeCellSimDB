from django.test import TestCase
from wcdb.models import Option, OPTarget, State, Process


class OptionModelTests(TestCase):
   
    def test_create_option_with_OPTarget(self):
        target = OPTarget.objects.create(name="Test Target")
        Option.objects.create(name="Test 1", value="Value 1", index=1, target=target)
        self.assertQuerysetEqual(
                Option.objects.all(),
                ['<Option: Test Target - Test 1 = Value 1>'])

    def test_create_option_with_State(self):
        target = State.objects.create(name="Test Target")
        Option.objects.create(name="Test 1", value="Value 1", index=1, target=target)
        self.assertQuerysetEqual(
                Option.objects.all(),
                ['<Option: Test 1 - Value 1>'])

    def test_create_option_with_Process(self):
        target = Process.objects.create(name="Test Target")
        Option.objects.create(name="Test 1", value="Value 1", index=1, target=target)
        self.assertQuerysetEqual(
                Option.objects.all(),
                ['<Option: Test 1 - Value 1>'])


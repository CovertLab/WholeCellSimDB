from django.test import TestCase
from wc.models import Option


class OptionModelTests(TestCase):
    def test_create_option(self):
        Option.objects.create(name="Test 1", value="Value 1")
        self.assertQuerysetEqual(
                Option.objects.all(),
                ['<Option: Test 1 = Value 1>'])

    def test_create_two_different_options(self):
        Option.objects.create(name="Test 1", value="Value 1")
        Option.objects.create(name="Test 2", value="Value 2")
        self.assertQuerysetEqual(
                Option.objects.all(),
                ['<Option: Test 1 = Value 1>', '<Option: Test 2 = Value 2>'])

    def test_create_two_identical_options(self):
        Option.objects.create(name="Test 1", value="Value 1")
        Option.objects.get_or_create(name="Test 1", value="Value 1")
        self.assertQuerysetEqual(
                Option.objects.all(),
                ['<Option: Test 1 = Value 1>'])

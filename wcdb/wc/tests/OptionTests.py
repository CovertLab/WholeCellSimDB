from django.test import TestCase
#from wc.models.models import Option, OptionValue
from wc.models import Option, OptionValue


class OptionModelTests(TestCase):
    def test_create_option(self):
        Option.objects.create(name="Test 1")
        self.assertQuerysetEqual(
                Option.objects.all(),
                ['<Option: Test 1>'])

    def test_create_two_different_options(self):
        Option.objects.create(name="Test 1")
        Option.objects.create(name="Test 2")
        self.assertQuerysetEqual(
                Option.objects.all(),
                ['<Option: Test 1>', '<Option: Test 2>'])

    def test_create_two_identical_options(self):
        Option.objects.create(name="Test 1")
        Option.objects.get_or_create(name="Test 1")
        self.assertQuerysetEqual(
                Option.objects.all(),
                ['<Option: Test 1>'])


class OptionValueModelTests(TestCase):
    def test_create_optionvalue(self):
        test_option = Option.objects.create(name="Option 1")
        OptionValue.objects.create(option=test_option, value="1")
        self.assertQuerysetEqual(
                OptionValue.objects.all(),
                ['<OptionValue: Option 1 = 1>'])

    def test_create_two_values_for_same_option(self):
        test_option = Option.objects.create(name="Option 1")
        OptionValue.objects.create(option=test_option, value="1")
        OptionValue.objects.create(option=test_option, value="2")
        self.assertQuerysetEqual(
                OptionValue.objects.all(),
                ['<OptionValue: Option 1 = 1>',
                '<OptionValue: Option 1 = 2>'])

   

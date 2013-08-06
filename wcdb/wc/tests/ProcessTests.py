from django.test import TestCase
from wc.models import Process


class ProcessModelTests(TestCase):
    def test_create_process(self):
        Process.objects.create(name="Test 1")
        self.assertQuerysetEqual(
                Process.objects.all(),
                ['<Process: Test 1>'])

    def test_create_two_different_processs(self):
        Process.objects.create(name="Test 1")
        Process.objects.create(name="Test 2")
        self.assertQuerysetEqual(
                Process.objects.all(),
                ['<Process: Test 1>', '<Process: Test 2>'])

    def test_create_two_identical_processs(self):
        Process.objects.create(name="Test 1")
        Process.objects.get_or_create(name="Test 1")
        self.assertQuerysetEqual(
                Process.objects.all(),
                ['<Process: Test 1>'])

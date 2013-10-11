from django.test import TestCase
from wcdb.models import SimulationBatch, Organism, OrganismVersion, Investigator


class SimulationBatchTests(TestCase):
    def test_create_batch(self):
        o = Organism.objects.create(name="Organism")
        ov = OrganismVersion.objects.create(version_number="1.0", organism=o)
        i = Investigator.objects.create(affiliation="User")
        batch = SimulationBatch.objects.create(
                    name="Batch",
                    description="A test Simulation Batch.",
                    organism_version=ov,
                    investigator=i,
                    ip='0.0.0.0')

        self.assertQuerysetEqual(
            SimulationBatch.objects.all(),
            ['<SimulationBatch: Organism 1.0 - Batch>'])

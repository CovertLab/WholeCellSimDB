import sys
from wcdb.models import Investigator, SimulationBatch, OrganismVersion, Organism


def main():
    organism_name = sys.argv[1]
    organism_version = sys.argv[2]
    name = sys.argv[3]
    description = sys.argv[4]
    investigator_first = sys.argv[5]
    investigator_last = sys.argv[6]
    investigator_affiliation = sys.argv[7]
    investigator_email = sys.argv[8]
    ip = sys.argv[9]
    batch_dir = sys.argv[10]

    i = Investigator.objects.get_or_create(first_name=investigator_first,
                                           last_name=investigator_last,
                                           email=investigator_email,
                                           affiliation=investigator_affiliation)
    o = Organism.objects.get_or_create(name=organism_name)
    ovqs = OrganismVersion.objects.filter(version=organism_version,
                                          organism=o)
    if len(ovqs) == 0:
        OrganismVersion.objects.create_organism_version_from_mat(batch_dir + "/1")
    ov = ovqs[0]
    SimulationBatch.objects.create_simulation_batch_from_mat(name=name,
                                                             description=description,
                                                             organism_version=ov,
                                                             investigator=i,
                                                             ip=ip,
                                                             batch_dir=batch_dir)

if __name__ == "__main__":
    main()
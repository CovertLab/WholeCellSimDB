"""
> python loadmatbatch.py "M. genitalium" "r1" "Batch 1" "First batch in wcdb" "Jon" "Karr" "Stanford" "jrkarr@stanford.com" "128.41.235.12" "/home/nolan/Documents"
"""

import sys
from WholeCellDB import settings
from django.core.management import setup_environ

setup_environ(settings)

from wcdb.models import Investigator, SimulationBatch, OrganismVersion, Organism

def p(string):
    sys.stdout.write(string)

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

    p("Retrieving investigator...")
    i = Investigator.objects.get_or_create(first_name=investigator_first,
                                           last_name=investigator_last,
                                           email=investigator_email,
                                           affiliation=investigator_affiliation)[0]
    p("retrieved.\n")
    p("\tInvestigator: %s\n" % i.__unicode__())

    p("Retrieving organism...")
    o = Organism.objects.get_or_create(name=organism_name)[0]
    p("retrieved.\n")
    p("Organism: %s\n" % o.__unicode__())
    ovqs = OrganismVersion.objects.filter(version=organism_version,
                                          organism=o)
    if len(ovqs) == 0:
        p("Creating OrganismVersion...")
        OrganismVersion.objects.create_organism_version_from_mat(organism_name, organism_version, batch_dir + "/1")
        p("completed.")
    else:
        p("OrganismVersion already exists.\n")

    ovqs = OrganismVersion.objects.filter(version=organism_version,
                                          organism=o)
    ov = ovqs[0]
    print "Creating simulation batch from dir : %s" % batch_dir
    SimulationBatch.objects.create_simulation_batch_from_mat(name=name,
                                                             description=description,
                                                             organism_version=ov,
                                                             investigator=i,
                                                             ip=ip,
                                                             batch_dir=batch_dir)
    print "Batch saved!"

if __name__ == "__main__":
    main()

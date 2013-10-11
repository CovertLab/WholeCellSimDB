'''
Example: 
>> python wccli/save_simulation_batch.py \
    "Mycoplasma genitalium" \
    "r1" \
    "Test batch 1" \
    "Test batch #1 description" \
    "Jonathan" \
    "Karr" \
    "Stanford University" \
    "jkarr@alumni.stanford.edu" \
    "171.65.103.186" \
    "/home/nolan/"
'''

import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

from WholeCellDB import settings
from django.core.management import setup_environ
setup_environ(settings)

from _helpers import save_simulation_batch

def main():
    save_simulation_batch(
        organism_name = sys.argv[1],
        organism_version = sys.argv[2],
        name = sys.argv[3], 
        description = sys.argv[4], 
        investigator_first = sys.argv[5],
        investigator_last = sys.argv[6],
        investigator_affiliation = sys.argv[7],
        investigator_email = sys.argv[8],
        ip = sys.argv[9],
        batch_dir = sys.argv[10])

if __name__=="__main__":
    main()

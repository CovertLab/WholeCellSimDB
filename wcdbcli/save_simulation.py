'''
>> python wcdbcli/save_simulation.py \
    "Mycoplasma genitalium" \
    "Test batch 1" \
    "1" \
    "/home/projects/WholeCell/simulation/output/runSimulation/2011_10_19_02_53_45/1"
'''

import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

from WholeCellDB import settings
from django.core.management import setup_environ
setup_environ(settings)

from helpers import save_simulation

def main():
    save_simulation(
        organism_name = sys.argv[1],
        batch_name = sys.argv[2],
        batch_index = int(float(sys.argv[3])),
        sim_dir = sys.argv[4])    
    
if __name__=="__main__":
    main()

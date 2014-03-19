'''
Example: 
>> python wcdbcli/save_simulation_batch.py \
    "Mycoplasma genitalium" \
    "2011_10_19_02_53_45" \
    "/home/projects/WholeCell/simulation/output/runSimulation/2011_10_19_02_53_45" \
    "10" \
    "5"
'''

import datetime
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from WholeCellDB import settings
from django.core.management import setup_environ
setup_environ(settings)

from helpers import save_simulation_batch

def main():
    opts = {}
    if len(sys.argv) >= 5:
        opts['first_sim_idx'] = int(float(sys.argv[4]))
    if len(sys.argv) >= 6:
        opts['max_num_simulations'] = int(float(sys.argv[5]))
    if len(sys.argv) >= 7:
        opts['expand_sparse_mat'] = bool(float(sys.argv[6]))
    
    save_simulation_batch(
        organism_name = sys.argv[1], 
        batch_name = sys.argv[2], 
        batch_dir = sys.argv[3], 
        **opts
        )

if __name__=="__main__":
    main()

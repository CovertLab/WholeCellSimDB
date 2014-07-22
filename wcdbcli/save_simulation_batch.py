'''
Example: 
>> python wcdbcli/save_simulation_batch.py \
    -d /home/projects/WholeCell/simulation/output/runSimulation/2011_10_19_02_53_45 \
    -i 5 \
    -N 10    
'''

import argparse
import datetime
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from WholeCellDB import settings
from django.core.management import setup_environ
setup_environ(settings)

from helpers import save_simulation_batch

def main():
    parser = argparse.ArgumentParser(description='Save batch of simulations to database.')
    parser.add_argument('-d', metavar='batch-directory', help='Path to directory containing data and metadata for each simulation in the batch', required=True)
    parser.add_argument('-i', metavar='first-simulation-index', type=int, help='Index of first simulation to save to database')
    parser.add_argument('-N', metavar='max-number-simulations', type=int, help='Maximum number of simulations to save to database')    
    args = parser.parse_args()
    
    save_simulation_batch(
        batch_dir = args.d,
        first_sim_idx = args.i,
        max_num_simulations = args.N
        )

if __name__=="__main__":
    main()

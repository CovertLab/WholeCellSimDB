'''
Example: 
>> python wcdbcli/save_simulation_batch.py \
    -d /home/projects/WholeCell/simulation/output/runSimulation/2011_10_19_02_53_45 \
    -m /home/projects/WholeCell/simulation/output/runSimulation/2011_10_19_02_53_45/metadata.sedml.xml \
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
    parser.add_argument('-d', metavar='batch-directory', help='Path to directory containing HDF5 files containing data for each simulation in the batch', required=True)
    parser.add_argument('-m', metavar='metadata-file', help='Path to SED-ML XML file containing simulation batch metadata. If metadata file not specified, the program tries to read metadata from the HDF5 files.')
    parser.add_argument('-i', metavar='first-simulation-index', type=int, default=1, help='Index of first simulation to save to database.')
    parser.add_argument('-N', metavar='max-number-simulations', type=int, help='Maximum number of simulations to save to database.')
    args = parser.parse_args()
    
    batch_dir = args.d
    first_sim_idx = args.i
    max_num_simulations = args.N
    
    if args.m is not None:
        metadata_file = args.m
    else:
        metadata_file = os.path.join(batch_dir, '%d.h5' % first_sim_idx)
    
    save_simulation_batch(
        batch_dir = batch_dir,
        metadata_file = metadata_file,
        first_sim_idx = first_sim_idx,
        max_num_simulations = max_num_simulations
        )

if __name__=="__main__":
    main()

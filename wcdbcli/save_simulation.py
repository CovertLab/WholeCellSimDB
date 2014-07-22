'''
>> python wcdbcli/save_simulation.py \
    -d /home/projects/WholeCell/simulation/output/runSimulation/2011_10_19_02_53_45/1.h5
'''

import argparse
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from WholeCellDB import settings
from django.core.management import setup_environ
setup_environ(settings)

from helpers import save_simulation

def main():
    parser = argparse.ArgumentParser(description='Save simulation to database.')
    parser.add_argument('-d', metavar='data-file', help='Path to HDF5 file containing simulation data', required=True)
    args = parser.parse_args()
        
    save_simulation(data_file_h5=args.d)
    
if __name__=="__main__":
    main()

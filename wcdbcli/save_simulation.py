'''
>> python wcdbcli/save_simulation.py \
    "/home/projects/WholeCell/simulation/output/runSimulation/2011_10_19_02_53_45/1.h5" 
'''

import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from WholeCellDB import settings
from django.core.management import setup_environ
setup_environ(settings)

from helpers import save_simulation

def main():
    save_simulation(sim_file = sys.argv[1])
    
if __name__=="__main__":
    main()

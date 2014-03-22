import glob
import os
from wcdb.models import SimulationBatch, Simulation

def save_simulation_batch(batch_dir, first_sim_idx = None, max_num_simulations = None):
    if first_sim_idx is None:
        first_sim_idx = 1
    
    #save batch
    SimulationBatch.objects.create_simulation_batch(os.path.join(batch_dir, '%d' % first_sim_idx, 'data.h5'))
        
    #save simulations
    sim_dirs = glob.glob(os.path.join(batch_dir, "[0-9]*"))
    sim_dirs = sim_dirs[first_sim_idx-1:]
    if max_num_simulations is not None:
        sim_dirs = sim_dirs[:max_num_simulations]
    
    for sim_idx, sim_dir in enumerate(sim_dirs):
        print "Saving simulation %d of %d ... " % (sim_idx+1, len(sim_dirs))
        save_simulation(sim_dir)

def save_simulation(sim_dir):
    sim = Simulation.objects.create_simulation(os.path.join(sim_dir, 'data.h5'))
    sim.save()    

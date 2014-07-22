import glob
import os
from wcdb.models import SimulationBatch, Simulation

def save_simulation_batch(batch_dir, first_sim_idx = None, max_num_simulations = None):
    if first_sim_idx is None:
        first_sim_idx = 1
    
    #save batch
    SimulationBatch.objects.create_simulation_batch(os.path.join(batch_dir, '%d.h5' % first_sim_idx))
        
    #save simulations
    sim_files = glob.glob(os.path.join(batch_dir, "[0-9]*.h5"))
    sim_files = sim_files[first_sim_idx-1:]
    if max_num_simulations is not None:
        sim_files = sim_files[:max_num_simulations]
    
    for sim_idx, sim_file in enumerate(sim_files):
        print "Saving simulation %d of %d ... " % (sim_idx+1, len(sim_files))
        save_simulation(sim_file)

def save_simulation(data_file_h5):
    sim = Simulation.objects.create_simulation(data_file_h5)
    sim.save()

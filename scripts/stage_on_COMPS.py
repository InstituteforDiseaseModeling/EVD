import os
import json
import shutil
from COMPSJavaInterop import QueryCriteria,Simulation, SimulationFile, Client, Configuration
import time

demog_filename='Ebola_Demographics.json'
config_params={'parameters':{'Demographics_Filename':demog_filename}}
configstr = json.dumps( config_params, sort_keys=True, indent=4 )

from dtk.utils.core.DTKSetupParser import DTKSetupParser
setup=DTKSetupParser()
Client.Login(setup.get('HPC','server_endpoint'))

input_path = os.path.join(setup.get('HPC','input_root'), 'ebola')
print(input_path)

from dtk.utils.simulation.CommandlineGenerator import CommandlineGenerator
input_args={ '--config':'config.json', '--input-path':input_path }
commandline=CommandlineGenerator('',input_args,[])

if not os.path.exists(input_path):
    os.mkdir(input_path)
shutil.copy(demog_filename,input_path)

sim_root=os.path.join(setup.get('HPC','sim_root'),'ebola')
bldr = Configuration.getBuilderInstance();
config = bldr.setSimulationInputArgs(commandline.Options) \
             .setWorkingDirectoryRoot(sim_root) \
             .build()

s = Simulation('Ebola Case Data',config)
s.AddFile(SimulationFile('config.json', 'input', 'The configuration file'), configstr)
s.Save()

sim_id=s.getId().toString()
print('sim ID = %s' % sim_id)
sim_id=hex(int(sim_id[:3],16)+32)[-3:]+sim_id[3:]
sim_id_flat=sim_id.replace('-','')
s.Commission()
workdir=os.path.join(sim_root,sim_id_flat[:3],sim_id_flat[3:6],sim_id_flat[6:9],sim_id)
print('HPCJobs.WorkingDirectory = %s' % workdir)
while not os.path.exists(workdir):
    time.sleep(0.1)
output_path=os.path.join(workdir,'output')
os.mkdir(output_path)
shutil.copy('SpatialReport_EbolaCases.bin',output_path)
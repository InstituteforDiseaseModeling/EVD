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
Client.Login(setup.get('HPC','server_endpoint')) # COMPS
#Client.Login('https://comps2.idmod.org') # COMPS2 (staging)

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
s.Commission()
def get_HPCJobs():
    s.Refresh(QueryCriteria().Select('Id').SelectChildren('HPCJobs'))
    return s.getHPCJobs()
A=get_HPCJobs()
while not A:
    time.sleep(1)
    print('.'),
    A=get_HPCJobs()
workdir=A.toArray()[-1].getWorkingDirectory() 

print('HPCJobs.WorkingDirectory = %s' % workdir)
while not os.path.exists(workdir):
    time.sleep(1)
    print('.'),
output_path=os.path.join(workdir,'output')
os.mkdir(output_path)
shutil.copy('SpatialReport_EbolaCases.bin',output_path)
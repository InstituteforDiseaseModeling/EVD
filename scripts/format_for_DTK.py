import pandas as pd
import matplotlib.pyplot as plt
import datetime
import struct
import json
import math

def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = datetime.date(iso_year, 1, 4)
    delta = datetime.timedelta(fourth_jan.isoweekday()-1)
    return fourth_jan - delta 

def iso_to_gregorian(iso_year, iso_week, iso_day=0):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + datetime.timedelta(days=iso_day-1, weeks=iso_week-1)

iso_countries={'GIN':'guinee','SLE':'sierra_leone','LBR':'liberia'}

def weekly_counts(country):
    filename='../data/%s_EVD_2014.csv' % country
    df=pd.read_csv(filename,parse_dates=[0])
    df=df.rename(columns={'Unnamed: 0':'date'}).fillna(0)
    year_week=lambda x: x.isocalendar()[:2]
    weekly=df.groupby(df['date'].map(year_week)).sum()
    time_format=lambda t: iso_to_gregorian(*t)
    weekly.index=weekly.index.map(time_format)
    return weekly

weekly={}
for iso,country in iso_countries.items():
    weekly[iso]=weekly_counts(country)
all_counts=pd.concat(weekly.values(),axis=1).fillna(0)
all_counts[all_counts<0]=0    

#print(all_counts.head())
#all_counts[['Montserrado','Conakry','Kailahun']].plot()    
#plt.show()

alt_names={'Kissidougou':'Kisidougou',
           'Nzerekore':'N\'Zerekore',
           'Yamou':'Yomou',
           'Gbapolu':'Gbarpolu',
           'GrandBassa':'Grand Bassa',
           'GrandGedeh':'Grand Gedeh',
           'GrandKru':'Grand Kru',
           'River Cess':'Rivercess',
           'Western Urban':'Western (urban)',
           'Western Rural':'Western (rural)',
           }

resolution = 2.5/60   # 2.5 arcmin
#resolution = 30.0/3600 # 30 arcsec

def get_node_id(lat, lon):
    xpix = int(math.floor((lon + 180.0) / resolution))
    ypix = int(math.floor((lat + 90.0) / resolution))
    nodeid = (xpix << 16) + ypix + 1
    return nodeid

def get_nodes():
    nodes={}
    node_info=['Latitude','Longitude','InitialPopulation']
    with open('../model/geography/nodes.json','r') as fjson:
        j=json.loads(fjson.read())
    for n in j:
        district=n['Name'].split(':')[-1]
        if district in alt_names:
            district=alt_names[district]
        nodes[district]={k:n[k] for k in node_info}
    return nodes

node_names=all_counts.keys()
n_nodes=len(node_names)
n_tstep=len(all_counts.index)
print('(n_nodes,n_tstep)=(%s,%s)'%(n_nodes,n_tstep))
nodes=get_nodes()
for name in node_names:
    node=nodes.get(name)
    node.update({'data':all_counts[name].tolist(),
                 'id':get_node_id(node['Latitude'],node['Longitude'])})

nodeids=[n['id'] for n in nodes.values() if 'id' in n]

with open('SpatialReport_EbolaCases.bin','wb') as binfile:
    pack_header = struct.pack('ll',n_nodes,n_tstep)
    binfile.write(pack_header)
    pack_nodeids = struct.pack('%dl'%n_nodes,*nodeids)
    binfile.write(pack_nodeids)
    for t in range(n_tstep):
        for n in nodes.values():
            if 'id' not in n:
                continue
            pack_channel = struct.pack('f',n['data'][t])
            binfile.write(pack_channel)

demog_filename='Ebola_Demographics.json'
with open(demog_filename,'w') as demog:
    demog_nodes=[]
    for name,node in nodes.items():
        if 'data' not in node:
            continue
        node.pop('data')
        demog_nodes.append({'NodeID':node.pop('id'),
                            'NodeAttributes':node})
    json.dump({ "Metadata": { "Author": "ewenger", 
                              "IdReference": "Gridded world grump2.5arcmin", 
                              "NodeCount": len(demog_nodes) },
                "Nodes":demog_nodes },
              demog,indent=2)

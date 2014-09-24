import os
import json
import psycopg2
import csv
from collections import namedtuple

def get_country_shape(shapeid):
    try:
        cnxn = psycopg2.connect(host='ivlabsdssql01.na.corp.intven.com', port=5432, dbname='idm_db')
    except pycopg2.Error:
        raise Exception("Failed connection to %s." % server_name)
    cursor = cnxn.cursor()
    SQL = ("SELECT ST_AsGeoJSON(d.geom) as geom, d.area_len, d.geogcenterlat as centerlat, d.geogcenterlon as centerlon "
            "FROM sd.shape_table d "
            "WHERE d.id = %s; ")
    params=(shapeid,)
    cursor.execute(SQL,params)
    geom,area,lat,lon = cursor.fetchone()
    geojson = json.loads(geom)['coordinates']
    return geojson,area,lat,lon

nodes=[]
with open('afripop_sierraleone_guinea_liberia.csv', 'rb') as f:
    reader = csv.reader(f)
    header=reader.next()
    region=namedtuple('region',header)
    for row in reader:
        r=region(*row)
        if int(r.hierarchy_name_set_id)==1 and (('Liberia' in r.dot_name and int(r.hid_level)==4) or ('Liberia' not in r.dot_name and int(r.hid_level)==5)):
            pop=float(r.st_stats_sum_population)
            clean_name=r.dot_name.replace('\xe9','e').replace('Conarky','Conakry') # ugh
            print(clean_name,pop)
            geojson,area,lat,lon=get_country_shape(int(r.shape_id))
            nodes.append({'GeoJSON':geojson, 
                          'Area':area, 
                          'Name':clean_name,
                          'InitialPopulation': pop, 
                          'Latitude': lat, 
                          'Longitude': lon
                          })

with open('../geography/nodes.json',mode='w') as f:
    json.dump(nodes,f)
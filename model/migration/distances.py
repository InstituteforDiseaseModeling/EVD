import os
import json
import urllib
import itertools
import time
import csv
from geodistance import haversine

meters_per_km=1000.0
seconds_per_hour = 3600.0

# N.B. Bonthe, Sierra Leone is an island with a two-hour ferry from Yagoi
exceptions={ 'Bonthe': 'Yagoi',
             'Grand Cape Mount': 'Robertsport',
             'River Cess': 'River Cess Town' }

api_key='AIzaSyDswkJadwaVzGuSkJ8Z0gzBcEekqdn7Wi4'

if os.path.exists('known_locations.json'):
    with open('known_locations.json','r') as fknown:
        known_locations=json.loads(fknown.read())
else:
    known_locations={}

# Let's ask google where these places are
def google_geocode(placename):
    time.sleep(1)
    url="https://maps.googleapis.com/maps/api/geocode/json?address={0}".format(str(placename))
    result=json.load(urllib.urlopen(url))
    print(result)
    outcome=result['results'][0]['geometry']['location']
    return outcome['lat'],outcome['lng']

# Let's just ask Google how far it is to drive
def google_driving_time_distance(orig_coord,dest_coord):
    time.sleep(0.1)
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins=%f,%f&destinations=%f,%f&mode=driving&language=en-EN&sensor=false&key=%s'%(orig_coord[0],orig_coord[1],dest_coord[0],dest_coord[1],api_key)
    result= json.load(urllib.urlopen(url))
    print(result)
    outcome=result['rows'][0]['elements'][0]
    if 'duration' not in outcome:
        print('Failed to get directions',orig_coord,dest_coord)
        return [],[]
    driving_time_hours = outcome['duration']['value'] / seconds_per_hour
    driving_distance_km = outcome['distance']['value'] / meters_per_km
    return driving_time_hours,driving_distance_km

def format_placename(dot_name):
    s=dot_name.split(':')
    place=s[-1]
    country=s[1] # first index is continent
    if place in exceptions:
        print('Replacing known challenging location %s with %s'%(place,exceptions[place]))
        place = exceptions[place]
    return ','.join([place,country])

def find_location(place):
    # try to grab from cache
    if place in known_locations:
        return known_locations[place]
    else:
        location=google_geocode(format_placename(place))
        known_locations[place]=location
        return location

with open('../geography/nodes.json','r') as fjson:
    j=json.loads(fjson.read())

with open('driving_times.csv','wb') as ofile:
    writer = csv.writer(ofile)
    header=['origin','destination','hr','km']
    writer.writerow(header)
    for (n0,n1) in itertools.combinations(j,2):
        orig=n0['Name']
        dest=n1['Name']
        #if not 'Dalaba' in orig and not 'Dalaba' in dest:
        #    continue

        print(orig,dest)

        #haversine_distance_km = haversine(n0['Longitude'],n0['Latitude'],n1['Longitude'],n1['Latitude'])[0]/meters_per_km
        #writer.writerow([orig,dest,None,haversine_distance_km])

        driving_time_hours,driving_distance_km = google_driving_time_distance(find_location(orig),find_location(dest)) # directions by lat/lon from placename lookup
        if driving_time_hours:
            writer.writerow([orig,dest,driving_time_hours,driving_distance_km])
        else:
            writer.writerow([orig,dest])

with open('known_locations.json','w') as fknown:
    json.dump(known_locations,fknown)
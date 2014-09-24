class Node:

    default_density=200 # people/km^2

    def __init__(self, lat, lon, pop, name='', area=None, geojson=[]):
        self.name=name
        self.lat=lat
        self.lon=lon
        self.pop=pop
        self.geojson=geojson
        if area:
            self.density=pop/area
        else:
            self.density=self.default_density

    @classmethod
    def fromDict(cls,d):
        c = cls(d['Latitude'],d['Longitude'],d['InitialPopulation'],d['Name'],d['Area'])
        c.geojson=d['GeoJSON']
        return c

    def __str__(self):
        return '%s: (%0.3f,%0.2f), pop=%s, per km^2=%d' % (self.name, self.lat, self.lon, "{:,}".format(self.pop), self.density)

    def toDict(self):
        d={ 'Latitude':self.lat,
            'Longitude':self.lon,
            'InitialPopulation':self.pop,
            'GeoJSON':self.geojson}
        if self.name:
            d.update({'Name':self.name})
        return d

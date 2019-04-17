from geopy.geocoders import Nominatim


class LocationNode:

    accumulatedDistance = 0

    def __init__(self, id, name, userDefinedName, lat, long):
        self.id = id
        self.name = name
        self.userDefinedName = userDefinedName
        self.lat = lat
        self.long = long
        self.accumulatedDistance = 0


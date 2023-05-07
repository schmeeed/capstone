import pandas as pd
import numpy as np
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

def find_closest_poi(listing_address, poi_dataframe, poi_categories):
    """
    Finds the closest point of interest (POI) of specific categories to a specified listing address.

    Args:
        listing_address (str): The specified address to find the closest POI to.
        poi_dataframe (pandas.DataFrame): The dataframe containing the POI data.
        poi_categories (str or list): The category or list of categories of POIs to search for.

    Returns:
        dict: A dictionary containing the details (latitude, longitude, name, address, distance) of the closest POI for all selected categories.

    Example:
         find_closest_poi(listing_address='412 8th St NE, Atlanta, GA 30309', 
                         poi_dataframe=POI,
                         poi_categories=['school', 'primary_school','secondary_school']) 
        {'latitude': 33.77561779999999,
         'longitude': -84.39628499999999,
         'name': 'Georgia Institute of Technology',
         'address': 'North Ave NW, Atlanta',
         'distance_miles': 1.33}
    """
    geolocator = Nominatim(user_agent="my_geocoder")  # Instantiate the geocoder
    location = geolocator.geocode(listing_address)  # Geocode the specified address

    listing_coordinates = (location.latitude, location.longitude)  # Get the listing coordinates

    closest_poi = None
    closest_distance = float('inf')  # Set the initial distance to infinity

    if isinstance(poi_categories, str):
        poi_categories = [poi_categories]

    for category in poi_categories:
        for _, poi_row in poi_dataframe.iterrows():
            if poi_row['poi_types'] == category:
                poi_coordinates = (poi_row['latitude'], poi_row['longitude'])  # Get the POI coordinates
                distance = geodesic(listing_coordinates, poi_coordinates).miles  # Calculate the distance between listing and POI
                if distance < closest_distance:
                    closest_distance = distance
                    closest_poi = {
                        'latitude': poi_row['latitude'],
                        'longitude': poi_row['longitude'],
                        'name': poi_row['name'],
                        'address': poi_row['address'],
                        'distance_miles': round(distance,2)
                    }

    return closest_poi
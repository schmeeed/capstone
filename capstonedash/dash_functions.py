import pandas as pd
import numpy as np

from geopy.distance import geodesic
from geopy.geocoders import Nominatim

import boto3
from botocore.exceptions import ClientError
import json

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

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
    geolocator = Nominatim(user_agent="my_geocoder", timeout=10)  # Instantiate the geocoder
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


# MAPBOX Key Function

def get_secret(secret_name):
    region_name = "us-east-1"
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # Handle the exception appropriately for your application
        raise e
    # Parse and return the secret values
    secret = get_secret_value_response['SecretString']
    return secret
mapbox_api = get_secret('mapbox')
mapbox_data = json.loads(mapbox_api)
access_token = mapbox_data['mapbox_secret']



# Sim Zip Function

def sim_zip(zipcode, df, columns, POI_df, k=6, mode=1):
    '''
    Finds similar profiled zip codes to the user-entered zipcode and performs different operations based on the mode.

    Parameters:
        zipcode (int): User-entered zipcode.
        df (DataFrame): DataFrame with the zipcode column named 'zipcode' in the first index and various features.
        columns (list): List of column names to select.
        POI_df (DataFrame): DataFrame with point of interest data.
        k (int): Number of zipcodes to consider. Default is 6.
        mode (int): Mode of operation. Valid values are 1, 2, 3, or 4.

    Returns:
        - If mode is 1: Series with k additional similar profiled zipcodes based on KNN.
        - If mode is 2: DataFrame with with all df columns retained for reference.
        - If mode is 3: Series with top 5 point of interest names in similar profiled zipcodes.
        - If mode is 4: Series with top 5 primary categories of point of interests in similar profiled zipcodes.

    Raises:
        ValueError: If the zipcode value is not an integer, df doesn't have 'zipcode' column as the first column,
                    or if the mode is not 1, 2, 3, or 4.
    '''
    # Check if the zipcode is a number
    if not isinstance(zipcode, int):
        raise ValueError('The zipcode value must be an integer.')

    # Check if 'zipcode' is the first column in df
    if df.columns[0] != 'zipcode':
        raise ValueError("The 'zipcode' column must be the first column in the dataframe.")

    # Check if mode is valid
    valid_modes = [1, 2, 3, 4]
    if mode not in valid_modes:
        raise ValueError(f"Invalid mode value. Valid modes are: {valid_modes}")

    # Standardize Values
    column_to_exclude = 'zipcode'  # I don't want to standardize zipcode
    df_to_standardize = df[columns]
    scaler = StandardScaler()
    standardized_values = scaler.fit_transform(df_to_standardize)
    census_capita_standardized = pd.DataFrame(standardized_values, columns=df_to_standardize.columns)

    # Add Zipcode column back
    census_capita_standardized[column_to_exclude] = df[column_to_exclude]

    # Pop Zipcode to the first position
    zipcode_column = census_capita_standardized.pop(column_to_exclude)
    census_capita_standardized.insert(0, column_to_exclude, zipcode_column)

    # KNN
    X = census_capita_standardized.drop('zipcode', axis=1).values
    model = NearestNeighbors(n_neighbors=k)
    model.fit(X)

    # Filter df to my Zip Code
    my_zip_vals = census_capita_standardized[census_capita_standardized['zipcode'] == zipcode].iloc[:, 1:]

    # Find Similar Zip Codes
    new_X = my_zip_vals.values
    distances, indices = model.kneighbors(new_X)
    similar_zip_codes = census_capita_standardized.iloc[indices[0]]['zipcode']

    # Filter df by sim zips
    my_sim_zips = df[df['zipcode'].isin(similar_zip_codes)]

    if mode == 1:
        return my_sim_zips
    elif mode == 2:
        return my_sim_zips
    elif mode == 3:
        return POI_df[POI_df['zipcode'].isin(similar_zip_codes)].groupby(by='name').size().sort_values(ascending=False)[:5]  
    elif mode == 4:
        return POI_df[POI_df['zipcode'].isin(similar_zip_codes)].groupby(by='primary_category').size().sort_values(ascending=False)[:5]
    
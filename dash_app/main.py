import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import boto3 # AWS
import os
import json

# Load the ZIP code data
# Creating an S3 client object
s3 = boto3.client('s3')

# Specifying the name of the bucket
bucket_name = 'capstonehaystacks'

# List of CSV files to download
files = ['atlanta_cbsa_zip.csv']

# Dictionary to store the dataframes
dataframes = {}

# Downloading the files from S3 and parsing them into data
for file_name in files:
    _, file_ext = os.path.splitext(file_name)
    if file_ext == '.csv':
        s3.download_file(bucket_name, file_name, file_name)
        dataframes[file_name[:-4]] = pd.read_csv(file_name, index_col=False)
    elif file_ext == '.json':
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        json_content = response['Body'].read().decode('utf-8')
        dataframes[file_name[:-5]] = json.loads(json_content)

atlanta_geo = dataframes['atlanta_cbsa_zip']
df = atlanta_geo.copy()

# Create the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    dcc.Input(id='zipcode-input', type='number', placeholder='Enter a ZIP code: ', value=30301),
    dcc.Graph(id='map')
])

# Define the update_map callback function
@app.callback(
    dash.dependencies.Output('map', 'figure'),
    dash.dependencies.Input('zipcode-input', 'value'))
def update_map(value):
    if value is None:
        return {}
    else:
        # Get the coordinates for the entered ZIP code
        zip_df = df.loc[df['census_zcta5_geoid'] == value, ['census_zcta5_lat', 'census_zcta5_lon']]
        if zip_df.empty:
            return {}
        else:
            lat, lon = zip_df.iloc[0]

            # Create the map with the entered ZIP code highlighted
            fig = px.scatter_mapbox(df, lat='census_zcta5_lat', lon='census_zcta5_lon', zoom=3, height=600)
            fig.update_layout(mapbox_style="carto-positron")
            fig.add_scattermapbox(lat=[lat], lon=[lon], mode='markers', marker=dict(size=20, color='red'))
            return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import geojson
import json
import boto3
import os

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

fig = px.choropleth_mapbox(df, geojson=geojson, locations='zip', color='pop',
                           color_continuous_scale="Viridis",
                           mapbox_style="carto-positron",
                           zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                           opacity=0.5)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='US Zip Code Choropleth Map'),

    dcc.Input(id='zipcode-input', value='', type='text'),

    html.Div(id='output-container')
])

@app.callback(
    Output('output-container', 'children'),
    Output('choropleth-map', 'figure'),
    Input('zipcode-input', 'value'))
def update_map(zipcode):
    if zipcode is None or zipcode == '':
        return '', fig

    # Highlight the selected zipcode
    df_zip = df.loc[df['zip'] == zipcode]
    fig_zip = px.choropleth_mapbox(df_zip, geojson=geojson, locations='zip', color='pop',
                                   color_continuous_scale="Viridis",
                                   mapbox_style="carto-positron",
                                   zoom=9, center = {"lat": df_zip.iloc[0]['lat'], "lon": df_zip.iloc[0]['long']},
                                   opacity=0.5,
                                   hover_name='city', hover_data=['state'])

    fig_zip.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return f'You selected zipcode {zipcode}.', fig_zip

if __name__ == '__main__':
    app.run_server(debug=True)


#####################


# import dash
# from dash import dcc
# from dash import html
# from dash.dependencies import Input, Output
# import plotly.express as px
# import geojson
# import pandas as pd
# import boto3  # AWS
# import os
# import json
#
# # Load the ZIP code data
# # Creating an S3 client object
# s3 = boto3.client('s3')
#
# # Specifying the name of the bucket
# bucket_name = 'capstonehaystacks'
#
# # List of CSV files to download
# files = ['atlanta_cbsa_zip.csv']
#
# # Dictionary to store the dataframes
# dataframes = {}
#
# # Downloading the files from S3 and parsing them into data
# for file_name in files:
#     _, file_ext = os.path.splitext(file_name)
#     if file_ext == '.csv':
#         s3.download_file(bucket_name, file_name, file_name)
#         dataframes[file_name[:-4]] = pd.read_csv(file_name, index_col=False)
#     elif file_ext == '.json':
#         response = s3.get_object(Bucket=bucket_name, Key=file_name)
#         json_content = response['Body'].read().decode('utf-8')
#         dataframes[file_name[:-5]] = json.loads(json_content)
#
# atlanta_geo = dataframes['atlanta_cbsa_zip']
# df = atlanta_geo.copy()


##############


# import dash
# from dash import dcc
# from dash import html
# from dash.dependencies import Input, Output
# import plotly.express as px
# import geojson
# import pandas as pd
# import boto3  # AWS
# import os
# import json
#
# # Load the ZIP code data
# # Creating an S3 client object
# s3 = boto3.client('s3')
#
# # Specifying the name of the bucket
# bucket_name = 'capstonehaystacks'
#
# # List of CSV files to download
# files = ['atlanta_cbsa_zip.csv']
#
# # Dictionary to store the dataframes
# dataframes = {}
#
# # Downloading the files from S3 and parsing them into data
# for file_name in files:
#     _, file_ext = os.path.splitext(file_name)
#     if file_ext == '.csv':
#         s3.download_file(bucket_name, file_name, file_name)
#         dataframes[file_name[:-4]] = pd.read_csv(file_name, index_col=False)
#     elif file_ext == '.json':
#         response = s3.get_object(Bucket=bucket_name, Key=file_name)
#         json_content = response['Body'].read().decode('utf-8')
#         dataframes[file_name[:-5]] = json.loads(json_content)
#
# atlanta_geo = dataframes['atlanta_cbsa_zip']
# df = atlanta_geo.copy()
#
# # Initialize the app
# app = dash.Dash(__name__)
#
# # Define the layout
# app.layout = html.Div([
#     html.H1("Atlanta Zip Code Map"),
#     dcc.Input(
#         id="input-zipcode",
#         type="number",
#         placeholder="Enter a zipcode",
#         value=""
#     ),
#     html.Br(),
#     dcc.Graph(id="zip-code-map")
# ])
#
# # Define the callback function
# @app.callback(
#     Output("zip-code-map", "figure"),
#     [Input("input-zipcode", "value")]
# )
# def update_map(zipcode):
#     if zipcode is None:
#         fig = px.choropleth_mapbox(df, geojson=atlanta_geo, locations='GEOID10', color='median_household_income',
#                                    color_continuous_scale="Viridis",
#                                    range_color=(0, 300000),
#                                    mapbox_style="carto-positron",
#                                    zoom=9, center={"lat": 33.772, "lon": -84.385},
#                                    opacity=0.5,
#                                    labels={'median_household_income': 'Median Household Income'}
#                                    )
#     else:
#         fig = px.choropleth_mapbox(df[df['ZCTA5CE10'] == str(zipcode)], geojson=atlanta_geo, locations='GEOID10', color='median_household_income',
#                                    color_continuous_scale="Viridis",
#                                    range_color=(0, 300000),
#                                    mapbox_style="carto-positron",
#                                    zoom=10, center={"lat": 33.772, "lon": -84.385},
#                                    opacity=0.5,
#                                    labels={'median_household_income': 'Median Household Income'}
#                                    )
#     fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
#     return fig
#
# if __name__ == '__main__':
#     app.run_server(debug=True)



################



# import dash
# from dash import dcc
# from dash import html
# import plotly.graph_objects as go
# import pandas as pd
# import boto3  # AWS
# import os
# import json
#
# # Load the ZIP code data
# # Creating an S3 client object
# s3 = boto3.client('s3')
#
# # Specifying the name of the bucket
# bucket_name = 'capstonehaystacks'
#
# # List of CSV files to download
# files = ['atlanta_cbsa_zip.csv']
#
# # Dictionary to store the dataframes
# dataframes = {}
#
# # Downloading the files from S3 and parsing them into data
# for file_name in files:
#     _, file_ext = os.path.splitext(file_name)
#     if file_ext == '.csv':
#         s3.download_file(bucket_name, file_name, file_name)
#         dataframes[file_name[:-4]] = pd.read_csv(file_name, index_col=False)
#     elif file_ext == '.json':
#         response = s3.get_object(Bucket=bucket_name, Key=file_name)
#         json_content = response['Body'].read().decode('utf-8')
#         dataframes[file_name[:-5]] = json.loads(json_content)
#
# atlanta_geo = dataframes['atlanta_cbsa_zip']
# df = atlanta_geo.copy()
#
# # Define the app
# app = dash.Dash(__name__)
#
# # Define the layout
# app.layout = html.Div([
#     dcc.Input(id='zip-code-input', type='text', value='30308'),
#     dcc.Graph(id='zip-code-map', style={'height': '80vh'})
# ])
#
#
# # Define the callback
# @app.callback(
#     dash.dependencies.Output('zip-code-map', 'figure'),
#     [dash.dependencies.Input('zip-code-input', 'value')]
# )
# def update_map(zip_code):
#     try:
#         selected_zip = df[df['census_zcta5_geoid'] == int(zip_code)]
#         selected_color = 'red'
#         zoom = 11
#         lat_center = selected_zip.iloc[0]['census_zcta5_lat']
#         lon_center = selected_zip.iloc[0]['census_zcta5_lon']
#     except:
#         selected_color = 'blue'
#         zoom = 9.5
#         lat_center = 33.7
#         lon_center = -84.3
#
#     fig = go.Figure(go.Choroplethmapbox(
#         geojson=atlanta_geo,
#         locations=df['census_zcta5_geoid'],
#         z=[1 if str(zip_code) == str(geoid) else 0 for geoid in df['census_zcta5_geoid']],
#         colorscale=[[0, 'blue'], [1, selected_color]],
#         marker_opacity=0.5,
#         marker_line_width=0,
#         zmin=0,
#         zmax=1,
#     ))
#
#     fig.update_layout(
#         mapbox_style='carto-darkmatter',
#         mapbox_zoom=zoom,
#         mapbox_center={'lat': lat_center, 'lon': lon_center},
#         mapbox_accesstoken='pk.eyJ1Ijoic2NobWVlZWQiLCJhIjoiY2xoMmd4dzlkMDJvYTNkcGhjN3g4YWY3aSJ9.XmDvHtt1PnWiZYIXpclq8g',
#         mapbox={'center': {'lat': lat_center, 'lon': lon_center}}
#     )
#
#     return fig
#
#
# if __name__ == '__main__':
#     app.run_server(debug=True)

###########################

# import dash
# from dash import dcc
# from dash import html
# import plotly.express as px
# import pandas as pd
# import boto3  # AWS
# import os
# import json
#
# # Load the ZIP code data
# # Creating an S3 client object
# s3 = boto3.client('s3')
#
# # Specifying the name of the bucket
# bucket_name = 'capstonehaystacks'
#
# # List of CSV files to download
# files = ['atlanta_cbsa_zip.csv']
#
# # Dictionary to store the dataframes
# dataframes = {}
#
# # Downloading the files from S3 and parsing them into data
# for file_name in files:
#     _, file_ext = os.path.splitext(file_name)
#     if file_ext == '.csv':
#         s3.download_file(bucket_name, file_name, file_name)
#         dataframes[file_name[:-4]] = pd.read_csv(file_name, index_col=False)
#     elif file_ext == '.json':
#         response = s3.get_object(Bucket=bucket_name, Key=file_name)
#         json_content = response['Body'].read().decode('utf-8')
#         dataframes[file_name[:-5]] = json.loads(json_content)
#
# atlanta_geo = dataframes['atlanta_cbsa_zip']
# df = atlanta_geo.copy()
#
# # Define the app
# app = dash.Dash(__name__)
#
# # Define the layout
# app.layout = html.Div([
#     dcc.Input(id='zip-code-input', type='text', value='30308'),
#     dcc.Graph(id='zip-code-map')
# ])
#
#
# # Define the callback
# @app.callback(
#     dash.dependencies.Output('zip-code-map', 'figure'),
#     [dash.dependencies.Input('zip-code-input', 'value')]
# )
# def update_map(zip_code):
#     filtered_df = df[df['census_zcta5_geoid'] == int(zip_code)]
#
#     fig = px.scatter_mapbox(df, lat='census_zcta5_lat', lon='census_zcta5_lon', zoom=10, height=600)
#     fig.update_layout(mapbox_style='carto-darkmatter')
#
#     fig.update_traces(
#         marker={
#             'color': ['red' if (zip_code != '' and str(zip_code) == str(geoid)) else 'blue' for geoid in df['census_zcta5_geoid']],
#             'size': [20 if (zip_code != '' and str(zip_code) == str(geoid)) else 10 for geoid in df['census_zcta5_geoid']]
#         }
#     )
#
#     return fig
#
#
# if __name__ == '__main__':
#     app.run_server(debug=True)
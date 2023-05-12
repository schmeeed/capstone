
import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import boto3
import json
import requests
from plotly.graph_objs import Scattermapbox, Layout, Figure
import plotly.express as px
from dash_functions import find_closest_poi # my custom functions
import plotly.graph_objects as go

mapbox_access_token = "Public_API"


# Fetching data
s3 = boto3.client("s3")
bucket_name = "capstonehaystacks"

# file_obj1 = s3.get_object(Bucket=bucket_name, Key="jason_listing.csv")
# listings = pd.read_csv(file_obj1["Body"])
#
# file_obj2 = s3.get_object(Bucket=bucket_name, Key="points-of-interest-google2.csv")
# poi = pd.read_csv(file_obj2["Body"])

file_obj3 = s3.get_object(Bucket=bucket_name, Key="zipcodes_111meter.min.json")
zipcodes = json.loads(file_obj3["Body"].read().decode("utf-8"))

file_obj4 = s3.get_object(Bucket=bucket_name, Key="atlanta_hdma_2021.csv")
df = pd.read_csv(file_obj4["Body"])

file_obj5 = s3.get_object(Bucket=bucket_name, Key="poi_combined_haystack_ALL_CLEANED.csv")
POI = pd.read_csv(file_obj5["Body"])

# Extracting unique zip codes
unique_zip_codes = sorted(df["zip_code"].unique())

# Creating the app
app = dash.Dash(__name__)


@app.callback(
    Output("output_boxes", "children"),
    [Input("zip_code_dropdown", "value"), Input("data_dropdown", "value")]
)
def update_output(selected_zip_code, selected_column):
    if selected_zip_code is None:
        return []

    data = df[df["zip_code"] == selected_zip_code]
    display_values = data[selected_column]

    columns_to_display = [
        "loan_count_home_purchase_approved",
        "loan_count_home_purchase_denied",
        "total_loan_count",
        "total_approved_loans",
        "total_denied_loans",
        selected_column,
    ]

    return [
        html.Div(
            [
                html.H4(column),
                html.P(data.iloc[0][column])
            ],
            className="box",
            style={"width": "16%", "display": "inline-block", "margin": "1%"}
        ) for column in columns_to_display
    ]

@app.callback(
    Output("map", "figure"),
    [Input("data_dropdown", "value")]
)

def update_map(selected_column):
    # calculate the center of the zipcodes
    lat_center = 33.751900
    lon_center = -84.414314

    fig = px.choropleth(
        df,
        geojson=zipcodes,
        locations="zip_code",
        color=selected_column,
        color_continuous_scale="Viridis",
        featureidkey="properties.ZCTA5CE10",
        labels={selected_column: selected_column},
        projection='albers usa',
        scope="usa",
        center={"lat": lat_center, "lon": lon_center}, # set the center of the map
        fitbounds="geojson",  # set the initial zoom level
    )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      mapbox_style="carto-positron"
                      )

    return fig


def get_addresses(query):
    # Replace YOUR_API_KEY with your actual Mapbox API key
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json?access_token=pk.eyJ1Ijoic2NobWVlZWQiLCJhIjoiY2xoMmd4dzlkMDJvYTNkcGhjN3g4YWY3aSJ9.XmDvHtt1PnWiZYIXpclq8g"
    response = requests.get(url)
    data = json.loads(response.text)
    center = data["features"][0]["center"]
    return {"lon": center[0], "lat": center[1]}

@app.callback(
    Output("address_map", "figure"),
    [Input("address_search_box", "value")]
)
def update_address_map(selected_address):
    if selected_address is None:
        return {}

    # Use the filtered get_addresses function to get the lat/lon coordinates of the selected address
    center = get_addresses(selected_address)
    if center is None:
        return {}

    lat = center["lat"]
    lon = center["lon"]

    fig = {
        "data": [{"type": "scattermapbox", "lat": [lat], "lon": [lon]}],
        "layout": {"mapbox": {"style": "carto-positron", "center": {"lat": lat, "lon": lon}, "zoom": 12}}
    }

    return fig


    # Replace YOUR_API_KEY with your actual Mapbox API key
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{selected_address}.json?access_token=pk.eyJ1Ijoic2NobWVlZWQiLCJhIjoiY2xoMmd4dzlkMDJvYTNkcGhjN3g4YWY3aSJ9.XmDvHtt1PnWiZYIXpclq8g"
    response = requests.get(url)
    data = response.json()

    lat = data["features"][0]["center"][1]
    lon = data["features"][0]["center"][0]

    fig = {
        "data": [{"type": "scattermapbox", "lat": [lat], "lon": [lon]}],
        "layout": {"mapbox": {"style": "carto-positron", "center": {"lat": lat, "lon": lon}, "zoom": 12}}
    }

    return fig
@app.callback(
    Output("school_indicator", "figure"),
    [Input("address_search_box", "value")]
)
def school_indicator(user_address):
    cats = ['school', 'primary_School', 'secondary_school']
    closest_school = find_closest_poi(listing_address=user_address, poi_dataframe=POI, poi_categories=cats)

    fig = go.Figure(go.Indicator(
        mode="number",
        value=closest_school['distance_miles'],
        number={'suffix': " mi"},
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Distance to Nearest School<br><span style='font-size:0.8em;color:gray'>{closest_school['name']}</span>"}))

    fig.update_layout(paper_bgcolor="lightgray")

    return fig

@app.callback(
    Output("worship_indicator", "figure"),
    [Input("address_search_box", "value")]
)
def worship_indicator(user_address):
    cats = ['hindu_temple', 'place_of_worship', 'church']
    closest = find_closest_poi(listing_address=user_address, poi_dataframe=POI, poi_categories=cats)

    fig = go.Figure(go.Indicator(
        mode="number",
        value=closest['distance_miles'],
        number={'suffix': " mi"},
        domain={'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Distance to Nearest Place of Worship<br><span style='font-size:0.8em;color:gray'>{closest['name']}</span>"}))

    fig.update_layout(paper_bgcolor="lightgray")

    return fig

@app.callback(
    Output("grocery_indicator", "figure"),
    [Input("address_search_box", "value")]
)
def grocery_indicator(user_address):
    cats = ['convenience_store', 'grocery_or_supermarket', 'supermarket']
    closest = find_closest_poi(listing_address=user_address, poi_dataframe=POI, poi_categories=cats)

    fig = go.Figure(go.Indicator(
        mode="number",
        value=closest['distance_miles'],
        number={'suffix': " mi"},
        domain={'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Distance to Nearest Grocery<br><span style='font-size:0.8em;color:gray'>{closest['name']}</span>"}))

    fig.update_layout(paper_bgcolor="lightgray")

    return fig

@app.callback(
    Output("restaurant_indicator", "figure"),
    [Input("address_search_box", "value")]
)
def restaurant_indicator(user_address):
    cats = ['restaurant', 'meal_takeaway']
    closest = find_closest_poi(listing_address=user_address, poi_dataframe=POI, poi_categories=cats)

    fig = go.Figure(go.Indicator(
        mode="number",
        value=closest['distance_miles'],
        number={'suffix': " mi"},
        domain={'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Distance to Nearest Restaurant<br><span style='font-size:0.8em;color:gray'>{closest['name']}</span>"}))

    fig.update_layout(paper_bgcolor="lightgray")

    return fig

@app.callback(
    Output("airport_indicator", "figure"),
    [Input("address_search_box", "value")]
)
def airport_indicator(user_address):
    cats = ['airport']
    closest = find_closest_poi(listing_address=user_address, poi_dataframe=POI, poi_categories=cats)

    fig = go.Figure(go.Indicator(
        mode="number",
        value=closest['distance_miles'],
        number={'suffix': " mi"},
        domain={'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Distance to Nearest Airport<br><span style='font-size:0.8em;color:gray'>{closest['name']}</span>"}))

    fig.update_layout(paper_bgcolor="lightgray")

    return fig


app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Zipcode Map', value='tab-1', children=[
            html.H1("Zip Code Analytics"),
            dcc.Dropdown(
                id="data_dropdown",
                options=[{"label": col, "value": col} for col in df.columns],
                value="approval_percentage",
                placeholder="Select a Column"
            ),

            dcc.Dropdown(
                id="zip_code_dropdown",
                options=[{"label": str(zip_code), "value": zip_code} for zip_code in unique_zip_codes],
                value=30004,
                placeholder="Select a Zip Code"
            ),
            html.Div(id="output_boxes"),
            dcc.Graph(id="map", figure=update_map("approval_percentage"))  # Call update_map() to set the initial map figure
        ]),
        dcc.Tab(label='Address Search', value='tab-2', children=[
            dbc.Row(
                [
                    dbc.Col(html.Div(dcc.Graph(id='school_indicator'))),
                    dbc.Col(html.Div(dcc.Graph(id='worship_indicator'))),
                    dbc.Col(html.Div(dcc.Graph(id='restaurant_indicator'))),
                    dbc.Col(html.Div(dcc.Graph(id='grocery_indicator'))),
                    dbc.Col(html.Div(dcc.Graph(id='airport_indicator')))
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(html.Div([dcc.Input(id="address_search_box",
                                                type="text",
                                                placeholder="Enter an address",
                                                debounce=True),
                                      dcc.Graph(id="address_map")]), width=12),
                ]
            )
        ])
    ])
])

if __name__ == "__main__":
    app.run_server(debug=True)


# app.layout = html.Div([
#     html.H1("Zip Code Analytics"),
#     dcc.Dropdown(
#         id="zip_code_dropdown",
#         options=[{"label": str(zip_code), "value": zip_code} for zip_code in unique_zip_codes],
#         value=30004,
#         placeholder="Select a Zip Code"
#     ),
#     html.Div(id="output_boxes"),
#     dcc.Graph(id="map", figure=update_map())  # Call update_map() to set the initial map figure
# ])



# app.layout = html.Div([
#     html.H1("Atlanta Metro Zip Code Analytics"),
#     dcc.Dropdown(
#         id="zip_code_dropdown",
#         options=[{"label": str(zip_code), "value": zip_code} for zip_code in unique_zip_codes],
#         value=30004,
#         placeholder="Select a Zip Code"
#     ),
#     html.Div(id="output_boxes"),
#     dcc.Graph(id="map")
# ])

# Callback function
# @app.callback(
#     Output("output_boxes", "children"),
#     [Input("zip_code_dropdown", "value"), Input("column_dropdown", "value")]
# )
#
# def update_output(selected_zip_code, selected_column):
#     if selected_zip_code is None:
#         return []
#
#     grouped_data = df[df["zip_code"] == selected_zip_code].median()
#
#     columns_to_display = [
#         "loan_count_home_purchase_approved",
#         "loan_count_home_purchase_denied",
#         "total_loan_count",
#         "total_approved_loans",
#         "total_denied_loans",
#         selected_column,
#     ]
#
#     return [
#         html.Div(
#             [
#                 html.H4(column),
#                 html.P(grouped_data[column])
#             ],
#             className="box",
#             style={"width": "16%", "display": "inline-block", "margin": "1%"}
#         ) for column in columns_to_display
#     ]
#
# @app.callback(
#     Output("map", "figure"),
#     [Input("zip_code_dropdown", "value"), Input("column_dropdown", "value")]
# )
#
#
# def update_map(selected_column):
#     fig = px.choropleth(
#         df,  # Use the entire df DataFrame
#         geojson=zipcodes,
#         locations="zip_code",
#         color=selected_column,
#         color_continuous_scale="Viridis",
#         featureidkey="properties.ZCTA5CE10",
#         locationmode='USA-states',
#         scope="usa",
#         labels={selected_column: selected_column},
#     )
#
#     # Set the default center of the map to Atlanta (33.7490, -84.3880) and adjust the zoom level
#     fig.update_geos(center=dict(lat=33.7490, lon=-84.3880) )
#     fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
#
#     # Return the created figure
#     return fig
#
#
# app.layout = html.Div([
#     html.H1("Zip Code Analytics"),
#     dcc.Dropdown(
#         id="column_dropdown",
#         options=[{"label": col, "value": col} for col in df.columns],
#         value="approval_percentage",
#         placeholder="Select a Column"
#     ),
#
#     dcc.Dropdown(
#         id="zip_code_dropdown",
#         options=[{"label": str(zip_code), "value": zip_code} for zip_code in unique_zip_codes],
#         value=30004,
#         placeholder="Select a Zip Code"
#     ),
#     html.Div(id="output_boxes"),
#     dcc.Graph(id="map", figure=update_map())  # Call update_map() to set the initial map figure
# ])
# def get_zip_code_center(zip_code):
#     # Georgia bounding box coordinates (min_lon, min_lat, max_lon, max_lat)
#     georgia_bbox = "-85.605165, 30.355644, -80.840841, 35.000771"
#
#     url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{zip_code}.json?access_token={mapbox_access_token}&bbox={georgia_bbox}"
#     response = requests.get(url)
#     data = json.loads(response.text)
#     center = data["features"][0]["center"]
#     return {"lon": center[0], "lat": center[1]}







#
# def update_output(selected_zip_code):
#     if selected_zip_code is None:
#         return []
#
#     grouped_data = listings[listings["zip_code"] == selected_zip_code].median()
#
#     columns_to_display = [
#         "loan_count_home_purchase_approved",
#         "loan_count_home_purchase_denied",
#         "total_loan_count",
#         "total_approved_loans",
#         "total_denied_loans",
#         "approval_percentage",
#         "zip_median_income",
#         "population",
#         "zip_owner_occupied_units",
#         "total_one_to_four_family_homes",
#         "median_age_of_housing_units"
#     ]
#
#     return [
#         html.Div(
#             [
#                 html.H4(column),
#                 html.P(grouped_data[column])
#             ],
#             className="box",
#             style={"width": "16%", "display": "inline-block", "margin": "1%"}
#         ) for column in columns_to_display
#     ]
#
# def update_map(selected_zip_code):
#     # Add this line to create the choropleth map with the selected zip code
#     df = listings[listings["zip_code"] == selected_zip_code]
#
#     fig = px.choropleth(
#         df,
#         geojson=zipcodes,
#         locations="zip_code",
#         color="approval_percentage",
#         color_continuous_scale="Viridis",
#         featureidkey="properties.ZCTA5CE10",
#         scope="usa",
#         labels={"approval_percentage": "Approval_Percentage"},
#     )
#
#     fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
#
#     # Return the created figure
#     return fig
# Modify the update_map function to not depend on the input



# @app.callback(
#     Output("map", "figure"),
#     [Input("zip_code_dropdown", "value")]
# )
# def update_map(selected_zip_code):
#     # Create the choropleth map with the selected zip code
#     df = listings[listings["zip_code"] == selected_zip_code]
#
#     choropleth_map = px.choropleth(
#         df,
#         geojson=zipcodes,
#         locations="zip_code",
#         color="approval_percentage",
#         color_continuous_scale="Viridis",
#         featureidkey="properties.ZCTA5CE10",
#         scope="usa",
#         labels={"approval_percentage": "Approval_Percentage"},
#     )
#
#     center = get_zip_code_center(selected_zip_code)
#
#     # scatter_map = Scattermapbox(
#     #     lat=[center["lat"]],
#     #     lon=[center["lon"]],
#     #     mode="markers",
#     #     marker=dict(size=10, color="red"),
#     #     text=[str(selected_zip_code)],
#     # )
#
#     layout = Layout(
#         autosize=True,
#         hovermode="closest",
#         mapbox=dict(
#             accesstoken=mapbox_access_token,
#             bearing=0,
#             center=dict(lat=center["lat"], lon=center["lon"]),
#             pitch=0,
#             zoom=10,
#             style="light"
#         ),
#         margin=dict(l=0, r=0, t=0, b=0)
#     )
#
#     # Merge the choropleth map and scatter map data
#     map_data = list(choropleth_map.data) + [scatter_map]
#
#     # Return the combined figure
#     return Figure(data=map_data, layout=layout)




# def update_map(selected_zip_code):
#     center = get_zip_code_center(selected_zip_code)
#
#     data = Scattermapbox(
#         lat=[center["lat"]],
#         lon=[center["lon"]],
#         mode="markers",
#         marker=dict(size=10, color="red"),
#         text=[str(selected_zip_code)],
#     )
#
#     layout = Layout(
#         autosize=True,
#         hovermode="closest",
#         mapbox=dict(
#             accesstoken=mapbox_access_token,
#             bearing=0,
#             center=dict(lat=center["lat"], lon=center["lon"]),
#             pitch=0,
#             zoom=10,
#             style="light"
#         ),
#         margin=dict(l=0, r=0, t=0, b=0)
#     )
#
#     return Figure(data=[data], layout=layout)












#
# file_obj2 = s3.get_object(Bucket=bucket_name, Key="points-of-interest-google2.csv")
# poi = pd.read_csv(file_obj2["Body"])
#
#
# poi['latitude'] = poi['latitude'].astype(float)
# poi['longitude'] = poi['longitude'].astype(float)
# # Importing Mapbox Geocoder plugin
# external_scripts = [
#     {
#         "src": "https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-geocoder/v5.0/mapbox-gl-geocoder.min.js",
#         "type": "text/javascript"
#     }
# ]
# external_stylesheets = [
#     {
#         "href": "https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-geocoder/v5.0/mapbox-gl-geocoder.min.css",
#         "rel": "stylesheet"
#     }
# ]
#
# app = dash.Dash(__name__, external_scripts=external_scripts, external_stylesheets=external_stylesheets)
#
# # Removed key to upload to github
# mapbox_access_token = "REMOVED"
# app.layout = html.Div([
#     dcc.Dropdown(
#         id="address-input",
#         placeholder="Enter address",
#         style={
#             "width": "70%",
#             "padding": "12px 20px",
#             "margin": "8px 0",
#             "box-sizing": "border-box",
#         }
#     ),
#     dcc.Graph(id="poi-map")
# ])
#


# @app.callback(
#     dash.dependencies.Output("address-input", "options"),
#     dash.dependencies.Input("address-input", "search_value"),
# )
# def update_address_options(search_value):
#     if search_value is None:
#         return []
#
#     geocoder_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{search_value}.json"
#     geocoder_params = {
#         "access_token": mapbox_access_token,
#         "country": "US",
#         "types": "address",
#         "autocomplete": True,
#     }
#     response = requests.get(geocoder_url, params=geocoder_params)
#     response_json = response.json()
#
#     options = []
#     for feature in response_json["features"]:
#         options.append({
#             "label": feature["place_name"],
#             "value": json.dumps(feature["center"]),
#         })
#
#     return options
#
# @app.callback(
#     dash.dependencies.Output("poi-map", "figure"),
#     dash.dependencies.Input("address-input", "value")
# )
# def update_poi_map(address_json):
#     # If no address has been entered yet, center the map on Atlanta
#     if address_json is None:
#         center = {"lat": 33.749, "lon": -84.388}
#     else:
#         # If an address has been entered, get the latitude and longitude from the address_json
#         center = json.loads(address_json)
#         center = {"lat": center[1], "lon": center[0]}
#
#     # Filter the dataframe to only include markers within the determined radius. This can later be a slider in the UI
#     radius = 2  # miles
#     df['distance'] = df.apply(
#         lambda row: distance((row['latitude'], row['longitude']), (center["lat"], center["lon"])).miles, axis=1)
#     filtered_df = df[df['distance'] <= radius]
#
#     # Creating the map
#     fig = go.Figure()
#     fig.add_trace(go.Scattermapbox(
#         lat=filtered_df['latitude'],
#         lon=filtered_df['longitude'],
#         mode='markers',
#         marker=go.scattermapbox.Marker(
#             size=5,
#             color='blue'
#         ),
#         hoverinfo='text',
#         text=filtered_df['primary_category']
#     ))
#
#     fig.update_layout(
#         title=f"POI Locations<br>Within {radius} Miles of ({center['lat']:.4f}, {center['lon']:.4f})",
#         autosize=True,
#         hovermode='closest',
#         showlegend=False,
#         mapbox=dict(
#             accesstoken=mapbox_access_token,
#             bearing=0,
#             center=dict(
#                 lat=center["lat"],
#                 lon=center["lon"]
#             ),
#             pitch=0,
#             zoom=10.5,
#             style='light'
#         ),
#     )
#
#     return fig


import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
import boto3
import json
import requests
from plotly.graph_objs import Scattermapbox, Layout, Figure

mapbox_access_token = "pk.eyJ1IjoiamF5c29ucDIiLCJhIjoiY2xoMmkwd3RmMDJ3czNrcGgya3ozYWZuZSJ9.As2xZKIQlr3FOQukHkdPCQ"

# Fetching data
s3 = boto3.client("s3")
bucket_name = "capstonehaystacks"


file_obj1 = s3.get_object(Bucket=bucket_name, Key="jason_listing.csv")
listings = pd.read_csv(file_obj1["Body"])

file_obj2 = s3.get_object(Bucket=bucket_name, Key="points-of-interest-google2.csv")
poi = pd.read_csv(file_obj2["Body"])

# file_obj3 = s3.get_object(Bucket=bucket_name, Key='ga_georgia_zip_codes_geo.min.json')
# zip_codes_geojson = json.loads(file_obj3["Body"].read().decode("utf-8"))

# Extracting unique zip codes
unique_zip_codes = sorted(listings["zip_code"].unique())

# Creating the app
app = dash.Dash(__name__)



app.layout = html.Div([
    html.H1("Zip Code Analytics"),
    dcc.Dropdown(
        id="zip_code_dropdown",
        options=[{"label": str(zip_code), "value": zip_code} for zip_code in unique_zip_codes],
        value=30004,
        placeholder="Select a Zip Code"
    ),
    html.Div(id="output_boxes"),
    dcc.Graph(id="map")
])

# Callback function
@app.callback(
    Output("output_boxes", "children"),
    [Input("zip_code_dropdown", "value")]
)
def update_output(selected_zip_code):
    if selected_zip_code is None:
        return []

    grouped_data = listings[listings["zip_code"] == selected_zip_code].median()

    columns_to_display = [
        "loan_count_home_purchase_approved",
        "loan_count_home_purchase_denied",
        "total_loan_count",
        "total_approved_loans",
        "total_denied_loans",
        "approval_percentage",
        "zip_median_income",
        "population",
        "zip_owner_occupied_units",
        "total_one_to_four_family_homes",
        "median_age_of_housing_units"
    ]

    return [
        html.Div(
            [
                html.H4(column),
                html.P(grouped_data[column])
            ],
            className="box",
            style={"width": "16%", "display": "inline-block", "margin": "1%"}
        ) for column in columns_to_display
    ]


@app.callback(
    Output("map", "figure"),
    [Input("zip_code_dropdown", "value")]
)
def update_map(selected_zip_code):
    center = get_zip_code_center(selected_zip_code)

    data = Scattermapbox(
        lat=[center["lat"]],
        lon=[center["lon"]],
        mode="markers",
        marker=dict(size=10, color="red"),
        text=[str(selected_zip_code)],
    )

    layout = Layout(
        autosize=True,
        hovermode="closest",
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(lat=center["lat"], lon=center["lon"]),
            pitch=0,
            zoom=10,
            style="light"
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return Figure(data=[data], layout=layout)


def get_zip_code_center(zip_code):
    # Georgia bounding box coordinates (min_lon, min_lat, max_lon, max_lat)
    georgia_bbox = "-85.605165, 30.355644, -80.840841, 35.000771"

    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{zip_code}.json?access_token={mapbox_access_token}&bbox={georgia_bbox}"
    response = requests.get(url)
    data = json.loads(response.text)
    center = data["features"][0]["center"]
    return {"lon": center[0], "lat": center[1]}


if __name__ == "__main__":
    app.run_server(debug=True)









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

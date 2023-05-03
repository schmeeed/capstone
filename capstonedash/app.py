
import dash
from dash import html
from dash import dcc
import plotly.graph_objects as go
import pandas as pd
import requests
from geopy.distance import geodesic as distance
import json


# This will need to be changed to AWS
df = pd.read_csv("points-of-interest-google2.csv")
df['latitude'] = df['latitude'].astype(float)
df['longitude'] = df['longitude'].astype(float)

# Importing Mapbox Geocoder plugin
external_scripts = [
    {
        "src": "https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-geocoder/v5.0/mapbox-gl-geocoder.min.js",
        "type": "text/javascript"
    }
]
external_stylesheets = [
    {
        "href": "https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-geocoder/v5.0/mapbox-gl-geocoder.min.css",
        "rel": "stylesheet"
    }
]

app = dash.Dash(__name__, external_scripts=external_scripts, external_stylesheets=external_stylesheets)

# Removed key to upload to github
mapbox_access_token = "REMOVED"
app.layout = html.Div([
    dcc.Dropdown(
        id="address-input",
        placeholder="Enter address",
        style={
            "width": "70%",
            "padding": "12px 20px",
            "margin": "8px 0",
            "box-sizing": "border-box",
        }
    ),
    dcc.Graph(id="poi-map")
])



@app.callback(
    dash.dependencies.Output("address-input", "options"),
    dash.dependencies.Input("address-input", "search_value"),
)
def update_address_options(search_value):
    if search_value is None:
        return []

    geocoder_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{search_value}.json"
    geocoder_params = {
        "access_token": mapbox_access_token,
        "country": "US",
        "types": "address",
        "autocomplete": True,
    }
    response = requests.get(geocoder_url, params=geocoder_params)
    response_json = response.json()

    options = []
    for feature in response_json["features"]:
        options.append({
            "label": feature["place_name"],
            "value": json.dumps(feature["center"]),
        })

    return options

@app.callback(
    dash.dependencies.Output("poi-map", "figure"),
    dash.dependencies.Input("address-input", "value")
)
def update_poi_map(address_json):
    # If no address has been entered yet, center the map on Atlanta
    if address_json is None:
        center = {"lat": 33.749, "lon": -84.388}
    else:
        # If an address has been entered, get the latitude and longitude from the address_json
        center = json.loads(address_json)
        center = {"lat": center[1], "lon": center[0]}

    # Filter the dataframe to only include markers within the determined radius. This can later be a slider in the UI
    radius = 2  # miles
    df['distance'] = df.apply(
        lambda row: distance((row['latitude'], row['longitude']), (center["lat"], center["lon"])).miles, axis=1)
    filtered_df = df[df['distance'] <= radius]

    # Creating the map
    fig = go.Figure()
    fig.add_trace(go.Scattermapbox(
        lat=filtered_df['latitude'],
        lon=filtered_df['longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=5,
            color='blue'
        ),
        hoverinfo='text',
        text=filtered_df['primary_category']
    ))

    fig.update_layout(
        title=f"POI Locations<br>Within {radius} Miles of ({center['lat']:.4f}, {center['lon']:.4f})",
        autosize=True,
        hovermode='closest',
        showlegend=False,
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=center["lat"],
                lon=center["lon"]
            ),
            pitch=0,
            zoom=10.5,
            style='light'
        ),
    )

    return fig



if __name__ == "__main__":
    app.run_server(debug=True)










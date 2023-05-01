import dash
from dash import html
from dash import dcc
import plotly.graph_objects as go
import pandas as pd
from geopy.distance import distance
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="jason", timeout=10)

# this will need to be changed to AWS
df = pd.read_csv("points-of-interest-google2.csv")

# Removed key to upload to github
mapbox_access_token = "INSERT KEY HERE"

# target is the center point of the map.  this will be later be modified to accept user input to change
target = geolocator.geocode('Atlanta, Georgia')
lat, lon = target.latitude, target.longitude

# filtering the df to only include markers within the determined radius.  This can later be a slider in the UI
radius = 2  # miles
df['distance'] = df.apply(lambda row: distance((row['latitude'], row['longitude']), (lat, lon)).miles, axis=1)
df = df[df['distance'] <= radius]

# creating the map
fig = go.Figure()
fig.add_trace(go.Scattermapbox(
    lat=df['latitude'],
    lon=df['longitude'],
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=5,
        color='blue'
    ),
    hoverinfo='text',  # hoverinfo will display a text, and the text to be displayed is below
    text=df['primary_category']  # the text to be displayed.  category and categories score might be best
))

fig.update_layout(
    title='POI Locations <br>Within {} Miles of Atlanta, Georgia'.format(radius),
    autosize=True,
    hovermode='closest',
    showlegend=False,
    mapbox=dict(
        accesstoken=mapbox_access_token,
        # layers=layers,
        bearing=0,
        center=dict(
            lat=lat,
            lon=lon
        ),
        pitch=0,
        zoom=10.5,  # Adjust the zoom level to better display the 3-mile radius
        style='light'
    ),
)

app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig)
])

# running the app
if __name__ == "__main__":
    app.run_server(debug=True)

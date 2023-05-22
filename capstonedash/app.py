
import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import boto3
from botocore.exceptions import ClientError
import json
import requests
from plotly.graph_objs import Scattermapbox, Layout, Figure
import plotly.express as px
import dash_functions
import plotly.graph_objects as go
import dash_leaflet as dl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker



mapbox_api = dash_functions.get_secret('mapbox')
mapbox_data = json.loads(mapbox_api)
access_token = mapbox_data['mapbox_secret']

# Fetching data
s3 = boto3.client("s3")
bucket_name = "capstonehaystacks"


file_obj3 = s3.get_object(Bucket=bucket_name, Key="zipcodes_111meter.min.json")
zipcodes = json.loads(file_obj3["Body"].read().decode("utf-8"))

file_obj4 = s3.get_object(Bucket=bucket_name, Key="census_all.csv")
census_all = pd.read_csv(file_obj4["Body"])

file_obj5 = s3.get_object(Bucket=bucket_name, Key="poi_combined_haystack_ALL_CLEANED.csv")
POI = pd.read_csv(file_obj5["Body"])

file_obj5 = s3.get_object(Bucket=bucket_name, Key="POI_second_tab.csv")
poi_with_census = pd.read_csv(file_obj5["Body"])
# Extracting unique zip codes
unique_zip_codes = sorted(poi_with_census["zipcode"].unique())

# Creating the app
# app = dash.Dash(__name__)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY, dbc.icons.BOOTSTRAP])


column_names_mapping = {
    'average_loan_amount_home_improvement_approved': 'Avg. Loan Amount (Home Improvement)',
    'average_loan_amount_home_purchase_approved': 'Avg. Loan Amount (Home Purchase)',
    'total_loan_count': 'Total Loan Count',
    'total_approved_loans': 'Total Approved Loans',
    'total_denied_loans': 'Total Denied Loans',
    'approval_percentage': 'Approval Percentage',
    'zip_median_income': 'Median Income',
    'median_age_of_housing_units': 'Median Age of Housing',
}
column_dropdown_name_or_cat = {
    'name': 'Points of Interest',
    'primary_category': 'POI Categories'
}

column_dropdown_features = {
    'median_homeowner_value': 'Median Homeowner Value',
    'median_rental_value': 'Median Rental Value',
    'rental_vacancy_rate': 'Rental Vacancy Rate',
    'percent_owner_occupied': 'Percentage Owner Occupied',
    'percent_after_2019': 'Percentage Newer Residents',
    'approval_percentage': 'Approval Percentage(HMDA)',
    'gross_rental_yield': 'Gross Rental Yield',
    'car_commute': 'Percent Who Commute by Car',
    'travel_less_10': 'Commute < 10 Minutes',
    'travel_10_14': 'Commute 10-14 Minutes',
    'travel_15_19': 'Commute 15-19 Minutes',
    'travel_20_24': 'Commute 20-24 Minutes',
    'travel_25_29': 'Commute 25-29 Minutes',
    'travel_30_34': 'Commute 30-34 Minutes',
    'travel_35_44': 'Commute 35-44 Minutes',
    'travel_45_59': 'Commute 45-59 Minutes',
    'travel_more_60': 'Commute > 60 Minutes',
    'percent_male': 'Percentage Male',
    'percent_under_15': 'Percentage (Under 15)',
    'percent_teen_15_19': 'Percentage Teen (15-19)',
    'percent_college_20_24': 'Percentage College (20-24)',
    'percent_25_39': 'Percentage Young Adults (25-39)',
    'percent_40-59': 'Percentage Middle Aged Adults (40-59)',
    'percent_over_60': 'Percentage Seniors (Over 60)',
    'rent_less_15_percent_income': 'Rent Under 15% of Income',
    'rent_15_30_percent': 'Rent between 15-30% of Income',
    'rent_over_30_percent': 'Rent Over 30% of Income',
    'rent_less_999': 'Rent Under $999',
    'rent_1000_2500': 'Rent Between $1000-$2500',
    'rent_over_2500': 'Rent Over $2500',
    'percent_less_10k': 'Percentage Earning Less than $10k',
    'percent_10k_15k': 'Percentage Earning Between $10k-$15k',
    'percent_15k_25k': 'Percentage Earning Between $15k-$25k',
    'percent_25k_35k': 'Percentage Earning Between $25k-$35k',
    'percent_35k_50k': 'Percentage Earning Between $35k-$50k',
    'percent_50k_75k': 'Percentage Earning Between $50k-$75k',
    'percent_75k_100k': 'Percentage Earning Between $75k-$100k',
    'percent_100k_150k': 'Percentage Earning Between $100k-$150k',
    'percent_150k_200k': 'Percentage Earning Between $150k-$200k',
    'percent_more_200k': 'Percentage Earning Over $200k'

}

filtered_columns = [col for col in census_all.columns if col in column_dropdown_features]


@app.callback(
    Output("map", "figure"),
    [Input("data_dropdown", "value")]
)
def update_map_and_zipcodes(selected_column):
    fig = px.choropleth(
        census_all,
        geojson=zipcodes,
        locations="zipcode",
        color=selected_column,
        color_continuous_scale="Viridis",
        featureidkey="properties.ZCTA5CE10",
        labels={selected_column: column_dropdown_features[selected_column]},
        projection='albers usa',
        scope="usa",
        center={"lat": 33.751900, "lon": -84.414314},
        fitbounds="geojson",
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox_style="carto-positron"
    )
    return fig


global_selected_column = None  # Define the global_selected_column as a global variable

card_top = dbc.Card(
    dbc.CardBody(
        [
            html.H4("", id="top_zipcode_card_title", className="card-title text-start"),
            dbc.ListGroup([], id="top_zipcode_list_group", flush=True),
        ],
        className="border-start border-success border-5 p-3",
        style={"background-color": "#c3e6cb"}  # Set the background color to green
    ),
    className="text-center m-4",
)

card_bottom = dbc.Card(
    dbc.CardBody(
        [
            html.H4("", id="bottom_zipcode_card_title", className="card-title text-start"),
            dbc.ListGroup([], id="bottom_zipcode_list_group", flush=True),
        ],
        className="border-start border-danger border-5 p-3",  # Set the border color to red
        style={"background-color": "#f5c6cb"}  # Set the background color to red
    ),
    className="text-center m-4",
)

@app.callback(
    [Output("top_zipcode_list_group", "children"),
     Output("bottom_zipcode_list_group", "children"),
     Output("top_zipcode_card_title", "children"),
     Output("bottom_zipcode_card_title", "children")],
    [Input("data_dropdown", "value")]
)
def update_cards(selected_column):
    global global_selected_column  # Access the global_selected_column variable

    # Get the top 3 zip codes with highest values for selected_column as a dictionary
    top_zipcodes_dict = census_all.nlargest(3, selected_column).set_index("zipcode")[selected_column].to_dict()
    # Get the bottom 3 zip codes with lowest values for selected_column as a dictionary
    bottom_zipcodes_dict = census_all.nsmallest(3, selected_column).set_index("zipcode")[selected_column].to_dict()

    top_zipcode_items = [
        dbc.ListGroupItem(
            [
                dbc.Row(
                    [
                        dbc.Col(html.H5(f"{zipcode}", className="mb-0 font-weight-bold"), width=6),
                        dbc.Col(html.P(f"{value * 1:.0f}%", className="mb-0 font-weight-bold text-end"), width=6),
                    ]
                )
            ],
            className="text-start"
        )
        for zipcode, value in top_zipcodes_dict.items()
    ]

    bottom_zipcode_items = [
        dbc.ListGroupItem(
            [
                dbc.Row(
                    [
                        dbc.Col(html.H5(f"{zipcode}", className="mb-0 font-weight-bold"), width=6),
                        dbc.Col(html.P(f"{value * 1:.0f}%", className="mb-0 font-weight-bold text-end"), width=6),
                    ]
                )
            ],
            className="text-start"
        )
        for zipcode, value in bottom_zipcodes_dict.items()
    ]

    global_selected_column = column_dropdown_features.get(selected_column)  # Retrieve the value from column_dropdown_features

    return top_zipcode_items, bottom_zipcode_items, f"{global_selected_column} Top Zipcodes", f"{global_selected_column} Bottom Zipcodes"



def get_addresses(query):
    # Replace YOUR_API_KEY with your actual Mapbox API key
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json?access_token={access_token}"
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
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{selected_address}.json?access_token={access_token}"
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
    Output('top-graphic', 'figure'),
    Input('name_or_cat-dropdown', 'value'),
    Input('column_selected-dropdown', 'value'),
    Input('poi-slider', 'value')
)

def update_graph_top(name_or_cat, column_selected, poi_slider_value):
    category_counts = poi_with_census[name_or_cat].value_counts()
    valid_categories = category_counts[category_counts >= poi_slider_value]
    valid_merged = poi_with_census[poi_with_census[name_or_cat].isin(valid_categories.index)]
    category_approval = valid_merged.groupby(name_or_cat)[column_selected].mean()

    top_categories = category_approval.nlargest(10)
    title = "Top " + column_dropdown_name_or_cat[name_or_cat] + " by " + column_dropdown_features[column_selected]
    xaxis_title = column_dropdown_name_or_cat[name_or_cat]
    yaxis_title = column_dropdown_features[column_selected]



    fig = go.Figure(
        data=go.Bar(
            x=top_categories.index,
            y=top_categories,
            marker_color="green",
        )
    )

    fig.update_layout(
        title=title,
        title_x=0.5,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        yaxis=dict(
            tickformat=",.1f"
            if column_selected not in ["median_rental_value", "median_homeowner_value"]
            else ",.0f",
            ticksuffix="%"
            if column_selected not in ["median_rental_value", "median_homeowner_value"]
            else "",
            tickprefix=""
            if column_selected not in ["median_rental_value", "median_homeowner_value"]
            else "$",
            range=[top_categories.min() - 1, top_categories.max() + 1],
        ),
        # autosize=False,
        # width=700,
        # height=550,
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        paper_bgcolor="White",
    )

    return fig

@app.callback(
    Output('bottom-graphic', 'figure'),
    Input('name_or_cat-dropdown', 'value'),
    Input('column_selected-dropdown', 'value'),
    Input('poi-slider', 'value')
)
def update_graph_bottom(name_or_cat, column_selected, poi_slider_value):
    category_counts = poi_with_census[name_or_cat].value_counts()
    valid_categories = category_counts[category_counts >= poi_slider_value]
    valid_merged = poi_with_census[poi_with_census[name_or_cat].isin(valid_categories.index)]
    category_approval = valid_merged.groupby(name_or_cat)[column_selected].mean()
    bottom_categories = category_approval.nsmallest(10)
    # top_categories = category_approval.nlargest(10)
    title = "Bottom " + column_dropdown_name_or_cat[name_or_cat] + " by " + column_dropdown_features[column_selected]
    xaxis_title = column_dropdown_name_or_cat[name_or_cat]
    yaxis_title = column_dropdown_features[column_selected]



    fig = go.Figure(
        data=go.Bar(
            x=bottom_categories.index,
            y=bottom_categories,
            marker_color="red",
        )
    )

    fig.update_layout(
        title=title,
        title_x=0.5,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        yaxis=dict(
            tickformat=",.1f"
            if column_selected not in ["median_rental_value", "median_homeowner_value"]
            else ",.0f",
            ticksuffix="%"
            if column_selected not in ["median_rental_value", "median_homeowner_value"]
            else "",
            tickprefix=""
            if column_selected not in ["median_rental_value", "median_homeowner_value"]
            else "$",
            range=[bottom_categories.min() - 1, bottom_categories.max() + 1],
        ),
        # autosize=False,
        # width=700,
        # height=550,
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        paper_bgcolor="White",
    )

    return fig

@app.callback(
    Output("school_indicator", "figure"),
    [Input("address_search_box", "value")]
)
def school_indicator(user_address):
    cats = ['school', 'primary_School', 'secondary_school']
    closest_school = dash_functions.find_closest_poi(listing_address=user_address, poi_dataframe=POI, poi_categories=cats)

    fig = go.Figure(go.Indicator(
        mode="number",
        value=closest_school['distance_miles'],
        number={'suffix': " mi"},
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"School<br><span style='font-size:0.8em;color:gray'>{closest_school['name']}</span>"}))

    fig.update_layout(paper_bgcolor="lightgray")

    return fig

@app.callback(
    Output("worship_indicator", "figure"),
    [Input("address_search_box", "value")]
)
def worship_indicator(user_address):
    cats = ['hindu_temple', 'place_of_worship', 'church']
    closest = dash_functions.find_closest_poi(listing_address=user_address, poi_dataframe=POI, poi_categories=cats)

    fig = go.Figure(go.Indicator(
        mode="number",
        value=closest['distance_miles'],
        number={'suffix': " mi"},
        domain={'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Place of Worship<br><span style='font-size:0.8em;color:gray'>{closest['name']}</span>"}))

    fig.update_layout(paper_bgcolor="lightgray")

    return fig

@app.callback(
    Output("grocery_indicator", "figure"),
    [Input("address_search_box", "value")]
)
def grocery_indicator(user_address):
    cats = ['convenience_store', 'grocery_or_supermarket', 'supermarket']
    closest = dash_functions.find_closest_poi(listing_address=user_address, poi_dataframe=POI, poi_categories=cats)

    fig = go.Figure(go.Indicator(
        mode="number",
        value=closest['distance_miles'],
        number={'suffix': " mi"},
        domain={'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Grocery<br><span style='font-size:0.8em;color:gray'>{closest['name']}</span>"}))

    fig.update_layout(paper_bgcolor="lightgray")

    return fig

@app.callback(
    Output("restaurant_indicator", "figure"),
    [Input("address_search_box", "value")]
)
def restaurant_indicator(user_address):
    cats = ['restaurant', 'meal_takeaway']
    closest = dash_functions.find_closest_poi(listing_address=user_address, poi_dataframe=POI, poi_categories=cats)

    fig = go.Figure(go.Indicator(
        mode="number",
        value=closest['distance_miles'],
        number={'suffix': " mi"},
        domain={'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Restaurant<br><span style='font-size:0.8em;color:gray'>{closest['name']}</span>"}))

    fig.update_layout(paper_bgcolor="lightgray")

    return fig

@app.callback(
    Output("airport_indicator", "figure"),
    [Input("address_search_box", "value")]
)
def airport_indicator(user_address):
    cats = ['airport']
    closest = dash_functions.find_closest_poi(listing_address=user_address, poi_dataframe=POI, poi_categories=cats)

    fig = go.Figure(go.Indicator(
        mode="number",
        value=closest['distance_miles'],
        number={'suffix': " mi"},
        domain={'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Airport<br><span style='font-size:0.8em;color:gray'>{closest['name']}</span>"}))

    fig.update_layout(paper_bgcolor="lightgray")

    return fig


app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
         dcc.Tab(label='Zipcode HeatMap', value='tab-1', children=[
              # html.H1("Zip Code Analytics"),
              html.Div([
                 dcc.Dropdown(
                      id="data_dropdown",
                    options=[{"label": column_dropdown_features[col], "value": col} for col in filtered_columns],
                    value="car_commute",
                     placeholder="Select a Column"
                  )
            ], style={'width': '50%', 'margin': 'auto'}),

            html.Div([
                dcc.Graph(id="map", style={'height': '800px', 'width': '100%'})

                # dcc.Graph(id="map", figure=update_map("car_commute"),
                #           style={'height': '600px', 'width': '100%'})
            ], style={'width': '100%', 'margin': 'auto', 'display': 'flex', 'justify-content': 'center'}),

            dbc.Container(
                 dbc.Row(
                        [dbc.Col(card_top), dbc.Col(card_bottom)],
                    ),
                    fluid=True,
                )
        ]),
        dcc.Tab(label='Points of Interest', value='tab-2', children=[
            dcc.Dropdown(
                    id='name_or_cat-dropdown',
                    options=[{'label': v, 'value': k} for k, v in column_dropdown_name_or_cat.items()],
                    value='primary_category'
                ),
                dcc.Dropdown(
                    id='column_selected-dropdown',
                    options=[{'label': v, 'value': k} for k, v in column_dropdown_features.items()],
                    value='rent_over_2500'
                ),
                html.Div(
                    id='poi-graph-container',
                    children=[
                        dcc.Graph(id='top-graphic', style={'width': '50%', 'height': '50vh'}),
                        dcc.Graph(id='bottom-graphic', style={'width': '50%', 'height': '50vh'})
                    ],
                    style={'display': 'flex', 'justify-content': 'space-between'}
                ),
                html.Div([
                    html.Label('Filter by Minimum Amount of POI Locations in Entire Region:'),
                    dcc.Slider(
                        id='poi-slider',
                        min=50,
                        max=400,
                        step=50,
                        value=50,
                        # marks=None,
                        marks={i: str(i) for i in range(50, 401, 50)},
                        tooltip={"placement": "bottom", "always_visible": True},
                        className='p-0'
                    )
                ]),
                ]),


        dcc.Tab(label='Address Search', value='tab-3', children=[

            html.Div(
                [
                    html.Div(dcc.Graph(id='school_indicator',
                                        config={'staticPlot': True},
                                        figure={'layout': {'width': 200, 'height': 200}})),
                    html.Div(dcc.Graph(id='worship_indicator',
                                        config={'staticPlot': True},
                                        figure={'layout': {'width': 200, 'height': 200}})),
                    html.Div(dcc.Graph(id='restaurant_indicator',
                                        config={'staticPlot': True},
                                        figure={'layout': {'width': 200, 'height': 200}})),
                    html.Div(dcc.Graph(id='grocery_indicator',
                                        config={'staticPlot': True},
                                        figure={'layout': {'width': 200, 'height': 200}})),
                    html.Div(dcc.Graph(id='airport_indicator',
                                        config={'staticPlot': True},
                                        figure={'layout': {'width': 200, 'height': 200}}))
                ],
                style={
                    'display': 'flex',
                    "gap": "20px",
                    "align-items": "flex-end"
                }
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

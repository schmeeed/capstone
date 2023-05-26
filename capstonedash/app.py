import dash
from dash import html
from dash import dcc
from dash import dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import boto3
import json
import plotly.express as px
import dash_functions
import plotly.graph_objects as go

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

file_obj6 = s3.get_object(Bucket=bucket_name, Key="POI_second_tab.csv")
poi_with_census = pd.read_csv(file_obj6["Body"])

file_obj6 = s3.get_object(Bucket=bucket_name, Key="census_all_perCapita.csv")
census_capita = pd.read_csv(file_obj6["Body"])
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
    'primary_category': 'Categories'
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


def format_value(column_selected, value):
    if column_selected in ["median_rental_value", "median_homeowner_value"]:
        return f"${value:,.0f}"
    else:
        return f"{value * 1:,.1f}%"



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

    # fig.update_layout(
    #     title_text="Atlanta Metro Area",
    #     title_font_size=24,
    #     title_font_family="Arial",
    #     margin={"r": 0, "t": 0, "l": 0, "b": 0},
    #     mapbox_style="carto-positron"
    # )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox_style="carto-positron"
    )
    return fig


global_selected_column = None  # defining global_selected_column as a global variable

card_top = dbc.Card(
    dbc.CardBody(
        [
            html.H4("", id="top_zipcode_card_title", className="card-title text-start"),
            dbc.ListGroup([], id="top_zipcode_list_group", flush=True),
        ],
        className="border-start border-success border-5 p-3",
        style={"background-color": "#c3e6cb"}  # green
    ),
    className="text-center m-4",
)

card_bottom = dbc.Card(
    dbc.CardBody(
        [
            html.H4("", id="bottom_zipcode_card_title", className="card-title text-start"),
            dbc.ListGroup([], id="bottom_zipcode_list_group", style={"background-color": "#f5c6cb"}),
        ],
        className="border-start border-danger border-5 p-3",  # border color to red
        style={"background-color": "#f5c6cb"}  # background color to red
    ),
    className="text-center m-4",
)

checklist1 = html.Div(
    [
        html.Label("Select Individual Categories:", style={"font-weight": "bold"}),
        dcc.Checklist(
            id='checkboxes1',
            options=[
                {'label': value, 'value': key}
                for key, value in column_dropdown_features.items()
            ],
            value=[],
            labelStyle={'display': 'block'},
        )
    ],
    className="m-4 border border-success",
    style={'columnCount': 3}
)

switch_all_categories = html.Div(
    [
        dbc.Label(""),
        dbc.Checklist(
            options=[
                {"label": "Select all Categories", "value": 1},
            ],
            value=[1],
            id="switch-all",
            inline=True,
            switch=True,
        ),
    ]
)

zip_dropdown = html.Div(
    [
        dbc.Label("Select Preferred Zip Code"),
        dcc.Dropdown(
            id="zip1",
            options=[
                {"label": str(zip_code), "value": zip_code}
                for zip_code in unique_zip_codes
            ],
            value=30004,
            placeholder="Select a Zip Code",
            clearable=False,
        ),
    ],
    className="mb-4",
)

knn_slider = html.Div(
    [
        html.Label("Select Number of Similar Zip Codes to View"),
        dcc.Slider(min=6, max=20, step=1, value=6, id="knn-slider"),
        dcc.Store(id='knn_slider')
    ]
)

update_button = html.Div(
    [
        dbc.Button('Update Results', id='update-button', n_clicks=0)
    ],
    className="d-grid gap-2",
)


@app.callback(
    Output('checkboxes1', 'value'),
    Input('switch-all', 'value')
)
def update_checklist(selected_switch):
    if selected_switch == [1]:  # if switch is on
        # return all the keys as the value of the checklist
        return list(column_dropdown_features.keys())
    else:  # if switch is off
        # return an empty list to deselect all checkmarks
        return []

knn_table = dash_table.DataTable(
    id="knn_table",
    data=dash_functions.sim_zip(zipcode=30002, df=census_capita, columns=['travel_less_10', 'percent_25_39',
                                                                          'percent_100k_150k', 'rental_vacancy_rate'],
                                POI_df=POI, k=10, mode=1).to_dict('records'),
    page_size=25,
    style_table={"overflowX": "scroll"},
    style_data_conditional=[]
)


@app.callback(
    Output('knn_table', 'data'),
    Output('knn_table', 'style_data_conditional'),
    Input('update-button', 'n_clicks'),  # added button as input
    State('checkboxes1', 'value'),
    State('zip1', 'value'),
    State('knn-slider', 'value')
)
def update_table(n_clicks, selected_features, selected_zip, k):
    # If the button hasn't been clicked, don't update the table
    if n_clicks == 0:
        raise dash.exceptions.PreventUpdate

    # If the button has been clicked, compute the new data and update the table
    new_data = dash_functions.sim_zip(zipcode=selected_zip, df=census_capita, columns=selected_features, POI_df=POI,
                                      k=k, mode=1).to_dict('records')

    style_data_conditional = [
        {
            'if': {'column_id': c},
            'backgroundColor': 'lightyellow',
        } for c in selected_features
    ]

    return new_data, style_data_conditional



@app.callback(
    Output("map2", "figure"),
    Input('update-button', 'n_clicks'),  # added button as input
    State('checkboxes1', 'value'),
    State('zip1', 'value'),
    State('knn-slider', 'value')
)
def update_map_with_zipcodes(n_clicks, selected_features, selected_zip, k):
    # If the button hasn't been clicked, don't update the table
    if n_clicks == 0:
        raise dash.exceptions.PreventUpdate
    # using mode 2 for list of zipc odes
    zipcode_list = dash_functions.sim_zip(zipcode=selected_zip, df=census_capita, columns=selected_features, POI_df=POI,
                                          k=k, mode=2)

    # new column to differentiate the selected zip code and the other zip codes
    census_all['color'] = census_all['zipcode'].apply(
        lambda x: 'Selected' if x == zipcode_list[0] else ('Similar' if x in zipcode_list else 'Other'))

    fig = px.choropleth(
        census_all,
        geojson=zipcodes,
        locations="zipcode",
        color="color",
        color_discrete_map={'Selected': '#0000FF', 'Similar': '#00FFFF', 'Other': '#F0F8FF'},
        featureidkey="properties.ZCTA5CE10",
        labels={"color": "Zip Code Type"},
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


@app.callback(
    [Output("top_zipcode_list_group", "children"),
     Output("bottom_zipcode_list_group", "children"),
     Output("top_zipcode_card_title", "children"),
     Output("bottom_zipcode_card_title", "children")],
    [Input("data_dropdown", "value")]
)
def update_cards(selected_column):
    global global_selected_column
    # top 3 zip codes with highest values for selected_column as a dictionary
    top_zipcodes_dict = census_all.nlargest(3, selected_column).set_index("zipcode")[selected_column].to_dict()
    # bottom 3 zip codes with lowest values for selected_column as a dictionary
    bottom_zipcodes_dict = census_all.nsmallest(3, selected_column).set_index("zipcode")[selected_column].to_dict()
    top_zipcode_items = [
        dbc.ListGroupItem(
            [
                dbc.Row(
                    [
                        dbc.Col(html.H5(f"{zipcode}", className="mb-0 font-weight-bold"), width=6),
                        dbc.Col(
                            html.P(format_value(selected_column, value), className="mb-0 font-weight-bold text-end"),
                            width=6),
                    ]
                )
            ],
            className="text-start", color="success"
        )
        for zipcode, value in top_zipcodes_dict.items()
    ]

    bottom_zipcode_items = [
        dbc.ListGroupItem(
            [
                dbc.Row(
                    [
                        dbc.Col(html.H5(f"{zipcode}", className="mb-0 font-weight-bold"), width=6),
                        dbc.Col(
                            html.P(format_value(selected_column, value), className="mb-0 font-weight-bold text-end"),
                            width=6),
                    ]
                )
            ],
            className="text-start", color="danger"
        )
        for zipcode, value in bottom_zipcodes_dict.items()
    ]

    global_selected_column = column_dropdown_features.get(
        selected_column)  # Retrieve the value from column_dropdown_features

    return top_zipcode_items, bottom_zipcode_items, f"{global_selected_column} Top Zipcodes", f"{global_selected_column} Bottom Zipcodes"


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
    bottom_categories = category_approval.nsmallest(10)
    top_categories = category_approval.nlargest(10)
    title = "Top 10 " + column_dropdown_name_or_cat[name_or_cat] + " by " + column_dropdown_features[column_selected]
    xaxis_title = column_dropdown_name_or_cat[name_or_cat]
    yaxis_title = column_dropdown_features[column_selected] + " for All Locations"

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
        height=900,
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
            range = [bottom_categories.min() - 1, top_categories.max() + 1],
        ),
            xaxis=dict(
                tickfont=dict(size=10),
                title_standoff=50,
                tickangle=25,
            ),
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
    bottom_categories = category_approval.nsmallest(10)[::-1]
    top_categories = category_approval.nlargest(10)
    title = "Bottom 10 " + column_dropdown_name_or_cat[name_or_cat] + " by " + column_dropdown_features[column_selected]
    xaxis_title = column_dropdown_name_or_cat[name_or_cat]
    yaxis_title = column_dropdown_features[column_selected] + " for All Locations"

    fig = go.Figure(
        data=go.Bar(
            x=bottom_categories.index[::-1],
            # x=bottom_categories.index,
            y=bottom_categories,
            marker_color="red",
        )
    )

    fig.update_layout(
        title=title,
        title_x=0.5,
        height = 900,
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
            range=[bottom_categories.min() - 1, top_categories.max() + 1],
        ),
            xaxis=dict(
                tickfont=dict(size=10),
                title_standoff=50,
                tickangle=25,
            ),
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        paper_bgcolor="White",
    )

    return fig

table_header = html.Thead(html.Tr([html.Th("Most Common POI Names in Selected Zip Codes"), html.Th("Count")]))

table_header2 = html.Thead(html.Tr([html.Th("Most Common POI Categories in Selected Zip Codes"), html.Th("Count")]))

table_body = html.Tbody([])  # Initialize empty table body
table_body2 = html.Tbody([])


poi_table = dbc.Table(
    children=[table_header, table_body],
    id="table-poi",
    color="secondary",
)

poi_table2 = dbc.Table(
    children=[table_header, table_body2],
    id="table-poi2",
    color="secondary",
)

@app.callback(
    Output("table-poi", "children"),
    Input('update-button', 'n_clicks'),  # added button as input
    State('checkboxes1', 'value'),
    State('zip1', 'value'),
    State('knn-slider', 'value')
)
def update_poi_table(n_clicks, selected_features, selected_zip, k):
    # If the button hasn't been clicked, don't update the table
    if n_clicks == 0:
        raise dash.exceptions.PreventUpdate

    # Call your function to get the poi_name_dict
    poi_name_dict = dash_functions.sim_zip(zipcode=selected_zip, df=census_capita, columns=selected_features,
                                           POI_df=poi_with_census, k=k, mode=3)

    table_rows = []
    for key, value in poi_name_dict.items():
        row = html.Tr([html.Td(key), html.Td(str(value))])  # Convert value to string
        table_rows.append(row)

    table_body.children = table_rows  # updating table body directly

    return [poi_table]  # wrapping the poi_table in a list for the callback return value

@app.callback(
    Output("table-poi2", "children"),
    Input('update-button', 'n_clicks'),  # added button as input
    State('checkboxes1', 'value'),
    State('zip1', 'value'),
    State('knn-slider', 'value')
)
def update_poi_table2(n_clicks, selected_features, selected_zip, k):
    # If the button hasn't been clicked, don't update the table
    if n_clicks == 0:
        raise dash.exceptions.PreventUpdate

    # Call your function to get the poi_name_dict
    poi_name_dict = dash_functions.sim_zip(zipcode=selected_zip, df=census_capita, columns=selected_features,
                                           POI_df=poi_with_census, k=k, mode=4)  # Update poi_name_dict using mode=4

    table_rows = []
    for key, value in poi_name_dict.items():
        row = html.Tr([html.Td(key), html.Td(str(value))])  # Convert value to string
        table_rows.append(row)

    table_body2.children = table_rows  # Update table body for the second table directly

    return [poi_table2]  # Wrap the poi_table2 in a list for the callback return value





app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Atlanta Metro Region Heat Map', value='tab-1', children=[
            html.Div([
                html.Div([
                    html.Label('Select a Zip Code Feature:'),
                    dcc.Dropdown(
                        id="data_dropdown",
                        options=[{"label": column_dropdown_features[col], "value": col} for col in filtered_columns],
                        value="car_commute",
                        placeholder="Select a Column"
                    )
                ], style={'margin-top': '0.5in', 'margin-bottom': '0.5in'}),
                dcc.Loading(
                    id="loading",
                    type="dot",  # a value equal to: 'graph', 'cube', 'circle', 'dot' or 'default';
                    children=[
                        dcc.Graph(id="map", style={'height': '800px', 'width': '100%'})
                    ],
                    style={'width': '100%', 'minHeight': '800px'}
                ),

                dbc.Container(
                    dbc.Row(
                        [dbc.Col(card_top), dbc.Col(card_bottom)],
                    ),
                    fluid=True,
                )
            ])
        ]),
        dcc.Tab(label='Points of Interest Demographics', value='tab-2', children=[
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Label('Select POI Name or Category:'),
                        dcc.Dropdown(
                            id='name_or_cat-dropdown',
                            options=[{'label': v, 'value': k} for k, v in column_dropdown_name_or_cat.items()],
                            value='primary_category'
                        ),
                    ], width=4),
                    dbc.Col([
                        html.Div([
                            html.Label('Filter by Minimum Amount of POI Locations in Entire Region:'),
                            dcc.Slider(
                                id='poi-slider',
                                min=10,
                                max=400,
                                step=10,
                                value=10,
                                marks={i: str(i) for i in range(50, 401, 50)},
                                tooltip={"placement": "bottom", "always_visible": True},
                                className='p-0'
                            )
                        ], style={'padding': '20px'})  # increased padding to prevent cutoff
                    ], width=4),
                    dbc.Col([
                        html.Label('Select Interested Feature:'),
                        dcc.Dropdown(
                            id='column_selected-dropdown',
                            options=[{'label': v, 'value': k} for k, v in column_dropdown_features.items()],
                            value='rent_over_2500'
                        )
                    ], width=4),
                ], justify='around'),
            ], style={'border': '3px solid #d2f0eb', 'padding': '20px', 'margin-top': '0.5in'}),  # increased padding for the outline

            html.Div(
                id='poi-graph-container',
                children=[
                    dcc.Graph(id='top-graphic', style={'width': '48%', 'height': '1000px'}),
                    dcc.Graph(id='bottom-graphic', style={'width': '48%', 'height': '1000px'})
                ],
                style={'display': 'flex', 'justify-content': 'space-between'}
            ),
        ]),

        dcc.Tab(label='Recommendations', value='tab-3', children=[
            html.Div([
                dbc.Row([
                    dbc.Col(zip_dropdown, width=6),
                    dbc.Col(knn_slider, width=6),
                ], style={'border': '3px solid 	#d2f0eb', 'padding': '20px','margin-top': '0.5in'}),

                    switch_all_categories,
                    checklist1,
                    update_button,
                    knn_table,
                    dbc.Container(
                        dbc.Row(
                            [
                                dbc.Col(poi_table, width=4),
                                dbc.Col(poi_table2, width=4),
                            ],
                            justify="around",
                        ),
                        fluid=True,
                        style={"marginTop": "0.2in"},
                    ),
                    # dbc.Container(
                    #     dbc.Row(
                    #         [dbc.Col(poi_table), dbc.Col(poi_table2)],
                    #     ),
                    #     fluid=True,
                    #     style={"marginTop": "0.2in"}
                    # ),

                    dcc.Loading(
                        id="graph-loading",
                        type="circle",
                        children=[
                            dcc.Graph(
                                id="map2",
                                style={'height': '1000px', 'width': '100%', 'margin-left': '20px', 'margin-right': '20px'},
                                config={'displayModeBar': False}
                            )
                        ],
                        style={'width': '100%', 'margin': 'auto', 'display': 'flex', 'justify-content': 'center',
                               'height': '800px'}
                    )

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

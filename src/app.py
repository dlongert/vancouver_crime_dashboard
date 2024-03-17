import pandas as pd
import altair as alt
import calendar
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from collections import Counter
import base64

alt.data_transformers.disable_max_rows()
crime = pd.read_csv("data/processed/crime_processed.csv")
crime = crime.dropna()
crime["HUNDRED_BLOCK"] = crime["HUNDRED_BLOCK"].str.replace("\d*X+ ", "", regex=True)
crime['DATE'] = pd.to_datetime(crime[['YEAR', 'MONTH', 'DAY']])

# map plot
vancouver_coordinates = {"lat": 49.25, "lon": -123.075833}

# heatmap trace
heatmap_trace = go.Densitymapbox(
    lat=crime['Latitude'],
    lon=crime['Longitude'],
    z=crime.index,
    radius=10,
    colorscale='plasma',
    colorbar=dict(
        title='Density'
    ),
)

layout = go.Layout(
    title='<b>Vancouver City Map</b>',
    title_x=0.5,
    title_y=0.9,
    title_font=dict(size=24),
    mapbox=dict(
        style="carto-positron",
        center=vancouver_coordinates,
        zoom=10
    ),
    height=700,
    width=1000
)

fig = go.Figure(data=heatmap_trace, layout=layout)

def neighbourhood_crime_plot(selected_neighbourhoods):
    filtered_crime = crime[crime['NEIGHBOURHOOD'].isin(selected_neighbourhoods)]
    chart = alt.Chart(filtered_crime).mark_bar().encode(
        x=alt.X("count()", title="Number of Crimes"),
        y=alt.Y("NEIGHBOURHOOD", title = None, sort='-x'),
        tooltip=["NEIGHBOURHOOD", 'count()']
    ).properties(title="Number of Crimes by Neighbourhood", height=300, width=400)
    return chart.to_html()

def street_crime_plot(selected_crime_types):
    filtered_crime = crime[crime['TYPE'].isin(selected_crime_types)]
    street_counts = filtered_crime['HUNDRED_BLOCK'].str.replace("\d*X+ ", "", regex=True).value_counts().reset_index()
    street_counts.columns = ['STREET_NAME', 'count']
    top_streets = street_counts.sort_values(by='count', ascending=False).head(5)['STREET_NAME']
    filtered_crime = filtered_crime[filtered_crime['HUNDRED_BLOCK'].str.replace("\d*X+ ", "", regex=True).isin(top_streets)]
    chart = alt.Chart(filtered_crime).mark_bar().encode(
        alt.X("count()", title="Number of Crimes"),
        alt.Y("HUNDRED_BLOCK", title=None, sort='-x'),
        tooltip=["HUNDRED_BLOCK", 'count()']
    ).properties(title="Top 5 Streets by Number of Crimes", height=300, width=400)
    return chart.to_html()

def map_month_to_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    elif month in [9, 10, 11]:
        return 'Fall'

crime['SEASON'] = crime['MONTH'].apply(map_month_to_season)
crime['MONTH'] = crime['MONTH'].apply(lambda x: calendar.month_name[x])

def crimes_by_year(selected_years_range, selected_crime_types):
    filtered_crime = crime[(crime['YEAR'] >= selected_years_range[0]) & (crime['YEAR'] <= selected_years_range[1])]
    filtered_crime = filtered_crime[filtered_crime['TYPE'].isin(selected_crime_types)]
    chart = alt.Chart(filtered_crime).mark_bar().encode(
        alt.X('YEAR:O', title=None,  axis=alt.Axis(labelAngle=45)),
        alt.Y('count():Q', title="Number of Crimes"),
        color='TYPE:N',
        tooltip=['YEAR', 'count()']
    ).properties(title='Number of Crimes by Year', height=300, width=400)
    return chart.to_html()

def crimes_by_season(selected_years_range, selected_crime_types):
    filtered_crime = crime[(crime['YEAR'].between(selected_years_range[0], selected_years_range[1])) & 
                           (crime['TYPE'].isin(selected_crime_types))]
    chart = alt.Chart(filtered_crime).mark_line(point=True).encode(
        alt.X('SEASON:N', title=None,  axis=alt.Axis(labelAngle=0)),
        alt.Y('count():Q', title="Number of Crimes"),
        color='TYPE:N',
        tooltip=['SEASON', 'count()']
    ).properties(title='Number of Crimes by Season', height=300, width=400)
    return chart.to_html()

def crimes_by_day(selected_years_range, selected_crime_types, selected_month):
    filtered_crime = crime[(crime['YEAR'].between(selected_years_range[0], selected_years_range[1])) & 
                           (crime['TYPE'].isin(selected_crime_types)) &
                           (crime['MONTH'] == selected_month)]
    chart = alt.Chart(filtered_crime).mark_point().encode(
        alt.X('DAY:O', title="Day", axis=alt.Axis(labelAngle=0)),
        alt.Y('count():Q', title="Number of Crimes"),
        color='TYPE:N',
        tooltip=['DAY', 'count()']
    ).properties(title=f'Number of Crimes in {selected_month}', height=300, width=500)
    return chart.to_html()

app = dash.Dash(__name__, title = "Crime in Vancouver", external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

logo_filename = 'image_folder/WechatIMG2476.png' 
encoded_logo = base64.b64encode(open(logo_filename, 'rb').read())
app.layout = dbc.Container([
     dbc.Row([
        dbc.Col(html.Div(), width=9),  
        dbc.Col(
            html.Img(
                src='data:image/png;base64,{}'.format(encoded_logo.decode()),
                style={'height': '100px', 'float': 'right'}  
            ),
            width=3
        ),
    ]),
    dbc.Tabs([
        dbc.Tab([
            html.Div('Geographic Analysis of Crime in Vancouver', style={'color': 'red', 'fontSize': 44, 'textAlign': 'center'}),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H3('Most Dangerous Vancouver Neighbourhood:', style={'fontSize': 24, 'textAlign': 'center'}),
                        html.H4(id='most_dangerous_neighbourhood', style={'color': 'blue', 'fontSize': 24, 'textAlign': 'center'}),
                    ])
                ], width=6),
                dbc.Col([
                    html.Div([
                        html.H3('Most Dangerous Vancouver Street:', style={'fontSize': 24, 'textAlign': 'center'}),
                        html.H4(id='most_dangerous_street', style={'color': 'blue','fontSize': 24, 'textAlign': 'center'}),
                    ])
                ], width=6)
            ], style={'margin': 'auto', 'width': '80%', 'marginTop': '20px'}),
            html.Div([
                dbc.Container([
                    dbc.Row([
                        dbc.Col(
                            html.Label('Select Crime Type:', style={'textAlign': 'center'}),
                            width={'size': 10, 'offset': 2},
                            style={'marginTop': '20px'} 
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id='crime-type-map-dropdown-db',
                                options=[{'label': crime_type, 'value': crime_type} for crime_type in crime["TYPE"].unique()],
                                value=[crime["TYPE"].unique()[2]],
                                multi=True),
                                width={'size': 7, 'offset': 2},
                                style={'textAlign': 'center'}
                        ),
                    ]),
                    dbc.Row([
                        dbc.Col(
                            dcc.Graph(id='crime-heatmap', figure=fig, config={'displayModeBar': False}),
                            width={'size': 10, 'offset': 1}
                        )
                    ])
                ])
            ]),
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Label('Select Neighbourhood:', style={'textAlign': 'center'}),
                            dcc.Dropdown(
                                id='neighbourhood-dropdown',
                                options=[{'label': neighbourhood, 'value': neighbourhood} for neighbourhood in crime["NEIGHBOURHOOD"].unique()],
                                value=[crime["NEIGHBOURHOOD"].unique()[i] for i in range(5)], multi=True),
                        ], style={'textAlign': 'center', 'marginBottom': '20px'}),
                        html.Iframe(id='neighbourhood-chart',
                                    srcDoc=neighbourhood_crime_plot([crime["NEIGHBOURHOOD"].unique()[i] for i in range(5)]),
                                    style={'borderWidth': '0', 'width': '100%', 'height': '400px'})
                    ], width=6),
                    dbc.Col([
                        html.Label('Select Crime Type:', style={'textAlign': 'center'}),
                        dcc.Dropdown(
                            id='crime-type-dropdown-db',
                            options=[{'label': crime_type, 'value': crime_type} for crime_type in crime["TYPE"].unique()],
                            value=[crime["TYPE"].unique()[i] for i in range(5)], multi=True, style={'marginBottom': '20px'}
                            ),
                        html.Iframe(id='street-chart',
                                    srcDoc=street_crime_plot([crime["TYPE"].unique()[2]]),
                                    style={'borderWidth': '0', 'width': '100%', 'height': '400px'})
                    ], width=6)
                ], style={'marginTop': 50})
            ])
        ],
        label='Vancouver Geography'),

        dbc.Tab([
            html.Div('Temporal Analysis of Crime in Vancouver', style={'color': 'blue', 'fontSize': 44, 'textAlign': 'center'}),
            html.Div([
                html.Label('Select Crime Type:'),
                dcc.Dropdown(
                    id='crime-type-dropdown',
                    options=[{'label': crime_type, 'value': crime_type} for crime_type in crime["TYPE"].unique()],
                    value=[crime["TYPE"].unique()[0]],
                    multi=True),
                html.Label('Select Year:', style={'marginTop': 50}),
                html.Div(
                    dcc.RangeSlider(
                        id='year-slider',
                        min=min(crime['YEAR']),
                        max=max(crime['YEAR']),
                        value=[min(crime['YEAR']), max(crime['YEAR'])],
                        marks={str(year): str(year) for year in range(min(crime['YEAR']), max(crime['YEAR']) + 1)},
                        step=None
                    ),
                    style={'width': '50%', 'textAlign': 'center'}
                ),
                html.Div([
                    html.Div([
                        html.Iframe(id='year-chart', style={'borderWidth': '0', 'width': '100%', 'height': '400px', 'textAlign': 'center'}),
                    ]),
                    html.Div([
                        html.Iframe(id='season-chart', style={'borderWidth': '0', 'width': '50%', 'height': '400px', 'display': 'inline-block'}),
                        html.Iframe(id='day-chart', style={'borderWidth': '0', 'width': '50%', 'height': '400px', 'display': 'inline-block'})
                    ], style={'display': 'flex'}),
                    html.Div([
                        html.Div([
                            html.Label('Select Month:', style={'marginTop': '20px'}),
                        ], style={'textAlign': 'center'}),
                        dcc.Dropdown(
                            id='month-dropdown',
                            options=[{'label': calendar.month_name[i], 'value': calendar.month_name[i]} for i in range(1, 13)],
                            value='January',
                            style={'width': '50%', 'margin-left': '5px', 'margin-right': '0'}
                        ),
                    ], style={'textAlign': 'center', 'width': '100%', 'display': 'flex', 'justifyContent': 'flex-end'})
                ]),
            ], style={'marginTop': 50}),
        ],
            label='Vancouver Temporal Crime')
    ])
])

@app.callback(
    [Output('crime-heatmap', 'figure'),
     Output('neighbourhood-chart', 'srcDoc'),
     Output('street-chart', 'srcDoc'),
     Output('most_dangerous_neighbourhood', 'children'),
     Output('most_dangerous_street', 'children')],
    [Input('crime-type-map-dropdown-db', 'value'),
     Input('neighbourhood-dropdown', 'value')])

def update_data_geographic(selected_crime_types_map, selected_neighbourhoods):
    # Filter data based on selected inputs
    filtered_data_map = crime[crime['TYPE'].isin(selected_crime_types_map)]
    filtered_data_neighbourhood = crime[crime['NEIGHBOURHOOD'].isin(selected_neighbourhoods)]
    filtered_data_db = crime[crime['TYPE'].isin(selected_crime_types_map)]

    # Update heatmap figure
    heatmap_trace = go.Densitymapbox(
        lat=filtered_data_map['Latitude'],
        lon=filtered_data_map['Longitude'],
        z=filtered_data_map.index,
        radius=10,
        colorscale='plasma',
        colorbar=dict(title='Density'),
    )

    layout = go.Layout(
        title='<b>Vancouver City Map</b>',
        title_x=0.5,
        title_y=0.9,
        title_font=dict(size=24),
        mapbox=dict(
            style="carto-positron",
            center=vancouver_coordinates,
            zoom=10
        ),
        height=700,
        width=1000
    )

    updated_fig = go.Figure(data=heatmap_trace, layout=layout)

    # Update other charts
    neighbourhood_html = neighbourhood_crime_plot(selected_neighbourhoods)
    street_html = street_crime_plot(selected_crime_types_map)

    # Calculate the most dangerous Vancouver neighbourhood
    most_dangerous_neighbourhood = Counter(filtered_data_neighbourhood['NEIGHBOURHOOD']).most_common(1)[0][0]

    # Calculate the most dangerous Vancouver street
    most_dangerous_street = Counter(filtered_data_db['HUNDRED_BLOCK']).most_common(1)[0][0]

    return (updated_fig, neighbourhood_html, street_html,
            most_dangerous_neighbourhood,
            most_dangerous_street)

@app.callback(
    [Output('year-chart', 'srcDoc'),
     Output('season-chart', 'srcDoc'),
     Output('day-chart', 'srcDoc')],
    [Input('year-slider', 'value'),
     Input('crime-type-dropdown', 'value'),
     Input('month-dropdown', 'value')])

def update_data_temporal(selected_years_range, selected_crime_types_temporal, selected_month):
    # Filter data based on selected inputs
    year_html = crimes_by_year(selected_years_range, selected_crime_types_temporal)
    season_html = crimes_by_season(selected_years_range, selected_crime_types_temporal)
    day_html = crimes_by_day(selected_years_range, selected_crime_types_temporal, selected_month)
    return (year_html, season_html, day_html)


if __name__ == '__main__':
    app.run_server(debug=True)

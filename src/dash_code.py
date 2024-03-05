import pandas as pd
import altair as alt
import vegafusion as vf
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# vf.enable()
crime = pd.read_csv("data/processed/crime_processed.csv")
crime = crime.dropna()
crime = crime.loc[1:5000]
crime['DATE'] = pd.to_datetime(crime[['YEAR', 'MONTH', 'DAY']])

# map plot
vancouver_coordinates = {"lat": 49.25, "lon": -123.075833}

map_trace = go.Scattermapbox(
    lat=[vancouver_coordinates["lat"]],
    lon=[vancouver_coordinates["lon"]],
    mode="markers",
    marker=dict(size=14, color="red"),
    text=["Vancouver"],
    hoverinfo="text"
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

fig = go.Figure(data=map_trace, layout=layout)

def neighbourhood_crime_plot(selected_neighbourhoods):
    filtered_crime = crime[crime['NEIGHBOURHOOD'].isin(selected_neighbourhoods)]
    chart = alt.Chart(filtered_crime).mark_bar().encode(
        alt.X("count()", title="Number of Crimes"),
        alt.Y("NEIGHBOURHOOD", title="Neighbourhood")
    ).properties(title="Number of Crimes by Neighbourhood", height=200, width=200)
    return chart.to_html()

def street_crime_plot(selected_crime_types):
    filtered_crime = crime[crime['TYPE'].isin(selected_crime_types)]
    street_counts = filtered_crime['HUNDRED_BLOCK'].value_counts().reset_index()
    street_counts.columns = ['HUNDRED_BLOCK', 'count']
    top_streets = street_counts.sort_values(by='count', ascending=False).head(5)['HUNDRED_BLOCK']  
    filtered_crime = filtered_crime[filtered_crime['HUNDRED_BLOCK'].isin(top_streets)]   
    chart = alt.Chart(filtered_crime).mark_bar().encode(
        alt.X("HUNDRED_BLOCK", title=None),
        alt.Y("count()", title="Number of Crimes")
    ).properties(title="Top 5 Streets by Number of Crimes", height=200, width=200)
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

def crimes_by_year(selected_crime_types):
    filtered_crime = crime[crime['TYPE'].isin(selected_crime_types)]
    chart = alt.Chart(filtered_crime).mark_bar().encode(
        x='YEAR:O',
        y='count():Q',
        color='TYPE:N',
        tooltip=['YEAR', 'count()']
    ).properties(title='Number of Crimes by Year')
    return chart.to_html()

def crimes_by_season(selected_crime_types):
    filtered_crime = crime[crime['TYPE'].isin(selected_crime_types)]
    chart = alt.Chart(filtered_crime).mark_line(point=True).encode(
        x='SEASON:N',
        y='count():Q',
        color='TYPE:N',
        tooltip=['SEASON', 'count()']
    ).properties(title='Number of Crimes by Season')
    return chart.to_html() 

def crimes_by_day(selected_crime_types):
    filtered_crime = crime[crime['TYPE'].isin(selected_crime_types)]
    chart = alt.Chart(filtered_crime).mark_point().encode(
        x='DAY:O',
        y='count():Q',
        color='TYPE:N',
        tooltip=['DAY', 'count()']
    ).properties(title='Number of Crimes by Day')
    return chart.to_html()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
    dbc.Tabs([
        dbc.Tab([
            html.P('Geographic Analysis of Crime in Vancouver', style={'color': 'red', 'fontSize': 44, 'textAlign': 'center'}),
            html.Div([
                dbc.Container(
                    dbc.Row(
                        dbc.Col(
                            dcc.Graph(figure=fig, config={'displayModeBar': False}),
                            width={'size': 10, 'offset': 1}
                        )
                    )
                )
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
                        ], style={'textAlign': 'center'}),
                        html.Iframe(id='neighbourhood-chart',
                                    srcDoc=neighbourhood_crime_plot([crime["NEIGHBOURHOOD"].unique()[i] for i in range(5)]),
                                    style={'border-width': '0', 'width': '100%', 'height': '400px'})
                    ], width=6),
                    dbc.Col([
                        html.Label('Select Crime Type:'),
                        dcc.Dropdown(
                            id='crime-type-dropdown-db',
                            options=[{'label': crime_type, 'value': crime_type} for crime_type in crime["TYPE"].unique()],
                            value=[crime["TYPE"].unique()[2]],
                            multi=True),
                        html.Iframe(id='street-chart',
                                    srcDoc=street_crime_plot([crime["TYPE"].unique()[2]]),
                                    style={'border-width': '0', 'width': '100%', 'height': '400px'})
                    ], width=6)
                ], style={'marginTop': 50})
            ])
        ],
        label='Vancouver Geography'),
            
        dbc.Tab([
            html.P('Temporal Analysis of Crime in Vancouver', style={'color': 'blue', 'fontSize': 44, 'textAlign': 'center'}),
            html.P([
                html.Label('Select Crime Type:'),
                dcc.Dropdown(
                    id='crime-type-dropdown',
                    options=[{'label': crime_type, 'value': crime_type} for crime_type in crime["TYPE"].unique()],
                    value=[crime["TYPE"].unique()[0]],
                    multi=True),
                html.Div([
                    html.Div([
                        html.Iframe(id='year-chart', style={'border-width': '0', 'width': '100%', 'height': '400px', 'textAlign': 'center'}),
                    ], style={'textAlign': 'center'}),
                    html.Div([
                        html.Iframe(id='season-chart', style={'border-width': '0', 'width': '50%', 'height': '400px', 'display': 'inline-block'}),
                        html.Iframe(id='day-chart', style={'border-width': '0', 'width': '50%', 'height': '400px', 'display': 'inline-block'})
                    ], style={'textAlign': 'center'})
                ]),
            ], style={'marginTop': 50}),
        ], 
        label='Vancouver Temporal Crime')
    ])
])

@app.callback(
    [Output('neighbourhood-chart', 'srcDoc'),
     Output('street-chart', 'srcDoc'),
     Output('year-chart', 'srcDoc'),
     Output('season-chart', 'srcDoc'),
     Output('day-chart', 'srcDoc')],
    [Input('neighbourhood-dropdown', 'value'),
     Input('crime-type-dropdown-db', 'value'),
     Input('crime-type-dropdown', 'value')])

def update_charts(selected_neighbourhoods, selected_crime_types, selected_crime_types_temporal):
    neighbourhood_html = neighbourhood_crime_plot(selected_neighbourhoods)
    street_html = street_crime_plot(selected_crime_types)
    year_html = crimes_by_year(selected_crime_types_temporal)
    season_html = crimes_by_season(selected_crime_types_temporal)
    day_html = crimes_by_day(selected_crime_types_temporal)
    return neighbourhood_html, street_html, year_html, season_html, day_html

if __name__ == '__main__':
    app.run_server(debug=True)

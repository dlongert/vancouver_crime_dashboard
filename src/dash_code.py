import pandas as pd
import altair as alt
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

crime = pd.read_csv("data/processed/crime_processed.csv")
crime = crime.loc[1:500]
crime['DATE'] = pd.to_datetime(crime[['YEAR', 'MONTH', 'DAY']])


def neighbourhood_crime_plot(selected_neighbourhoods):
    filtered_crime = crime[crime['NEIGHBOURHOOD'].isin(selected_neighbourhoods)]
    chart = alt.Chart(filtered_crime).mark_bar().encode(
        alt.X("count()", title="Number of crimes by neighbourhood"),
        alt.Y("NEIGHBOURHOOD", title="Neighbourhood")
    )
    return chart.to_html()

def street_crime_plot(selected_crime_types):
    filtered_crime = crime[crime['TYPE'].isin(selected_crime_types)]
    chart = alt.Chart(filtered_crime).mark_bar().encode(
        alt.X("HUNDRED_BLOCK", title="Street Name"),
        alt.Y("count()", title="Number of crimes per street")
    )
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
    chart = alt.Chart(filtered_crime).mark_point().encode(  # Changed from mark_bar to mark_point
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
            html.P([
                html.Label('Select Neighbourhood:'),
                dcc.Dropdown(
                    id='neighbourhood-dropdown',
                    options=[{'label': neighbourhood, 'value': neighbourhood} for neighbourhood in crime["NEIGHBOURHOOD"].unique()],
                    value=[crime["NEIGHBOURHOOD"].unique()[0]],
                    multi=True),
                html.Iframe(id='neighbourhood-chart',
                    srcDoc=neighbourhood_crime_plot([crime["NEIGHBOURHOOD"].unique()[0]]),
                    style={'border-width': '0', 'width': '100%', 'height': '400px'})
            ]),
            html.P([
                html.Label('Select Crime Type:'),
                dcc.Dropdown(
                    id='crime-type-dropdown-db',
                    options=[{'label': crime_type, 'value': crime_type} for crime_type in crime["TYPE"].unique()],
                    value=[crime["TYPE"].unique()[2]],
                    multi=True),
                html.Iframe(id='street-chart',
                    srcDoc=street_crime_plot([crime["TYPE"].unique()[2]]),
                    style={'border-width': '0', 'width': '100%', 'height': '400px'})
            ], style={'marginTop': 50})
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
            html.Iframe(id='year-chart', style={'border-width': '0', 'width': '100%', 'height': '400px'}),
            html.Iframe(id='season-chart', style={'border-width': '0', 'width': '100%', 'height': '400px'}),
            html.Iframe(id='day-chart', style={'border-width': '0', 'width': '100%', 'height': '400px'})
        ], style={'marginTop': 50}),
    ], 
        label='Vancouver Temporal Crime')
    ])
])

@app.callback(
    Output('neighbourhood-chart', 'srcDoc'),
    Input('neighbourhood-dropdown', 'value'))

def update_neighbourhood_chart(selected_neighbourhoods):
    return neighbourhood_crime_plot(selected_neighbourhoods)

@app.callback(
    Output('street-chart', 'srcDoc'),
    Input('crime-type-dropdown-db', 'value'))

def update_street_chart(selected_crime_types):
    return street_crime_plot(selected_crime_types)

@app.callback(
    [Output('year-chart', 'srcDoc'),
     Output('season-chart', 'srcDoc'),
     Output('day-chart', 'srcDoc')],
    Input('crime-type-dropdown', 'value'))

def update_charts(selected_crime_types):
    year_html = crimes_by_year(selected_crime_types)
    season_html = crimes_by_season(selected_crime_types)
    day_html = crimes_by_day(selected_crime_types)
    return year_html, season_html, day_html

if __name__ == '__main__':
    app.run_server(debug=True)

import pandas as pd
import altair as alt
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

crime = pd.read_csv("data/processed/crime_processed.csv")
crime = crime.loc[1:500]

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

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
    dbc.Tabs([
        dbc.Tab([
            html.P('Geographic Analysis of Crime', style={'color': 'red', 'fontSize': 44}),
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
                    id='crime-type-dropdown',
                    options=[{'label': crime_type, 'value': crime_type} for crime_type in crime["TYPE"].unique()],
                    value=[crime["TYPE"].unique()[2]],
                    multi=True),
                html.Iframe(id='street-chart',
                    srcDoc=street_crime_plot([crime["TYPE"].unique()[2]]),
                    style={'border-width': '0', 'width': '100%', 'height': '400px'})
            ])
        ],
        label='Vancouver Geography'),
            
        dbc.Tab("KATO AND TOMMY'S SIDE OF THE DASH", label='Tab two')])])

@app.callback(
    Output('neighbourhood-chart', 'srcDoc'),
    Input('neighbourhood-dropdown', 'value'))

def update_neighbourhood_chart(selected_neighbourhoods):
    return neighbourhood_crime_plot(selected_neighbourhoods)

@app.callback(
    Output('street-chart', 'srcDoc'),
    Input('crime-type-dropdown', 'value'))

def update_street_chart(selected_crime_types):
    return street_crime_plot(selected_crime_types)

if __name__ == '__main__':
    app.run_server(debug=True)
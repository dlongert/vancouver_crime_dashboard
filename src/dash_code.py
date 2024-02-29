import pandas as pd
import altair as alt
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

crime = pd.read_csv("data/processed/crime_processed.csv")
crime = crime.iloc[1:100]

def neighbourhood_crime(selected_neighbourhoods):
    filtered_crime = crime[crime['NEIGHBOURHOOD'].isin(selected_neighbourhoods)]
    chart = alt.Chart(filtered_crime).mark_bar().encode(
        alt.X("count()", title="Number of crimes by neighbourhood"),
        alt.Y("NEIGHBOURHOOD", title="Neighbourhood")
    )
    return chart.to_html()

def street_crime(selected_crime_types):
    filtered_crime = crime[crime['TYPE'].isin(selected_crime_types)]
    chart = alt.Chart(filtered_crime).mark_bar().encode(
        alt.X("HUNDRED_BLOCK", title="Street Name"),
        alt.Y("count()", title="Number of crimes per street")
    )
    return chart.to_html()

app = dash.Dash(__name__)
app.layout = html.Div([
    html.Div('Geographic Analysis of Crime', style={'color': 'red', 'fontSize': 44}),
    html.P(['Longitude', dcc.Slider(min=-125, max=0, value=2, marks={-125: '-125', 0: '0'})]),
    html.P(['Latitude', dcc.Slider(min=0, max=50, value=2, marks={0: '0', 50: '50'})]),
    
    html.Div([
        html.Label('Select Neighbourhood:'),
        dcc.Dropdown(
            id='neighbourhood-dropdown',
            options=[{'label': neighbourhood, 'value': neighbourhood} for neighbourhood in crime["NEIGHBOURHOOD"].unique()],
            value=[crime["NEIGHBOURHOOD"].unique()[0]],
            multi=True),
        html.Iframe(id='neighbourhood-chart',
                    srcDoc=neighbourhood_crime([crime["NEIGHBOURHOOD"].unique()[0]]),
                    style={'border-width': '0', 'width': '100%', 'height': '400px'})
    ]),
    html.Div([
        html.Label('Select Crime Type:'),
        dcc.Dropdown(
            id='crime-type-dropdown',
            options=[{'label': crime_type, 'value': crime_type} for crime_type in crime["TYPE"].unique()],
            value=[crime["TYPE"].unique()[2]],
            multi=True),
        html.Iframe(id='street-chart',
                    srcDoc=street_crime([crime["TYPE"].unique()[2]]),
                    style={'border-width': '0', 'width': '100%', 'height': '400px'})
    ]),
], style={'marginTop': 50})
@app.callback(
    Output('neighbourhood-chart', 'srcDoc'),
    Input('neighbourhood-dropdown', 'value'))

def update_neighbourhood_chart(selected_neighbourhoods):
    return neighbourhood_crime(selected_neighbourhoods)

@app.callback(
    Output('street-chart', 'srcDoc'),
    Input('crime-type-dropdown', 'value'))

def update_street_chart(selected_crime_types):
    return street_crime(selected_crime_types)

if __name__ == '__main__':
    app.run_server(debug=True)
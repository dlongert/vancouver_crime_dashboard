import pandas as pd
import altair as alt
import dash
from dash import dcc, html

crime = pd.read_csv("data/processed/crime_processed.csv")
crime = crime.iloc[1:100]


def neighbourhood_crime():
    chart = alt.Chart(crime).mark_bar().encode(
    alt.X("count()", title = "Number of crimes by neighbourhood"),
    alt.Y("NEIGHBOURHOOD", title = "Neighbourhood")
    )
    return chart.to_html()

def street_crime():
    chart = alt.Chart(crime).mark_bar().encode(
    alt.X("HUNDRED_BLOCK", title = "Street Name"),
    alt.Y("count()", title = "Number of crimes per street")
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
            id='Neighbourhood',
            options=[row for row in crime["NEIGHBOURHOOD"].unique()],
            value=crime["NEIGHBOURHOOD"].unique()[0],
            multi = True),
        html.Iframe(srcDoc=neighbourhood_crime(),
                    style={'border-width': '0', 'width': '100%', 'height': '400px'})]),

    html.Div([
        html.Label('Select Crime Type:'),
        dcc.Dropdown(
            id='Crime Type',
            options=[{'label': row, 'value': row} for row in crime["TYPE"].unique()],
            value=crime["TYPE"].unique()[2],
            multi = True),
        html.Iframe(srcDoc=street_crime(),
                    style={'border-width': '0', 'width': '100%', 'height': '400px'})
    ]),
], style={'marginTop': 50})

if __name__ == '__main__':
    app.run_server(debug=True)
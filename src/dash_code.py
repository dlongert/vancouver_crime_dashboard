import pandas as pd
import dash
from dash import dcc, html

crime = pd.read_csv("data/raw/crime.csv")

app = dash.Dash(__name__)
app.layout = html.Div([
    html.Div('Geographic Analysis of Crime', style={'color': 'red', 'fontSize': 44}), 
    html.P(['Longitude', dcc.Slider(min=-125, max=0, value=2, marks={-125: '-125', 0: '0'})]),
    html.P(['Latitude', dcc.Slider(min=0, max=50, value=2, marks={0: '0', 50: '50'})]),
    html.P([dcc.Dropdown(
            id='Neighbourhood',
            options=[row for row in crime["NEIGHBOURHOOD"].unique()],
            value=crime["NEIGHBOURHOOD"].unique()[0])
    ]),
    html.P([dcc.Dropdown(
        id='Crime Type',
        options=[row for row in crime["TYPE"].unique()],
        value=crime["TYPE"].unique()[2])
    ]),
], style={'marginTop': 50})

if __name__ == '__main__':
    app.run_server(debug=True)


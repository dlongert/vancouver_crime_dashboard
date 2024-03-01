import pandas as pd
import altair as alt
import dash
from dash import dcc, html
from dash.dependencies import Input, Output


crime = pd.read_csv('/Users/zhaoxunyan/Desktop/data551/crime_processed.csv')
crime = crime.iloc[1:100] 
crime['DATE'] = pd.to_datetime(crime[['YEAR', 'MONTH', 'DAY']])



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
    chart = alt.Chart(filtered_crime).mark_bar().encode(
        x='SEASON:N',
        y='count():Q',
        color='TYPE:N',
        tooltip=['SEASON', 'count()']
    ).properties(title='Number of Crimes by Season')
    return chart.to_html()

def crimes_by_day(selected_crime_types):
    filtered_crime = crime[crime['TYPE'].isin(selected_crime_types)]
    chart = alt.Chart(filtered_crime).mark_bar().encode(
        x='DAY:O',
        y='count():Q',
        color='TYPE:N',
        tooltip=['DAY', 'count()']
    ).properties(title='Number of Crimes by Day')
    return chart.to_html()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div('Geographic Analysis of Crime', style={'color': 'red', 'fontSize': 44}),
    html.Div([
        html.Label('Select Crime Type:'),
        dcc.Dropdown(
            id='crime-type-dropdown',
            options=[{'label': crime_type, 'value': crime_type} for crime_type in crime["TYPE"].unique()],
            value=[crime["TYPE"].unique()[0]],
            multi=True),
        html.Iframe(id='year-chart', style={'border-width': '0', 'width': '100%', 'height': '400px'}),
        html.Iframe(id='season-chart', style={'border-width': '0', 'width': '100%', 'height': '400px'}),
        html.Iframe(id='day-chart', style={'border-width': '0', 'width': '100%', 'height': '400px'})
    ]),
], style={'marginTop': 50})

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
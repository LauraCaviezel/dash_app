#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

df = pd.read_csv('nama_10_gdp_1_Data.csv')

import numpy as np

# Change Value column into numbers, drop zero's
df['Value'] = df['Value'].str.replace('.', '')
df['Value'] = df['Value'].str.replace(',', '.')

# Remove NA's (:) and 0.0
df = df[df['Value'] != ':']
df = df[df['Value'] != '0.0']
df['Value'] = df['Value'].astype(np.float)
df['GEO'] = df['GEO'].astype(str)
df.dtypes
df = df[~df['GEO'].str.contains('Euro')]

# There are multiple values in different units per year so we only keep current prices
df = df[~df['UNIT'].str.startswith('Chain')]


app = dash.Dash(__name__)
server = app.server

available_indicators = df['NA_ITEM'].unique()

app.layout = html.Div([
    html.Div([

        # Define the two dropdowns and their layout
        html.Div([
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Indicator 1'
            ),
            dcc.RadioItems(
                id='crossfilter-xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Indicator 2'
            ),
            dcc.RadioItems(
                id='crossfilter-yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '48%', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),

    # Define the first graph (scatterplot)
    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'customdata': 'Belgium'}]}
        )
    ], style={'width': '100%', 'display': 'inline-block', 'padding': '15px 5px'}),
    
    # Next define the slider
    html.Div(dcc.Slider(
       id='crossfilter-year--slider',
       min=df['TIME'].min(),
       max=df['TIME'].max(),
       value=df['TIME'].max(),
       marks={str(year): str(year) for year in df['TIME'].unique()}
    )
             , style={'width': '94%', "display": "block",
            "margin-left": "auto",
            "margin-right": "auto"}),
   
    # Define the time series graph, set background transparent
    html.Div([
        dcc.Graph(id='x-time-series'),
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(0, 0, 0, 0)',
        'padding': '50px 5px'
    })

])

# Change Scatterplot based on input from the two dropdown menus and the slider
@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-type', 'value'),
     dash.dependencies.Input('crossfilter-year--slider', 'value')])

def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 year_value):
    dff = df[df['TIME'] == year_value]

    return {
        'data': [go.Scatter(
            x=dff[dff['NA_ITEM'] == xaxis_column_name]['Value'],
            y=dff[dff['NA_ITEM'] == yaxis_column_name]['Value'],
            text=dff[dff['NA_ITEM'] == yaxis_column_name]['GEO'],
            customdata=dff[dff['NA_ITEM'] == yaxis_column_name]['GEO'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 70, 'b': 100, 't': 60, 'r': 30},
            height=450,
            hovermode='closest'
        )
    }


def create_time_series(dff, axis_type, title):
    return {
        'data': [go.Scatter(
            x=dff['TIME'],
            y=dff['Value'],
            mode='lines+markers'
        )],
        'layout': {
            'height': 225,
            'margin': {'l': 70, 'b': 50, 'r': 30, 't': 100},
            'annotations': [{
                'x': 0.01, 'y': 1, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(0,0,0, 0)',
                'text': title
            }],
            'yaxis': {'type': 'linear' if axis_type == 'Linear' else 'log'},
            'xaxis': {'showgrid': False}
        }
    }

# Change timeseries based on hoverdata from scatterplot
@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value')])

def update_y_timeseries(hoverData, xaxis_column_name, axis_type):
    country_name = hoverData['points'][0]['customdata']
    dff = df[df['GEO'] == country_name]
    dff = dff[dff['NA_ITEM'] == xaxis_column_name]
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(dff, axis_type, title)

if __name__ == '__main__':
    app.run_server(debug=False)


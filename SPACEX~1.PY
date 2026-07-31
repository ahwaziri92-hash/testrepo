# SpaceX Launch Records Dashboard
# Author: Ahmad Waziri
#
# Interactive Plotly Dash app for exploring SpaceX Falcon 9 launch outcomes.
#
# Run with:  python3 spacex_dash_app.py
# Then open the printed local URL (default http://127.0.0.1:8050) in a browser.
#
# Requires spacex_launch_dash.csv in the same directory, with columns:
#   Flight Number, Launch Site, class, Payload Mass (kg),
#   Booster Version, Booster Version Category

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_sites = spacex_df['Launch Site'].unique().tolist()
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in launch_sites
]

# ---------------------------------------------------------------------------
# App layout
# ---------------------------------------------------------------------------
app = Dash(__name__)
app.title = "SpaceX Launch Records Dashboard"

app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 34}
    ),

    # TASK 1: Launch Site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True,
        style={'width': '80%', 'margin': '0 auto', 'textAlign': 'center'}
    ),
    html.Br(),

    # TASK 2: Pie chart of launch success
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):", style={'marginLeft': '10%'}),
    # TASK 3: Payload range slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Payload vs. launch outcome scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# ---------------------------------------------------------------------------
# TASK 2 callback: pie chart of launch success count
# ---------------------------------------------------------------------------
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Total successful launches for all sites, one slice per site
        fig = px.pie(
            spacex_df[spacex_df['class'] == 1],
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # Success vs. failure count for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        counts = filtered_df['class'].value_counts().rename({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            values=counts.values,
            names=counts.index,
            title=f'Success vs. Failure Launches for site {entered_site}'
        )
    return fig


# ---------------------------------------------------------------------------
# TASK 4 callback: payload vs. outcome scatter chart
# ---------------------------------------------------------------------------
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Correlation Between Payload Mass and Launch Outcome'
              + ('' if entered_site == 'ALL' else f' — {entered_site}'),
        labels={'class': 'Launch Outcome (0 = Failure, 1 = Success)'}
    )
    return fig


if __name__ == '__main__':
    app.run(debug=True)

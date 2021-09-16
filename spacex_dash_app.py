# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

dropdownOptions = []
dropdownOptions.extend([{'label': 'All Sites', 'value': 'ALL'}])
dropdownOptions.extend([{'label': k, 'value': k} for k in spacex_df['Launch Site'].unique()])

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=dropdownOptions,
                                            value='ALL',
                                            placeholder='Select a Launch Site here',
                                            searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[min_payload, max_payload],
                                    tooltip={'always_visible': True}
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def render_success_pie_chart(value):
    if value == 'ALL':
        title = 'Total Success Launches By Site'
        df = spacex_df[spacex_df['class'] == 1]
        df = pd.DataFrame(df.groupby('Launch Site').size(), columns=['count'])
        df.reset_index(inplace=True)
        return px.pie(df, values='count', names='Launch Site', title=title)
    else:
        title = 'Total Success Launches for site ' + value
        df = spacex_df[spacex_df['Launch Site'] == value]
        df = pd.DataFrame(df.groupby('class').size(), columns=['count'])
        df.reset_index(inplace=True)
        return px.pie(df, values='count', names='class', title=title)
    

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")]
)
def render_payload_scatter_chart(sitename, payloadrange):
    if sitename == 'ALL':
        title = 'Correlation between Payload and Success for all Sites'
        df = spacex_df[spacex_df['Payload Mass (kg)'].between(payloadrange[0], payloadrange[1])]
        fig = px.scatter(df, x='Payload Mass (kg)', y='class', color='Booster Version Category')
        return fig
    else:
        title = 'Correlation between Payload and Success for ' + sitename
        df = spacex_df[spacex_df['Payload Mass (kg)'].between(payloadrange[0], payloadrange[1])]
        df = df[df['Launch Site'] == sitename]
        fig = px.scatter(df, x='Payload Mass (kg)', y='class', color='Booster Version Category')
        return fig


# Run the app
if __name__ == '__main__':
    app.run_server()

# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv(r'Capstone\data\spacex_launch_dash.csv')
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

slider_marks_dict = {int(x):str(x) for x in range(int(min_payload),int(max_payload),int(1e3))}
slider_marks_dict[int(max_payload)] = str(max_payload)

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1('SpaceX Launch Records Dashboard',
                       style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
        # TASK 1: Add a dropdown list to enable Launch Site selection
        # The default select value is for ALL sites
        dcc.Dropdown(
            id='site-dropdown', 
            options=[
                {'label':'All Sites','value':'ALL'},
                {'label':'CCAFS LC-40','value':'CCAFS LC-40'},
                {'label':'CCAFS SLC-40','value':'CCAFS SLC-40'},
                {'label':'KSC LC-39A','value':'KSC LC-39A'},
                {'label':'VAFB SLC-4E','value':'VAFB SLC-4E'},
            ],
            value='ALL',
            placeholder="Site Selection",
            searchable=True,
            style= { 'width' : '80%', 'margin': 'auto' }
        ),
        html.Br(),

        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(dcc.Graph(id='success-pie-chart',
                           style={'width':'650px','margin':'auto'}
                           )),
        html.Br(),

        html.P("Payload range (Kg):"),
        # TASK 3: Add a slider to select payload range
        dcc.RangeSlider(id='payload-slider',
                        min=min_payload, max=max_payload, step=100,
                        marks=slider_marks_dict,
                        value=[min_payload, max_payload]
                        ),

        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id='success-payload-scatter-chart')),
    ]
)

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        data = filtered_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(
            data, 
            values='class', 
            names='Launch Site', 
            title='Successful Launches by Site'
        )
        return fig
    else:
        # return the outcomes piechart for a selected site
        data = filtered_df.query(f'`Launch Site` == "{entered_site}"')['class'].value_counts(
                ).rename(index={0:'Failure',1:'Success'}).reset_index()
        fig = px.pie(
            data, 
            values='count', 
            names='class', 
            title=f'Success Ratio at {entered_site}'
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), 
               Input(component_id="payload-slider", component_property="value")] )
def get_scatter_chart(entered_site, payload_range):
    site_df = None
    color_selector = None
    if entered_site == 'ALL':
        site_df = spacex_df
        color_selector = 'Launch Site'
    else:
        site_df = spacex_df.query(f'`Launch Site` == "{entered_site}"')
        color_selector = 'Booster Version Category'

    data = site_df.query(f'`Payload Mass (kg)` >= {payload_range[0]} & `Payload Mass (kg)` <= {payload_range[1]}')

    # print(data)
    fig = px.scatter(
        data,
        x='Payload Mass (kg)',
        y='class',
        color=color_selector,
        range_x= (payload_range)
    )
    return fig

# print(spacex_df)

# Run the app
if __name__ == '__main__':
    app.run_server()
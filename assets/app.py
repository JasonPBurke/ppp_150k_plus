###-----------------------------------------------------------------------------------------###
###-----------------------------------------------------------------------------------------###
# Need to eventually implement a config file (.yml or .ini) to load the mapbox_access_token
# from so as to keep it private.  For now it will be exposed in my code
'''
import yaml
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
mapbox_access_token = cfg['mysql']['key]
'''
###-----------------------------------------------------------------------------------------###
###-----------------------------------------------------------------------------------------###

mapbox_access_token = 'pk.eyJ1IjoiZnV6enlsb2dpYzEzIiwiYSI6ImNrY2xjOGR5NTF4eWcycm5xYjY5eXA5ejUifQ.o3nz27PTtPI5JxztLiw_Tw'

from ppp_helper_functions import NAICS_SECTOR_LIST
import pandas as pd 
import numpy as np 
import dash 
import dash_table
import dash_core_components as dcc 
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import plotly.offline as py 
import plotly.graph_objs as go 

# external_stylesheets = ['dash.css']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
df = pd.read_csv("final_state_data.csv")



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

blackbold = {'color': 'black', 'font-weight': 'bold'} # 'color': 'black'
bluebold = {'color': '#7fa9eb', 'font-weight': 'bold'} # 'color': 'black'
####---------------------------------------------------------------#####
# For use with the Sector options below
keys=['label', 'value']


# state_checklist = dbc.Checklist(
#     id='state',
#     options=[{'label':' ' + str(l), 'value':l} for l in sorted(df['State'].unique())],
#     value=[s for s in sorted(df['State'].unique())],
#     className='state_checklist_height dcc_control',
#     style={'overflow-y': 'auto', 'max-height': '150px'},
#     labelCheckedStyle={'color': 'red'},
# )

           # The Map
map_graph=dcc.Graph(id='graph', config={'displayModeBar': False, 'scrollZoom': True},
            style={'height':'80vh'},
)
map_graph.uirevision='FOO'

app.layout = dbc.Container(html.Div([
    html.Div(
            [html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "U.S. Paycheck Protection Program",
                                    style={"margin-bottom": "0px", 'color': '#7fa9eb', 'font-weight': 'bold'},
                                ),
                                html.H5(
                                    " Loan Disbursement Overview", style={"margin-top": "0px", 'color': '#7fa9eb', 'font-weight': 'bold'}
                                ),
                            ]
                        )
                    ],
                    className="twelve columns",
                    id="title",
                ),
            ], 
            id="header",
            className="row flex-display",
            style={"margin-bottom": "10px", 'text-align': 'center'},
        ),
        
    html.Div([

        # Left Column
        html.Div([


            # loan range
            html.Label(children=['Loan Range:'], style=bluebold, className='control_label'),
            dcc.Checklist(id='loan_range',
                          options=[{'label':str(l)[1:], 'value':l} for l in sorted(df['LoanRange'].unique())],
                          value=[l for l in sorted(df['LoanRange'].unique())],
                          className='dcc_control',
            ),

            # State
            html.Label(children=['State:'], style=bluebold, className='control_label'),
            # state_checklist,
            dcc.Checklist(id='state',
                          options=[{'label':' ' + str(l), 'value':l} for l in sorted(df['State'].unique())],
                          value=[s for s in sorted(df['State'].unique())],
                        #   value=['CA'],
                          className='state_checklist_height dcc_control',
                          style={'overflow-y': 'auto', 'max-height': '150px'},
            ),

            # # Lender
            # html.Label(children=['Lender:'], style=bluebold),
            # dcc.Checklist(id='lender',
            #               options=[{'label':str(l), 'value':l} for l in sorted(df['Lender'].unique())],
            #               value=[l for l in sorted(df['Lender'].unique())],
            # ),

            # NAICS Code Sectors

            html.Label(children=['Buisness Sector:'], style=bluebold, className='control_label'),
            dcc.Checklist(id='sectors',
                          options=[{ k:v for (k,v) in zip(keys, n)} for n in NAICS_SECTOR_LIST],
                          value=[k[1] for k in NAICS_SECTOR_LIST],
                          className='sector_checklist_height dcc_control', #
                          style={'overflow-y': 'auto'},
            ),
            
        ], className='pretty_container three columns media_xs_order_last', style={'min-width': '150px'}),#, style={'fontSize': '13px'}  , 'margin-left': '15px'

        # Right Column/ Map
        html.Div([
            map_graph,
        #     # The Map
        #     dcc.Graph(id='graph', config={'displayModeBar': False, 'scrollZoom': True},
        #         style={'height':'80vh'},
        # )
        ], className='pretty_container nine columns media_xs_order_first'), # , style={'margin-right': '10px', 'margin-left': '10px'}
        
    ], className='row flex-display', style={'margin-right': '10px', 'margin-left': '10px'}),
    

], className='twelve columns', style={'margin-bottom': '20px'}), fluid=True,#  flex-display

)
##----------------------------------------------------------------##
# Output of Graph
@app.callback(Output('graph', 'figure'),
             [Input('loan_range', 'value'),
              Input('state', 'value'),
              Input('sectors', 'value')])

def update_figure(chosen_range, chosen_state, chosen_sector): #chosen_lender
    df_sub = df[(df['LoanRange'].isin(chosen_range) &
                 df['State'].isin(chosen_state) &
                 df['Sector'].isin(chosen_sector))] #(df['Lender'].isin(chosen_lender))

    # Create the figure
    locations=[go.Scattermapbox(
                    lon=df_sub['Long'],
                    lat=df_sub['Lat'],
                    mode='markers',
                    marker={'color': df_sub['color']},
                    unselected={'marker': {'opacity':1}},
                    selected={'marker': {'opacity':0.5, 'size':25}},
                    hoverinfo='text',
                    hovertext=df_sub['BusinessName']
    )]

    layout=go.Layout(
                # uirevision='foo', # preserves the state of the figure/map after callback is activated
                # clickmode= 'event+select',   
                hovermode='closest',
                hoverdistance=2,
                paper_bgcolor="#dedede",
                margin=dict(t=10, b=10, l=10, r=10), # t=45 W/ the title in use
                # title=dict(text='PPP Loan Distribution', font=dict(size=30, color='#7fa9eb')),
                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    bearing=8,
                    style='dark',
                    center=dict(
                        lat=37.0902,
                        lon=-95.7129
                    ),
                    pitch=40,
                    zoom=3.2,
                ),
            )

    # layout.legend.uirevision = 'foo'
    # layout['layout']['uirevision'] = 'foo'

    # Return figure
    # return {
    #     'data': locations,
    #     'layout': layout  
    # }
    return dict(data=locations, layout=layout)



if __name__ == '__main__':

    app.run_server(debug=True)

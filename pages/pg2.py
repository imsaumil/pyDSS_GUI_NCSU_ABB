import dash
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table

dash.register_page(__name__,
                   path='/analysis',
                   name='ANALYSIS RESULTS')

# Default start values
system_dummy_log = pd.DataFrame(["-", "-", "-", "-", "-"]).T
system_dummy_log.columns = ["Hour", "Sec", "ControlIter", "Element", "Action"]

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div(id='report-log-data', children=[
                dash_table.DataTable(system_dummy_log.to_dict('records'),
                                     [{"name": str(i), "id": str(i)} for i in system_dummy_log.columns],
                                     style_cell={'padding': '5px'},
                                     style_table={'maxWidth': '100%'},
                                     style_header={
                                         'backgroundColor': 'white',
                                         'fontWeight': 'bold'
                                     },
                                     style_cell_conditional=[
                                         {
                                             'if': {'column_id': c},
                                             'textAlign': 'center'
                                         } for c in system_dummy_log.columns
                                     ]
                                     )
            ])
        ], width=8),
        dbc.Col([], width=4)
    ])
])

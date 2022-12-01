# Importing required libraries
import dash
import numpy as np
import dash_cytoscape as cyto
import pandas as pd
import base64
import os
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table, callback, ctx
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

# Importing custom helper functions
from element_generator import elem_gen
from data_processing import data_processor
from dynamic_study import dynamic_study_pf
from report_generator import xlsx_report_writer, image_insert

# Enabling plot download
cyto.load_extra_layouts()

# Registering the home page
dash.register_page(__name__, path='/', name='SYSTEM DASHBOARD')

file_path = os.path.dirname(os.path.abspath(__file__))

legend_img = os.path.join(file_path, 'page_assets', 'legend.png')
encoded_legend_image = base64.b64encode(open(legend_img, 'rb').read()).decode('ascii')

# Importing the required data
line_data, bus_data, pf_bus_v_data_pivot = data_processor()

# Defining the diagram style sheet
default_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'label': 'data(id)',
            'font-size': '80px',
            'width': "90%",
            'height': "90%",
        }
    },

    {
        'selector': '.nodeColor',
        'style': {
            'background-color': 'black',
            'line-color': 'black'
        }
    },

    {
        'selector': '.switch_img',
        'style': {
            'content': 'FUSE',
            'color': 'white',
            'background-color': 'purple',
            'text-halign': 'center',
            'text-valign': 'center',
            'font-size': '30px',
            'width': '80px',
            'height': '80px',
            'shape': 'square'
        }
    },

    {
        'selector': '[orientation *=  "h"]',
        'style': {
            'shape': 'polygon',
            'shape-polygon-points': np.array([-0.3, -1, 0.3, -1, 0.3, 1, -0.3, 1])
        }
    },

    {
        'selector': '[orientation *=  "v"]',
        'style': {
            'shape': 'polygon',
            'shape-polygon-points': np.array([-1, -0.3, 1, -0.3, 1, 0.3, -1, 0.3])
        }
    },

    {
        'selector': '[orientation *=  "o"]',
        'style': {
            'shape': 'polygon',
            'shape-polygon-points': np.array([-0.3, -1, 0.3, -1, 0.3, 1, -0.3, 1])
        }
    },

    {
        'selector': '[phases > 1]',
        'style': {
            'background-color': 'red',
            'line-color': 'red',
            'width': 8
        }
    },

    {
        'selector': '[phases < 2]',
        'style': {
            'background-color': 'darkgreen',
            'line-color': 'darkgreen',
            'width': 8
        }
    },

    {
        'selector': '[line_name *=  "sw"]',
        'style': {
            'background-color': 'purple',
            'line-color': 'purple',
            'width': 12
        }
    },

    {
        'selector': '[id = "150"]',
        'style': {
            'shape': 'rectangle',
            'width': '130px',
            'height': '130px',
            'background-fit': 'cover',
            'background-image': ['./assets/gen_image.png']
        }
    },

    {
        'selector': '.fault_img',
        'style': {
            'shape': 'rectangle',
            'width': '100px',
            'height': '100px',
            'background-fit': 'cover',
            'background-image': ['./assets/fault.png']
        }
    },

    {
        'selector': '.pv_img',
        'style': {
            'shape': 'rectangle',
            'width': '100px',
            'height': '100px',
            'background-fit': 'cover',
            'background-image': ['./assets/pv.png']
        }
    },

    {
        'selector': '.pv_plus_fault_img',
        'style': {
            'shape': 'rectangle',
            'width': '100px',
            'height': '100px',
            'background-fit': 'cover',
            'background-image': ['./assets/pv_plus_fault.png']
        }
    },
]

# Default start values
system_dummy_table = pd.DataFrame(["-", "-", "-", "-", "-"]).T
system_dummy_table.columns = ["Hovered Line", "Hovered Node", "Node V (Ph-1)", "Node V (Ph-2)", "Node V (Ph-3)"]

# Setting the layout with elements
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Row([
                html.Div("DISPLAY SYSTEM DATA", style={'color': 'Brown',
                                                       'fontWeight': 'bold',
                                                       'fontSize': 20,
                                                       'text-decoration': 'underline',
                                                       }),

                html.Div(id='system-data-table-output', children=[
                    dash_table.DataTable(system_dummy_table.to_dict('records'),
                                         [{"name": str(i), "id": str(i)} for i in system_dummy_table.columns],
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
                                             } for c in system_dummy_table.columns
                                         ]
                                         )
                ]),
            ], style={'margin-left': '0%'}),

            html.Br(),

            # ISSUE FOR INITIAL LOAD
            dbc.Row([html.Div(id='system-gui',
                              children=[
                                  cyto.Cytoscape(
                                      id='dist-protection-graph',
                                      layout={'name': 'preset'},
                                      minZoom=0.15, maxZoom=2, responsive=True,
                                      style={'width': '920px', 'height': '650px',
                                             "border": "1px black solid"},
                                      stylesheet=default_stylesheet,
                                      elements=elem_gen()
                                  ),
                                  html.Img(src='data:image/png;base64,{}'.format(encoded_legend_image),
                                           style={'margin-left': '81.5%'}
                                           )
                              ])
                     ], style={'margin-left': '0%'}),

            dcc.Store('element-storage', data=elem_gen(), storage_type='memory')

        ], xs=6, sm=6, md=6, lg=6, xl=6, xxl=6),

        dbc.Col([
            dcc.Store('fuse-spec-list', data=[], storage_type='memory'),
            dcc.Store('fault-bus-loc-list', data=[], storage_type='memory'),
            dcc.Store('pv-loc-list', data=[], storage_type='memory'),

            dbc.Row([
                dbc.Col([
                    html.Div("TCC SELECTION", style={'color': 'Brown',
                                                     'fontWeight': 'bold',
                                                     'fontSize': 20,
                                                     'text-decoration': 'underline',
                                                     'width': '90%'}),

                    dcc.Dropdown(
                        id='tcc-curve-selector',
                        options=[
                            {'label': '65E_TCC_curve', 'value': '65E'},
                            {'label': '40E_TCC_curve', 'value': '40E'},
                            {'label': 'a_TCC_curve', 'value': 'a'},
                            {'label': 'd_TCC_curve', 'value': 'd'},
                            {'label': 'tlink_TCC_curve', 'value': 'tlink'},
                            {'label': 'klink_TCC_curve', 'value': 'klink'},
                        ],
                        value='65E',
                        placeholder='65E_TCC_curve', style={'width': '90%'}),
                ], style={'margin-left': '1%'}),

                dbc.Col([
                    html.Div("RATED FUSE CURRENT", style={'color': 'Brown',
                                                          'fontWeight': 'bold',
                                                          'fontSize': 20,
                                                          'text-decoration': 'underline',
                                                          'width': '80%',
                                                          }),

                    dcc.Input(id='fuse-rated-current-input', type='number',
                              value=50,
                              placeholder="50",
                              debounce=True, style={'width': '80%'}),
                ], width=4),

                dbc.Col([
                    html.Div("PV PENETRATION", style={'color': 'Brown',
                                                      'fontWeight': 'bold',
                                                      'fontSize': 20,
                                                      'text-decoration': 'underline',
                                                      'width': '80%'}),
                    html.Div([
                        dcc.Slider(3000, 5000, 100,
                                   value=4000,
                                   id='pv-penn-slider',
                                   tooltip={"placement": "bottom", "always_visible": True},
                                   updatemode='drag',
                                   marks={
                                       3000: {'label': '3000 KW'},
                                       5000: {'label': '5000 KW'}},
                                   )
                    ])
                ], width=4)
            ]),

            dbc.Row([
                html.Hr(style={'margin-bottom': '1%', 'margin-top': '3%', 'width': '90%'}),
                html.Div(id='message-output-container', children=["MESSAGE: No message yet !"],
                         style={'font-weight': 'bold', 'color': 'black'}),
                html.Hr(style={'margin-bottom': '3%', 'margin-top': '1%', 'width': '90%'}),
            ], style={'margin-left': '1%'}),

            dbc.Row([html.Div("ACTION SECTION", style={'color': 'Brown',
                                                       'fontWeight': 'bold',
                                                       'fontSize': 20,
                                                       'text-decoration': 'underline'})
                     ], style={'margin-left': '0%'}),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Button('Add protection element', id='add_protection_button', color="primary",
                                   className="me-1", n_clicks=0),

                        dbc.Button('Remove protection element', id='remove_protection_button', color="primary",
                                   className="me-1", n_clicks=0)
                    ], className="d-grid gap-1 col-12")
                ], width=4),

                dbc.Col([
                    html.Div([
                        dbc.Button('Add fault', id='add_fault_button', color="dark",
                                   className="me-1", n_clicks=0),

                        dbc.Button('Remove fault', id='remove_fault_button', color="dark",
                                   className="me-1", n_clicks=0)
                    ], className="d-grid gap-1 col-12")
                ], width=4),

                dbc.Col([
                    html.Div([
                        dbc.Button('Add PV', id='add_pv_button', color="success",
                                   className="me-1", n_clicks=0),

                        dbc.Button('Remove PV', id='remove_pv_button', color="success",
                                   className="me-1", n_clicks=0)
                    ], className="d-grid gap-1 col-12")
                ], width=4),
            ], style={'margin-bottom': '1%', 'margin-left': '0%'}),

            dbc.Row([
                html.Div([
                    dbc.Button('RUN SIMULATION', id='simulation_run_button', color="danger",
                               className='me-1', n_clicks=0),
                ], className="d-grid gap-1 col-8"),

                html.Div([
                    dbc.Button(children=[html.I(className="fa fa-download mr-1"), ' Download Report'],
                               id='download_report_button', color="info",
                               className='me-1', n_clicks=0),
                ], className="d-grid gap-1 col-4"),

                html.Div(id='sim-report-xlsx', hidden=True)

            ], style={'margin-bottom': '1%', 'margin-left': '0%'}),

            html.Br(),

            dbc.Row([
                dbc.Col([
                    html.Div(id='sim-table-out-1', children=[]),

                    html.Div(id='sim-table-out-2', children=[]),
                ], width=12)
            ], style={'margin-left': '0%'}),

        ], width=6)
    ])

], fluid=True, style={'padding': '0.1%'})


# Callback to update the system data output
@callback(
    Output('system-data-table-output', 'children'),
    Input('dist-protection-graph', 'mouseoverNodeData'),
    Input('dist-protection-graph', 'mouseoverEdgeData'),
    State('system-data-table-output', 'children')
)
def update_nodes(input_node, input_edge, _):
    if (input_node is None) or (input_edge is None) or (len(input_node) < 4):
        raise PreventUpdate
    else:
        system_data_table = pd.DataFrame(
            [input_edge['line_name'] + " ({})".format(input_edge['label']), input_node['id'],
             input_node['v_phase1'], input_node['v_phase2'], input_node['v_phase3']]).T
        system_data_table.columns = ["Hovered Line", "Hovered Node", "Node V (Ph-1)", "Node V (Ph-2)", "Node V (Ph-3)"]

        system_data = html.Div([
            dash_table.DataTable(system_data_table.to_dict('records'),
                                 [{"name": str(i), "id": str(i)} for i in ["Hovered Line",
                                                                           "Hovered Node",
                                                                           "Node V (Ph-1)",
                                                                           "Node V (Ph-2)",
                                                                           "Node V (Ph-3)"]],
                                 style_cell={'padding': '5px'},
                                 style_table={'maxWidth': '98.5%'},
                                 style_header={
                                     'backgroundColor': 'white',
                                     'fontWeight': 'bold'
                                 },
                                 style_cell_conditional=[
                                     {
                                         'if': {'column_id': c},
                                         'textAlign': 'center'
                                     } for c in system_data_table.columns
                                 ]
                                 )
        ])

    return system_data


@callback(
    Output('system-gui', 'children'),
    Output('message-output-container', 'children'),
    Output('element-storage', 'data'),
    Output('fuse-spec-list', 'data'),
    Output('pv-loc-list', 'data'),
    Output('fault-bus-loc-list', 'data'),
    [Input('element-storage', 'data'),
     Input('fuse-spec-list', 'data'),
     Input('fault-bus-loc-list', 'data'),
     Input('pv-loc-list', 'data'),
     Input('dist-protection-graph', 'tapEdge'),
     Input('dist-protection-graph', 'tapNode'),
     Input('add_protection_button', 'n_clicks'),
     Input('remove_protection_button', 'n_clicks'),
     Input('add_fault_button', 'n_clicks'),
     Input('remove_fault_button', 'n_clicks'),
     Input('add_pv_button', 'n_clicks'),
     Input('remove_pv_button', 'n_clicks'),
     Input('tcc-curve-selector', 'value'),
     Input('fuse-rated-current-input', 'value'),
     Input('pv-penn-slider', 'value')],
    [State('system-gui', 'children'),
     State('element-storage', 'data'),
     State('fuse-spec-list', 'data'),
     State('pv-loc-list', 'data'),
     State('fault-bus-loc-list', 'data'),
     ],
)
def gui_interactions(element_storage, fuse_spec_list, fault_bus_loc_list, pv_loc_list,
                     selected_edge, selected_node_elem,
                     add_prot_clicks, remove_prot_clicks,
                     add_fault_clicks, remove_fault_clicks,
                     add_pv_clicks, remove_pv_clicks,
                     tcc_curve_value, fuse_current_value, pv_penn_slider_value,
                     system_gui_child, elem_storage_state, fuse_spec_list_state,
                     pv_loc_list_state, fault_bus_loc_list_state
                     ):
    # Prevent any updates at the fresh start of GUI
    if (selected_edge is None) and (selected_node_elem is None):
        raise PreventUpdate

    else:
        ## -> Changes on line
        # For adding and removing a protective element on the GUI
        if ("add_protection_button" == ctx.triggered_id) and (selected_edge is not None):
            if (tcc_curve_value and fuse_current_value) is not None:

                # Appending the fuse with line name for location and corresponding specifications
                fuse_spec_list.append([selected_edge['data']['line_name'], tcc_curve_value, fuse_current_value])

                display_msg = "New fuse added at {} with rated current " \
                              "of : {} A and TCC curve as : {}".format(selected_edge['data']['line_name'],
                                                                       fuse_current_value,
                                                                       tcc_curve_value)

                element_storage.append({
                    'data': {'id': selected_edge['data']['line_name'], 'tcc': tcc_curve_value,
                             'fuse_curr': fuse_current_value},
                    'position': {'x': selected_edge['midpoint']['x'], 'y': selected_edge['midpoint']['y']},
                    'locked': True,
                    'selectable': True,
                    'autoungrabify': True,
                    'autounselectify': False,
                    'classes': 'switch_img'
                })

                system_gui_child = html.Div([
                    cyto.Cytoscape(
                        id='dist-protection-graph',
                        layout={'name': 'preset'},
                        minZoom=0.15, maxZoom=2, responsive=True,
                        style={'width': '920px', 'height': '650px',
                               "border": "1px black solid"},
                        stylesheet=default_stylesheet,
                        elements=element_storage
                    ),
                    html.Img(src='data:image/png;base64,{}'.format(encoded_legend_image),
                             style={'margin-left': '81.5%'}
                             )
                ])

            elif (tcc_curve_value is None) and (fuse_current_value is not None):
                display_msg = "Select a TCC curve for the fuse before adding it."

            elif (fuse_current_value is None) and (tcc_curve_value is not None):
                display_msg = "Input the rated current for fuse before adding it."

            else:
                display_msg = "Inputs for both TCC curve and rated fuse current missing!"

        elif ("remove_protection_button" == ctx.triggered_id) and (selected_node_elem is not None):
            # Fetching the data from nodeTap
            node_id = selected_node_elem['data']['id']
            node_fuse_tcc = selected_node_elem['data']['tcc']
            node_fuse_curr = selected_node_elem['data']['fuse_curr']

            if [node_id, node_fuse_tcc, node_fuse_curr] in fuse_spec_list:

                # Removing the fuse from fuse spec list
                fuse_spec_list.remove([node_id, node_fuse_tcc, node_fuse_curr])

                display_msg = "Fuse removed from {} with rated current " \
                              "of : {} A and TCC curve as : {}.".format(node_id, node_fuse_curr, node_fuse_tcc)

                element_storage.remove({
                    'data': {'id': node_id, 'tcc': node_fuse_tcc, 'fuse_curr': node_fuse_curr},
                    'position': {'x': selected_node_elem['position']['x'], 'y': selected_node_elem['position']['y']},
                    'locked': True,
                    'selectable': True,
                    'autoungrabify': True,
                    'autounselectify': False,
                    'classes': 'switch_img'
                })

                system_gui_child = html.Div([
                    cyto.Cytoscape(
                        id='dist-protection-graph',
                        layout={'name': 'preset'},
                        minZoom=0.15, maxZoom=2, responsive=True,
                        style={'width': '920px', 'height': '650px',
                               "border": "1px black solid"},
                        stylesheet=default_stylesheet,
                        elements=element_storage
                    ),
                    html.Img(src='data:image/png;base64,{}'.format(encoded_legend_image),
                             style={'margin-left': '81.5%'}
                             )
                ])
            else:
                display_msg = "Non existing fuse cannot be removed !"

        elif (selected_node_elem is not None) and (len(selected_node_elem['edgesData']) > 0):

            # Creating elements for ready use
            original_node_elem = {
                'data': {'id': selected_node_elem['data']['id'],
                         'v_phase1': selected_node_elem['data']['v_phase1'],
                         'v_phase2': selected_node_elem['data']['v_phase2'],
                         'v_phase3': selected_node_elem['data']['v_phase3'],
                         'orientation': selected_node_elem['data']['orientation']},
                'position': {'x': selected_node_elem['position']['x'], 'y': selected_node_elem['position']['y']},
                'locked': True,
                'classes': 'nodeColor'
            }

            modified_fault_elem = {
                'data': {'id': selected_node_elem['data']['id'],
                         'v_phase1': selected_node_elem['data']['v_phase1'],
                         'v_phase2': selected_node_elem['data']['v_phase2'],
                         'v_phase3': selected_node_elem['data']['v_phase3'],
                         'orientation': selected_node_elem['data']['orientation']},
                'position': {'x': selected_node_elem['position']['x'], 'y': selected_node_elem['position']['y']},
                'locked': True,
                'classes': 'fault_img'
            }

            modified_pv_elem = {
                'data': {'id': selected_node_elem['data']['id'],
                         'v_phase1': selected_node_elem['data']['v_phase1'],
                         'v_phase2': selected_node_elem['data']['v_phase2'],
                         'v_phase3': selected_node_elem['data']['v_phase3'],
                         'orientation': selected_node_elem['data']['orientation']},
                'position': {'x': selected_node_elem['position']['x'], 'y': selected_node_elem['position']['y']},
                'locked': True,
                'classes': 'pv_img'
            }

            modified_pv_plus_fault_elem = {
                'data': {'id': selected_node_elem['data']['id'],
                         'v_phase1': selected_node_elem['data']['v_phase1'],
                         'v_phase2': selected_node_elem['data']['v_phase2'],
                         'v_phase3': selected_node_elem['data']['v_phase3'],
                         'orientation': selected_node_elem['data']['orientation']},
                'position': {'x': selected_node_elem['position']['x'], 'y': selected_node_elem['position']['y']},
                'locked': True,
                'classes': 'pv_plus_fault_img'
            }

            # Checking the phases of selected bus
            voltage_list = [selected_node_elem['data']['v_phase1'], selected_node_elem['data']['v_phase2'],
                            selected_node_elem['data']['v_phase3']]

            # Checking the phases of the bus before adding fault
            phase_check = (3 - voltage_list.count("-"))

            if "add_fault_button" == ctx.triggered_id:

                # Adding the element only if it does not exist in the fault loc list
                if ([str(selected_node_elem['data']['id']), phase_check]) not in fault_bus_loc_list:

                    # Appending the new fault location to the list
                    fault_bus_loc_list.append([str(selected_node_elem['data']['id']), phase_check])

                    # Scenario A -> Original replaced by fault object
                    if original_node_elem in element_storage:

                        # Removing the original element first
                        element_storage.remove(original_node_elem)

                        # Adding the fault image on the same location
                        element_storage.append(modified_fault_elem)

                        display_msg = "New fault created on a {} - phase " \
                                      "bus at {}.".format(phase_check, selected_node_elem['data']['id'])

                    # Scenario B -> PV already exists and need to create fault on top
                    elif modified_pv_elem in element_storage:

                        # Removing the pv element first
                        element_storage.remove(modified_pv_elem)

                        # Adding the fault + pv image on the same location
                        element_storage.append(modified_pv_plus_fault_elem)

                        display_msg = "New fault created on a {} - phase " \
                                      "bus at {} with an existing PV.".format(phase_check,
                                                                              selected_node_elem['data']['id'])
                    else:
                        display_msg = "Error updating the fault condition ! - (ERROR)"
                else:
                    display_msg = "The desired fault already exists !"


            elif "remove_fault_button" == ctx.triggered_id:

                # Removing the element only if it exists in the fault loc list
                if ([str(selected_node_elem['data']['id']), phase_check]) in fault_bus_loc_list:

                    # Removing the fault location from the list
                    fault_bus_loc_list.remove([str(selected_node_elem['data']['id']), phase_check])

                    # Scenario C -> Fault replaced by original object
                    if modified_fault_elem in element_storage:

                        # Removing the fault element first
                        element_storage.remove(modified_fault_elem)

                        # Adding back the original element
                        element_storage.append(original_node_elem)

                        display_msg = "Fault removed from a {} - phase " \
                                      "bus at {}.".format(phase_check, selected_node_elem['data']['id'])

                    # Scenario D -> PV + Fault replaced by just PV object
                    elif modified_pv_plus_fault_elem in element_storage:

                        # Removing the PV + Fault element first
                        element_storage.remove(modified_pv_plus_fault_elem)

                        # Replacing with just the PV object
                        element_storage.append(modified_pv_elem)

                        display_msg = "New fault created on a {} - phase " \
                                      "bus at {} with an existing PV.".format(phase_check,
                                                                              selected_node_elem['data']['id'])
                    else:
                        display_msg = "Error updating the fault condition ! - (ERROR)"
                else:
                    display_msg = "Fault already removed and does not exist !"

            # For adding and removing a PV on the GUI
            elif "add_pv_button" == ctx.triggered_id:

                # PV can only be added on a 3-phase bus
                if phase_check == 3:

                    # Adding a pV only if it does not exist already
                    if ([str(selected_node_elem['data']['id']), phase_check, pv_penn_slider_value]) not in pv_loc_list:

                        # Appending the new PV location to the list
                        pv_loc_list.append([str(selected_node_elem['data']['id']), phase_check, pv_penn_slider_value])

                        # Scenario A -> Original replaced by pv object
                        if original_node_elem in element_storage:
                            # Removing the fault element first
                            element_storage.remove(original_node_elem)

                            # Adding back the original element
                            element_storage.append(modified_pv_elem)

                            display_msg = "New PV added on a {} - phase " \
                                          "bus at {} with a rating of {} KW.".format(phase_check,
                                                                                     selected_node_elem['data']['id'],
                                                                                     pv_penn_slider_value)

                        # Scenario B -> PV already exists and need to create fault on top
                        elif modified_fault_elem in element_storage:
                            # Removing the only fault element first
                            element_storage.remove(modified_fault_elem)

                            # Replacing with the fault + PV object
                            element_storage.append(modified_pv_plus_fault_elem)

                            display_msg = "New PV added on a {} - phase " \
                                          "bus at {} with a rating of {} KW and " \
                                          "with an existing fault.".format(phase_check,
                                                                           selected_node_elem['data']['id'],
                                                                           pv_penn_slider_value)
                        else:
                            display_msg = "Error updating the PV condition ! - (ERROR)"
                    else:
                        display_msg = "PV already exists and cannot be added twice !"
                else:
                    display_msg = "PV can only be added to a 3-phase bus."

            # For adding and removing a PV on the GUI
            elif "remove_pv_button" == ctx.triggered_id:

                # Modified list for removing PVs
                rm_pv_loc_list = [i[:-1] for i in pv_loc_list]

                # Adding a PV only if it does not exist already
                if ([str(selected_node_elem['data']['id']), phase_check]) in rm_pv_loc_list:

                    # Fetching the element to be removed
                    rm_pv_elem = pv_loc_list[rm_pv_loc_list.index([str(selected_node_elem['data']['id']), phase_check])]

                    # Appending the new PV location to the list
                    pv_loc_list.remove(rm_pv_elem)
                    rm_pv_loc_list.remove([str(selected_node_elem['data']['id']), phase_check])

                    # Scenario C -> PV replaced by original object
                    if modified_pv_elem in element_storage:
                        # Removing the PV element first
                        element_storage.remove(modified_pv_elem)

                        # Adding back the original element
                        element_storage.append(original_node_elem)

                        display_msg = "PV removed from a {} - phase " \
                                      "bus at {} with a rating of {} KW.".format(phase_check,
                                                                                 selected_node_elem['data']['id'],
                                                                                 rm_pv_elem[2])

                    # Scenario D -> PV + Fault replaced by just PV object
                    elif modified_pv_plus_fault_elem in element_storage:
                        # Removing the fault + PV object element first
                        element_storage.remove(modified_pv_plus_fault_elem)

                        # Replacing with only fault object
                        element_storage.append(modified_fault_elem)

                        display_msg = "PV removed from a {} - phase " \
                                      "bus at {} with a rating of {} KW, " \
                                      "but fault still exists.".format(phase_check,
                                                                       selected_node_elem['data']['id'],
                                                                       rm_pv_elem[2])
                    else:
                        display_msg = "Error updating the PV condition ! - (ERROR)"
                else:
                    display_msg = "Non existing PV cannot be removed !"

            else:
                display_msg = "BLANK"  # -> CHECK
                raise PreventUpdate

            system_gui_child = html.Div([
                cyto.Cytoscape(
                    id='dist-protection-graph',
                    layout={'name': 'preset'},
                    minZoom=0.15, maxZoom=2, responsive=True,
                    style={'width': '920px', 'height': '650px',
                           "border": "1px black solid"},
                    stylesheet=default_stylesheet,
                    elements=element_storage
                ),
                html.Img(src='data:image/png;base64,{}'.format(encoded_legend_image),
                         style={'margin-left': '81.5%'}
                         )
            ])

        else:
            # MORE DISPLAY MESSAGES CAN BE ADDED HERE !
            if selected_node_elem and len(selected_node_elem['edgesData']) == 0:
                display_msg = "Fuse on line {} selected.".format(selected_node_elem['data']['id'])
            elif selected_edge is not None:
                display_msg = "Line {} selected.".format(selected_edge['data']['line_name'])
            else:
                display_msg = "BLANK"  # -> CHECK

    return system_gui_child, "MESSAGE: {0}".format(
        display_msg), element_storage, fuse_spec_list, pv_loc_list, fault_bus_loc_list


# Callback for running the case study
@callback(
    Output('sim-table-out-1', 'children'),
    Output('sim-table-out-2', 'children'),
    Output("dist-protection-graph", "generateImage"),
    [Input('simulation_run_button', 'n_clicks'),
     Input('fuse-spec-list', 'data'),
     Input('fault-bus-loc-list', 'data'),
     Input('pv-loc-list', 'data')],
    State('sim-table-out-1', 'children'),
    State('sim-table-out-2', 'children'),
)
def simulation_run(sim_run_click, fuse_spec_list, fault_bus_loc_list, pv_loc_list,
                   sim_table_1, sim_table_2):
    if sim_run_click in [0, None]:
        raise PreventUpdate

    if "simulation_run_button" == ctx.triggered_id:
        sim_run_data_1, sim_run_data_2 = dynamic_study_pf(fuse_spec_list=fuse_spec_list,
                                                          fault_bus_loc_list=fault_bus_loc_list,
                                                          pv_loc_list=pv_loc_list)

        sim_run_out_1 = html.Div([
            html.Div("SIMULATION DATA", style={'color': 'Brown',
                                               'fontWeight': 'bold',
                                               'fontSize': 20,
                                               'text-decoration': 'underline'}),

            html.Div("1. CASE DATA (A)", style={'color': 'Navy',
                                                'fontSize': 15,
                                                'fontWeight': 'bold'}),

            dash_table.DataTable(sim_run_data_1.to_dict('records'),
                                 [{"name": str(i), "id": str(i)} for i in sim_run_data_1.columns],
                                 style_cell={'padding': '5px'},
                                 style_table={'maxWidth': '90%'},
                                 style_header={
                                     'backgroundColor': 'white',
                                     'fontWeight': 'bold'
                                 },
                                 style_cell_conditional=[
                                     {
                                         'if': {'column_id': c},
                                         'textAlign': 'center'
                                     } for c in sim_run_data_1.columns
                                 ]
                                 ),
            html.Br()

        ])

        sim_run_out_2 = html.Div([
            html.Div("2. FAULT CONTRIBUTION DATA (%)", style={'color': 'Navy',
                                                              'fontSize': 15,
                                                              'fontWeight': 'bold'}),

            dash_table.DataTable(sim_run_data_2.to_dict('records'),
                                 [{"name": str(i), "id": str(i)} for i in sim_run_data_2.columns],
                                 style_cell={'padding': '5px'},
                                 style_table={'maxWidth': '90%'},
                                 style_header={
                                     'backgroundColor': 'white',
                                     'fontWeight': 'bold'
                                 },
                                 style_cell_conditional=[
                                     {
                                         'if': {'column_id': c},
                                         'textAlign': 'center'
                                     } for c in sim_run_data_2.columns
                                 ]
                                 )
        ])

        # Creating a report
        report_path = xlsx_report_writer(sim_run_data_1, sim_run_data_2)
        #
        # Checking for existing image, if found delete
        download_path = os.path.join(os.path.expanduser("~"), 'Downloads')
        img_path = os.path.join(download_path, 'ieee123_bus.jpg')

        if os.path.isfile(img_path):
            os.remove(img_path)

        return sim_run_out_1, sim_run_out_2, {'type': 'jpg',
                                              'action': 'download',
                                              'filename': 'ieee123_bus'
                                              }
    else:
        raise PreventUpdate


@callback(
    Output('sim-report-xlsx', 'children'),
    Input("download_report_button", "n_clicks"),
    prevent_initial_call=True,
)
def download_report(download_click):
    image_insert()

# Importing required libraries
from copy import deepcopy

# Importing custom helper functions
from data_processing import data_processor

# Importing the required data
line_data, bus_data, pf_bus_v_data_pivot = data_processor()


def elem_gen():
    # Holder dictionaries to access and update data for bus and line elements
    line_element_dict = {'data': {'source': 'PHolder11', 'target': 'PHolder12', 'label': 'PHolder13',
                                  'line_name': 'PHolder14', 'phases': 'PHolder15'},
                         'classes': 'PHolder16'}

    bus_element_dict = {
        'data': {'id': 'PHolder0', 'v_phase1': 'PHolder1', 'v_phase2': 'PHolder2', 'v_phase3': 'PHolder3',
                 'orientation': 'PHolder4'},
        'position': {'x': 000, 'y': 000},
        'locked': True,
        'classes': 'PHolder5'
    }

    # Line elements generator
    line_element_list = []
    for idx, row in line_data.iterrows():
        # Slicing the source and target from each row
        row_list = list(row)

        # Updating the line element dictionary
        line_element_dict['data']['line_name'] = row_list[0]
        line_element_dict['data']['source'] = row_list[1]
        line_element_dict['data']['target'] = row_list[2]
        line_element_dict['data']['label'] = row_list[1] + " -> " + row_list[2]
        line_element_dict['data']['phases'] = row_list[3]

        # Appending each element to the list of elements
        line_element_list.append(deepcopy(line_element_dict))

    # Bus elements generator
    bus_element_list = []
    for idx, row in bus_data.iterrows():
        bus_element_dict['position']['x'] = row["Bus_x"]
        bus_element_dict['position']['y'] = row["Bus_y"]
        bus_element_dict['data']['id'] = row["Bus"]
        bus_element_dict['data']['v_phase1'] = pf_bus_v_data_pivot.loc[row["Bus"]][0]
        bus_element_dict['data']['v_phase2'] = pf_bus_v_data_pivot.loc[row["Bus"]][1]
        bus_element_dict['data']['v_phase3'] = pf_bus_v_data_pivot.loc[row["Bus"]][2]
        bus_element_dict['data']['orientation'] = row["Orient"]
        bus_element_dict['classes'] = 'nodeColor'

        # Appending each element to the list of elements
        bus_element_list.append(deepcopy(bus_element_dict))

    return bus_element_list + line_element_list

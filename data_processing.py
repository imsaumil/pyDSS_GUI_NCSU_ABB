# Importing required libraries
import py_dss_interface
import os
import pandas as pd

# Importing custom helper functions
from setting_bus_orientation import bus_orienter

## Stetting up pyDSS and compiling master file
# Defining file path
file_path = os.path.dirname(os.path.abspath(__file__))

# Defining the master file path
dss_file = os.path.join(file_path, "base_IEEE123Bus_System", "IEEE123Master.dss")

# Creating a py-dss object
dss = py_dss_interface.DSSDLL()

# Compiling the DSS master file
dss.text(f"compile [{dss_file}")


def data_processor():
    ## LINE DATA PROCESSING
    # Fetching all the line names beforehand
    line_names = dss.lines_all_names()

    bus_1_names = []
    bus_2_names = []
    phase_det = []
    line_lengths = []

    for line in line_names:
        dss.lines_write_name(line)
        bus_1_names.append(dss.lines_read_bus1())
        bus_2_names.append(dss.lines_read_bus2())
        phase_det.append(dss.lines_read_phases())
        line_lengths.append(dss.lines_read_length())

    line_data = pd.DataFrame(list(zip(line_names, bus_1_names, bus_2_names, phase_det, line_lengths)),
                             columns=["Line", "Bus1", "Bus2", "Phases", "Line_length"])

    line_data.Bus1 = line_data.Bus1.str.split(".", 1).str[0]
    line_data.Bus2 = line_data.Bus2.str.split(".", 1).str[0]

    ## BUS DATA PROCESSING
    bus_names = dss.circuit_all_bus_names()
    bus_x_coords = []
    bus_y_coords = []

    for bus in bus_names:
        dss.circuit_set_active_bus(bus)
        bus_x_coords.append(dss.bus_read_x())
        bus_y_coords.append(dss.bus_read_y())

    bus_data = pd.DataFrame(list(zip(bus_names, bus_x_coords, bus_y_coords)),
                            columns=["Bus", "Bus_x", "Bus_y"])

    bus_data[["Bus_x", "Bus_y"]] = bus_data[["Bus_x", "Bus_y"]].astype("int")

    # Performing power flow on the master file
    dss.text("solve")

    ## BUS VOLTAGE (PER_PHASE) ANALYSIS
    # Fetching the bus voltages for all available phases
    pf_bus_names = dss.circuit_all_node_names()
    pf_bus_volts = dss.circuit_all_bus_vmag()

    pf_bus_v_data = pd.DataFrame(list(zip(pf_bus_names, pf_bus_volts)),
                                 columns=["Bus_names", "Bus_voltages"])

    pf_bus_v_data = pd.concat([pf_bus_v_data["Bus_names"].str.split(".", expand=True),
                               pf_bus_v_data["Bus_voltages"].round(3)], axis=1)

    # Pivoting the table to easy see the per phase voltages
    pf_bus_v_data_pivot = pf_bus_v_data.pivot(index=0, columns=1, values="Bus_voltages")

    # Filling the empty phase entries with "-"
    pf_bus_v_data_pivot = pf_bus_v_data_pivot.fillna("-")

    ## PROCESSING THE FETCHED DATA
    # Fetching the data for switches / fuses
    switch_data = line_data[line_data.Line.str.contains("sw")]

    # Fetching and removing repeated entries with r
    bus_data_r_duplicate = bus_data[bus_data.Bus.str.contains("r")]
    bus_data = bus_data[~bus_data.Bus.str.contains("r")]

    # Removing the redundant pos 0 values
    bus_zero_data = bus_data[(bus_data.Bus_x == 0) & (bus_data.Bus_y == 0)]
    bus_data = bus_data[(bus_data.Bus_x != 0) & (bus_data.Bus_y != 0)]

    # Removing leftover repeated entries with same co-ordinates
    bus_data_duplicate = bus_data[bus_data.duplicated(["Bus_x", "Bus_y"], keep="first")]
    if not bus_data_duplicate.empty:
        print("We still  have duplicate entries left !")
        bus_data = bus_data.drop_duplicates(["Bus_x", "Bus_y"], keep="first")

    # Combining the total removed data
    bus_data_removed = pd.concat([bus_data_r_duplicate, bus_data_duplicate], axis=0)

    # Treating the line data to remove additional r from bus names
    line_data.Bus1 = line_data.Bus1.str.replace("r", "")
    line_data.Bus2 = line_data.Bus2.str.replace("r", "")

    # Removing the open redundant data from line data
    line_data = line_data[~((line_data.Bus1.isin(bus_zero_data.Bus)) |
                            (line_data.Bus2.isin(bus_zero_data.Bus)))]

    # Using the bus orienter function to get the bus orientation ready
    line_data, bus_data = bus_orienter(line_data, bus_data)

    return line_data, bus_data, pf_bus_v_data_pivot

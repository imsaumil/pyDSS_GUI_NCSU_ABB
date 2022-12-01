import math
import pandas as pd


def check_the_line(spl, limit=1):
    if (not limit < spl <= 360 - limit) or (180 - limit <= spl < 180 + limit):
        return "h"
    elif (90 - limit < spl < 90 + limit) or (270 - limit < spl < 270 + limit):
        return "v"

    return "o"


def bus_orienter(line_data, bus_data):

    for idx, row in bus_data.iterrows():

        # Matching line data
        line_data_avail = line_data[(line_data.Bus1 == row["Bus"]) | (line_data.Bus2 == row["Bus"])]

        calc_slopes = pd.DataFrame(columns=["slope"])

        for sub_idx, sub_row in line_data_avail.iterrows():

            # Fetching the bus_a and bus_b names
            bus_a, bus_b = sub_row["Bus1"], sub_row["Bus2"]

            # Getting the corresponding coordinates
            coords_a, coords_b = bus_data[bus_data.Bus == bus_a], bus_data[bus_data.Bus == bus_b]

            # Calculate slope only if values are present
            if not (coords_a.empty | coords_b.empty):
                calc_slopes.loc[sub_idx, "slope"] = math.degrees(math.atan2(
                    (coords_a.loc[:, "Bus_y"].tolist()[0] - coords_b.loc[:, "Bus_y"].tolist()[0]),
                    (coords_a.loc[:, "Bus_x"].tolist()[0] - coords_b.loc[:, "Bus_x"].tolist()[0])
                )
                )
            else:
                print("Coords not available !")

        if not calc_slopes.empty:

            # If calc slope is available
            calc_slopes = calc_slopes.astype("int")
            calc_slopes["Orient"] = calc_slopes["slope"].apply(check_the_line)

            bus_data.loc[idx, "Orient"] = calc_slopes["Orient"].mode()[0]
        else:
            bus_data.loc[idx, "Orient"] = "o"

    return line_data, bus_data

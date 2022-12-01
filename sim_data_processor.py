# Importing required libraries
import pandas as pd


def tab_1_processor(dss, file_path, index_name):
    # Finding and verifying all added fuses
    fuse_pos = [pos.replace("fuse_", "").upper() for pos in dss.fuses_all_names()]

    # Processing the csv file
    read_file = pd.read_csv(file_path)
    read_file.columns = [name.strip() for name in read_file.columns]
    line_fuse_elem = list(map(lambda x: 'Line.' + x, fuse_pos))

    # Filtering the required data
    req_df = read_file.loc[(read_file.Element.isin(line_fuse_elem)) & (read_file.Terminal == 1)]
    req_df = req_df[["Element", "I1"]].T
    req_df.columns = [elem_name.replace("Line.", "Fuse on ") for elem_name in req_df.loc["Element"]]
    req_df = req_df.drop(index="Element")
    req_df.index = [index_name]

    # Processing in final form
    req_df = req_df.reset_index()
    req_df = req_df.rename(columns={'index': 'CASE NAME'})
    req_df.iloc[:, 1:] = req_df.iloc[:, 1:] .round(3).astype("str") + " A"

    return req_df


def tab_2_processor(dss, file_path_partial, file_path_full, index_name, pv_bus):
    # Finding and verifying all added fuses
    fuse_pos = [pos.replace("fuse_", "").upper() for pos in dss.fuses_all_names()]

    # Processing the csv file
    read_file = pd.read_csv(file_path_partial)
    read_file.columns = [name.strip() for name in read_file.columns]

    # Processing the retained full file path
    read_file_full = pd.read_csv(file_path_full)
    read_file_full.columns = [name.strip() for name in read_file_full.columns]

    line_fuse_elem = list(map(lambda x: 'Line.' + x, fuse_pos))

    # Filtering the required data
    req_df = read_file.loc[(read_file.Element.isin(line_fuse_elem)) & (read_file.Terminal == 1)]
    req_df = req_df[["Element", "I1"]]

    # Filtering required data from full study file
    req_full_df = read_file_full.loc[(read_file_full.Element.isin(line_fuse_elem)) & (read_file_full.Terminal == 1)]
    req_full_df = req_full_df[["Element", "I1"]]

    # Processing on pv
    pv_pos = [pos.upper() for pos in dss.pvsystems_all_names()]
    line_pv_elem = list(map(lambda x: 'PVSystem.' + x, pv_pos))

    req_pv_df = read_file.loc[read_file.Element.isin(line_pv_elem)]
    req_pv_df = req_pv_df[["Element", "I1"]]

    numer = req_df.I1.reset_index(drop=True)
    denom = req_full_df.I1.reset_index(drop=True)

    pv_ratio = pd.DataFrame(numer.divide(denom)).rename(columns={"I1": pv_pos[0]}) * 100
    pv_ratio.index = req_df.Element

    # Processing in final form
    pv_ratio = pv_ratio.round()
    pv_ratio.index = [name.replace("Line.", "") for name in pv_ratio.index]
    pv_ratio = pv_ratio.astype(str) + " %"


    return pv_ratio

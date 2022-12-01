# Importing required libraries
import py_dss_interface
import os
import pandas as pd
from add_system_elements import add_fuse, add_fault, add_pv
from sim_data_processor import tab_1_processor, tab_2_processor


def dynamic_study_pf(fuse_spec_list, fault_bus_loc_list, pv_loc_list):

    # Defining file path
    file_path = os.path.dirname(os.path.abspath(__file__))

    # Creating dataframe to collect simulation results
    case_result = pd.DataFrame()
    contrib_result = pd.DataFrame()
    save_full_study_path = []

    # Specifying the run mode and required iterations
    for mode, iter_num in zip(["base_mode", "pre_fault", "full_study", "partial_study"],
                              [1, 1, 1, len(pv_loc_list)]):

        # Specifying study run iterations
        for study_iter in range(iter_num):

            # Defining the master file path
            dss_file = os.path.join(file_path, "base_IEEE123Bus_System", "IEEE123Master.dss")

            # Creating a py-dss object
            dss = py_dss_interface.DSSDLL()

            # Compiling the DSS master file
            dss.text(f"compile [{dss_file}")

            # Solving the system before adding anything
            dss.text("Solve mode=snap")

            if mode == "base_mode":
                # Adding the fuse element
                add_fuse(dss=dss, fuse_spec_list=fuse_spec_list)
                # print("Number of actual added fuse: ", dss.fuses_count())
                # print("The actual fuse curve used: ", dss.fuses_read_tcc_curve())

                # Solving the system after adding just fuse
                dss.text("Solve mode=snap")
                base_wo_pv_path = dss.text("export SeqCurrents ssm_base_wo_pv.csv")

                # Processing the data
                base_wo_pv = tab_1_processor(dss, base_wo_pv_path, index_name="Base w/o PV")
                case_result = pd.concat([case_result, base_wo_pv], axis=0)

                # Creating faults in the system
                add_fault(dss=dss, fault_bus_loc_list=fault_bus_loc_list)

                # Solving the system after adding a fault
                dss.text("Solve mode=snap")
                # Solving the system in dynamic mode
                dss.text("Solve mode=Dynamic stepsize=0.0001 Number= 1000")

                # Saving the data in csv format
                base_fault_wo_pv_path = dss.text("export SeqCurrents ssm_base_fault_wo_pv.csv")

                # Processing the data
                base_w_fault = tab_1_processor(dss, base_fault_wo_pv_path, index_name="Base fault w/o PV")
                case_result = pd.concat([case_result, base_w_fault], axis=0)

            # Adding PV first just
            if mode == "pre_fault":

                # Adding the fuse elements -> Need fuse
                add_fuse(dss=dss, fuse_spec_list=fuse_spec_list)
                # print("Number of actual added fuse: ", dss.fuses_count())
                # print("The actual fuse curve used: ", dss.fuses_read_tcc_curve())

                # Adding PV in the system
                pre_w_pv_path = add_pv(dss=dss, pv_loc_list=pv_loc_list, mode=mode, study_iter=study_iter)

                # Processing the data
                pre_w_pv = tab_1_processor(dss, pre_w_pv_path, index_name="Pre-fault w/ PV")
                case_result = pd.concat([case_result, pre_w_pv], axis=0)

            # For the other modes
            if mode in ["partial_study", "full_study"]:

                # Adding the fuse elements
                add_fuse(dss=dss, fuse_spec_list=fuse_spec_list)
                # print("Number of actual added fuse: ", dss.fuses_count())
                # print("The actual fuse curve used: ", dss.fuses_read_tcc_curve())

                # Creating faults in the system
                add_fault(dss=dss, fault_bus_loc_list=fault_bus_loc_list)

                if mode == "full_study":
                    # Adding PV in the system
                    post_f_w_pv_path = add_pv(dss=dss, pv_loc_list=pv_loc_list, mode=mode, study_iter=study_iter)
                    save_full_study_path.append(post_f_w_pv_path)

                    # Processing the data
                    post_f_w_pv = tab_1_processor(dss, post_f_w_pv_path, index_name="Post-fault w/ PV")
                    case_result = pd.concat([case_result, post_f_w_pv], axis=0)

                # For partial study
                else:
                    # Adding PV in the system
                    partial_study_path = add_pv(dss=dss, pv_loc_list=pv_loc_list, mode=mode, study_iter=study_iter)

                    # Fetching full study path
                    full_study_retained_path = save_full_study_path[0]

                    pv_bus = pv_loc_list[study_iter][0]

                    # Processing the data
                    pv_ratio = tab_2_processor(dss, partial_study_path, full_study_retained_path,
                                               index_name="Partial Study {}".format(pv_bus), pv_bus=pv_bus)
                    contrib_result = pd.concat([contrib_result, pv_ratio], axis=1)

    return case_result, contrib_result.reset_index().rename(columns={'index': 'FUSE POSITION'})

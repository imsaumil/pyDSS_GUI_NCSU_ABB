from dash.exceptions import PreventUpdate


# Creating a function to add new fuses in the system
def add_fuse(dss, fuse_spec_list):
    if len(fuse_spec_list) > 0:
        for new_fuse, new_tcc, new_r_current in fuse_spec_list:
            # Adding new fuse to the compiled system
            dss.text("New Fuse.Fuse_{} line.{} Fusecurve={} ratedcurrent={}".format(new_fuse,
                                                                                    new_fuse,
                                                                                    new_tcc,
                                                                                    new_r_current))


# Creating a function to add fault on buses
def add_fault(dss, fault_bus_loc_list):
    if len(fault_bus_loc_list) > 0:
        for fault in fault_bus_loc_list:
            # Adding new fault to the compiled system
            dss.text("New Fault.{} phases={} Bus1={}".format(fault[0], fault[1], fault[0]))


# Creating a function to add pv on buses
def add_pv(dss, pv_loc_list, mode, study_iter):
    if len(pv_loc_list) > 0:

        # Setting a XY Efficiency curve -> Constant for all PVs
        dss.text("New XYCurve.Eff npts=4 xarray=[.1 .2 .4 1.0] yarray=[1 1 1 1]")

        # Setting XY FatorPVst curve -> Constant for all PVs
        dss.text("New XYCurve.FatorPvsT npts=4 xarray=[0 25 75 100] yarray=[1.2 1 0.8 0.6]")

        # Setting a VV XY curve -> For inverter control
        dss.text("New XYCurve.vv_curve npts= 10 "
                 "Yarray=(0.9545,0.9048,0.8352,0.7457,0.6363,0.5071,0.35796,0.18892,0,0,-1,-1)"
                 "XArray=(0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,0.98,1,1.08,1.2)")

        # Setting a VW XY curve -> For inverter control
        dss.text("New XYCurve.vw_curve npts= 9 "
                 "Yarray=(0.6148,0.7120,0.8072,0.9,0.989,1,1,1,1,1,0.2,0.2) "
                 "XArray=(0.6, 0.65,0.7,0.75,0.8,0.85,0.9,0.95,0.98,1,1.08,1.2)")

        dss.text("Solve mode=snap")

        # Pre-defined dummy bus range
        pv_bus_nums = [800 + i for i in range(len(pv_loc_list))]

        if mode == "partial_study":
            # Looping over the number of PV
            pv_dum_bus = pv_bus_nums[study_iter]
            pv_bus = pv_loc_list[study_iter]

            # Add transformer -> Use the dummy bus for PV (low)
            dss.text("New Transformer.XFMPV{} Phases=3 Windings=2 Xhl=5.75 "
                     "wdg=1 bus={} conn=star kv=12.47 kva=4000 %r=0.635 "
                     "wdg=2 bus={} conn=star kv=0.48 kva={} %r=0.635".format(pv_dum_bus,
                                                                             pv_bus[0],
                                                                             pv_dum_bus,
                                                                             pv_bus[2]))

            dss.text("Solve mode=snap")

            # Inserting a static PV system -> Contains TP
            dss.text("New PVSystem.PV{} phases={} bus1={} Pmpp={} kV=0.48 kVA={} conn=delta irrad=1 "
                     "EffCurve=Eff P-TCurve=FatorPvsT %Pmpp=100 Temperature=25 kvarMax={} kvarMaxAbs={} "
                     "%cutout=0.1 %PminkvarMax=5 %PminNoVars=5 "
                     "Vminpu=0.00001 Limitcurrent=Yes Balanced=Yes ".format(pv_bus[0],
                                                                            pv_bus[1],
                                                                            pv_dum_bus,
                                                                            pv_bus[2],
                                                                            pv_bus[2] * 1.2,
                                                                            pv_bus[2] * 1.2 * 0.44,
                                                                            pv_bus[2] * 1.2 * 0.44,
                                                                            ))

            # Use high side of transformer as monitor
            dss.text("New Monitor.Transformer element=Transformer.XFMPV{} mode=0".format(pv_dum_bus))

            # Solving in static mode
            dss.text("Solve mode=snap")
            # Solving in dynamic mode as well
            dss.text("Solve mode=Dynamic stepsize=0.0001 Number= 1000")

            # Mentioning file path
            data_path = dss.text("export SeqCurrents ssm_partial_{}.csv".format(pv_bus[0]))

        else:
            # Looping over the number of PV
            for pv_dum_bus, pv_bus in zip(pv_bus_nums, pv_loc_list):

                # Add transformer -> Use the dummy bus for PV (low)
                dss.text("New Transformer.XFMPV{} Phases=3 Windings=2 Xhl=5.75 "
                         "wdg=1 bus={} conn=star kv=12.47 kva=4000 %r=0.635 "
                         "wdg=2 bus={} conn=star kv=0.48 kva={} %r=0.635".format(pv_dum_bus,
                                                                                 pv_bus[0],
                                                                                 pv_dum_bus,
                                                                                 pv_bus[2]))

                dss.text("Solve mode=snap")

                # Inserting a static PV system -> Contains TP
                dss.text("New PVSystem.PV{} phases={} bus1={} Pmpp={} kV=0.48 kVA={} conn=delta irrad=1 "
                         "EffCurve=Eff P-TCurve=FatorPvsT %Pmpp=100 Temperature=25 kvarMax={} kvarMaxAbs={} "
                         "%cutout=0.1 %PminkvarMax=5 %PminNoVars=5 "
                         "Vminpu=0.00001 Limitcurrent=Yes Balanced=Yes ".format(pv_bus[0],
                                                                                pv_bus[1],
                                                                                pv_dum_bus,
                                                                                pv_bus[2],
                                                                                pv_bus[2] * 1.2,
                                                                                pv_bus[2] * 1.2 * 0.44,
                                                                                pv_bus[2] * 1.2 * 0.44,
                                                                                ))

                # Only if in pre-fault mode -> pre-fault
                if mode == "pre_fault":
                    # Setting an inverter control for the added PV -> Contains TP
                    dss.text("New InvControl.PV{} CombiMode=VV_VW voltage_curvex_ref=ravg vvc_curve1=vv_curve "
                             "voltwatt_curve=vw_curve deltaQ_factor=0.35 deltaP_factor=0.3 EventLog=yes "
                             "RefReactivePower=VARMAX_VARS VoltageChangeTolerance=0.001".format(pv_bus[0]))

            if mode in ["pre_fault", "full_study"]:
                # Solving in static mode
                dss.text("Solve mode=snap")
                # Solving the system in dynamic mode
                dss.text("Solve mode=Dynamic stepsize=0.0001 Number= 1000")
                # Mentioning file path
                data_path = dss.text("export SeqCurrents ssm_{}.csv".format(mode))

        return data_path

    else:
        raise PreventUpdate

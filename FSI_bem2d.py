#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
BEM-2D
A 2D boundary element method code

"""
import time
import numpy as np
from data_IO_class import DataIO
from input_parameters import PARAMETERS as P
from swimmer_class import Swimmer
import parameter_classes as PC
from functions_influence import quilt, wake_rollup
from terminal_output import print_output as po
import functions_graphics as graph
from SolidClass import solid
from PyFEA import PyFEA
from FSIClass import FSI
from functions_general import panel_vectors, archive, absoluteToBody, geom_setup

po().prog_title('1.0.0')
DIO = DataIO(P['OUTPUT_DIR'])
start_time = time.time()

COUNTER = P['COUNTER']
DEL_T = P['DEL_T']
DSTEP = P['DSTEP']
TSTEP = P['TSTEP']
T = P['T']
RHO = P['RHO']
RE = P['RE']

(SwiP, GeoP, MotP, Swimmers, SolidP, FSIP, PyFEAP) = geom_setup(P, PC, Swimmer, solid, FSI, PyFEA)

po().calc_input(MotP[0].THETA_MAX/np.pi*180.,RE,MotP[0].THETA_MAX/np.pi*180.,DEL_T)

for i in xrange(COUNTER):
    if i == 0:
        po().initialize_output(T[i])

        for Swim in Swimmers:
                Swim.Body.panel_positions(DSTEP, T[i], P['THETA'][i])
                Swim.Body.surface_kinematics(DSTEP, TSTEP, P['THETA_MINUS'][i], P['THETA_PLUS'][i], DEL_T, T[i], i)
                Swim.edge_shed(DEL_T, i)
                Swim.wake_shed(DEL_T, i)
        quilt(Swimmers, RHO, DEL_T, i)
        wake_rollup(Swimmers, DEL_T, i)
        archive(Swimmers[0].Body.AF.x_mid)
        archive(Swimmers[0].Body.AF.z_mid)
        SolidP[0].nodes[:,0] = (SolidP[0].nodesNew[:,0] - SolidP[0].nodesNew[0,0])*np.cos(P['THETA'][i])
        SolidP[0].nodes[:,1] = (SolidP[0].nodesNew[:,0] - SolidP[0].nodesNew[0,0])*np.sin(P['THETA'][i])
        graph.plot_n_go(Swimmers[0].Edge, Swimmers[0].Body, SolidP[0])
        DIO.write_data(P, i, DEL_T, SwiP, GeoP, MotP, Swimmers, SolidP, FSIP, PyFEAP)

    else:
        if np.fmod(i,P['VERBOSITY']) == 0:
            po().timestep_header(i,T[i])
            po().fsi_header()

        FSIP[0].readFsiControls(P['FIXED_PT_RELAX'], P['N_OUTERCORR_MAX'])       
        FSIP[0].__init__(Swimmers[0].Body, SolidP[0])
        outerCorr = 0
        while True:
            outerCorr += 1
            FSIP[0].setInterfaceDisplacemet(outerCorr, P['COUPLING_SCHEME'])
            for Swim in Swimmers:
                if (outerCorr == 1):
                    Swim.Body.panel_positions(DSTEP, T[i], P['THETA'][i])
                else:
                    Swim.Body.AF.x += (FSIP[0].fluidNodeDispl[:,0] - FSIP[0].fluidNodeDisplOld[:,0])
                    Swim.Body.AF.z += (FSIP[0].fluidNodeDispl[:,1] - FSIP[0].fluidNodeDisplOld[:,1])
                    
                    Swim.Body.AF.x_mid[0,:] = (Swim.Body.AF.x[:-1] + Swim.Body.AF.x[1:])/2
                    Swim.Body.AF.z_mid[0,:] = (Swim.Body.AF.z[:-1] + Swim.Body.AF.z[1:])/2
                    
                    BFx = (Swim.Body.AF.x - Swim.Body.AF.x_le) * np.cos(-1*P['THETA'][i]) - (Swim.Body.AF.z - Swim.Body.AF.z_le) * np.sin(-1*P['THETA'][i])
                    BFz = (Swim.Body.AF.z - Swim.Body.AF.z_le) * np.cos(-1*P['THETA'][i]) + (Swim.Body.AF.x - Swim.Body.AF.x_le) * np.sin(-1*P['THETA'][i])
                    BFx_col = ((BFx[1:] + BFx[:-1])/2)
                    BFz_col =  ((BFz[1:] + BFz[:-1])/2)
                    Swim.Body.AF.x_col = Swim.Body.AF.x_mid[0,:] - Swim.Body.S*panel_vectors(Swim.Body.AF.x, Swim.Body.AF.z)[2]*np.absolute(BFz_col)
                    Swim.Body.AF.z_col = Swim.Body.AF.z_mid[0,:] - Swim.Body.S*panel_vectors(Swim.Body.AF.x, Swim.Body.AF.z)[3]*np.absolute(BFz_col)

                Swim.Body.surface_kinematics(DSTEP, TSTEP, P['THETA_MINUS'][i], P['THETA_PLUS'][i], DEL_T, T[i], i)
                Swim.edge_shed(DEL_T, i)
                if (outerCorr == 1):
                    Swim.wake_shed(DEL_T, i)                           

            quilt(Swimmers, RHO, DEL_T, i)

            #TODO: Replace '0' with viscous drag component when available
            FSIP[0].setInterfaceForce(SolidP[0], Swimmers[0].Body, PyFEAP[0], P['THETA'][i], P['HEAVE'][i], outerCorr,
                          P['SW_VISC_DRAG'], 0, P['SW_INTERP_MTD'], P['C'], i)
            PyFEAP[0].solve(Swimmers[0].Body, SolidP[0], outerCorr, P['M_TYPE'], P['INT_METHOD'], P['ALPHA'], P['BETA'], P['GAMMA'])
            FSIP[0].getDisplacements(SolidP[0], Swimmers[0].Body, PyFEAP[0], P['THETA'][i], P['HEAVE'][i], P['SW_INTERP_MTD'], P['FLEX_RATIO'])
            FSIP[0].calcFSIResidual(SolidP[0], outerCorr)

            if np.fmod(i,P['VERBOSITY']) == 0:
                po().fsi_iter_out(outerCorr,FSIP[0].fsiRelaxationFactor,FSIP[0].maxDU,FSIP[0].maxMagFsiResidual,FSIP[0].fsiResidualNorm,FSIP[0].maxFsiResidualNorm)

            if (FSIP[0].fsiResidualNorm <= P['OUTER_CORR_TOL'] or outerCorr >= P['N_OUTERCORR_MAX']):
                if (FSIP[0].fsiResidualNorm <= P['OUTER_CORR_TOL']):
                    po().fsi_converged()
                else:
                    po().fsi_not_converged()
                if np.fmod(i,P['VERBOSITY']) == 0:
                    po().solution_output(0,0,0,0,0,0)
                    po().solution_complete_output(i/float(COUNTER-1)*100.)
                wake_rollup(Swimmers, DEL_T, i)
                absoluteToBody(Swimmers[0].Body, SolidP[0], P['THETA'][i], P['HEAVE'][i])
                archive(Swimmers[0].Body.AF.x_mid)
                archive(Swimmers[0].Body.AF.z_mid)
                graph.plot_n_go(Swimmers[0].Edge, Swimmers[0].Body, SolidP[0])
                DIO.write_data(P, i, DEL_T, SwiP, GeoP, MotP, Swimmers, SolidP, FSIP, PyFEAP)
                break

total_time = time.time()-start_time
print "Simulation time:", np.round(total_time, 3), "seconds"

graph.body_wake_plot(Swimmers)
#    graph.cp_plot(S1.Body)
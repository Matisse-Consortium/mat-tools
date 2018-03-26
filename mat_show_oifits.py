#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  $Id: $

  This file is part of the Matisse pipeline GUI series
  Copyright (C) 2017- Observatoire de la Côte d'Azur

  Created on Sat Mar 17 06:39:49 2018
  @author: fmillour
  fmillour@oca.eu

  This software is a computer program whose purpose is to show oifits
  files from the MATISSE instrument.

  This software is governed by the CeCILL  license under French law and
  abiding by the rules of distribution of free software.  You can  use,
  modify and/ or redistribute the software under the terms of the CeCILL
  license as circulated by CEA, CNRS and INRIA at the following URL
  "http://www.cecill.info".

  As a counterpart to the access to the source code and  rights to copy,
  modify and redistribute granted by the license, users are provided only
  with a limited warranty  and the software's author,  the holder of the
  economic rights,  and the successive licensors  have only  limited
  liability.

  In this respect, the user's attention is drawn to the risks associated
  with loading,  using,  modifying and/or developing or reproducing the
  software by the user in light of its specific status of free software,
  that may mean  that it is complicated to manipulate,  and  that  also
  therefore means  that it is reserved for developers  and  experienced
  professionals having in-depth computer knowledge. Users are therefore
  encouraged to load and test the software's suitability as regards their
  requirements in conditions enabling the security of their systems and/or
  data to be ensured and,  more generally, to use and operate it in the
  same conditions as regards security.

  The fact that you are presently reading this means that you have had
  knowledge of the CeCILL license and that you accept its terms.

  Changelog:
  2018-03-23: new functions: oi_data_select_frame, filter_oi_list, open_oi_dir, show_vis2_tf2_vs_time, show_oi_vs_time (jvarga)
  2018-03-26: new GUI interface ready: oi_data_select_frame (jvarga)
"""

import sys
import wx
import math
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
from mat_fileDialog import mat_FileDialog
from mat_fileDialog import identifyFile
from astropy.io import fits as fits
import os
import glob
import robust

###############################################################################

def open_oi(oi_file):
    try:
        hdu = fits.open(oi_file)
    except IOError:
        print ("Unable to read fits file: " + oi_file)
        return {}

    hdr = hdu[0].header

    wl = hdu['OI_WAVELENGTH'].data['EFF_WAVE']
    dic = {'WLEN': wl}

    target_name = hdu['OI_TARGET'].data['TARGET'][0]
    if not target_name:
        try:
            target_name = hdr['HIERARCH ESO OBS TARG NAME']
        except KeyError:
            print ("Target name not found.")
            target_name = ""
    dic['TARGET'] = target_name
    target_category = hdu['OI_TARGET'].data['CATEGORY'][0]  # "CAL" or "SCI"
    if not target_category:
        print ("Target category not found.")
        target_category = "CAL"
    dic['CATEGORY'] = target_category
    try:
        dateobs = hdr['DATE-OBS']
    except KeyError:
        dateobs = ""
    dic['DATEOBS'] = dateobs
    try:
        det_name = hdr['HIERARCH ESO DET CHIP NAME']
    except KeyError:
        print ("Detector name not found.")
        det_name = ""
    if (det_name == 'AQUARIUS'):
        band = 'N'
    elif (det_name == 'HAWAII-2RG'):
        band = 'LM'
    else:
        band = ''
    dic['BAND'] = band
    try:
        dispersion_name = hdr['HIERARCH ESO DET DISP NAME']
    except KeyError:
        print ("Dispersion name not found.")
        dispersion_name = ""
    dic['DISP'] = dispersion_name
    try:
        DIT = hdr["HIERARCH ESO DET SEQ1 DIT"]  # (s)
    except KeyError:
        DIT = np.nan
        print ("DIT not found")
    dic['DIT'] = DIT
    try:
        BCD1 = hdr["HIERARCH ESO INS BCD1 NAME"]
        BCD2 = hdr["HIERARCH ESO INS BCD2 NAME"]
    except KeyError:
        BCD1 = ""
        BCD2 = ""
        print ("BCD NAME not found")
    dic['BCD1NAME'] = BCD1
    dic['BCD2NAME'] = BCD2
    try:
        dic['TEL_NAME'] = hdu['OI_ARRAY'].data["TEL_NAME"]
        dic['STA_NAME'] = hdu['OI_ARRAY'].data["STA_NAME"]
        dic['STA_INDEX'] = hdu['OI_ARRAY'].data["STA_INDEX"]
    except KeyError:
        dic['TEL_NAME'] = {}
        dic['STA_NAME'] = {}
        dic['STA_INDEX'] = {}
        print ("Key in table OI_ARRAY not found")
    try:
        dic['VIS'] = {}
        dic['VIS']['CFLUX'] = hdu['OI_VIS'].data['VISAMP']
        dic['VIS']['CFLUXERR'] = hdu['OI_VIS'].data['VISAMPERR']
        dic['VIS']['DPHI'] = hdu['OI_VIS'].data['VISPHI']
        dic['VIS']['DPHIERR'] = hdu['OI_VIS'].data['VISPHIERR']
        dic['VIS']['U'] = hdu['OI_VIS'].data['UCOORD']
        dic['VIS']['V'] = hdu['OI_VIS'].data['VCOORD']
        dic['VIS']['TIME'] = hdu['OI_VIS'].data['MJD']
        dic['VIS']['STA_INDEX'] = hdu['OI_VIS'].data['STA_INDEX']
    except:
        print("WARNING: No OI_VIS table!")

    try:
        dic['VIS2'] = {}
        dic['VIS2']['VIS2'] = hdu['OI_VIS2'].data['VIS2DATA']
        dic['VIS2']['VIS2ERR'] = hdu['OI_VIS2'].data['VIS2ERR']
        dic['VIS2']['U'] = hdu['OI_VIS2'].data['UCOORD']
        dic['VIS2']['V'] = hdu['OI_VIS2'].data['VCOORD']
        dic['VIS2']['TIME'] = hdu['OI_VIS2'].data['MJD']
        dic['VIS2']['STA_INDEX'] = hdu['OI_VIS2'].data['STA_INDEX']
    except:
        print("WARNING: No OI_VIS2 table!")

    try:
        dic['TF2'] = {}
        dic['TF2']['TF2'] = hdu['OI_TF2'].data['TF2']
        dic['TF2']['TF2ERR'] = hdu['OI_TF2'].data['TF2ERR']
        # dic['TF2']['U']       = hdu['OI_TF2'].data['UCOORD']
        # dic['TF2']['V']       = hdu['OI_TF2'].data['VCOORD']
        dic['TF2']['TIME'] = hdu['OI_TF2'].data['MJD']
        dic['TF2']['STA_INDEX'] = hdu['OI_TF2'].data['STA_INDEX']
    except:
        print("WARNING: No OI_TF2 table!")

    try:
        dic['T3'] = {}
        dic['T3']['T3AMP'] = hdu['OI_T3'].data['T3AMP']
        dic['T3']['T3AMPERR'] = hdu['OI_T3'].data['T3AMPERR']
        dic['T3']['CLOS'] = hdu['OI_T3'].data['T3PHI']
        dic['T3']['CLOSERR'] = hdu['OI_T3'].data['T3PHIERR']
        dic['T3']['U1'] = hdu['OI_T3'].data['U1COORD']
        dic['T3']['V1'] = hdu['OI_T3'].data['V1COORD']
        dic['T3']['U2'] = hdu['OI_T3'].data['U2COORD']
        dic['T3']['V2'] = hdu['OI_T3'].data['V2COORD']
        dic['T3']['TIME'] = hdu['OI_T3'].data['MJD']
        dic['T3']['STA_INDEX'] = hdu['OI_T3'].data['STA_INDEX']
    except:
        print("WARNING: No OI_T3 table!")

    try:
        dic['FLUX'] = {}
        dic['FLUX']['FLUX'] = hdu['OI_FLUX'].data['FLUXDATA']
        dic['FLUX']['FLUXERR'] = hdu['OI_FLUX'].data['FLUXERR']
        dic['FLUX']['TIME'] = hdu['OI_FLUX'].data['MJD']
        dic['FLUX']['STA_INDEX'] = hdu['OI_FLUX'].data['STA_INDEX']
    except:
        print("WARNING: No OI_FLUX table!")

    return dic


###############################################################################

def show_oi_vs_freq(dic, log=False):
    wl = dic['WLEN'];
    vis2 = dic['VIS2']['VIS2'];
    vis2e = dic['VIS2']['VIS2ERR'];
    u = dic['VIS2']['U'];
    v = dic['VIS2']['V'];
    cp = dic['T3']['CLOS'];
    cpe = dic['T3']['CLOSERR'];
    u1 = dic['T3']['U1'];
    v1 = dic['T3']['V1'];
    u2 = dic['T3']['U2'];
    v2 = dic['T3']['V2'];

    plt.figure(figsize=(9, 6))
    G = gridspec.GridSpec(2, 1)

    axes_v2 = plt.subplot(G[0, :])

    # Plot all data first
    for i, j in enumerate(u):
        r = np.sqrt(u[i] ** 2 + v[i] ** 2);
        freq = r / wl;
        if log:
            axes_v2.semilogy(freq, vis2[i, :], color='lightgray')
            plt.ylim([1e-4, 1.1])
        else:
            axes_v2.plot(freq, vis2[i, :], color='lightgray')

    # Plot valid data
    for i, j in enumerate(u):
        r = np.sqrt(u[i] ** 2 + v[i] ** 2);
        freq = r / wl;
        test = np.logical_and(vis2[i, :] >= 0, vis2e[i, :] / vis2[i, :] < 1)
        if log:
            axes_v2.semilogy(freq[test], vis2[i, test])
            plt.ylim([1e-4, 1.1])
        else:
            axes_v2.plot(freq[test], vis2[i, test])

    plt.ylim([-0.1, 1.1])
    plt.ylabel('V2')
    # plt.xlabel('Spatial Frequency (B/$\lambda$)')
    axes_v2.set_title('Squared visibilities vs frequencies')

    # Plot all data first
    axes_cp = plt.subplot(G[1, :])
    for i, j in enumerate(u1):
        r1 = np.sqrt(u1[i] ** 2 + v1[i] ** 2);
        r2 = np.sqrt(u2[i] ** 2 + v2[i] ** 2);
        r3 = np.sqrt((u1[i] + u2[i]) ** 2 + (v1[i] + v2[i]) ** 2);
        freq = np.maximum(np.maximum(r1, r2), r3) / wl;
        axes_cp.plot(freq, cp[i, :], color='lightgray')

    # Plot valid data only
    for i, j in enumerate(u1):
        r1 = np.sqrt(u1[i] ** 2 + v1[i] ** 2);
        r2 = np.sqrt(u2[i] ** 2 + v2[i] ** 2);
        r3 = np.sqrt((u1[i] + u2[i]) ** 2 + (v1[i] + v2[i]) ** 2);
        freq = np.maximum(np.maximum(r1, r2), r3) / wl;
        test = np.absolute(cpe[i, :]) < 180 / math.pi / 3
        axes_cp.plot(freq[test], cp[i, test])

    plt.ylim([-200, 200])
    axes_cp.set_title('Closure phase vs frequencies')
    plt.ylabel('Closure phase')
    plt.xlabel('Spatial Frequency (B/$\lambda$)')

    plt.show()


###############################################################################

def show_oi_vs_wlen(dic,key='VIS2', datatype="VIS2"):
    plot_colors = ['red', 'blue', 'green', 'gold', 'magenta', 'cyan', 'orange', 'pink', 'purple', 'darkgreen']
    wl = dic['WLEN'];
    data = dic[key][datatype];
    datae = dic[key][datatype + "ERR"];
    #print datae
    #print datae.shape
    for i, j in enumerate(data):
        plt.errorbar(wl*1e6, data[i,:],yerr=datae[i,:],ecolor='grey',alpha=0.25,capsize=0.5,elinewidth=1)
        plt.plot(wl * 1e6, data[i, :])
    if datatype == 'VIS2' or datatype == 'TF2':
        plt.ylim([-0.1,1.1])
    else:
        try:
            plt.ylim([np.nanmin(data),np.nanmax(data)])
        except:
            pass
    plt.title(datatype+' vs. wavelength')
    plt.xlabel(r"$\lambda\ \mu\mathrm{m}$")
    plt.ylabel(datatype)
    plt.show()


###############################################################################
# This function shows the selected oifits data (flux, visibility, closure phase etc.)
# as a function of time. It reads data from multiple oifits files in a given
# directory.
# The data to be plotted can be filtered with the filter_oi_list function.
# Example usage:
# filtered_list_of_dicts = filter_oi_list(list_of_dicts,dates=["2018-03-14"],bands=['LM'],spectral_resolutions=['MED'],DIT_range=[0,0.2],targets=['l pup'])
# show_oi_vs_time(filtered_list_of_dicts, [3.5, 3.95], key="VIS2", datatype='VIS2') #[3.5, 3.95] [10.2,10.9]
#
def show_oi_vs_time(list_of_dicts, wlenRange, key="VIS2", datatype="VIS2"):
    # check if list is not empty:
    if list_of_dicts:
        target_names_cal = []
        MJD_arr_cal = []
        arr_cal = []
        err_arr_cal = []
        sta_index_cal = []

        target_names_sci = []
        MJD_arr_sci = []
        arr_sci = []
        err_arr_sci = []
        sta_index_sci = []

        for dic in list_of_dicts:
            wl = np.array(dic['WLEN'])
            wlenRange_idx = np.logical_and(wl > wlenRange[0] / 1.0e6, wl < wlenRange[1] / 1.0e6)
            category = dic['CATEGORY'].lower()
            if 'cal' in category:
                try:
                    datay = np.array(dic[key][datatype])
                    datayerr = np.array(dic[key][datatype+'ERR'])
                    datax = np.array(dic[key]["TIME"])
                    n_rows = datay.shape[0]
                    # print datay.shape
                    for i in range(n_rows):
                        arr_cal.append(robust.mean(datay[i, wlenRange_idx]))
                        err_arr_cal.append(robust.mean(datayerr[i, wlenRange_idx]))
                        MJD_arr_cal.append(datax[i])
                        target_names_cal.append(dic['TARGET'])
                        if key == 'FLUX':
                            sta_index = dic[key]['STA_INDEX'][i]
                            sta_index_cal.append([sta_index])
                        else:
                            sta_index = np.sort(dic[key]['STA_INDEX'][i])
                            sta_index_cal.append(sta_index)
                        # print dic[key]['STA_INDEX'][i]
                except:
                    print (dic['TARGET'], dic['DATEOBS'], "No CAL data found.")
            elif 'sci' in category:
                try:
                    datay = np.array(dic[key][datatype])
                    datayerr = np.array(dic[key][datatype+'ERR'])
                    datax = np.array(dic[key]["TIME"])
                    n_rows = datay.shape[0]
                    # print datay.shape
                    for i in range(n_rows):
                        arr_sci.append(robust.mean(datay[i, wlenRange_idx]))
                        err_arr_sci.append(robust.mean(datayerr[i, wlenRange_idx]))
                        MJD_arr_sci.append(datax[i])
                        target_names_sci.append(dic['TARGET'])
                        if key == 'FLUX':
                            sta_index = dic[key]['STA_INDEX'][i]
                            sta_index_sci.append([sta_index])
                        else:
                            sta_index = np.sort(dic[key]['STA_INDEX'][i])
                            sta_index_sci.append(sta_index)
                except:
                    print (dic['TARGET'], dic['DATEOBS'], "No SCI data found.")
            sta_names = dic['STA_NAME']

        target_names_cal = np.array(target_names_cal)
        MJD_arr_cal = np.array(MJD_arr_cal)
        arr_cal = np.array(arr_cal)
        err_arr_cal = np.array(err_arr_cal)
        sta_index_cal = np.array(sta_index_cal)

        target_names_sci = np.array(target_names_sci)
        MJD_arr_sci = np.array(MJD_arr_sci)
        arr_sci = np.array(arr_sci)
        err_arr_sci = np.array(err_arr_sci)
        sta_index_sci = np.array(sta_index_sci)

        sta_indices = np.unique(sta_index_cal, axis=0)
        if key == 'VIS' or key == 'VIS2' or key == 'TF2':
            n_max_config = np.nanmax([6, sta_indices.shape[0]])
            n_plot_rows = 3
        elif key == 'T3' or key == 'FLUX':
            n_max_config = np.nanmax([4, sta_indices.shape[0]])
            n_plot_rows = 2
        # print sta_indices.shape

        if len(MJD_arr_cal) > 0 and len(MJD_arr_sci) > 0:
            MJD_range = [np.nanmin([np.nanmin(MJD_arr_cal), np.nanmin(MJD_arr_sci)]),
                         np.nanmax([np.nanmax(MJD_arr_cal), np.nanmax(MJD_arr_sci)])]
        elif len(MJD_arr_sci) > 0:
            MJD_range = [np.nanmin(MJD_arr_sci), np.nanmax(MJD_arr_sci)]
        elif len(MJD_arr_cal) > 0:
            MJD_range = [np.nanmin(MJD_arr_cal), np.nanmax(MJD_arr_cal)]
        else:
            MJD_range = [0.0, 1.0]
        text_width_MJD = (MJD_range[1] - MJD_range[0]) / 20.0

        fig1, axs1 = plt.subplots(n_plot_rows, 2, figsize=(15, 16), sharex=True, sharey=True)
        axs1 = axs1.ravel()
        for i in range(n_max_config):
            # print i
            if datatype == 'DPHI' or datatype == 'CLOS':
                axs1[i + 0].plot(MJD_range, [0.0, 0.0], '-', color='gray', lw=1.5)
            if len(sta_index_cal) > 0:
                idxst = np.all(sta_index_cal == sta_indices[i], axis=1)
                if len(arr_cal[idxst]) > 0:
                    label = datatype +' cal'
                    axs1[i].errorbar(MJD_arr_cal[idxst], arr_cal[idxst],
                                                 yerr=err_arr_cal[idxst],
                                                 fmt='o', color='blue', elinewidth=1.0,
                                                 label=label)
                    if i in range(2):
                        text_tag_flag = 1
                        prev_text_MJD = 0.0
                        prev_target_name = ""
                        for j in range(np.sum(idxst)):
                            if MJD_arr_cal[idxst][j] > (prev_text_MJD + text_width_MJD):
                                text_tag_flag = 1
                            if text_tag_flag == 1 or (prev_target_name != target_names_cal[idxst][j]):
                                ymin, ymax = axs1[i + 0].get_ylim()
                                axs1[i].text(MJD_arr_cal[idxst][j], ymax * 1.05,
                                             target_names_cal[idxst][j].replace('_', ' '), rotation=90,
                                             va='bottom')
                                text_tag_flag = 0
                                prev_text_MJD = MJD_arr_cal[idxst][j]
                                prev_target_name = target_names_cal[idxst][j]
            if len(sta_index_sci) > 0:
                label = datatype +' sci'
                idxst = np.all(sta_index_sci == sta_indices[i], axis=1)
                if len(arr_sci[idxst]) > 0:
                    axs1[i].errorbar(MJD_arr_sci[idxst], arr_sci[idxst], yerr=err_arr_sci[idxst],
                                                 fmt='o', color='red', elinewidth=1.0,
                                                 label=label)
                    if i in range(2):
                        text_tag_flag = 1
                        prev_text_MJD = 0.0
                        prev_target_name = ""
                        for j in range(np.sum(idxst)):
                            if MJD_arr_sci[idxst][j] > (prev_text_MJD + text_width_MJD):
                                text_tag_flag = 1
                            if text_tag_flag == 1 or (prev_target_name != target_names_sci[idxst][j]):
                                ymin, ymax = axs1[i + 0].get_ylim()
                                axs1[i].text(MJD_arr_sci[idxst][j], ymax*1.05, target_names_sci[idxst][j].replace('_', ' '),
                                             rotation=90, va='bottom', color='darkred')
                                text_tag_flag = 0
                                prev_text_MJD = MJD_arr_sci[idxst][j]
                                prev_target_name = target_names_sci[idxst][j]
            if key == 'VIS' or key == 'VIS2' or key == 'TF2':
                axlabel = sta_names[sta_indices[i, 0] == dic['STA_INDEX']][0] + ' - ' + \
                      sta_names[sta_indices[i, 1] == dic['STA_INDEX']][0]
            elif key == 'T3':
                axlabel = sta_names[sta_indices[i, 0] == dic['STA_INDEX']][0] + ' - ' + \
                      sta_names[sta_indices[i, 1] == dic['STA_INDEX']][0] + ' - ' + \
                      sta_names[sta_indices[i, 2] == dic['STA_INDEX']][0]
            elif key == 'FLUX':
                axlabel = sta_names[sta_indices[i, 0] == dic['STA_INDEX']][0]
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            axs1[i].text(0.05, 0.95, axlabel, horizontalalignment='left', verticalalignment='top',
                         transform=axs1[i].transAxes, bbox=props)
            if i == 0:
                leg = axs1[i].legend(loc='upper right')
                leg.get_frame().set_alpha(0.5)
            if datatype == 'VIS2' or datatype == 'TF2':
                axs1[i].set_ylim([-0.1, 1.1])
            else:
                try:
                    axs1[i].set_ylim([np.nanmin([np.nanmin(arr_cal),np.nanmin(arr_sci)]), np.nanmax([np.nanmax(arr_cal),np.nanmax(arr_sci)])])
                except:
                    pass
            ylabel = datatype
            axs1[i].set_ylabel(ylabel)
            axs1[i].set_xlabel('$\mathrm{MJD}$')
        plt.suptitle('$\mathrm{'+datatype+'\ vs.\ time}$')
        # fig1.subplots_adjust(hspace=0, wspace=0)
        # for i in range(4):
        #     plt.setp(axs1[i].get_xticklabels(), visible=False)
        #     x_axis = axs1[i].axes.get_xaxis()
        #     x_axis.get_label().set_visible(False)
        # for i in range(1, 6, 2):
        #     plt.setp(axs1[i].get_yticklabels(), visible=False)
        #     y_axis = axs1[i].axes.get_yaxis()
        #     y_axis.get_label().set_visible(False)
        plt.tight_layout()
        plt.show()

###############################################################################
# showvis: if True, plot visibilities (V) instead of V^2: V is calculated from V^2 (not from the VISAMP table)
def show_vis2_tf2_vs_time(list_of_dicts, wlenRange, showvis=False, saveplots=False, output_path=""):
    # check if list is not empty:
    if list_of_dicts:
        # colors: BCD: out-out, in-in, in-out, out-in
        BCD_configs = np.array([[0, 0], [1, 1], [1, 0], [0, 1]])
        BCD_labels = np.array(['OUT-OUT', 'IN-IN', 'IN-OUT', 'OUT-IN'])
        BCD_markers = np.array(['o', 's', 'd', 'p'])
        V2_cal_colors = np.array(['darkseagreen', 'yellowgreen', 'olivedrab', 'darkkhaki'])
        V2_colors = np.array(['red', 'orange', 'salmon', 'pink'])
        TF2_colors = np.array(['blue', 'dodgerblue', 'royalblue', 'indigo'])

        target_names_cal = []
        V2_BCD_arr_cal = []
        V2_MJD_arr_cal = []
        V2_arr_cal = []
        V2err_arr_cal = []
        V2_sta_index_cal = []

        target_names_CP_cal = []
        CP_BCD_arr_cal = []
        CP_MJD_arr_cal = []
        CP_arr_cal = []
        CPerr_arr_cal = []
        CP_sta_index_cal = []

        target_names_TF2 = []
        TF2_BCD_arr = []
        TF2_MJD_arr = []
        TF2_arr = []
        TF2err_arr = []
        TF2_sta_index = []

        target_names = []
        V2_BCD_arr = []
        V2_MJD_arr = []
        V2_arr = []
        V2err_arr = []
        V2_sta_index = []

        target_names_CP = []
        CP_BCD_arr = []
        CP_MJD_arr = []
        CP_arr = []
        CPerr_arr = []
        CP_sta_index = []

        for dic in list_of_dicts:
            wl = np.array(dic['WLEN'])
            wlenRange_idx = np.logical_and(wl > wlenRange[0] / 1.0e6, wl < wlenRange[1] / 1.0e6)
            category = dic['CATEGORY'].lower()
            if 'cal' in category:
                try:
                    datay = np.array(dic['VIS2']['VIS2'])
                    datayerr = np.array(dic['VIS2']['VIS2ERR'])
                    datax = np.array(dic['VIS2']["TIME"])
                    n_rows = datay.shape[0]
                    # print datay.shape
                    for i in range(n_rows):
                        # print robust.mean(datay[i, wlenRange_idx])
                        if dic['BCD1NAME'] == 'IN':
                            BCD1 = 1
                        elif dic['BCD1NAME'] == 'OUT':
                            BCD1 = 0
                        else:
                            BCD1 = 0
                        if dic['BCD2NAME'] == 'IN':
                            BCD2 = 1
                        elif dic['BCD2NAME'] == 'OUT':
                            BCD2 = 0
                        else:
                            BCD2 = 0
                        V2_arr_cal.append(robust.mean(datay[i, wlenRange_idx]))
                        V2err_arr_cal.append(robust.mean(datayerr[i, wlenRange_idx]))
                        V2_BCD_arr_cal.append([BCD1, BCD2])
                        V2_MJD_arr_cal.append(datax[i])
                        target_names_cal.append(dic['TARGET'])
                        sta_index = np.sort(dic['VIS2']['STA_INDEX'][i])
                        V2_sta_index_cal.append(sta_index)
                except:
                    print (dic['TARGET'], dic['DATEOBS'], "No CAL VIS2 data found.")
                try:
                    datay = np.array(dic['T3']['CLOS'])
                    datayerr = np.array(dic['T3']['CLOSERR'])
                    datax = np.array(dic['T3']["TIME"])
                    n_rows = datay.shape[0]
                    for i in range(n_rows):
                        if dic['BCD1NAME'] == 'IN':
                            BCD1 = 1
                        elif dic['BCD1NAME'] == 'OUT':
                            BCD1 = 0
                        else:
                            BCD1 = 0
                        if dic['BCD2NAME'] == 'IN':
                            BCD2 = 1
                        elif dic['BCD2NAME'] == 'OUT':
                            BCD2 = 0
                        else:
                            BCD2 = 0
                        CP_arr_cal.append(robust.mean(datay[i, wlenRange_idx]))
                        CPerr_arr_cal.append(robust.mean(datayerr[i, wlenRange_idx]))
                        CP_BCD_arr_cal.append([BCD1, BCD2])
                        CP_MJD_arr_cal.append(datax[i])
                        target_names_CP_cal.append(dic['TARGET'])
                        sta_index = np.sort(dic['T3']['STA_INDEX'][i])
                        CP_sta_index_cal.append(sta_index)
                except:
                    print (dic['TARGET'], dic['DATEOBS'], "No CAL CP data found.")
                try:
                    datay = np.array(dic['TF2']['TF2'])
                    datayerr = np.array(dic['TF2']['TF2ERR'])
                    datax = np.array(dic['TF2']["TIME"])
                    n_rows = datay.shape[0]
                    # print datay.shape
                    for i in range(n_rows):
                        # print robust.mean(datay[i, wlenRange_idx])
                        if dic['BCD1NAME'] == 'IN':
                            BCD1 = 1
                        elif dic['BCD1NAME'] == 'OUT':
                            BCD1 = 0
                        else:
                            BCD1 = 0
                        if dic['BCD2NAME'] == 'IN':
                            BCD2 = 1
                        elif dic['BCD2NAME'] == 'OUT':
                            BCD2 = 0
                        else:
                            BCD2 = 0
                        TF2_arr.append(robust.mean(datay[i, wlenRange_idx]))
                        TF2err_arr.append(robust.mean(datayerr[i, wlenRange_idx]))
                        TF2_BCD_arr.append([BCD1, BCD2])
                        TF2_MJD_arr.append(datax[i])
                        target_names_TF2.append(dic['TARGET'])
                        sta_index = np.sort(dic['TF2']['STA_INDEX'][i])
                        TF2_sta_index.append(sta_index)
                except:
                    print (dic['TARGET'], dic['DATEOBS'], "No CAL TF2 data found.")
            if 'sci' in category:
                try:
                    datay = np.array(dic['VIS2']['VIS2'])
                    datayerr = np.array(dic['VIS2']['VIS2ERR'])
                    datax = np.array(dic['VIS2']["TIME"])
                    n_rows = datay.shape[0]
                    # print datay.shape
                    for i in range(n_rows):
                        if dic['BCD1NAME'] == 'IN':
                            BCD1 = 1
                        elif dic['BCD1NAME'] == 'OUT':
                            BCD1 = 0
                        else:
                            BCD1 = 0
                        if dic['BCD2NAME'] == 'IN':
                            BCD2 = 1
                        elif dic['BCD2NAME'] == 'OUT':
                            BCD2 = 0
                        else:
                            BCD2 = 0
                        V2_arr.append(robust.mean(datay[i, wlenRange_idx]))
                        V2err_arr.append(robust.mean(datayerr[i, wlenRange_idx]))
                        V2_BCD_arr.append([BCD1, BCD2])
                        V2_MJD_arr.append(datax[i])
                        target_names.append(dic['TARGET'])
                        sta_index = np.sort(dic['VIS2']['STA_INDEX'][i])
                        V2_sta_index.append(sta_index)
                except:
                    print (dic['TARGET'], dic['DATEOBS'], "No SCI VIS2 data found.")
                try:
                    datay = np.array(dic['T3']['CLOS'])
                    datayerr = np.array(dic['T3']['CLOSERR'])
                    datax = np.array(dic['T3']["TIME"])
                    n_rows = datay.shape[0]
                    for i in range(n_rows):
                        if dic['BCD1NAME'] == 'IN':
                            BCD1 = 1
                        elif dic['BCD1NAME'] == 'OUT':
                            BCD1 = 0
                        else:
                            BCD1 = 0
                        if dic['BCD2NAME'] == 'IN':
                            BCD2 = 1
                        elif dic['BCD2NAME'] == 'OUT':
                            BCD2 = 0
                        else:
                            BCD2 = 0
                        CP_arr.append(robust.mean(datay[i, wlenRange_idx]))
                        CPerr_arr.append(robust.mean(datayerr[i, wlenRange_idx]))
                        target_names_CP.append(dic['TARGET'])
                        sta_index = np.sort(dic['T3']['STA_INDEX'][i])
                        CP_sta_index.append(sta_index)
                        CP_BCD_arr.append([BCD1, BCD2])
                        CP_MJD_arr.append(datax[i])
                except:
                    print (dic['TARGET'], dic['DATEOBS'], "No SCI CP data found.")

        sta_names = dic['STA_NAME']

        target_names_cal = np.array(target_names_cal)
        V2_BCD_arr_cal = np.array(V2_BCD_arr_cal)
        V2_MJD_arr_cal = np.array(V2_MJD_arr_cal)
        V2_arr_cal = np.array(V2_arr_cal)
        V2err_arr_cal = np.array(V2err_arr_cal)
        V2_sta_index_cal = np.array(V2_sta_index_cal)

        target_names_CP_cal = np.array(target_names_CP_cal)
        CP_BCD_arr_cal = np.array(CP_BCD_arr_cal)
        CP_MJD_arr_cal = np.array(CP_MJD_arr_cal)
        CP_arr_cal = np.array(CP_arr_cal)
        CPerr_arr_cal = np.array(CPerr_arr_cal)
        CP_sta_index_cal = np.array(CP_sta_index_cal)

        target_names_TF2 = np.array(target_names_TF2)
        TF2_BCD_arr = np.array(TF2_BCD_arr)
        TF2_MJD_arr = np.array(TF2_MJD_arr)
        TF2_arr = np.array(TF2_arr)
        TF2err_arr = np.array(TF2err_arr)
        TF2_sta_index = np.array(TF2_sta_index)

        target_names = np.array(target_names)
        V2_BCD_arr = np.array(V2_BCD_arr)
        V2_MJD_arr = np.array(V2_MJD_arr)
        V2_arr = np.array(V2_arr)
        V2err_arr = np.array(V2err_arr)
        V2_sta_index = np.array(V2_sta_index)

        target_names_CP = np.array(target_names_CP)
        CP_BCD_arr = np.array(CP_BCD_arr)
        CP_MJD_arr = np.array(CP_MJD_arr)
        CP_arr = np.array(CP_arr)
        CPerr_arr = np.array(CPerr_arr)
        CP_sta_index = np.array(CP_sta_index)

        sta_indices = np.unique(V2_sta_index_cal, axis=0)
        n_max_config = np.nanmax([6, sta_indices.shape[0]])
        # print sta_indices.shape

        if len(V2_MJD_arr_cal) > 0 and len(V2_MJD_arr) > 0:
            MJD_range = [np.nanmin([np.nanmin(V2_MJD_arr_cal), np.nanmin(V2_MJD_arr)]),
                         np.nanmax([np.nanmax(V2_MJD_arr_cal), np.nanmax(V2_MJD_arr)])]
        elif len(V2_MJD_arr) > 0:
            MJD_range = [np.nanmin(V2_MJD_arr), np.nanmax(V2_MJD_arr)]
        elif len(V2_MJD_arr_cal) > 0:
            MJD_range = [np.nanmin(V2_MJD_arr_cal), np.nanmax(V2_MJD_arr_cal)]
        else:
            MJD_range = [0.0, 1.0]
        text_width_MJD = (MJD_range[1] - MJD_range[0]) / 20.0
        fig1, axs1 = plt.subplots(3, 2, figsize=(15, 16), sharex=True, sharey=True)
        axs1 = axs1.ravel()
        text_y = 1.15
        for i in range(n_max_config):
            # print i
            if len(V2_sta_index_cal) > 0:
                idxst = np.all(V2_sta_index_cal == sta_indices[i], axis=1)
                if len(V2_arr_cal[idxst]) > 0:
                    if showvis == True:
                        label = 'V cal '
                    else:
                        label = 'V2 cal '
                    for j in range(len(BCD_configs)):
                        BCDidx = np.all(V2_BCD_arr_cal == BCD_configs[j], axis=1)
                        cidxst = np.logical_and(idxst, BCDidx)
                        if len(V2_arr_cal[cidxst]) > 0:
                            if showvis == True:
                                axs1[i].errorbar(V2_MJD_arr_cal[cidxst], np.sqrt(V2_arr_cal[cidxst]),
                                                 yerr=0.5 * V2err_arr_cal[cidxst] / np.sqrt(V2_arr_cal[cidxst]),
                                                 fmt=BCD_markers[j], color=V2_cal_colors[j], elinewidth=1.5,
                                                 label=label + BCD_labels[j])
                            else:
                                axs1[i].errorbar(V2_MJD_arr_cal[cidxst], V2_arr_cal[cidxst],
                                                 yerr=V2err_arr_cal[cidxst],
                                                 fmt=BCD_markers[j], color=V2_cal_colors[j], elinewidth=1.5,
                                                 label=label + BCD_labels[j])
                    if i in range(2):
                        text_tag_flag = 1
                        prev_text_MJD = 0.0
                        prev_target_name = ""
                        for j in range(np.sum(idxst)):
                            if V2_MJD_arr_cal[idxst][j] > (prev_text_MJD + text_width_MJD):
                                text_tag_flag = 1
                            if text_tag_flag == 1 or (prev_target_name != target_names_cal[idxst][j]):
                                axs1[i].text(V2_MJD_arr_cal[idxst][j], text_y,
                                             target_names_cal[idxst][j].replace('_', ' '), rotation=90,
                                             va='bottom')
                                text_tag_flag = 0
                                prev_text_MJD = V2_MJD_arr_cal[idxst][j]
                                prev_target_name = target_names_cal[idxst][j]
            if len(TF2_sta_index) > 0:
                if showvis == True:
                    label = 'TF '
                else:
                    label = 'TF2 '
                idxst = np.all(TF2_sta_index == sta_indices[i], axis=1)
                if len(TF2_arr[idxst]) > 0:
                    for j in range(len(BCD_configs)):
                        BCDidx = np.all(TF2_BCD_arr == BCD_configs[j], axis=1)
                        cidxst = np.logical_and(idxst, BCDidx)
                        if len(TF2_arr[cidxst]) > 0:
                            if showvis == True:
                                axs1[i].errorbar(TF2_MJD_arr[cidxst], np.sqrt(TF2_arr[cidxst]),
                                                 yerr=0.5 * TF2err_arr[cidxst] / np.sqrt(TF2_arr[cidxst]),
                                                 fmt=BCD_markers[j], color=TF2_colors[j], elinewidth=1.5,
                                                 label=label + BCD_labels[j])
                            else:
                                axs1[i].errorbar(TF2_MJD_arr[cidxst], TF2_arr[cidxst], yerr=TF2err_arr[cidxst],
                                                 fmt=BCD_markers[j], color=TF2_colors[j], elinewidth=1.5,
                                                 label=label + BCD_labels[j])
            if len(V2_sta_index) > 0:
                if showvis == True:
                    label = 'V sci '
                else:
                    label = 'V2 sci '
                idxst = np.all(V2_sta_index == sta_indices[i], axis=1)
                if len(V2_arr[idxst]) > 0:
                    for j in range(len(BCD_configs)):
                        BCDidx = np.all(V2_BCD_arr == BCD_configs[j], axis=1)
                        cidxst = np.logical_and(idxst, BCDidx)
                        if len(V2_arr[cidxst]) > 0:
                            if showvis == True:
                                axs1[i].errorbar(V2_MJD_arr[cidxst], np.sqrt(V2_arr[cidxst]),
                                                 yerr=0.5 * V2err_arr[cidxst] / np.sqrt(V2_arr[cidxst]),
                                                 fmt=BCD_markers[j], color=V2_colors[j], elinewidth=1.5,
                                                 label=label + BCD_labels[j])
                            else:
                                axs1[i].errorbar(V2_MJD_arr[cidxst], V2_arr[cidxst], yerr=V2err_arr[cidxst],
                                                 fmt=BCD_markers[j], color=V2_colors[j], elinewidth=1.5,
                                                 label=label + BCD_labels[j])
                    if i in range(2):
                        text_tag_flag = 1
                        prev_text_MJD = 0.0
                        prev_target_name = ""
                        for j in range(np.sum(idxst)):
                            if V2_MJD_arr[idxst][j] > (prev_text_MJD + text_width_MJD):
                                text_tag_flag = 1
                            if text_tag_flag == 1 or (prev_target_name != target_names[idxst][j]):
                                axs1[i].text(V2_MJD_arr[idxst][j], text_y, target_names[idxst][j].replace('_', ' '),
                                             rotation=90, va='bottom', color='darkred')
                                text_tag_flag = 0
                                prev_text_MJD = V2_MJD_arr[idxst][j]
                                prev_target_name = target_names[idxst][j]

            axlabel = sta_names[sta_indices[i, 0] == dic['STA_INDEX']][0] + ' - ' + \
                      sta_names[sta_indices[i, 1] == dic['STA_INDEX']][0]
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            axs1[i].text(0.05, 0.95, axlabel, horizontalalignment='left', verticalalignment='top',
                         transform=axs1[i].transAxes, bbox=props)
            if i == 0:
                leg = axs1[i].legend(loc='upper right')
                leg.get_frame().set_alpha(0.5)
            axs1[i].set_ylim([-0.1, 1.1])
            if showvis == True:
                ylabel = '$V$'
            else:
                ylabel = '$V^2$'
            axs1[i].set_ylabel(ylabel)
            axs1[i].set_xlabel('$\mathrm{MJD}$')
        if showvis == True:
            plt.suptitle('$V\mathrm{\ vs.\ time}$')
        else:
            plt.suptitle('$V^2\mathrm{\ vs.\ time}$')
        fig1.subplots_adjust(hspace=0, wspace=0)
        for i in range(4):
            plt.setp(axs1[i].get_xticklabels(), visible=False)
            x_axis = axs1[i].axes.get_xaxis()
            x_axis.get_label().set_visible(False)
        for i in range(1, 6, 2):
            plt.setp(axs1[i].get_yticklabels(), visible=False)
            y_axis = axs1[i].axes.get_yaxis()
            y_axis.get_label().set_visible(False)
        # plt.tight_layout()
        if saveplots == True:
            if showvis == True:
                label = '_VIS_TF'
            else:
                label = '_VIS2_TF2'
            fig1.savefig(output_path + label + '.png', dpi=150)
            fig1.savefig(output_path + label + '.eps', format='eps', dpi=300)
            plt.close(fig1)

        CP_sta_indices = np.unique(CP_sta_index_cal, axis=0)
        # print CP_sta_indices
        n_max_config = np.nanmax([4, CP_sta_indices.shape[0]])

        fig2, axs = plt.subplots(2, 2, figsize=(14, 12), sharex=True, sharey=True)
        axs = axs.ravel()
        text_y = 60
        for i in range(n_max_config):
            axs[i + 0].plot(MJD_range, [0.0, 0.0], '-', color='gray', lw=1.5)
            if len(CP_sta_index_cal) > 0:
                idxst = np.all(CP_sta_index_cal == CP_sta_indices[i], axis=1)
                if len(CP_arr_cal[idxst]) > 0:
                    for j in range(len(BCD_configs)):
                        BCDidx = np.all(CP_BCD_arr_cal == BCD_configs[j], axis=1)
                        cidxst = np.logical_and(idxst, BCDidx)
                        if len(CP_arr_cal[cidxst]) > 0:
                            axs[i + 0].errorbar(CP_MJD_arr_cal[cidxst], CP_arr_cal[cidxst], yerr=CPerr_arr_cal[cidxst],
                                                fmt=BCD_markers[j], color=V2_cal_colors[j], elinewidth=1.5,
                                                label='CP cal ' + BCD_labels[j])
                    if i in range(2):
                        text_tag_flag = 1
                        prev_text_MJD = 0.0
                        prev_target_name = ""
                        for j in range(np.sum(idxst)):
                            if CP_MJD_arr_cal[idxst][j] > (prev_text_MJD + text_width_MJD):
                                text_tag_flag = 1
                            if text_tag_flag == 1 or (prev_target_name != target_names_CP_cal[idxst][j]):
                                ymin, ymax = axs[i + 0].get_ylim()
                                axs[i + 0].text(CP_MJD_arr_cal[idxst][j], ymax * 1.05,
                                                target_names_CP_cal[idxst][j].replace('_', ' '), rotation=90,
                                                va='bottom')
                                text_tag_flag = 0
                                prev_text_MJD = CP_MJD_arr_cal[idxst][j]
                                prev_target_name = target_names_CP_cal[idxst][j]
            if len(CP_sta_index) > 0:
                idxst = np.all(CP_sta_index == CP_sta_indices[i], axis=1)
                if len(CP_arr[idxst]) > 0:
                    for j in range(len(BCD_configs)):
                        BCDidx = np.all(CP_BCD_arr == BCD_configs[j], axis=1)
                        cidxst = np.logical_and(idxst, BCDidx)
                        if len(CP_arr[cidxst]) > 0:
                            axs[i + 0].errorbar(CP_MJD_arr[cidxst], CP_arr[cidxst], yerr=CPerr_arr[cidxst],
                                                fmt=BCD_markers[j], color=V2_colors[j], elinewidth=1.5,
                                                label='CP sci ' + BCD_labels[j])
                    if i in range(2):
                        text_tag_flag = 1
                        prev_text_MJD = 0.0
                        prev_target_name = ""
                        for j in range(np.sum(idxst)):
                            if CP_MJD_arr[idxst][j] > (prev_text_MJD + text_width_MJD):
                                text_tag_flag = 1
                            if text_tag_flag == 1 or (prev_target_name != target_names_CP[idxst][j]):
                                ymin, ymax = axs[i + 0].get_ylim()
                                axs[i + 0].text(CP_MJD_arr[idxst][j], ymax * 1.05,
                                                target_names_CP[idxst][j].replace('_', ' '),
                                                rotation=90,
                                                va='bottom')
                                text_tag_flag = 0
                                prev_text_MJD = CP_MJD_arr[idxst][j]
                                prev_target_name = target_names_CP[idxst][j]
            axlabel = sta_names[CP_sta_indices[i, 0] == dic['STA_INDEX']][0] + ' - ' + \
                      sta_names[CP_sta_indices[i, 1] == dic['STA_INDEX']][0] + ' - ' + \
                      sta_names[CP_sta_indices[i, 2] == dic['STA_INDEX']][0]
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            axs[i + 0].text(0.05, 0.95, axlabel, horizontalalignment='left', verticalalignment='top',
                            transform=axs[i + 0].transAxes, bbox=props)
            if i == 0:
                leg = axs[i + 0].legend(loc='upper right')
                leg.get_frame().set_alpha(0.5)
            axs[i + 0].set_ylabel('$CP\,\left(^\circ\\right)$')
            axs[i + 0].set_xlabel('$\mathrm{MJD}$')
        plt.suptitle('$CP\mathrm{\ vs.\ time}$')
        fig2.subplots_adjust(hspace=0, wspace=0)
        for i in range(2):
            plt.setp(axs[i + 0].get_xticklabels(), visible=False)
            x_axis = axs[i + 0].axes.get_xaxis()
            x_axis.get_label().set_visible(False)
        for i in range(1, 4, 2):
            plt.setp(axs[i + 0].get_yticklabels(), visible=False)
            y_axis = axs[i + 0].axes.get_yaxis()
            y_axis.get_label().set_visible(False)
        # plt.tight_layout()
        if saveplots == True:
            fig2.savefig(output_path + '_CP' + '.png', dpi=150)
            fig2.savefig(output_path + '_CP' + '.eps', format='eps', dpi=300)
            plt.close(fig2)
        else:
            plt.show()


###############################################################################
def open_oi_dir(input_dir):
    oifits_file_list = glob.glob(input_dir + '/*fits*')

    N_files = len(oifits_file_list)
    list_of_dicts = []
    for file in oifits_file_list:
        dic = open_oi(file)
        if dic:
            print (dic['TARGET'], dic['DATEOBS'], dic['BAND'], dic['DISP'], dic['DIT'], dic['CATEGORY'])
            list_of_dicts.append(dic)

    return list_of_dicts


###############################################################################
# dates = example format: ["2018-03-16"]
# bands = 'L','M','LM', 'N'
# spectral_resolutions: 'LOW','MED','HIGH'
# DIT_range: [min,max] (s)
# targets = []
def filter_oi_list(list_of_dicts, dates=[], bands=[], spectral_resolutions=[], DIT_range=[], targets=[]):
    filtered_list_of_dicts = []
    if bands:
        # print  'old:',bands
        bands_new = []
        for i in range(len(bands)):
            if bands[i] == 'M':
                bands_new.append('LM')
            elif bands[i] == 'L':
                bands_new.append('LM')
            else:
                bands_new.append(bands[i])
                # print 'new: ', bands_new
    for dic in list_of_dicts:
        if dic:
            date = dic['DATEOBS'][0:10]
            if dates:
                if date not in dates:
                    continue
            if bands:
                if dic['BAND'] not in bands_new:
                    continue
            if spectral_resolutions:
                if dic['DISP'] not in spectral_resolutions:
                    continue
            if DIT_range:
                if not (dic['DIT'] >= DIT_range[0] and dic['DIT'] <= DIT_range[1]):
                    continue
            target = dic['TARGET']
            if targets:
                targets = [x.lower().replace("_", " ") for x in targets]
                target = target.lower().replace("_", " ")
                if target not in targets:
                    continue
            print ("Selected: ", target, date, dic['BAND'], dic['DISP'], dic['DIT'], dic['CATEGORY'])
            filtered_list_of_dicts.append(dic)

    return filtered_list_of_dicts

###############################################################################
# Example code for TF and VIS plots.
# name_dir = r"D:\jvarga\Dokumentumok\MATISSE\data\OIFITS/"
# # outputdir = r"D:/jvarga/Dokumentumok/MATISSE/data/OIFITS/"
# list_of_dicts = open_oi_dir(name_dir+"2018-03-15")
# filtered_list_of_dicts = filter_oi_list(list_of_dicts,dates=["2018-03-15"],bands=['L'],spectral_resolutions=['LOW'],DIT_range=[0.045,0.055],targets=[])
# show_vis2_tf2_vs_time(filtered_list_of_dicts, wlenRange=[3.6,4.0], showvis=False, saveplots=False)

# dates=["2018-03-14","2018-03-15","2018-03-16","2018-03-11","2018-03-13"]
# bands=['L','M', 'N']
# sp_res = ['MED','LOW','HIGH']
# wlenRange = [[3.6,4.0],[4.6,4.8],[10.0,11.0]]
# DITs = np.array([0.2,0.02,0.05,0.1])
# dt = 0.001
# DITranges = np.transpose(np.array([DITs-dt,DITs+dt])).tolist()
# i=0
# j=0
# k=0
# l=0
# for i in range(len(dates)):
#     list_of_dicts = open_oi_dir(name_dir + dates[i])
#     for j in range(len(bands)):
#         for k in range(len(sp_res)):
#             for l in range(len(DITranges)):
#                 filtered_list_of_dicts = filter_oi_list(list_of_dicts,dates=[dates[i]],bands=[bands[j]],spectral_resolutions=[sp_res[k]],DIT_range=DITranges[l],targets=[])
#                 #show_oi_vs_time(filtered_list_of_dicts, [3.5, 3.95], key="VIS2", datatype='VIS2') #[3.5, 3.95] [10.2,10.9]
#                 print "Selected",len(filtered_list_of_dicts),"objects"
#                 fname = dates[i] + "_" + bands[j] + "_" + sp_res[k] + "_DIT" + ("%.2f"%(DITs[l])).replace('.','_')
#                 #show_oi_vs_wlen(filtered_list_of_dicts[3],datatype="VIS2")
#                 show_vis2_tf2_vs_time(filtered_list_of_dicts,wlenRange=wlenRange[j],showvis=False,saveplots=True,output_path=outputdir+fname) # wlenRange=[3.5, 3.95]);
#
# raise SystemExit

class oi_data_select_frame(wx.Frame):
    wl_min_def_L = 3.0
    wl_max_def_L = 4.2
    wl_min_def_M = 4.5
    wl_max_def_M = 5.0
    wl_min_def_LM = 3.0
    wl_max_def_LM = 5.0
    wl_min_def_N = 7.5
    wl_max_def_N = 13.0
    DIT = 0.2
    DIT_range = 0.4
    wl_min = wl_min_def_LM
    wl_max = wl_max_def_LM
    date = "2018-03-16"
    bands = np.array(['L','M','LM','N'])
    spectral_resolutions = np.array(['LOW','MED','HIGH'])
    name_file = ""
    name_dir = ""

    def __init__(self, *args, **kwds):
        self.dic = {}
        self.list_of_dicts = [{}]
        self.filtered_list_of_dicts = [{}]

        # begin wxGlade: oi_data_select_frame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((407, 414))

        self.statusbar = self.CreateStatusBar(1)
        self.statusbar.SetStatusText('')

        # Menu Bar
        self.frame_menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        self.frame_menubar.Append(wxglade_tmp_menu, "File")
        self.SetMenuBar(self.frame_menubar)
        # Menu Bar end
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.btn_open_oifits = wx.Button(self.panel, 10, "Open OIFITS data")
        self.tb_date = wx.TextCtrl(self.panel, wx.ID_ANY, self.date)
        self.tb_DIT = wx.TextCtrl(self.panel, wx.ID_ANY, "%.2f"%(self.DIT))
        self.tb_DIT_range = wx.TextCtrl(self.panel, wx.ID_ANY, "%.3f"%(self.DIT_range))
        self.cb_disp_LOW = wx.CheckBox(self.panel, wx.ID_ANY, "LOW")
        self.cb_disp_MED = wx.CheckBox(self.panel, wx.ID_ANY, "MED")
        self.cb_disp_MED.SetValue(True)
        self.cb_disp_HIGH = wx.CheckBox(self.panel, wx.ID_ANY, "HIGH")
        self.cb_b_L = wx.CheckBox(self.panel, wx.ID_ANY, "L")
        self.cb_b_LM = wx.CheckBox(self.panel, wx.ID_ANY, "LM")
        self.cb_b_LM.SetValue(True)
        self.cb_b_M = wx.CheckBox(self.panel, wx.ID_ANY, "M")
        self.cb_b_N = wx.CheckBox(self.panel, wx.ID_ANY, "N")
        self.tb_wl_min = wx.TextCtrl(self.panel, wx.ID_ANY, "3.6")
        self.tb_wl_max = wx.TextCtrl(self.panel, wx.ID_ANY, "4.0")
        self.btn_def_wl = wx.Button(self.panel, 9, "Default wl")
        self.btn_VISAMP = wx.Button(self.panel, 0, "VISAMP")
        self.VIS2 = wx.Button(self.panel, 1, "VIS2")
        self.btn_VISPHI = wx.Button(self.panel, 2, "VISPHI")
        self.btn_TF2 = wx.Button(self.panel, 3, "TF2")
        self.btn_T3AMP = wx.Button(self.panel, 4, "T3AMP")
        self.btn_FLUX = wx.Button(self.panel, 5, "FLUX")
        self.btn_T3PHI = wx.Button(self.panel, 6, "T3PHI")
        self.cb_pl_OI_t = wx.CheckBox(self.panel, wx.ID_ANY, "Plot OI vs. time")
        self.cb_pl_OI_wl = wx.CheckBox(self.panel, wx.ID_ANY, "Plot OI vs. wavelength")
        self.cb_pl_OI_wl.SetValue(True)
        self.btn_oi_vs_freq = wx.Button(self.panel, 7, "OI vs. spatial frequency")
        self.btn_vis2_tf2_cp_vs_time = wx.Button(self.panel, 8, "VIS2, TF2, T3PHI vs. time")

        self.Bind(wx.EVT_BUTTON, self.OnButtonClicked)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: oi_data_select_frame.__set_properties
        self.SetTitle("OIFITS plotter")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: oi_data_select_frame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(0, 2, 3, 3)
        sizer_8 = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Plot options"), wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_6 = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Plot special"), wx.VERTICAL)
        sizer_9 = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Plot"), wx.HORIZONTAL)
        grid_sizer_2 = wx.FlexGridSizer(0, 2, 3, 3)
        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Band"), wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_5 = wx.FlexGridSizer(0, 3, 3, 3)
        grid_sizer_4 = wx.FlexGridSizer(0, 2, 3, 3)
        sizer_7 = wx.BoxSizer(wx.VERTICAL)
        sizer_11 = wx.StaticBoxSizer(wx.StaticBox(self.panel, wx.ID_ANY, "Spectral resolution"), wx.HORIZONTAL)
        sizer_12 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_7 = wx.FlexGridSizer(3, 3, 3, 3)
        sizer_7.Add(self.btn_open_oifits, 0, 30, 15)
        label_17 = wx.StaticText(self.panel, wx.ID_ANY, "Date")
        grid_sizer_7.Add(label_17, 0, 0, 0)
        grid_sizer_7.Add(self.tb_date, 0, 0, 0)
        label_18 = wx.StaticText(self.panel, wx.ID_ANY, "")
        grid_sizer_7.Add(label_18, 0, 0, 0)
        label_19 = wx.StaticText(self.panel, wx.ID_ANY, "DIT")
        grid_sizer_7.Add(label_19, 0, 0, 0)
        grid_sizer_7.Add(self.tb_DIT, 0, 0, 0)
        label_20 = wx.StaticText(self.panel, wx.ID_ANY, "s")
        grid_sizer_7.Add(label_20, 0, 0, 0)
        label_21 = wx.StaticText(self.panel, wx.ID_ANY, "DITrange")
        grid_sizer_7.Add(label_21, 0, 0, 0)
        grid_sizer_7.Add(self.tb_DIT_range, 0, 0, 0)
        label_22 = wx.StaticText(self.panel, wx.ID_ANY, "s")
        grid_sizer_7.Add(label_22, 0, 0, 0)
        sizer_7.Add(grid_sizer_7, 1, wx.EXPAND, 0)
        sizer_12.Add(self.cb_disp_LOW, 0, 0, 0)
        sizer_12.Add(self.cb_disp_MED, 0, 0, 0)
        sizer_12.Add(self.cb_disp_HIGH, 0, 0, 0)
        sizer_11.Add(sizer_12, 1, wx.ALL | wx.EXPAND, 6)
        sizer_7.Add(sizer_11, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(sizer_7, 1, wx.EXPAND, 0)
        grid_sizer_4.Add(self.cb_b_L, 0, 0, 0)
        grid_sizer_4.Add(self.cb_b_LM, 0, 0, 0)
        grid_sizer_4.Add(self.cb_b_M, 0, 0, 0)
        grid_sizer_4.Add(self.cb_b_N, 0, 0, 0)
        sizer_4.Add(grid_sizer_4, 1, wx.EXPAND, 0)
        label_7 = wx.StaticText(self.panel, wx.ID_ANY, "Wl min")
        grid_sizer_5.Add(label_7, 0, 0, 0)
        grid_sizer_5.Add(self.tb_wl_min, 0, 0, 0)
        label_9 = wx.StaticText(self.panel, wx.ID_ANY, "um")
        grid_sizer_5.Add(label_9, 0, 0, 0)
        label_8 = wx.StaticText(self.panel, wx.ID_ANY, "Wl max")
        grid_sizer_5.Add(label_8, 0, 0, 0)
        grid_sizer_5.Add(self.tb_wl_max, 0, 0, 0)
        label_10 = wx.StaticText(self.panel, wx.ID_ANY, "um")
        grid_sizer_5.Add(label_10, 0, 0, 0)
        sizer_5.Add(grid_sizer_5, 1, wx.EXPAND, 0)
        sizer_5.Add(self.btn_def_wl, 0, 0, 0)
        sizer_4.Add(sizer_5, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(sizer_4, 1, wx.EXPAND, 0)
        grid_sizer_2.Add(self.btn_VISAMP, 0, 0, 0)
        grid_sizer_2.Add(self.VIS2, 0, 0, 0)
        grid_sizer_2.Add(self.btn_VISPHI, 0, 0, 0)
        grid_sizer_2.Add(self.btn_TF2, 0, 0, 0)
        grid_sizer_2.Add(self.btn_T3AMP, 0, 0, 0)
        grid_sizer_2.Add(self.btn_FLUX, 0, 0, 0)
        grid_sizer_2.Add(self.btn_T3PHI, 0, 0, 0)
        sizer_9.Add(grid_sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(sizer_9, 1, wx.EXPAND, 0)
        sizer_2.Add(self.cb_pl_OI_t, 0, 0, 0)
        sizer_2.Add(self.cb_pl_OI_wl, 0, 0, 0)
        sizer_6.Add(self.btn_oi_vs_freq, 0, 0, 0)
        sizer_6.Add(self.btn_vis2_tf2_cp_vs_time, 0, 0, 0)
        sizer_2.Add(sizer_6, 1, wx.EXPAND, 0)
        sizer_8.Add(sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(sizer_8, 1, wx.EXPAND, 0)
        self.panel.SetSizer(grid_sizer_1)
        sizer_1.Add(self.panel, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

    def OnButtonClicked(self, e):
        plot_t_flag = self.cb_pl_OI_t.GetValue()
        plot_wl_flag = self.cb_pl_OI_wl.GetValue()
        self.DIT = float(self.tb_DIT.GetValue())
        self.DIT_range = float(self.tb_DIT_range.GetValue())
        band_mask = [self.cb_b_L.GetValue(),self.cb_b_M.GetValue(),self.cb_b_LM.GetValue(),self.cb_b_N.GetValue()]
        selected_bands = self.bands[band_mask].tolist()
        spectral_resolution_mask = [self.cb_disp_LOW.GetValue(),self.cb_disp_MED.GetValue(),self.cb_disp_HIGH.GetValue()]
        selected_spectral_resolutions = self.spectral_resolutions[spectral_resolution_mask].tolist()
        self.wl_min = float(self.tb_wl_min.GetValue())
        self.wl_max = float(self.tb_wl_max.GetValue())
        eID = e.GetId()
        if eID < 9:
            if len(self.list_of_dicts) > 1:
                self.filtered_list_of_dicts = filter_oi_list(self.list_of_dicts, dates=[self.date], bands=selected_bands,
                                                         spectral_resolutions=selected_spectral_resolutions,
                                                         DIT_range=[self.DIT - self.DIT_range,
                                                                    self.DIT + self.DIT_range], targets=[])
            else:
                self.filtered_list_of_dicts = self.list_of_dicts
            if eID == 0:
                self.statusbar.SetStatusText('Show VISAMP.')
                print ('Show VISAMP.')
                if plot_t_flag == True:
                    show_oi_vs_time(self.filtered_list_of_dicts, [self.wl_min,self.wl_max], key="VIS", datatype="CFLUX")
                elif plot_wl_flag == True:
                    show_oi_vs_wlen(self.filtered_list_of_dicts[0],key='VIS', datatype='CFLUX')
            elif eID == 1:
                self.statusbar.SetStatusText('Show VIS2.')
                print ('Show VIS2.')
                if plot_t_flag == True:
                    show_oi_vs_time(self.filtered_list_of_dicts, [self.wl_min,self.wl_max], key="VIS2", datatype="VIS2")
                elif plot_wl_flag == True:
                    show_oi_vs_wlen(self.filtered_list_of_dicts[0],key='VIS2', datatype='VIS2')
            elif eID == 2:
                self.statusbar.SetStatusText('Show VISPHI.')
                print ('Show VISPHI.')
                if plot_t_flag == True:
                    show_oi_vs_time(self.filtered_list_of_dicts, [self.wl_min,self.wl_max], key="VIS", datatype="DPHI")
                elif plot_wl_flag == True:
                    show_oi_vs_wlen(self.filtered_list_of_dicts[0],key='VIS', datatype='DPHI')
            elif eID == 3:
                self.statusbar.SetStatusText('Show TF2.')
                if plot_t_flag == True:
                    show_oi_vs_time(self.filtered_list_of_dicts, [self.wl_min,self.wl_max], key="TF2", datatype="TF2")
                elif plot_wl_flag == True:
                    show_oi_vs_wlen(self.filtered_list_of_dicts[0],key='TF2', datatype='TF2')
                print ('Show TF2.')
            elif eID == 4:
                self.statusbar.SetStatusText('Show T3AMP.')
                print ('Show T3AMP.')
                if plot_t_flag == True:
                    show_oi_vs_time(self.filtered_list_of_dicts, [self.wl_min,self.wl_max], key="T3", datatype="T3AMP")
                elif plot_wl_flag == True:
                    show_oi_vs_wlen(self.filtered_list_of_dicts[0],key='T3', datatype='T3AMP')
            elif eID == 5:
                self.statusbar.SetStatusText('Show FLUX.')
                print ('Show FLUX.')
                if plot_t_flag == True:
                    show_oi_vs_time(self.filtered_list_of_dicts, [self.wl_min,self.wl_max], key="FLUX", datatype="FLUX")
                elif plot_wl_flag == True:
                    show_oi_vs_wlen(self.filtered_list_of_dicts[0],key='FLUX',datatype='FLUX')
            elif eID == 6:
                self.statusbar.SetStatusText('Show T3PHI.')
                if plot_t_flag == True:
                    show_oi_vs_time(self.filtered_list_of_dicts, [self.wl_min,self.wl_max], key="T3", datatype="CLOS")
                elif plot_wl_flag == True:
                    show_oi_vs_wlen(self.filtered_list_of_dicts[0],key='T3',datatype='CLOS')
                print ('Show T3PHI.')
            elif eID == 7:
                self.statusbar.SetStatusText('Show OI vs. spatial frequency.')
                print ('Show OI vs. spatial frequency.')
                show_oi_vs_freq(self.filtered_list_of_dicts[0],log=False)
            elif eID == 8:
                self.statusbar.SetStatusText('Show VIS2, TF2, T3PHI vs time.')
                print ('Show VIS2, TF2, T3PHI vs time.')
                show_vis2_tf2_vs_time(self.filtered_list_of_dicts, [self.wl_min,self.wl_max], showvis=False, saveplots=False, output_path="")
        else:
            if eID == 9:
                self.statusbar.SetStatusText('Default wavelength range.')
                print ('Default wavelength range.')
                self.tb_wl_min.Clear()
                self.tb_wl_max.Clear()
                if self.cb_b_M.GetValue() == True:
                    self.wl_min = self.wl_min_def_M
                    self.wl_max = self.wl_max_def_M
                    self.tb_wl_min.write("%.2f" % (self.wl_min))
                    self.tb_wl_max.write("%.2f" % (self.wl_max))
                if self.cb_b_L.GetValue() == True:
                    self.wl_min = self.wl_min_def_L
                    self.wl_max = self.wl_max_def_L
                    self.tb_wl_min.write("%.2f" % (self.wl_min))
                    self.tb_wl_max.write("%.2f" % (self.wl_max))
                if self.cb_b_N.GetValue() == True:
                    self.wl_min = self.wl_min_def_N
                    self.wl_max = self.wl_max_def_N
                    self.tb_wl_min.write("%.2f" % (self.wl_min))
                    self.tb_wl_max.write("%.2f" % (self.wl_max))
                if self.cb_b_LM.GetValue() == True:
                    self.wl_min = self.wl_min_def_LM
                    self.wl_max = self.wl_max_def_LM
                    self.tb_wl_min.write("%.2f" % (self.wl_min))
                    self.tb_wl_max.write("%.2f" % (self.wl_max))
                # e.Skip()
            elif eID == 10:
                self.statusbar.SetStatusText('Open OIFITS data.')
                print ('Open OIFITS data.')
                print("Running file selector...")
                openFileDialog = mat_FileDialog(None, 'Open a file', "lmk,")
                if openFileDialog.ShowModal() == wx.ID_OK:
                    self.name_file = openFileDialog.GetPaths()[0]
                    print(self.name_file)
                else:
                    self.name_file = ""
                openFileDialog.Destroy()

                if os.path.isfile(self.name_file):
                    self.dic = {}
                    print("Reading file " + self.name_file + "...")
                    self.dic = open_oi(self.name_file)
                    self.list_of_dicts = [self.dic]
                    #update the values in the form
                    if self.dic['BAND'] == 'LM':
                        self.cb_b_L.SetValue(False)
                        self.cb_b_M.SetValue(False)
                        self.cb_b_N.SetValue(False)
                        self.cb_b_LM.SetValue(True)
                        self.wl_min = self.wl_min_def_LM
                        self.wl_max = self.wl_max_def_LM
                    elif self.dic['BAND'] == 'N':
                        self.cb_b_L.SetValue(False)
                        self.cb_b_M.SetValue(False)
                        self.cb_b_N.SetValue(True)
                        self.cb_b_LM.SetValue(False)
                        self.wl_min = self.wl_min_def_N
                        self.wl_max = self.wl_max_def_N

                    if self.dic['DISP'] == 'LOW':
                        self.cb_disp_LOW.SetValue(True)
                        self.cb_disp_MED.SetValue(False)
                        self.cb_disp_HIGH.SetValue(False)
                    elif self.dic['DISP'] == 'MED':
                        self.cb_disp_LOW.SetValue(False)
                        self.cb_disp_MED.SetValue(True)
                        self.cb_disp_HIGH.SetValue(False)
                    elif self.dic['DISP'] == 'HIGH':
                        self.cb_disp_LOW.SetValue(False)
                        self.cb_disp_MED.SetValue(False)
                        self.cb_disp_HIGH.SetValue(True)

                    self.tb_DIT.SetValue("%.3f"%(self.dic['DIT']))
                    self.tb_wl_min.Clear()
                    self.tb_wl_max.Clear()
                    self.tb_wl_min.write("%.2f" % (self.wl_min))
                    self.tb_wl_max.write("%.2f" % (self.wl_max))
                elif os.path.isdir(self.name_file):
                    name_dir = self.name_file
                    self.dic = {}
                    self.list_of_dicts = [{}]
                    self.list_of_dicts = open_oi_dir(name_dir)
                self.date = self.list_of_dicts[0]['DATEOBS'][0:10]
                self.tb_date.SetValue(self.date)

class OI_plotter(wx.App):
    def OnInit(self):
        self.frame = oi_data_select_frame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == '__main__':
    listArg = sys.argv
    name_file = []
    typePlot = "VIS2"
    for elt in listArg:
        if ('--help' in elt):
            print("Usage: mat_show_....py [--dir=start directory]")
            sys.exit(0)
        elif ('--typePlot' in elt):
            typePlot = elt.split("=")[1]
            # elif len(listArg) == 2:
            #     name_file = sys.argv[1]
            #     print(name_file)

    if typePlot == "VIS2":
        table = "VIS2"
    elif typePlot == "CLOS":
        table = "T3"
    elif typePlot == "TF2":
        typePlot = "TF2"
        table = "TF2"
    elif typePlot == "FLUX":
        table = "FLUX"
    elif typePlot == "DPHI":
        table = "VIS"

    app = OI_plotter(0)
    app.MainLoop()

    # app = wx.App()
    # if not name_file:
    #     print("No input name given, running file selector...")
    #     openFileDialog = mat_FileDialog(None, 'Open a file', "lmk,")
    #     if openFileDialog.ShowModal() == wx.ID_OK:
    #         name_file = openFileDialog.GetPaths()[0]
    #         print(name_file)
    #     openFileDialog.Destroy()
    # app.MainLoop()
    # app.Destroy()
    #
    # dic = {};
    # if os.path.isfile(name_file):
    #     print("Reading file " + name_file + "...")
    #     dic = open_oi(name_file)
    #     print("Plotting data " + name_file + "...")
    #     show_oi_vs_freq(dic)
    #     print("Plotting data " + name_file + "...")
    #     plt.figure()
    #     show_oi_vs_wlen(dic['FLUX'], dic['WLEN'], datatype='FLUX')
    #     print("Plotting data " + name_file + "...")
    #     plt.figure()
    #     wlen = dic['WLEN']
    #     print(wlen)
    # elif os.path.isdir(name_file):
    #     name_dir = name_file
    #     list_of_dicts = open_oi_dir(name_dir)
    #     filtered_list_of_dicts = filter_oi_list(list_of_dicts)
    #     show_vis2_tf2_vs_time(filtered_list_of_dicts, [3.5, 3.95])
    #     # show_oi_vs_time(filtered_list_of_dicts ,[3.5,3.95],key=table, datatype=typePlot)

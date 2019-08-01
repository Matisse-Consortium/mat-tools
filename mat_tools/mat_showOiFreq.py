#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of the Matisse pipeline GUI series
Copyright (C) 2017- Observatoire de la Côte d'Azur

Created on Tue Jul 22 2019
@author: fmillour

This software is governed by the CeCILL license under French law and
abiding by the rules of distribution of free software.

You can use, modify and/ or redistribute the software under the terms
of the CeCILL license as circulated by CEA, CNRS and INRIA at the
following URL "http://www.cecill.info". You have a copy of the licence
in the LICENCE.md file.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.
"""

import matplotlib.pyplot as plt
import argparse
import numpy as np
from astropy.io import fits
import sys
import mat_show_oifits as msoi
import os
from matplotlib.backends.backend_pdf import PdfPages


inch=1/2.54

if __name__ == '__main__':
    print("Starting...")

    #--------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description='Plots the oi data as a function of spatial frequency.')
    parser.add_argument('fileOrDir', metavar='fileOrDir', type=str,
                        help='A directory, a oifits file or a list of oifits files', default=None)
    parser.add_argument('--log',action="store_true",
                        help='Set logscale')
    parser.add_argument('--showvis', action="store_true",
                        help='Plot visibilities instead of V squared.')
    parser.add_argument('--pdf',   action="store_true",
                        help='Create a pdf file for each target.')
    parser.add_argument('--mergedpdf',   action="store_true",
                        help='Create a single pdf file for all targets.')

    try:
        args = parser.parse_args()
    except:
        print("\n\033[93mRunning mat_showOiFreq.py --help to be kind with you:\033[0m\n")
        parser.print_help()
        sys.exit(0)

    if "[" in args.fileOrDir:
        listOffile=eval(args.fileOrDir)
        list_of_dicts = [msoi.open_oi(fi) for fi in listOffile]
        dir0=os.path.realpath(os.path.dirname(args.fileOrDir[0]))
    else:
        if os.path.isdir(args.fileOrDir):
            list_of_dicts = msoi.open_oi_dir(args.fileOrDir)
            dir0=os.path.realpath(args.fileOrDir)
        else:
            list_of_dicts = [msoi.open_oi(args.fileOrDir)]
            dir0=os.path.realpath(os.path.dirname(args.fileOrDir))


    targets=[dic['TARGET'] for dic in list_of_dicts]
    targets=np.unique(np.array(targets))
    print(targets)


    if args.mergedpdf:
        pdfname=dir0+"/"+ os.path.basename(dir0) +'_plots_freq.pdf'
        pdf = PdfPages(pdfname)
        print("saving to {0}".format(pdfname))

    for band in ["LM","N"]:
        for target in targets:
            print("***************************{0}_{1}***************************".format(target,band))
            filtered_list_of_dicts = msoi.filter_oi_list(list_of_dicts,targets=[target],bands=[band])
            print("number of files = {0}".format(len(filtered_list_of_dicts)))

            fig = plt.figure(figsize=(29.7*inch,21*inch))
            fig.suptitle( target + "_"+ band)
            plts={}
            plts['VIS2'] = fig.add_axes([0.075, 0.50, 0.85,0.35])
            plts['CP']   = fig.add_axes([0.075, 0.08, 0.85,0.35],sharex=plts['VIS2'])

            for idic in filtered_list_of_dicts:
                msoi.show_oi_vs_freq(idic, log=args.log,showvis=args.showvis, subplotV2=plts['VIS2'], subplotCP=plts['CP'])


            if args.pdf and not(args.mergedpdf):
                pdfname = dir0 + "/" + target + "_"+ band + "_plot_freq.pdf"
                plt.savefig(pdfname)
                plt.close(fig)
                print("saving to {0}".format(pdfname))
            if args.mergedpdf:
                pdf.savefig(fig)
                plt.close(fig)


   	if not(args.pdf or args.mergedpdf):
            plt.show()

    if args.mergedpdf:
        pdf.close()

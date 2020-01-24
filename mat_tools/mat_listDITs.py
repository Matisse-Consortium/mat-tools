#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of the Matisse pipeline GUI series
Copyright (C) 2017- Observatoire de la Côte d'Azur

@author: fmillour

Lists the detector integration times in a directory

This software is a computer program whose purpose is to show oifits
files from the MATISSE instrument.

This software is governed by the CeCILL license under French law and
abiding by the rules of distribution of free software. 

You can use, modify and/ or redistribute the software under the
terms of the CeCILL license as circulated by CEA, CNRS and INRIA at
the following URL "http://www.cecill.info". You have a copy of the
licence in the LICENCE.md file.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.
"""

import sys
import os
import numpy as np
from astropy.io import fits
import fnmatch
from libAutoPipeline import matisseType

RES_LM = []
RES_N = []
obsTypes = ["TARGET_RAW", "CALIB_RAW", "SKY_RAW"]

for root, dir, files in os.walk("."):
        print(root)
        print("")
        for file in fnmatch.filter(files, "*.fits*"):
            print((file), end=' ')
        
            header  = fits.open(os.path.join(root,file))[0].header
            type = matisseType(header)
            
            for typ in obsTypes:
                if type == typ:
                    print((typ), end=' ')
                    try:
                        dit  = header['HIERARCH ESO DET SEQ1 DIT']
                        chip = header["HIERARCH ESO DET CHIP NAME"]
                        mod  = header["HIERARCH ESO DET READ CURNAME"]
                    except:
                        pass
                    if chip == "HAWAII-2RG":
                        try:
                            res     = header["HIERARCH ESO INS DIL NAME"]
                            strin = chip+" "+res+" "+mod+" "+str(dit)
                            RES_LM   = np.append(RES_LM, strin)
                            print(strin)
                        except:
                            pass
                    elif chip == "AQUARIUS":
                        try:
                            res     = header["HIERARCH ESO INS DIN NAME"]
                            strin = chip+" "+res+" "+mod+" "+str(dit)
                            RES_N   = np.append(RES_N, strin)
                            print(strin)
                        except:
                            pass
                        
                        
            print(' ')

res, idx = np.unique(RES_LM, return_index=True)
print(("DITs LM",res))
res, idx = np.unique(RES_N, return_index=True)
print(("DITs N", res))

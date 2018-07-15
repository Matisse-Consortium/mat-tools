#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  $Id$

  This file is part of the Matisse pipeline GUI series
  Copyright (C) 2017- Observatoire de la Côte d'Azur
  
  Created in 2016
  @author: pbe

  Automatic MATISSE pipeline !

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
"""

import numpy as np
from astropy.io import fits
from astropy.io.fits import getheader
import matplotlib.pyplot as plt
import sys
import os
import glob
import shutil
import subprocess
import filecmp
from libAutoPipeline import matisseType,matisseAction,matisseRecipes,matisseCalib
from multiprocessing.pool import Pool
from functools import partial
#import pdb

# Run esorex recipes
def runEsorex(cmd):
    item = cmd.split()
    out  = item[-1]+".log"
    err  = item[-1]+".err"
    print("    Recipes",item[2],"running...")
    val  = item[1].split("=")
    os.system("cd "+val[1]+";"+cmd+" > "+out+" 2> "+err)
    print("Done.")

# Initialize variables
repRaw      = ""
repArchive  = ""
repResult   = ""
tplidsel    = ""
tplstartsel = ""
nbCore      = 0
listArg     = sys.argv

for elt in listArg:
    if ('--help' in elt):
        print("Usage: python automaticPipeline.py --dirRaw=RawDataPath [--dirCalib=CalibrationMapPath] [--dirResult=ResultsPath] [--nbCore=NumberOfCores] [--tplID=template ID] [--tplSTART=template start] [--overwrite] [--skipL] [--skipN]")
        sys.exit(0)

# Parse arguments of the command line
raw_est_opts = "";
for elt in listArg:
    if ('--dirRaw' in elt):
        item=elt.split('=')
        repRaw=item[1]
    elif ('--dirCalib' in elt):
        item=elt.split('=')
        repArchive=item[1]
    elif ('--dirResult' in elt):
        item=elt.split('=')
        repResult=item[1]
    elif ('--nbCore' in elt):
        item   = elt.split('=')
        nbCore = int(item[1])
    elif ('--tplID' in elt):
        item     = elt.split('=')
        tplidsel = item[1]
    elif ('--tplSTART' in elt):
        item        = elt.split('=')
        tplstartsel = item[1]
        
    elif ('--replaceTel' in elt):
        raw_est_opts += elt + " "
    elif ('--corrFlux' in elt):
        raw_est_opts += elt + " "
    elif ('--useOpdMod' in elt):
        raw_est_opts += elt + " "
    ##########################################################################
    if ('--overwrite' in elt):
        overwrite=1
    else:
        overwrite=0
    if ('--skipOddBCD' in elt):
        skipOddBCD=1
    else:
        skipOddBCD=0
    if ('--skipL' in elt):
        skipL=1
    else:
        skipL=0
    if ('--skipN' in elt):
        skipN=1
    else:
        skipN=0

# Print meaningful error messages if something is wrong in the command line
print(" ")
print("------------------------------------------------------------------------")
if (repRaw == ""):
    print("ERROR : You have to specifiy a Raw Data Directory with --dirRaw=DirectoryPath")
    sys.exit(0)
else:
    print('%-40s' % ("Raw Data Directory:",),repRaw)
if (repArchive==""):
    repArchive="/data/CalibMap"
    print("Info: Calibration Directory not specified. We used the default directory")
print('%-40s' % ("Calibration Directory:",),repArchive)
if (repResult==""):
        repResult=os.getcwd()
        print("Info : Results Directory not specified. We use current directory")
print('%-40s' % ("Results Directory:",),repResult)
if (nbCore==0):
    nbCore=8
    print("Info : Number of Cores not specified. We use "+str(nbCore)+" cores")
print('%-40s' % ("Number of Cores:",),nbCore)    
print("------------------------------------------------------------------------")
 

listRaw = glob.glob(repRaw+"/MATIS*.fits")

if (repArchive != ""):
    listArchive = glob.glob(repArchive+"/*.fits")
else:
    listArchive =[]

# Sort listRaw using template ID and template start
print("Sorting files according to constraints...")
allhdr        = []
for filename in listRaw:
    allhdr.append(getheader(filename,0))
        
listRawSorted = []
allhdrSorted  = []
for hdr,filename in zip(allhdr,listRaw):
    if ('HIERARCH ESO TPL START' in hdr and 'HIERARCH ESO DET CHIP NAME' in hdr) :
        tplid    = hdr['HIERARCH ESO TPL ID']
        tplstart = hdr['HIERARCH ESO TPL START']
        chip     = hdr['HIERARCH ESO DET CHIP NAME']

        # Skip L band data
        if skipL == 1 and chip == 'HAWAII-2RG':
            continue;
        
        # Skip N band data
        if skipN == 1 and chip == 'AQUARIUS':
            continue;
        
        # Go through all 4 cases. First case: tplid and tplstart given by user
        if (tplidsel != "" and tplstartsel != ""):
            if (tplid == tplidsel and tplstart == tplstartsel):
                listRawSorted.append(filename)
                allhdrSorted.append(hdr)
        # Second case: tpl ID given but not tpl start
        if (tplidsel != "" and tplstartsel == ""):
            if (tplid == tplidsel):
                listRawSorted.append(filename)
                allhdrSorted.append(hdr)
        # Third case: tpl start given but not tpl ID
        if (tplidsel == "" and tplstartsel != ""):
            if (tplstart == tplstartsel):
                listRawSorted.append(filename)
                allhdrSorted.append(hdr)
        # Fourth case: nothing given by user
        if (tplidsel == "" and tplstartsel == ""):
               listRawSorted.append(filename)
               allhdrSorted.append(hdr)
               
# Replace original list with the sorted one
listRaw = listRawSorted
allhdr  = allhdrSorted

    
# Determination of the number of Reduction Blocks
keyTplStart    = []
listIterNumber = []
print("Determining the number of reduction blocks...")

for hdr,filename in zip(allhdr,listRaw):
    try:
        tplstart = hdr['HIERARCH ESO TPL START']
    except:
        print(("WARNING, "+filename+" is not a valid MATISSE fits file!"))
        continue;
    chipname = hdr['HIERARCH ESO DET CHIP NAME']
   # Reduction blocks are defined by template start and detector name
    temp = tplstart+"."+chipname
    keyTplStart.append(temp)
    
keyTplStart=list(set(keyTplStart))                       
for elt in keyTplStart:
    listIterNumber.append(0)
print(("Found "+str(len(keyTplStart))+" reduction blocks."))

iterNumber = 0
while True:
    iterNumber += 1
    print("")
    print("Iteration ",iterNumber)
    print("-----------------------")
    if (iterNumber > 1):
        listIter=[]
        print("listing stuff...")
        for iter in range(iterNumber-1):
            repIterPrev = repResult+'/Iter'+str(iter+1)
            listRepIter = [os.path.join(repIterPrev, f) for f in os.listdir(repIterPrev) if os.path.isdir(os.path.join(repIterPrev, f))]
            print("listing files from previous iteration...")
            for elt in listRepIter:
                listIter = listIter+[os.path.join(elt, f) for f in os.listdir(elt) if os.path.isfile(os.path.join(elt, f)) and f[-5:] == '.fits']

    print("listing reduction blocks...")
    listRedBlocks = []
    # Reduction Blocks List Initialization  
    cpt=0
    for elt in keyTplStart:
        listRedBlocks.append({"action":" ","recipes":" ","param":" ","input":[],"calib":[],"status":0,"tplstart":" ","iter":listIterNumber[cpt]})
        cpt += 1
    # Fill the list of raw data in the Reduction Blocks List
    print("listing files in the reduction blocks...")
    for hdr,filename in zip(allhdr,listRaw):
    #for filename in listRaw:
        try:
            stri = hdr['HIERARCH ESO TPL START']+'.'+hdr['HIERARCH ESO DET CHIP NAME']
        except:
            print(("WARNING, "+filename+" is not a valid MATISSE fits file!"))
            continue;
        tag  = matisseType(hdr)
        listRedBlocks[keyTplStart.index(stri)]["input"].append([filename,tag,hdr])

    # Fill the list of actions,recipes,params in the Reduction Blocks List
    print("listing actions in the reduction blocks...")
    for elt in listRedBlocks:
        hdr = elt["input"][0][2]
        keyTplStartCurrent=hdr['HIERARCH ESO TPL START']+'.'+hdr['HIERARCH ESO DET CHIP NAME']
        action        = matisseAction(hdr,elt["input"][0][1])
        if action=="ACTION_MAT_RAW_ESTIMATES":
            opts = raw_est_opts
        else:
            opts = ""
        recipes,param = matisseRecipes(action,hdr['HIERARCH ESO DET CHIP NAME'],opts)
        elt["action"]   = action
        elt["recipes"]  = recipes
        elt["param"]    = param
        elt["tplstart"] = keyTplStartCurrent

# Fill the list of calib in the Reduction Blocks List from repArchive
    print("listing calibrations in the reduction blocks...")
    for elt in listRedBlocks:
        hdr          = elt["input"][0][2]
        calib,status = matisseCalib(hdr,elt["action"],listArchive,elt['calib'])
        elt["calib"] = calib
        elt["status"] = status
            
# Fill the list of calib in the Reduction Blocks List from repResult Iter i-1
    print("listing calibrations from previous iteration in the reduction blocks...")
    if (iterNumber > 1):
        for elt in listRedBlocks:
            hdr          = elt["input"][0][2]
            calib,status = matisseCalib(hdr,elt["action"],listIter,elt['calib'])
            elt["calib"] = calib
            elt["status"] = status
            
# Create the SOF files
    print("creating the sof files and directories...")
    repIter = repResult+"/Iter"+str(iterNumber)
    if os.path.isdir(repIter) == True:
        if overwrite == 1:
            shutil.rmtree(repIter)
            os.mkdir(repIter)
    else:
        os.mkdir(repIter)

    listCmdEsorex = []
    cptStatusOne  = 0
    cptStatusZero = 0
    cptToProcess  = 0
    cpt           = 0
    for elt in listRedBlocks:
        if (elt["status"] == 1):
            cptStatusOne += 1

            filelist  = os.listdir(repIter)
            rbname    = elt["recipes"]+"."+elt["tplstart"]
            sofname   = os.path.join(repIter,rbname+".sof")
    
            if os.path.exists(sofname):
                print(("sof file "+sofname+" already exists..."))
                if overwrite:
                    print("WARNING: Overwriting existing file")
                    
                    fp = open(sofname,'w')
                    for frame,tag,hdr in elt['input']:
                        fp.write(frame+" "+tag+"\n")
                    for frame,tag in elt['calib']:
                        fp.write(frame+" "+tag+"\n")
                    fp.close()
                else:
                    print("WARNING: sof file exists. Skipping... (consider using --overwrite)")
                    #continue;
            else:
                print(("sof file "+sofname+" does not exist. Creating it..."))
                fp = open(sofname,'w')
                for frame,tag,hdr in elt['input']:
                    fp.write(frame+" "+tag+"\n")
                for frame,tag in elt['calib']:
                    fp.write(frame+" "+tag+"\n")
                fp.close()
            
            outputDir = os.path.join(repIter,rbname+".rb")
            
            if os.path.exists(outputDir):
                print(("outputDir "+outputDir+" already exists..."))
                # Remove any previous logfile
                print("Remove any previous logfile...")
                try:
                    os.remove(os.path.join(outputDir,".logfile"))
                except:
                    print("Nothing to remove...")
                if os.listdir(outputDir) == []:
                    print("outputDir is empty, continuing...")
                else:
                    print("outputDir already exists and is not empty...")
                    if overwrite:
                        print("WARNING: Overwriting existing files")
                    else:
                        print("WARNING: outputDir exists. Skipping... (consider using --overwrite)\n")
                        continue;
            else:
                print(("outputDir "+outputDir+" does not exist. Creating it...\n"))
                os.mkdir(outputDir)
            
            cmd="esorex --output-dir="+outputDir+" "+elt['recipes']+" "+elt['param']+" "+sofname

            if (iterNumber > 1):
                sofnamePrev = repIterPrev+"/"+elt["recipes"]+"."+elt["tplstart"]+".sof"
                if (os.path.exists(sofnamePrev)):
                    if (filecmp.cmp(sofname,sofnamePrev)):
                        #outputDirPrev=repIterPrev+"/"+elt["tplstart"]+".rb"
                        #print "copy "+outputDirPrev+" in "+outputDir
                        #os.system("cp "+outputDirPrev+"/* "+outputDir+"/.")
                        shutil.rmtree(outputDir)
                    else:  
                        listIterNumber[cpt] = iterNumber
                        elt["iter"]         = iterNumber
                        cptToProcess       += 1
                        listCmdEsorex.append(cmd)
                else:
                    listIterNumber[cpt]     = iterNumber
                    elt["iter"]             = iterNumber
                    cptToProcess           += 1
                    listCmdEsorex.append(cmd)
            else:
                listIterNumber[cpt]         = iterNumber
                elt["iter"]                 = iterNumber
                cptToProcess               += 1
                listCmdEsorex.append(cmd)
        else:
            cptStatusZero+=1
        cpt+=1
    print('%-40s' % ("Reduction Blocks to process:",),cptToProcess)
                
    if (listCmdEsorex == []):
        print(" ")
        print("No more iteration to do")
        print("-----------------------")
        print(" ")
        print("Processing summary:")
        print(" ")
        for elt in listRedBlocks:
            if (elt["status"] == 1):
                msg="Processing done at iteration "+str(elt["iter"])
            else:
                if (elt["action"] == "NO-ACTION"):
                    msg = "Data not taken into account by the Pipeline"
                else:
                    msg = "Reduction Block not processed - Missing calibration"
            tplstart,detector = elt["tplstart"].split('.')
            print('%-24s' % (tplstart,),'%-14s' % (detector,),'%-30s' % (elt["action"],),msg)

        break
    else:
# Create a process pool with a maximum of 10 worker processes
        pool = Pool(processes=nbCore)
# Map our function to a data set - number 1 through 20
        pool.map(runEsorex, listCmdEsorex)
    print('%-40s' % ("Reduction Blocks processed:",),cptStatusOne)
    print('%-40s' % ("Reduction Blocks not processed:",),cptStatusZero)

    

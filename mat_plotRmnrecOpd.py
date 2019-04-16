# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 14:16:01 2019

@author: ame
"""


import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits

dir0="D:\\Travail\\MATISSE\\Commisioning\\2019-04\\"
dirdata=dir0+"rmnrec\\"

file="MATISSE_OBS_RMNREC104_0055.fits"




def mat_plotRmnrecOpd(filename,removeAvg=True,relative=False):
    data=fits.open(filename)
    fig, ax=plt.subplots(4,1, sharex=True,sharey=removeAvg)   
    fig.suptitle("{0}".format(file))
    fig.text(0.03,0.5,"Offset ($\mu$m)",rotation=90,horizontalalignment='center',size="15")
    iplot=0
    offset0=[0]
    idx=np.where(data["OPD_DL1"].data['TIME']!=0)
    time=np.take( data["OPD_DL1"].data['TIME'],idx)[0]/1e6   
    for i in range(6): 
        if np.sum(data["DL{0}".format(i+1)].data['position'])!=0:
             offset=np.take(data["OPD_DL{0}".format(i+1)].data['rtOffset'],idx)[0]*1e6
             avg=np.mean(offset)
             if removeAvg:
                 offset=offset-avg
             if offset0[0]==0:
                 offset0=offset
             if (relative):
                offset=offset-offset0
             ax[iplot].plot(time,offset,marker="+",linestyle="-",color='red')
             ax[iplot].text(-3,avg,"DL{0}".format(i+1),horizontalalignment='left',verticalalignment='center',color='black',size="20")
             iplot+=1
             #ax[i].set_ylim()
    ax[3].set_xlabel("Time (s)",size="15") 
    ax[3].set_xlim(-4,np.max(time))
    plt.show()  
    print(data["OPD_DL1"].data['TIME'])


if  __name__== '__main__' :


    arg=sys.argv

    if (arg[1]=="--help" or arg[1]== "-h"):
        print "mat_plotRmnecOpd script to visualize OD offset from RMNREC file"
        print "Usage : filename [-options]"
        print "options :"
        print " --removeAvg [True False]"
        print " --relative [True False]"   
    else:   
        filename=arg[1]
        

        narg=len(arg)
        removeAvg=False
        relative=False
        #print arg
        for i in range(2,narg):
            if (arg[i] == '--removeAvg' ):
                removeAvg=arg[i+1]
            if (arg[i] == '--relative' ):
                relative=arg[i+1]    
                
        mat_plotRmnrecOpd(filename,removeAvg=True,relative=False)

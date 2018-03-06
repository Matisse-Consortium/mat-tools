#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
  $Id: mat_raw_estimates_gui.py 59 2017-04-10 15:56:52Z fmillour $

  This file is part of the Matisse pipeline GUI series
  Copyright (C) 2017- Observatoire de la Côte d'Azur

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

  Created on Wed Apr  5 10:18:07 2017

  $Author: ame $
  $Date: 2017-04-10 17:56:52 +0200 (lun. 10 avril 2017) $
  $Revision: 59 $
  $Name:  $
"""

# Import necessary files
from libAutoPipeline import matisseType
import wx
import os
from ObjectListView import ObjectListView, ColumnDefn
from astropy.io import fits
import subprocess
from fitsheaderviewer import fitsHeaderViewer
import distutils.spawn
import fnmatch
import sys


listArg = sys.argv
for elt in listArg:
    if ('--help' in elt):
        print "Usage: mat_fileDialog.py [--dir=start directory]"
        sys.exit(0)

repBase = []
for elt in listArg:
    if ('--dir' in elt):
        item=elt.split('=')
        repBase=item[1]

# Set useful paths
fvpath    = distutils.spawn.find_executable("fv")
iconspath = os.path.join(os.path.dirname(__file__),"icons")

###############################################################################

class fileViewerKeyword:
    def __init__(self,headerkeyword=None,name=None,checkheader=None, checkheader_cases=None,function=None,source=None):
        self.headerkeyword     = headerkeyword
        self.name              = name
        self.checkheader       = checkheader
        self.checkheader_cases = checkheader_cases
        self.function          = function
        self.source            = source

    def evaluate(self,header=None,filename=None):
        res = ""
        if (self.function and self.source   == "header"):
            res = eval("{0}(header)".format(self.function))
        elif (self.function and self.source == "filename"):
            res = eval("{0}(filename)".format(self.function))
        elif self.headerkeyword and header:
            if self.checkheader:
               check = header[self.checkheader]
               for i in range(len(self.checkheader_cases)):
                   if check == self.checkheader_cases[i]:
                       res = header[self.headerkeyword[i]]
            else:
               res = header[self.headerkeyword]

        if (res == "PHOTO"):
            res = "SIPHOT";
        elif(res == "INTER"):
            res = "HISENS";
            
        return res

    def __str__(self):

        res="NAME={0}".format(self.name)
        if  self.headerkeyword:
            res+=" HEADERKEYWORD={0}".format(self.headerkeyword)
        if  self.checkheader:
            res+=" CHECKHEADER={0}".format(self.checkheader)
        if  self.checkheader_cases:
            res+=" CHECKHEADER8CASE={0}".format(self.checkheader_cases)
        if  self.function:
            res+=" FUNCTION={0}".format(self.function)
        if  self.source:
            res+=" SOURCE={0}".format(self.source)
        return res

###############################################################################

keywords=[]

keywords.append(fileViewerKeyword(
    headerkeyword="DATE-OBS",
    name="Date"))

keywords.append(fileViewerKeyword(
    function = "matisseType",
    source   = "header",
    name     = "DoCatg"))

keywords.append(fileViewerKeyword(
    headerkeyword = "HIERARCH ESO DET CHIP NAME",
    name          = "Detector"))

keywords.append(fileViewerKeyword(
    headerkeyword = "HIERARCH ESO DET NDIT",
    name          = "NDIT"))

keywords.append(fileViewerKeyword(
    headerkeyword = ["HIERARCH ESO DET SEQ1 DIT","HIERARCH ESO DET DIT"],
    checkheader       = "INSTRUME",
    checkheader_cases = ["MATISSE","AMBER"],
    name          = "DIT"))

keywords.append(fileViewerKeyword(
    headerkeyword  = ["HIERARCH ESO INS PIL NAME","HIERARCH ESO INS PIN NAME"],
    checkheader       = "HIERARCH ESO DET CHIP NAME",
    checkheader_cases = ["HAWAII-2RG","AQUARIUS"],
    name              = "Mode"))

keywords.append(fileViewerKeyword(
    headerkeyword  = ["HIERARCH ESO INS DIL NAME","HIERARCH ESO INS DIN NAME"],
    checkheader       = "HIERARCH ESO DET CHIP NAME",
    checkheader_cases = ["HAWAII-2RG","AQUARIUS"],
    name              = "Resolution"))

print(keywords)

###############################################################################

class identifyFile(object):
    def __init__(self,filename,folder):
        self.filename = filename
        self.folder   = folder

        self.header    = None
        self.isFits    = True
        self.isKnown   = True

        if os.path.isfile(folder+"/"+filename):
            self.isDir = False
        else:
            self.isDir = True

        if fnmatch.fnmatch(filename,"*.fits*"):
            #filename.endswith(".fits"):
            try:
                self.header = fits.getheader( self.folder+"/"+self.filename)
                #self.header=self.readFitsHeader( self.folder+"/"+self.filename)
                #print(self.header)
            except:
                self.isFits  = False
                self.isKnown = False
        else:
            self.isFits  = False
            self.isKnown = False

        for keywordi in keywords:
            try:
                self.__dict__[keywordi.name] = keywordi.evaluate(header=self.header,filename=folder+"/"+filename)

            except:
                self.__dict__[keywordi.name]=""
                self.isKnown=False

        if self.isDir:
            self.icon="Directory"
        else:
            if self.isKnown:
                self.icon = self.header["INSTRUME"]+" File"
            elif self.isFits:
                self.icon="Fits File"
            else:
                self.icon="Normal File"

###############################################################################

matisseColor={
# Palette here http://colrd.com/palette/19308/
# Dark files
"DARK"           :wx.Colour(64,64,64),
"HOT_DARK"       :wx.Colour(192,192,192),
"OBSDARK"        :wx.Colour(64,64,64),
"DISTOR_HOTDARK" :wx.Colour(124,159,176),
"SPECTRA_HOTDARK":wx.Colour(124,159,176),
"KAPPA_HOTDARK"  :wx.Colour(128,128,255),
"REF_HOTDARK"    :wx.Colour(124,159,176),
"IM_COLD"        :wx.Colour(124,159,176),

# Sky files
"SKY_RAW"        :wx.Colour(64,255,255),
    
# Files with fringes (observations)
"TARGET_RAW"     :wx.Colour(154,255,136),
"CALIB_RAW"      :wx.Colour(154,255,136),

# Shift map
"SHIFT_MAP"      :wx.Colour(116,196,147),

# Bad Pixel file
"BADPIX"         :wx.Colour(201,74,83),

# NLM file
"NONLINEARITY"   :wx.Colour(101,56,125),

# Flat files
"FLAT"           :wx.Colour(228,191,128),
"OBSFLAT"        :wx.Colour(228,191,128),
"OBS_FLATFIELD"  :wx.Colour(228,191,128),
"IM_FLAT"        :wx.Colour(228,191,128),

# Distorsion, spectral cliabration files
"DISTOR_IMAGES"  :wx.Colour(0,220,0),
"SPECTRA_IMAGES" :wx.Colour(0,220,0),

# Kappa matrix
"KAPPA_SKY"      :wx.Colour(150,0,50),
"KAPPA_SRC"      :wx.Colour(50,50,0),
"KAPPA_OBJ"      :wx.Colour(150,50,0),

    # Files with fringes (lab)
"CALIB_SRC_RAW"  :wx.Colour(154,191,136),

# Other files
"IM_PERIODIC"    :wx.Colour(0,200,50),
"IM_REF"         :wx.Colour(150,0,50),

# Palette here http://colrd.com/image-dna/23291/
# Also picked up some colours from "La Cinq"
# Products
"CALIB_CAL"      :wx.Colour(201,194,175),

"OBJ_CORR_FLUX"  :wx.Colour(96,189,175),
"PHOT_BEAMS"     :wx.Colour(161,216,177),
"OI_OPDWVPO"     :wx.Colour(107,150,129),
#"OI_OPDWVPO"    :wx.Colour(237,152,294),

# oifits
"RAW_DPHASE"     :wx.Colour(251,141,144),
"RAW_VIS2"       :wx.Colour(255,160,46),
"RAW_CPHASE"     :wx.Colour(255,229,93),
"RAW_SPECTRUM"   :wx.Colour(51,88,180),
"TARGET_RAW_INT" :wx.Colour(237,152,255),

"UNKNOWN"        :wx.Colour(235,235,235)
}
###############################################################################

def FileImageGetter(matFile):
   return matFile.icon

###############################################################################

class dirButtons(wx.BoxSizer):

    def __init__(self, parent,path="",updateFunction=None):
        super(dirButtons, self).__init__(wx.HORIZONTAL)
        self.parent=parent
        self.setPath(path)
        self.updateFunction = updateFunction

    def setPath(self,path):
        self.path=path
        #self.dirs=[diri for diri in path.split("/") if diri !='']
        self.dirs=path.split("/")
        self.Clear()
        self.Layout()
        self.ButtonList=[]
        size=0
        for diri in self.dirs:
            buti=wx.Button(self.parent,label=diri,style=wx.BU_EXACTFIT)
            self.ButtonList.append(buti)
            self.Add(buti,flag=wx.LEFT)
            size+=buti.GetSize()[0]
            buti.Bind(wx.EVT_BUTTON, self.ButtonClicked)

        if sys.platform=='win32' or sys.platform=='linux2':
            self.AddSpacer(-size) #je ne sais pas pourquoi il faut ajouter ça pour que l'affichage soit correct
        self.Layout()

    def ButtonClicked(self,event):
        label=event.GetEventObject().GetLabel()
        i=self.dirs.index(label)
        newDir= ''.join([diri+"/" for diri in self.dirs[0:i+1]])
        if self.updateFunction:
            self.updateFunction(newDir)

###############################################################################

class mat_FileDialog(wx.Dialog):

    def __init__(self, parent, title=None,defaultDir=None,defaultFile=None,wildcard=None,style=None,pos=None):
        super(mat_FileDialog, self).__init__(parent, title=title, size=(1400, 600))

        if defaultDir and os.path.isdir(defaultDir):
              self.dir=defaultDir
        else:
            self.dir=os.getcwd()

        self.InitUI()


        self.Centre()
        self.Show()
        self.path=""

    def InitUI(self):

        panel = wx.Panel(self)

        font  = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
            
        font.SetPointSize(9)

        vbox  = wx.BoxSizer(wx.VERTICAL)
        vbox.AddSpacer(10)

        hbox  = wx.BoxSizer(wx.HORIZONTAL)
        self.dirButtons = dirButtons(panel)
        hbox.Add(self.dirButtons)


        vbox.Add(hbox, proportion=0.1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND,border=10)

        vbox.AddSpacer(10)

        splitter     = wx.SplitterWindow(panel)
        self.dirTree = wx.GenericDirCtrl(splitter, style=wx.DIRCTRL_DIR_ONLY|wx.DIRCTRL_EDIT_LABELS)
        self.dirButtons.updateFunction=self.dirTree.SetPath
        if self.dir:
            self.dirTree.SetPath(self.dir)
        self.fileList = ObjectListView(splitter,wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.fileList.AddNamedImages("Directory",wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16,16)))
        self.fileList.AddNamedImages("Normal File",wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16,16)))
        self.fileList.AddNamedImages("MATISSE File",wx.Bitmap(os.path.join(iconspath,"matisseSmall.ico")))
        self.fileList.AddNamedImages("AMBER File",wx.Bitmap(os.path.join(iconspath,"amberSmall.ico")))
        self.fileList.AddNamedImages("GRAVITY File",wx.Bitmap(os.path.join(iconspath,"gravitySmall.ico")))
        self.fileList.AddNamedImages("Fits File",wx.Bitmap(os.path.join(iconspath,"fitsSmall.ico")))
        cols=[ColumnDefn("Filename","left",300,"filename",minimumWidth=250,imageGetter=FileImageGetter),
              ColumnDefn("Type","left",150,"icon",minimumWidth=50)]
        cols.extend([ColumnDefn(keywordi.name,"left",75,keywordi.name,minimumWidth=75) for keywordi in keywords])
        self.fileList.SetColumns(cols)
        self.fileList.rowFormatter=self.setRowColor
        self.fileList.AutoSizeColumns()
        
        # sort columns by default to file name and type
        self.fileList.SortBy(0, ascending=True)
        #self.fileList.SetSortColumn(0, resortNow=True)
        #self.fileList.SortBy(0)
        #self.fileList.SortBy(1)
        #self.fileList.SetSortColumn(1, resortNow=True)
        #self.fileList.DoSort("Type", SortOrder.Ascending)
        splitter.SplitVertically(self.dirTree,self.fileList, sashPosition=350)
        splitter.SetMinimumPaneSize(200)
        vbox.Add(splitter, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND,border=10)

        vbox.AddSpacer(10)

        hbox2             = wx.BoxSizer(wx.HORIZONTAL)
        self.addDirButton = wx.Button(panel,label="+")
        hbox2.Add(self.addDirButton, proportion=0.1,flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        self.pathText  = wx.TextCtrl(panel,style=wx.TE_READONLY)
        hbox2.Add(self.pathText, proportion=1,flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        self.filterBox = wx.ComboBox(panel,choices=["All Files","Fits Files","Matisse Files"],style    = wx.CB_DROPDOWN|wx.CB_READONLY)
        self.filterBox.SetValue("All Files")
        hbox2.Add(self.filterBox, proportion=0.2,flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        self.cancelButton = wx.Button(panel,wx.ID_CANCEL)
        hbox2.Add(self.cancelButton,proportion=0.1,flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        self.okButton = wx.Button(panel,wx.ID_OK )
        hbox2.Add(self.okButton,proportion=0.1,flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        vbox.Add(hbox2, proportion=0.2, flag=wx.LEFT|wx.RIGHT|wx.EXPAND,border=10)
        vbox.AddSpacer(10)

        panel.SetSizer(vbox)


        tree = self.dirTree.GetTreeCtrl()
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.dirChanged,tree)
        self.Bind(wx.EVT_BUTTON, self.okClicked, self.okButton)
        self.Bind(wx.EVT_BUTTON, self.cancelClicked, self.cancelButton)
        self.Bind(wx.EVT_COMBOBOX, self.filterChanged, self.filterBox)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED,self.fileSelected,self.fileList)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,self.fileListRightClicked,self.fileList)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.fileListDoubleClicked,self.fileList)
        self.Bind(wx.EVT_BUTTON, self.addDirClicked, self.addDirButton)

        self.dirChanged()

        # Colour of text
    def setRowColor(self,listItem, data):

        if data.DoCatg:
            try:
                txtcol=wx.BLACK
                bkgcol=matisseColor[data.DoCatg]
            except:
                txtcol=wx.BLACK
                bkgcol=matisseColor["UNKNOWN"]
        else:
            c=listItem.GetId() % 2
            bkgcol=wx.Colour(250+3*c,250+3*c,250+3*c)
            if data.isDir:
                txtcol=wx.Colour(0,0,0)
            else:
                txtcol=wx.Colour(180,180,180)
        listItem.SetTextColour(txtcol)
        listItem.SetBackgroundColour(bkgcol)

    def dirChanged(self,treeEvent=None):
       self.pathText.SetValue("")
       #newDir= self.dirTree.GetPath()
       self.dir=self.dirTree.GetPath().replace("\\","/")
       files=os.listdir(self.dir)
       matisseFileList=[]
       filt=self.filterBox.GetValue()

       for filei in files:
           #if os.path.isfile(self.dir+"/"+filei):
               matFile=identifyFile(filei,self.dir)
               if filt=="All Files":
                   Append=True
               elif filt=="Fits Files" and matFile.isFits:
                   Append=True
               elif filt=="Matisse Files" and matFile.isMatisse:
                   Append=True
               else:
                   Append=False
               if Append:
                   matisseFileList.append(matFile)
       self.fileList.SetObjects(matisseFileList)
       self.fileList.AutoSizeColumns()

       for icol in range(len(keywords)+1):
           self.fileList.SetColumnWidth(icol,wx.LIST_AUTOSIZE)
           wc=self.fileList.GetColumnWidth(icol)
           if wc<self.fileList.columns[icol].minimumWidth:
               self.fileList.SetColumnWidth(icol,self.fileList.columns[icol].minimumWidth)

       self.dirButtons.setPath(self.dir)

    def fileSelected(self,event):
        nfiles=self.fileList.GetSelectedItemCount()
        itemNum=-1
        selectedItems=[]
        for ifile in range(nfiles):
            itemNum=self.fileList.GetNextSelected(itemNum)
            selectedItems.append(self.fileList.GetItem(itemNum).GetText())
        self.path=selectedItems
        txt=""
        for itemi in selectedItems:
            txt=txt+itemi+" "
        self.pathText.SetValue(txt)


    def fileListDoubleClicked(self,event):
        print "doubleclicked"
        if identifyFile(self.path[0],self.dirTree.GetPath()).isDir:
             self.dirTree.SetPath(self.dirTree.GetPath()+'/'+self.path[0])

    def fileListRightClicked(self,event):
        print "rightclicked"
        menu = wx.Menu()

        menu.Append( 0, "Show Header" )
        wx.EVT_MENU( menu, 0, self.showHeader)
        menu.Append( 1, "Show IMAGING_DETECTOR")
        wx.EVT_MENU( menu, 1, self.showImagingDetector)
        menu.Append( 2, "Show IMAGING_DATA")
        wx.EVT_MENU( menu, 2, self.showImagingData)
        menu.Append( 3, "Open with fv" )
        wx.EVT_MENU( menu, 3, self.openWithFv)

        self.fileList.PopupMenu( menu, event.GetPoint())
    def okClicked(self,event):
        self.EndModal(wx.ID_OK)


    def cancelClicked(self,event):
         self.EndModal(wx.ID_CANCEL)

    def addDirClicked(self,event):

        os.makedirs(self.dir+"/"+"newDir")
        self.dirTree.ReCreateTree()
        self.dirTree.ExpandPath(self.dir+"/"+"newDir")

    def filterChanged(self,event):
        self.dirChanged()

    def GetPaths(self):
        return [self.dir+'/'+pathi for pathi in self.path]

    def showHeader(self,event):
        print "show header {0}".format(self.GetPaths())
        for filei in self.path:
             if filei.endswith('.fits'):
                 print self.dir+'/'+filei
                 fitsHeaderViewer(self.dirTree.GetPath()+'/'+filei)

    def showImagingDetector(self,event):
        print "show IMAGING_DETECTOR {0}".format(self.GetPaths())

    def showImagingData(self,event):
        print "show IMAGING_DATA {0}".format(self.GetPaths())

    def openWithFv(self,event):
        print "Open with fv {0}".format(self.GetPaths())
        for filei in self.path:
            if filei.endswith('.fits'):
                subprocess.Popen([fvpath,self.dirTree.GetPath()+'/'+filei])

###############################################################################

if __name__ == '__main__':

    app = wx.App()
    openFileDialog = mat_FileDialog(None, 'Open a file',repBase)
    if openFileDialog.ShowModal() == wx.ID_OK:
        print openFileDialog.GetPaths()
    openFileDialog.Destroy()
    app.MainLoop()
    app.Destroy()


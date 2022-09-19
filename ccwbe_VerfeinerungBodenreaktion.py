import os
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from osgeo import osr, gdal
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(2056) #LV95
gtiff_driver=gdal.GetDriverByName("GTiff")


#input data
myworkspace="D:/CCWBE/GIS"
referenceraster=myworkspace+"/bedem10m.tif"

#*************************************************************
#functions
#*************************************************************
def gridasciitonumpyarrayfloat(ingridfilefullpath):
    i=0
    row = 0
    headerstr=''
    infile=open(ingridfilefullpath, "r")
    for line in infile:
        if i==0:
            ncols=int(line.strip().split()[-1])
            headerstr+=line
        elif i==1:
            nrows=int(line.strip().split()[-1])
            headerstr += line
        elif i==2:
            xllcorner=float(line.strip().split()[-1])
            headerstr += line
        elif i==3:
            yllcorner=float(line.strip().split()[-1])
            headerstr += line
        elif i==4:
            cellsize=float(line.strip().split()[-1])
            headerstr += line
        elif i==5:
            NODATA_value=float(line.strip().split()[-1])
            arr=np.zeros((nrows, ncols), dtype=float)
            arr[:,:]=NODATA_value
            headerstr += line.replace("\n","")
        elif i>5:
            col=0
            while col<ncols:
                for item in line.strip().split():
                    arr[row,col]=float(item)
                    col+=1
            row+=1
        i+=1
    infile.close()
    return arr, ncols, nrows, xllcorner, yllcorner, cellsize, NODATA_value, headerstr
def gridasciitonumpyarrayint(ingridfilefullpath):
    i=0
    row = 0
    headerstr=''
    infile=open(ingridfilefullpath, "r")
    for line in infile:
        if i==0:
            ncols=int(line.strip().split()[-1])
            headerstr+=line
        elif i==1:
            nrows=int(line.strip().split()[-1])
            headerstr += line
        elif i==2:
            xllcorner=float(line.strip().split()[-1])
            headerstr += line
        elif i==3:
            yllcorner=float(line.strip().split()[-1])
            headerstr += line
        elif i==4:
            cellsize=float(line.strip().split()[-1])
            headerstr += line
        elif i==5:
            NODATA_value=float(line.strip().split()[-1])
            arr=np.zeros((nrows, ncols), dtype=int)
            arr[:,:]=NODATA_value
            headerstr += line.replace("\n","")
        elif i>5:
            col=0
            while col<ncols:
                for item in line.strip().split():
                    arr[row,col]=float(item)
                    col+=1
            row+=1
        i+=1
    infile.close()
    return arr, ncols, nrows, xllcorner, yllcorner, cellsize, NODATA_value, headerstr
def convert_tif_to_array(intifraster):
    inras = gdal.Open(intifraster)
    inband = inras.GetRasterBand(1)
    outarr = inband.ReadAsArray()
    return outarr
def convertarrtotif(arr, outfile, tifdatatype, referenceraster, nodatavalue):
    ds_in=gdal.Open(referenceraster)
    inband=ds_in.GetRasterBand(1)
    gtiff_driver=gdal.GetDriverByName("GTiff")
    ds_out = gtiff_driver.Create(outfile, inband.XSize, inband.YSize, 1, tifdatatype)
    ds_out.SetProjection(ds_in.GetProjection())
    ds_out.SetGeoTransform(ds_in.GetGeoTransform())
    outband=ds_out.GetRasterBand(1)
    outband.WriteArray(arr)
    outband.SetNoDataValue(nodatavalue)
    ds_out.FlushCache()
    del ds_in
    del ds_out
    del inband
    del outband
def cleanraster(xinarray):
    nrows=np.shape(xinarray)[0]
    ncols=np.shape(xinarray)[1]
    xoutarr = np.zeros((nrows, ncols), dtype=np.dtype(int))
    xoutarr[:, :]=xinarray[:, :]
    i=1
    while i <nrows-1:
        j=1
        while j<ncols-1:
            centercell=xinarray[i,j]
            listofneighborcells=[]
            listofneighborcells.append(xinarray[i,j+1])
            listofneighborcells.append(xinarray[i+1,j+1])
            listofneighborcells.append(xinarray[i+1,j])
            listofneighborcells.append(xinarray[i+1,j-1])
            listofneighborcells.append(xinarray[i,j-1])
            listofneighborcells.append(xinarray[i-1,j-1])
            listofneighborcells.append(xinarray[i-1,j])
            listofneighborcells.append(xinarray[i-1,j+1])
            while -9999 in listofneighborcells:
                listofneighborcells.remove(-9999)
            if len(listofneighborcells)>0:
                countneighborcells = np.unique(listofneighborcells, return_counts=True)
                maxcount=np.max(countneighborcells[1])
                majorityelement=countneighborcells[0][countneighborcells[1].tolist().index(maxcount)]
                if centercell==NODATA_value and len(listofneighborcells)>3:
                    xoutarr[i,j]=majorityelement
                if maxcount>=6 and centercell!=majorityelement:
                    xoutarr[i, j] = majorityelement
            j+=1
        i+=1
    return xoutarr
# *************************************************************
#end functions
# *************************************************************

#**************************************************************************************************************
#read the rasters
#reference tif raster
print("read reference raster")
referencetifraster=gdal.Open(referenceraster)
referencetifrasterband=referencetifraster.GetRasterBand(1)
referencerasterProjection=referencetifraster.GetProjection()
ncols=referencetifrasterband.XSize
nrows=referencetifrasterband.YSize
indatatype=referencetifrasterband.DataType
indatatypeint=gdal.Open(myworkspace+"/bemask.tif").GetRasterBand(1).DataType
#NODATA_value=np.min(dhmarr)
NODATA_value=-9999
cellsize=10.0
#*****************************************************************************************************************
#create a mask array
print("create a mask")
maskarr=convert_tif_to_array(myworkspace+"/bemask.tif")
maskarrbool=np.ones((nrows, ncols), dtype=bool)
#fill the mask array
maskarrbool=np.where(maskarr==1, False, maskarrbool)
#plt.imshow(maskarrbool)

#read pH raster
pharrin=convert_tif_to_array(myworkspace+"/beph.tif")
pharrin=np.where((pharrin>9),5,pharrin)
pharrout=np.where((pharrin>9),5,pharrin)
lagearr=convert_tif_to_array(myworkspace+"/belage.tif")
flachmoorarr=convert_tif_to_array(myworkspace+"/beflachmoor.tif")
hochmoorarr=convert_tif_to_array(myworkspace+"/behochmoor.tif")
sumpfarr=convert_tif_to_array(myworkspace+"/besumpf.tif")
#correct pharr
#Hochmoor
pharrout=np.where(((hochmoorarr==1)&(pharrin>5)),3,pharrout)
pharrout=np.where(((hochmoorarr==1)&(pharrin>=2)&(pharrin<=5)),pharrout-1,pharrout)
#Flachmoor
pharrout=np.where(((flachmoorarr==1)&(pharrin>1)&(pharrin<=7)),pharrout-1,pharrout)
pharrout=np.where(((flachmoorarr==1)&(pharrin>7)),7,pharrout)
#Sumpf
pharrout=np.where(((sumpfarr==1)&(pharrin>=1)&(pharrin<=5)),pharrout-1,pharrout)
pharrout=np.where(((sumpfarr==1)&(pharrin>5)),5,pharrout)
#Kuppe
pharrout=np.where(((lagearr==4)&(pharrin>=1)&(pharrin<=9)),pharrout-1,pharrout)
#Mulde
pharrout=np.where(((lagearr==2)&(pharrin>=1)&(pharrin<=7)),pharrout+1,pharrout)
pharrout=np.where((pharrout>9),5,pharrout)
pharrout=np.where((pharrout==0),5,pharrout)

np.min(pharrout)
pharrout=np.where((maskarr==1),pharrout,NODATA_value)
#plt.imshow(outarr2)
#write output
convertarrtotif(pharrout, myworkspace+"/"+"bebodenreaktionverfeinert.tif", 1, referenceraster, NODATA_value)
print("done ...")
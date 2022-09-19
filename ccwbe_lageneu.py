import os
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import matplotlib.colors
from osgeo import osr, gdal
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(2056) #LV95
gtiff_driver=gdal.GetDriverByName("GTiff")



#input data
#myworkspace="E:/CCWBE/GIS"
myworkspace="C:/DATA/projects/CCWBE/GIS"
referenceraster=myworkspace+"/bedem10m.tif"
deltademfuerkuppen=1.2
anzahlpixelfuerkuppen=5
deltademfuerhangfusslage=1.5

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

#read input raster
surfacerunoffin=convert_tif_to_array(myworkspace+"/besurfacerunoff.tif")
demarr=convert_tif_to_array(myworkspace+"/bedem10m.tif")
slopearr=convert_tif_to_array(myworkspace+"/beslopeprz10m.tif")
felsarr=convert_tif_to_array(myworkspace+"/befels.tif")
#np.min(slopearr)
slopearr=np.where((slopearr==np.min(slopearr)),NODATA_value,slopearr)
flaccarr=convert_tif_to_array(myworkspace+"/beflowacc10m.tif")
begrossflozschwemmgebietarr=convert_tif_to_array(myworkspace+"/begkghkwasser.tif")

#Bereinige surface runoff raster
#surfacerunoffout=cleanraster(surfacerunoffin)
#plt.imshow(surfacerunoffout)
#np.max(surfacerunoffout)
#np.min(surfacerunoffout)
#write output
#convertarrtotif(surfacerunoffout, myworkspace+"/"+"besurfacerunoffclean.tif", 1, referenceraster, NODATA_value)
#print("done ...")
#surfacerunoffout=convert_tif_to_array(myworkspace+"/besurfacerunoffclean.tif")

#create output array
outarr=np.zeros((nrows, ncols), dtype=int)
outarr[:,:]=NODATA_value

#1 Ebene
#2 Hangfuss/Mulde
#3 Hang
#4 Kuppe

#3 Hang
print("3 Hang")
outarr=np.where((maskarr==1),3,outarr)
outarr=np.where((maskarr!=1),NODATA_value,outarr)
#plt.imshow(outarr)

#1 Ebene
print("1 Ebene")
outarr=np.where((slopearr<10),1,outarr)


#4 Kuppen
print("4 Kuppen")
i=1
j=1
while i < nrows-1:
    if i%1000.0==0:
        print(i)
    j=1
    while j < ncols - 1:
        n_z=0
        z = demarr[i, j]
        if demarr[i - 1, j - 1] < (z-deltademfuerkuppen):
            n_z += 1
        if demarr[i - 1, j] < (z-deltademfuerkuppen):
            n_z += 1
        if demarr[i - 1, j + 1] < (z-deltademfuerkuppen):
            n_z += 1
        if demarr[i, j + 1] < (z-deltademfuerkuppen):
            n_z += 1
        if demarr[i + 1, j + 1] < (z-deltademfuerkuppen):
            n_z += 1
        if demarr[i + 1, j] < (z-deltademfuerkuppen):
            n_z += 1
        if demarr[i + 1, j - 1] < (z-deltademfuerkuppen):
            n_z += 1
        if demarr[i, j - 1] < (z-deltademfuerkuppen):
            n_z += 1
        if n_z >= anzahlpixelfuerkuppen and slopearr[i,j]<50:
            outarr[i,j] = 4
            outarr[i - 1, j - 1] = 4
            outarr[i - 1, j] = 4
            outarr[i - 1, j + 1] = 4
            outarr[i, j + 1] = 4
            outarr[i + 1, j + 1] = 4
            outarr[i + 1, j] = 4
            outarr[i + 1, j - 1] = 4
            outarr[i, j - 1] = 4
        elif n_z >= anzahlpixelfuerkuppen and slopearr[i,j]>=50:
            outarr[i,j] = 4
        j += 1
    i += 1

#4 Grate
print("4 Grate")
i=1
j=1
while i < nrows-1:
    if i%1000.0==0:
        print(i)
    j=1
    while j < ncols - 1:
        n_z=0
        z = demarr[i, j]
        if demarr[i - 1, j - 1] < (z-deltademfuerkuppen) and demarr[i + 1, j + 1] < (z-deltademfuerkuppen) and slopearr[i,j]<50 and begrossflozschwemmgebietarr[i,j]!=1:
            outarr[i,j] = 4
            outarr[i - 1, j - 1] = 4
            outarr[i - 1, j] = 4
            outarr[i - 1, j + 1] = 4
            outarr[i, j + 1] = 4
            outarr[i + 1, j + 1] = 4
            outarr[i + 1, j] = 4
            outarr[i + 1, j - 1] = 4
            outarr[i, j - 1] = 4
        elif demarr[i - 1, j - 1] < (z-deltademfuerkuppen) and demarr[i + 1, j + 1] < (z-deltademfuerkuppen) and slopearr[i,j]>=50 and begrossflozschwemmgebietarr[i,j]!=1:
            outarr[i,j] = 4
        if demarr[i + 1, j - 1] < (z-deltademfuerkuppen) and demarr[i - 1, j + 1] < (z-deltademfuerkuppen) and slopearr[i,j]<50 and begrossflozschwemmgebietarr[i,j]!=1:
            outarr[i,j] = 4
            outarr[i - 1, j - 1] = 4
            outarr[i - 1, j] = 4
            outarr[i - 1, j + 1] = 4
            outarr[i, j + 1] = 4
            outarr[i + 1, j + 1] = 4
            outarr[i + 1, j] = 4
            outarr[i + 1, j - 1] = 4
            outarr[i, j - 1] = 4
        elif demarr[i + 1, j - 1] < (z-deltademfuerkuppen) and demarr[i - 1, j + 1] < (z-deltademfuerkuppen) and slopearr[i,j]>=50 and begrossflozschwemmgebietarr[i,j]!=1:
            outarr[i,j] = 4
        if demarr[i - 1, j] < (z-deltademfuerkuppen) and demarr[i + 1, j] < (z-deltademfuerkuppen) and slopearr[i,j]<50  and begrossflozschwemmgebietarr[i,j]!=1:
            outarr[i,j] = 4
            outarr[i - 1, j - 1] = 4
            outarr[i - 1, j] = 4
            outarr[i - 1, j + 1] = 4
            outarr[i, j + 1] = 4
            outarr[i + 1, j + 1] = 4
            outarr[i + 1, j] = 4
            outarr[i + 1, j - 1] = 4
            outarr[i, j - 1] = 4
        elif demarr[i - 1, j] < (z-deltademfuerkuppen) and demarr[i + 1, j] < (z-deltademfuerkuppen) and slopearr[i,j]>=50:
            outarr[i,j] = 4
        if demarr[i, j - 1] < (z-deltademfuerkuppen) and demarr[i, j + 1] < (z-deltademfuerkuppen) and slopearr[i,j]<50:
            outarr[i,j] = 4
            outarr[i - 1, j - 1] = 4
            outarr[i - 1, j] = 4
            outarr[i - 1, j + 1] = 4
            outarr[i, j + 1] = 4
            outarr[i + 1, j + 1] = 4
            outarr[i + 1, j] = 4
            outarr[i + 1, j - 1] = 4
            outarr[i, j - 1] = 4
        elif demarr[i, j - 1] < (z-deltademfuerkuppen) and demarr[i, j + 1] < (z-deltademfuerkuppen) and slopearr[i,j]>=50:
            outarr[i,j] = 4
        j += 1
    i += 1

#2 Mulde
print("2 Mulden")
outarr=np.where(((flaccarr>=(50000.0/cellsize/cellsize))&(slopearr<40)&(felsarr!=1)),2,outarr)
outarr=np.where(((surfacerunoffin==1)&(slopearr<40)&(felsarr!=1)),2,outarr)#&(slopearr<30)
outarr=np.where((maskarr==0),NODATA_value,outarr)

#2 Ausscheidung von Hangfusslagen am Rand von Ebenen
outarrfix=outarr.copy()
i=1
j=1
while i < nrows-1:
    if i%1000.0==0:
        print(i)
    j=1
    while j < ncols - 1:
        z=demarr[i,j]
        if outarrfix[i,j]==1:
            if outarrfix[i - 1, j - 1]==3 and demarr[i - 1, j - 1]>(z+deltademfuerhangfusslage):
                outarr[i - 1, j - 1]=2
            if outarrfix[i - 1, j]==3 and demarr[i - 1, j]>(z+deltademfuerhangfusslage):
                outarr[i - 1, j]=2
            if outarrfix[i - 1, j + 1]==3 and demarr[i - 1, j + 1]>(z+deltademfuerhangfusslage):
                outarr[i - 1, j + 1]=2
            if outarrfix[i, j + 1]==3 and demarr[i, j + 1]>(z+deltademfuerhangfusslage):
                outarr[i, j + 1] = 2
            if outarrfix[i + 1, j + 1]==3 and demarr[i + 1, j + 1]>(z+deltademfuerhangfusslage):
                outarr[i + 1, j + 1]=2
            if outarrfix[i + 1, j]==3 and demarr[i + 1, j]>(z+deltademfuerhangfusslage):
                outarr[i + 1, j]=2
            if outarrfix[i + 1, j - 1]==3 and demarr[i + 1, j - 1]>(z+deltademfuerhangfusslage):
                outarr[i + 1, j - 1]=2
            if outarrfix[i, j - 1]==3 and demarr[i, j - 1]>(z+deltademfuerhangfusslage):
                outarr[i, j - 1]=2
        j += 1
    i += 1



#Bereinigung einzelne Mulden
i=1
j=1
while i < nrows-1:
    if i%1000.0==0:
        print(i)
    j=1
    while j < ncols - 1:
        n=0
        if outarr[i,j]==2:
            if outarr[i - 1, j - 1] ==3:
                n += 1
            if outarr[i - 1, j] ==3:
                n += 1
            if outarr[i - 1, j + 1] ==3:
                n += 1
            if outarr[i, j + 1]  ==3:
                n += 1
            if outarr[i + 1, j + 1] ==3:
                n += 1
            if outarr[i + 1, j]  ==3:
                n += 1
            if outarr[i + 1, j - 1] ==3:
                n += 1
            if outarr[i, j - 1] ==3:
                n += 1
        if n== 8:
            if slopearr[i - 1, j - 1] >= 10 and slopearr[i - 1, j - 1]<=20:
                outarr[i - 1, j-1] = 2
            if slopearr[i - 1, j] >= 10 and slopearr[i - 1, j] <= 20:
                outarr[i - 1, j] = 2
            if slopearr[i - 1, j + 1] >= 10 and slopearr[i - 1, j + 1] <= 20:
                outarr[i - 1, j + 1] = 2
            if slopearr[i, j + 1] >= 10 and slopearr[i, j + 1] <= 20:
                outarr[i, j + 1] = 2
            if slopearr[i + 1, j + 1] >= 10 and slopearr[i + 1, j + 1] <= 20:
                outarr[i + 1, j + 1] = 2
            if slopearr[i + 1, j] >= 10 and slopearr[i + 1, j] <= 20:
                outarr[i + 1, j] = 2
            if slopearr[i + 1, j - 1] >= 10 and slopearr[i + 1, j - 1] <= 20:
                outarr[i + 1, j - 1] = 2
            if slopearr[i, j - 1] >= 10 and slopearr[i, j - 1] <= 20:
                outarr[i, j - 1] = 2
        j += 1
    i += 1


#write output
outarr=np.where(((surfacerunoffin==1)&(slopearr<40)&(felsarr!=1)),2,outarr)#&(slopearr<30)
outarr=np.where((maskarr==0),NODATA_value,outarr)
outarr=np.where((maskarr!=1),NODATA_value,outarr)
#plt.imshow(outarr, cmap='tab20', interpolation='none')
#plt.colorbar()
convertarrtotif(outarr, myworkspace+"/"+"belage.tif", 1, referenceraster, NODATA_value)
print("done ...")



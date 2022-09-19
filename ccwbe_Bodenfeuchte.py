import os
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from osgeo import osr, gdal
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(21781) #LV03
gtiff_driver=gdal.GetDriverByName("GTiff")


#input data
myworkspace="C:/DATA/projects/CCWBE/GIS"
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
dhmarr=convert_tif_to_array(myworkspace+"/bedem10m.tif")
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

#create an output raster
outarr=np.zeros((nrows, ncols), dtype=int)
#outarr[::]=NODATA_value
#outarr=np.ma.masked_array(outarr, maskarrbool)
#plt.imshow(outarr)

#load arrays step by step and calculate soil humidity
#data level Gelaendeoberflaeche
tmpcredits=np.zeros((nrows, ncols), dtype=int)
#tmpcredits=np.ma.masked_array(tmpcredits, maskarrbool)
moorsumpfarr=convert_tif_to_array(myworkspace+"/bemoorsumpf.tif")
tmpcredits=np.where((moorsumpfarr==1),4,tmpcredits)
del moorsumpfarr
auenarr=convert_tif_to_array(myworkspace+"/beauen.tif")
tmpcredits=np.where((auenarr==1),4,tmpcredits)
del auenarr
geroellarr=convert_tif_to_array(myworkspace+"/begeroell.tif")
tmpcredits=np.where((geroellarr==1),-1,tmpcredits)
del geroellarr
felsarr=convert_tif_to_array(myworkspace+"/befels.tif")
tmpcredits=np.where((felsarr==1),-2,tmpcredits)
del felsarr
wasserarr=convert_tif_to_array(myworkspace+"/bewasser.tif")
tmpcredits=np.where((wasserarr==1),11,tmpcredits)
outarr=outarr+tmpcredits
del tmpcredits
#data level Topoindex
#topoindexarr=convert_tif_to_array(myworkspace+"/betopoindex.tif")
#tmpcredits=np.zeros((nrows, ncols), dtype=int)
##tmpcredits=np.ma.masked_array(tmpcredits, maskarrbool)
#tmpcredits=np.where((topoindexarr>50000),2,tmpcredits)
#tmpcredits=np.where(((topoindexarr>20000)&(topoindexarr<=50000)),1,tmpcredits)
#tmpcredits=np.where(((topoindexarr>500)&(topoindexarr<=20000)),-1,tmpcredits)
#tmpcredits=np.where((topoindexarr<500),-2,tmpcredits)
##plt.imshow(tmpcredits)
#outarr=outarr+tmpcredits
#del tmpcredits
#data level Tongehalt and Topoindex
tmpcredits=np.zeros((nrows, ncols), dtype=int)
#tmpcredits=np.ma.masked_array(tmpcredits, maskarrbool)
tongehaltarr=convert_tif_to_array(myworkspace+"/betg.tif")
tmpcredits=np.where((tongehaltarr==44),2,tmpcredits)
tmpcredits=np.where((tongehaltarr==34),1,tmpcredits)
#del topoindexarr
outarr=outarr+tmpcredits
del tmpcredits
#data level Exposition and Slope
tmpcredits=np.zeros((nrows, ncols), dtype=int)
#tmpcredits=np.ma.masked_array(tmpcredits, maskarrbool)
exparr=convert_tif_to_array(myworkspace+"/beaspect10m.tif")
slopearr=convert_tif_to_array(myworkspace+"/beslopeprz10m.tif")
tmpcredits=np.where(((exparr>135)&(exparr<225)&(slopearr>=100)),-2,tmpcredits)
tmpcredits=np.where(((exparr>320)&(slopearr<=10)),2,tmpcredits)
tmpcredits=np.where(((exparr>=0)&(exparr<45)&(slopearr<=10)),1,tmpcredits)
del exparr
del slopearr
outarr=outarr+tmpcredits
del tmpcredits
#data level Landslides
tmpcredits=np.zeros((nrows, ncols), dtype=int)
#tmpcredits=np.ma.masked_array(tmpcredits, maskarrbool)
rutscharr=convert_tif_to_array(myworkspace+"/berutsch.tif")
tmpcredits=np.where((rutscharr==1),1,tmpcredits)
del rutscharr
outarr=outarr+tmpcredits
del tmpcredits
#data level Kuppenlage
tmpcredits=np.zeros((nrows, ncols), dtype=int)
#tmpcredits=np.ma.masked_array(tmpcredits, maskarrbool)
lagearr=convert_tif_to_array(myworkspace+"/belage.tif")
tmpcredits=np.where((lagearr==4),-1,tmpcredits)
#tmpcredits=np.where((lagearr==2),1,tmpcredits)
del lagearr
outarr=outarr+tmpcredits
del tmpcredits
#data level flow accumulation
tmpcredits=np.zeros((nrows, ncols), dtype=int)
#tmpcredits=np.ma.masked_array(tmpcredits, maskarrbool)
flowaccarr=convert_tif_to_array(myworkspace+"/beflowacc10m.tif")
#tmpcredits=np.where((flowaccarr*cellsize*cellsize<=300),-1,tmpcredits)
tmpcredits=np.where((flowaccarr*cellsize*cellsize>=500000),11,tmpcredits)
del flowaccarr
outarr=outarr+tmpcredits
del tmpcredits
#data level Bergsturz
tmpcredits=np.zeros((nrows, ncols), dtype=int)
#tmpcredits=np.ma.masked_array(tmpcredits, maskarrbool)
#bergsturzgeroellarr=convert_tif_to_array(myworkspace+"/bebergsturzgeroell.tif")
bergsturzarr=convert_tif_to_array(myworkspace+"/bebergsturz.tif")
tmpcredits=np.where((bergsturzarr==1),-2,tmpcredits)
del bergsturzarr
outarr=outarr+tmpcredits
del tmpcredits
#data level Radiation
tmpcredits=np.zeros((nrows, ncols), dtype=int)
#tmpcredits=np.ma.masked_array(tmpcredits, maskarrbool)
radiationarr=convert_tif_to_array(myworkspace+"/beradyy10m.tif")
radiationarr=np.ma.masked_array(radiationarr, maskarrbool)
rad90quantile=np.quantile(radiationarr,0.90)
#rad50quantile=np.quantile(radiationarr,0.50)
rad20quantile=np.quantile(radiationarr,0.20)
tmpcredits=np.where((radiationarr<=rad20quantile),2,tmpcredits)
#tmpcredits=np.where(((radiationarr>rad25quantile)&(radiationarr<=rad50quantile)),2,tmpcredits)
#tmpcredits=np.where(((radiationarr>rad50quantile)&(radiationarr<=rad75quantile)),-1,tmpcredits)
tmpcredits=np.where((radiationarr>=rad90quantile),-2,tmpcredits)
del radiationarr
outarr=outarr+tmpcredits
del tmpcredits
#data layer Sinks
tmpcredits=np.zeros((nrows, ncols), dtype=int)
#tmpcredits=np.ma.masked_array(tmpcredits, maskarrbool)
#sinkarr=np.zeros((nrows, ncols), dtype=int)
##sinkarr=np.ma.masked_array(sinkarr, maskarrbool)
#i=1
#while i < nrows-1:
#    if i%1000==0:
#        print(i)
#    j=1
#    while j< ncols-1:
#        countsinks=0
#        z=dhmarr[i,j]
#        if dhmarr[i,j+1]>z:
#            countsinks+=1
#        if dhmarr[i+1, j + 1] > z:
#            countsinks += 1
#        if dhmarr[i+1,j]>z:
#            countsinks+=1
#        if dhmarr[i+1,j-1]>z:
#            countsinks+=1
#        if dhmarr[i,j-1]>z:
#            countsinks+=1
#        if dhmarr[i-1,j-1]>z:
#            countsinks+=1
#        if dhmarr[i-1,j]>z:
#            countsinks+=1
#        if dhmarr[i-1,j+1]>z:
#            countsinks+=1
#        if countsinks>=7:
#            sinkarr[i,j]=1
#        j+=1
#    i+=1
#write sinkarr out
#convertarrtotif(sinkarr, myworkspace+"/"+"besink2.tif", 5, referenceraster, NODATA_value)

sinkarr=convert_tif_to_array(myworkspace+"/besink2.tif")
tmpcredits=np.where((sinkarr==1),2,tmpcredits)
outarr=outarr+tmpcredits
del tmpcredits
#data layer surface runoff
tmpcredits=np.zeros((nrows, ncols), dtype=int)
#tmpcredits=np.ma.masked_array(tmpcredits, maskarrbool)
runoffarr=convert_tif_to_array(myworkspace+"/besurfacerunoff.tif")
tmpcredits=np.where((runoffarr==1),4,tmpcredits)
del runoffarr
outarr=outarr+tmpcredits
del tmpcredits

#data layer Niederschlag
tmpcredits=np.zeros((nrows, ncols), dtype=int)
#tmpcredits=np.ma.masked_array(tmpcredits, maskarrbool)
nsarr=convert_tif_to_array(myworkspace+"/beniederschlag.tif")
nsarr=np.ma.masked_array(nsarr, maskarrbool)
ns90quantile=np.quantile(nsarr,0.90)
ns80quantile=np.quantile(nsarr,0.80)
ns50quantile=np.quantile(nsarr,0.50)
ns10quantile=np.quantile(nsarr,0.10)
tmpcredits=np.where((nsarr<=ns10quantile),-2,tmpcredits)
tmpcredits=np.where(((nsarr>ns10quantile)&(nsarr<=ns50quantile)),-1,tmpcredits)
tmpcredits=np.where(((nsarr>ns50quantile)&(nsarr<=ns80quantile)),1,tmpcredits)
tmpcredits=np.where((nsarr>ns80quantile),2,tmpcredits)
del nsarr
outarr=outarr+tmpcredits
del tmpcredits



#correct water areas
outarr=np.where((wasserarr==1),11,outarr)
np.min(outarr>-9999)
#del wasserarr
#write output
outarr=np.where((maskarr==0),NODATA_value,outarr)
plt.imshow(outarr)
convertarrtotif(outarr, myworkspace+"/"+"bebodenfeuchteroh.tif", 5, referenceraster, NODATA_value)
#reclassify Bodenfeuchte

outarr2=np.zeros((nrows, ncols), dtype=int)#outarr.copy()
outarr2[:,:]=-9999
#q10=np.quantile(outarr,0.1)
#q20=np.quantile(outarr,0.2)
#q30=np.quantile(outarr,0.3)
#q40=np.quantile(outarr,0.4)
#q50=np.quantile(outarr,0.5)
#q60=np.quantile(outarr,0.6)
#q70=np.quantile(outarr,0.7)
#q80=np.quantile(outarr,0.8)
#q90=np.quantile(outarr,0.9)

#outarr2=np.where((outarr<=q10),9,outarr2)
#outarr2=np.where(((outarr>q10)&(outarr<=q20)),8,outarr2)
#outarr2=np.where(((outarr>q20)&(outarr<=q30)),7,outarr2)
#outarr2=np.where(((outarr>q30)&(outarr<=q40)),6,outarr2)
#outarr2=np.where(((outarr>q40)&(outarr<=q50)),5,outarr2)
#outarr2=np.where(((outarr>q50)&(outarr<=q60)),4,outarr2)
#outarr2=np.where(((outarr>q60)&(outarr<=q70)),3,outarr2)
#outarr2=np.where(((outarr>q70)&(outarr<=q80)),2,outarr2)
#outarr2=np.where((outarr>q80),1,outarr2)

flachmoorarr=convert_tif_to_array(myworkspace+"/beflachmoor.tif")
hochmoorarr=convert_tif_to_array(myworkspace+"/behochmoor.tif")
sumpfarr=convert_tif_to_array(myworkspace+"/besumpf.tif")
auarr=convert_tif_to_array(myworkspace+"/beauen.tif")
#1;sehr trocken
#2;trocken
#3;normal
#4;feucht
#5;nass

outarr2=np.where((outarr<=-4),1,outarr2)
outarr2=np.where((outarr==-3),2,outarr2)
outarr2=np.where((outarr==-2),2,outarr2)
outarr2=np.where(((outarr>=-1)&(outarr<=5)),3,outarr2)
outarr2=np.where(((outarr>=6)&(outarr<=10)),4,outarr2)
outarr2=np.where((outarr>=11),5,outarr2)
outarr2=np.where((flachmoorarr==1),5,outarr2)
outarr2=np.where((hochmoorarr==1),5,outarr2)
outarr2=np.where((sumpfarr==1),5,outarr2)
outarr2=np.where((auarr==1),5,outarr2)
outarr2=np.where((wasserarr==1),5,outarr2)
outarr2=np.where((maskarr==0),NODATA_value,outarr2)
#plt.imshow(outarr2)
np.min(outarr2)
#write output
convertarrtotif(outarr2, myworkspace+"/"+"bebodenfeuchte5klassen.tif", 1, referenceraster, NODATA_value)
print("done ...")

import os
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from osgeo import osr, gdal
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(2056) #LV95 #(21781) #LV03
gtiff_driver=gdal.GetDriverByName("GTiff")


#input data
myworkspace="E:\Masterarbeit\GIS"
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

#correct ph
#ph=convert_tif_to_array(myworkspace+"/bephcombiarr.tif")
#gadmengrimsel=convert_tif_to_array(myworkspace+"/gadmengrimsel.tif")
#ph=np.where(((gadmengrimsel==1)&(ph>4)),4,ph)
#convertarrtotif(ph, myworkspace+"/"+"bephcombiarr2.tif", 1, referenceraster, NODATA_value)

bachschuttarr=convert_tif_to_array(myworkspace+"/beflozbuffer1_2_15m.tif")
beflozbuffer1_6_30m_arr=convert_tif_to_array(myworkspace+"/sw13.tif")#beflozbuffer1_6_30m_schwemmebene.tif")
buffer20marr=convert_tif_to_array(myworkspace+"/befloz79buffer20m.tif")
#bachschuttarr=convert_tif_to_array(myworkspace+"/beflozbuffer30m.tif")
hochmoorarr=convert_tif_to_array(myworkspace+"/behochmoor_rcp45.tif")
sumpfarr=convert_tif_to_array(myworkspace+"/besumpf_rcp45.tif")
geroellarr=convert_tif_to_array(myworkspace+"/begeroell.tif")
bergsturzarr=convert_tif_to_array(myworkspace+"/bebergsturzgeroell.tif")
auarr=convert_tif_to_array(myworkspace+"/beauen_rcp45.tif")
felsarr=convert_tif_to_array(myworkspace+"/befels.tif")
rutscharr=convert_tif_to_array(myworkspace+"/berutsch.tif")
sturztrajektorienarr=convert_tif_to_array(myworkspace+"/besturztrajektorien.tif")
blockschuttarrarr=convert_tif_to_array(myworkspace+"/beblockschuttneu.tif")
nadelsumpfarr=convert_tif_to_array(myworkspace+"/beSW09_rcp45.tif")#benadelwaeldersumpfflachmooromhmsaosaJURA.tif")
sw14arr=convert_tif_to_array(myworkspace+"/beSW14_rcp45.tif")
begrossflozschwemmgebietarr=convert_tif_to_array(myworkspace+"/befloz7_9schwemmgebiet.tif")
rissmoraenearr=convert_tif_to_array(myworkspace+"/berissmoranenausserhalbLGM.tif")
slopearr=convert_tif_to_array(myworkspace+"/beslopeprz10m.tif")
#wniarr=convert_tif_to_array(myworkspace+"/bewni_rcp45.tif")
slopearr=np.where(slopearr<0.0,0.0,slopearr)
hoehenstufenarr=convert_tif_to_array(myworkspace+"/bevegetationshoehenstufen_rcp45.tif")
regionenarr=convert_tif_to_array(myworkspace+"/beregionen.tif")#beregionenplus.tif)
#behangschutt25przarr=convert_tif_to_array(myworkspace+"/behangschutt25prz.tif")
behangschutt40przarr=convert_tif_to_array(myworkspace+"/behangschutt40prz.tif")
aarmassivarr=convert_tif_to_array(myworkspace+"/aarmassiv.tif")
np.shape(behangschutt40przarr)
np.shape(aarmassivarr)

outarr=np.zeros((nrows, ncols), dtype=int)
#outarr=np.where((wniarr==1),13,outarr)
#11;Rissmoraene
outarr=np.where((rissmoraenearr==1),11,outarr)
#18; Kristallines Gebiet
outarr=np.where((aarmassivarr==1),18,outarr)
#1;Bachschuttwälder (Buffer um FLOZ1,2)
outarr=np.where(((bachschuttarr==1)&(hoehenstufenarr==4)&(slopearr>=0)&(slopearr<=30)),1,outarr)
outarr=np.where(((bachschuttarr==1)&(hoehenstufenarr==5)&(slopearr>=0)&(slopearr<=30)),1,outarr)
outarr=np.where(((bachschuttarr==1)&(hoehenstufenarr==6)&(slopearr>=0)&(slopearr<=30)),1,outarr)
#16 Bachschuttwald innerhalb Rissmoräne (1R) im MIttelland
outarr=np.where(((bachschuttarr==1)&(hoehenstufenarr==4)&(slopearr>=0)&(slopearr<=30)&(regionenarr==2)&(rissmoraenearr==1)),16,outarr)
outarr=np.where(((bachschuttarr==1)&(hoehenstufenarr==5)&(slopearr>=0)&(slopearr<=30)&(regionenarr==2)&(rissmoraenearr==1)),16,outarr)
outarr=np.where(((bachschuttarr==1)&(hoehenstufenarr==6)&(slopearr>=0)&(slopearr<=30)&(regionenarr==2)&(rissmoraenearr==1)),16,outarr)
#17; Bachschuttwald ausserhalb Rissmoräne (1W) im Mittelland
outarr=np.where(((bachschuttarr==1)&(hoehenstufenarr==4)&(slopearr>=0)&(slopearr<=30)&(regionenarr==2)&(rissmoraenearr!=1)),17,outarr)
outarr=np.where(((bachschuttarr==1)&(hoehenstufenarr==5)&(slopearr>=0)&(slopearr<=30)&(regionenarr==2)&(rissmoraenearr!=1)),17,outarr)
outarr=np.where(((bachschuttarr==1)&(hoehenstufenarr==6)&(slopearr>=0)&(slopearr<=30)&(regionenarr==2)&(rissmoraenearr!=1)),17,outarr)
#10;Entlang den groesseren Baechen/Flüssen (FLOZ>6) im SM/UM mit be_gk_ghk_wasser Überflutungsperimeter erstellen und dort 29a und 29ex bei 0-10%
outarr=np.where(((begrossflozschwemmgebietarr==1)&(slopearr>=0)&(slopearr<=10)&(hoehenstufenarr==5)),10,outarr)
outarr=np.where(((begrossflozschwemmgebietarr==1)&(slopearr>=0)&(slopearr<=10)&(hoehenstufenarr==4)),10,outarr)
#2;Bergsturz-Gesellschaften
outarr=np.where((bergsturzarr==1),2,outarr)
#4;Blockschutt
outarr=np.where(((blockschuttarrarr==1)&(slopearr<=50.0)),4,outarr)
#outarr=np.where(((behangschutt25przarr==1)&(regionenarr==3)&(outarr<=0)),4,outarr)
outarr=np.where(((behangschutt40przarr==1)&(regionenarr==3)&(outarr<=0)),4,outarr)
#3;Geroell/Schutt
outarr=np.where(((geroellarr==1)&(sturztrajektorienarr==1)&(aarmassivarr<1)),3,outarr)
outarr=np.where(((geroellarr==1)&(sturztrajektorienarr==1)&(aarmassivarr==1)),19,outarr)
#5;Fels
outarr=np.where((felsarr==1),5,outarr)
#13; Talschuttkegel (flache Lagen innerhalb von Buffer um FLOZ1-6 innerhalb des Überflutungsperimeters)
outarr=np.where(((beflozbuffer1_6_30m_arr==1)&(hoehenstufenarr==4)&(slopearr<=20)),13,outarr)
outarr=np.where(((beflozbuffer1_6_30m_arr==1)&(hoehenstufenarr==5)&(slopearr<=25)),13,outarr)
outarr=np.where(((beflozbuffer1_6_30m_arr==1)&(hoehenstufenarr==6)&(slopearr<=25)),13,outarr)
outarr=np.where(((beflozbuffer1_6_30m_arr==1)&(hoehenstufenarr==7)&(slopearr<=25)),13,outarr)
#9; Nadelwaelder auf sumpfigen Standorten (Sumpf und Flachmoor obermontan, hochmontan, subalpin, obersubalpin)
outarr=np.where(((nadelsumpfarr==1)&(regionenarr==2)),9,outarr)
outarr=np.where(((nadelsumpfarr==1)&(regionenarr==3)),9,outarr)
outarr=np.where(((nadelsumpfarr==1)&(regionenarr==1)),14,outarr)
#14
outarr=np.where((sw14arr==1),14,outarr)
#7;Sumpf-Gesellschaften (submontan, untermontan)
outarr=np.where((sumpfarr==1),7,outarr)
#8;Moor-Gesellschaften
outarr=np.where((hochmoorarr==1),8,outarr)
#6;Auen-Gesellschaften
outarr=np.where((auarr==1),6,outarr)
#12;Bei SW-Auenpolygonen Einheit 43 nur innerhalb Buffer entlang Fluessen von beidseits je 20m zulassen, dort wo gut passt, Rest mit anderem auffüllen.
outarr=np.where(((buffer20marr==1)&(hoehenstufenarr==4)&(auarr==1)),12,outarr)
outarr=np.where(((buffer20marr==1)&(hoehenstufenarr==5)&(auarr==1)),12,outarr)

np.max(outarr)
outarr=np.where((maskarr!=1),NODATA_value,outarr)
#plt.imshow(outarr)
#write output
convertarrtotif(outarr, myworkspace+"/"+"besonderwald_rcp45.tif", 1, referenceraster, NODATA_value)
print("done ...")


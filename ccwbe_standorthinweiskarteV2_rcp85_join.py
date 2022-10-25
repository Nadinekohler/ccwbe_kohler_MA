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
import fiona
import geopandas as gpd
import os
#import shapefile
import shapely
#import pyshp
from osgeo import ogr
#import psycopg2
import sqlalchemy
#import geoalchemy2
from sqlalchemy import create_engine
import xlrd
import openpyxl
from rasterstats import zonal_stats
from numpy.core.multiarray import ndarray
from scipy.interpolate import interp1d
import time
import affine
import rasterio.features
import xarray as xr
import shapely.geometry as sg

# *************************************************************
#environment settings
myworkspace="E:/Masterarbeit/GIS"
referenceraster=myworkspace+"/bedem10m.tif"
codespace="E:/Masterarbeit/Parametertabelle"
#outdir=myworkspace+"/out20220112_mitSturztrajektorien"
outdir=myworkspace+"/Modellergebnisse"
#model parameter file
parameterdf=pd.read_excel(codespace+"/"+"Anhang1_Parameter_Waldstandorte_BE_erweitert_220929.xlsx", dtype="str", engine='openpyxl')
parameterdf.columns

len(parameterdf)
parameterdf.dtypes
parameterdf=parameterdf.astype({"Sonderwald":str})
parameterdf=parameterdf.astype({"joinid":int})
NODATA_value=-9999
cellsize=10.0


#*************************************************************
#functions
#*************************************************************
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
if np.min(dhmarr)<NODATA_value:
    dhmarr=np.where((dhmarr<NODATA_value),NODATA_value,dhmarr)
#NODATA_value=np.min(dhmarr)
#*****************************************************************************************************************
#create a mask array
print("create a mask")
maskarr=convert_tif_to_array(myworkspace+"/bemask.tif")
maskarrbool=np.ones((nrows, ncols), dtype=bool)
#fill the mask array
maskarrbool=np.where(maskarr==1, False, maskarrbool)
#plt.imshow(maskarrbool)

#*****************************************************************************************************************
#create output array
outarr=np.zeros((nrows, ncols), dtype=int)
outarr[:]=NODATA_value
outscorearr=np.zeros((nrows, ncols), dtype=float)


#join parameter table to bestandortstypen Shapefile
bestandortstypengdf=gpd.read_file(outdir+"/"+"bestandortstypen_rcp85.shp")
bestandortstypengdf["region"]=""
bestandortstypengdf.loc[bestandortstypengdf["regionid"]==1,"region"]="Berner Jura"
bestandortstypengdf.loc[bestandortstypengdf["regionid"]==2,"region"]="Mittelland"
bestandortstypengdf.loc[bestandortstypengdf["regionid"]==3,"region"]="Oberland"

bestandortstypengdf.dtypes
bestandortstypengdf.columns
len(bestandortstypengdf)

bestandortstypengdf=bestandortstypengdf[bestandortstypengdf["joinid"]>0][["joinid","geometry","regionid","region"]]
bestandortstypengdf["area"]=bestandortstypengdf["geometry"].area
#bestandortstypengdf=bestandortstypengdf.astype({'joinid': 'int64'})
parameterdf.columns
parameterdf.dtypes
parameterdf=parameterdf.astype({'joinid': 'int64'})
parameterdf.dtypes
parameterdfjoin=parameterdf[["joinid","NrBE","BE","NaiS_LFI_JU","NaiS_LFI_M/A","Anforderungsprofil_NaiS_koll"]] #Nadine: "Anforderungsprofil NaiS" wurde um "-colline Variante" angepasst.
bestandortstypengdfmerge = bestandortstypengdf.merge(parameterdfjoin, on='joinid',how="left")
len(bestandortstypengdfmerge)
bestandortstypengdfmerge.columns
bestandortstypengdfmerge=bestandortstypengdfmerge[(bestandortstypengdfmerge["joinid"]>0)]
bestandortstypengdfmerge["nais"]=""
bestandortstypengdfmerge.loc[(bestandortstypengdfmerge["regionid"]==1),"nais"]=bestandortstypengdfmerge["NaiS_LFI_JU"]
bestandortstypengdfmerge.loc[(bestandortstypengdfmerge["regionid"]==2),"nais"]=bestandortstypengdfmerge["NaiS_LFI_M/A"]
bestandortstypengdfmerge.loc[(bestandortstypengdfmerge["regionid"]==3),"nais"]=bestandortstypengdfmerge["NaiS_LFI_M/A"]
len(bestandortstypengdfmerge)

bestandortstypengdfmerge.to_file(outdir+"/bestandortstypenjoined_rcp85.shp")
print("exported joined  shapefile")


#aggregate areas
bestandortstypengdfmergeclip=gpd.read_file(outdir+"/"+"bestandortstypenjoinedclipwald_rcp85.shp")
bestandortstypengdfmergeJURA=bestandortstypengdfmergeclip[bestandortstypengdfmergeclip["regionid"]==1]
bestandortstypengdfmergeMittelland=bestandortstypengdfmergeclip[bestandortstypengdfmergeclip["regionid"]==2]
bestandortstypengdfmergeAlpen=bestandortstypengdfmergeclip[bestandortstypengdfmergeclip["regionid"]==3]

areastatisticsJura=bestandortstypengdfmergeJURA.groupby(["BE"]).agg({'area': 'sum'})
areastatisticsMittelland=bestandortstypengdfmergeMittelland.groupby(["BE"]).agg({'area': 'sum'})
areastatisticsAlpen=bestandortstypengdfmergeAlpen.groupby(["BE"]).agg({'area': 'sum'})
areastatisticsJura["hektar"]=areastatisticsJura["area"]/10000.0
areastatisticsMittelland["hektar"]=areastatisticsMittelland["area"]/10000.0
areastatisticsAlpen["hektar"]=areastatisticsAlpen["area"]/10000.0

areastatisticsJura["BEeinheit"] = areastatisticsJura.index
areastatisticsMittelland["BEeinheit"] = areastatisticsMittelland.index
areastatisticsAlpen["BEeinheit"] = areastatisticsAlpen.index
#join Haeufigkeit
haeufigkeitdf=pd.read_excel(codespace+"/"+"Haeufigkeit_Schaetzung_def_20220314.xlsx", dtype="str", engine='openpyxl')
haeufigkeitdf=haeufigkeitdf.astype({"Priorisierung Jura":int})
haeufigkeitdf=haeufigkeitdf.astype({"Priorisierung Mittelland":int})
haeufigkeitdf=haeufigkeitdf.astype({"Priorisierung Alpen":int})
haeufigkeitdf.dtypes
joinJura=haeufigkeitdf[["BE","Priorisierung Jura"]].groupby(["BE"]).agg({'Priorisierung Jura': 'max'})
joinJura["BEeinheit"]=joinJura.index
joinML=haeufigkeitdf[["BE","Priorisierung Mittelland"]].groupby(["BE"]).agg({'Priorisierung Mittelland': 'max'})
joinML["BEeinheit"]=joinML.index
joinA=haeufigkeitdf[["BE","Priorisierung Alpen"]].groupby(["BE"]).agg({'Priorisierung Alpen': 'max'})
joinA["BEeinheit"]=joinA.index
areastatisticsJura=areastatisticsJura.merge(joinJura[["BEeinheit","Priorisierung Jura"]], on='BEeinheit',how="left")
areastatisticsMittelland=areastatisticsMittelland.merge(joinML[["BEeinheit","Priorisierung Mittelland"]], on='BEeinheit',how="left")
areastatisticsAlpen=areastatisticsAlpen.merge(joinA[["BEeinheit","Priorisierung Alpen"]], on='BE',how="left")

areastatisticsJura.to_excel(outdir+"/areastatisticsJura_rcp85.xlsx")
areastatisticsMittelland.to_excel(outdir+"/areastatisticsMittelland_rcp85.xlsx")
areastatisticsAlpen.to_excel(outdir+"/areastatisticsAlpen_rcp85.xlsx")


#arrondiertes file
bestandortstypenarrondiertgdf=gpd.read_file(outdir+"/"+"bestandortstypenarrondiert_rcp85.shp")
bestandortstypenarrondiertgdf["region"]=""
bestandortstypenarrondiertgdf.loc[bestandortstypenarrondiertgdf["regionid"]==1,"region"]="Berner Jura"
bestandortstypenarrondiertgdf.loc[bestandortstypenarrondiertgdf["regionid"]==2,"region"]="Mittelland"
bestandortstypenarrondiertgdf.loc[bestandortstypenarrondiertgdf["regionid"]==3,"region"]="Oberland"

bestandortstypenarrondiertgdf.dtypes
#bestandortstypengdf=bestandortstypengdf.astype({'value': 'int64'})
bestandortstypenarrondiertgdf.columns
len(bestandortstypenarrondiertgdf)

bestandortstypenarrondiertgdf=bestandortstypenarrondiertgdf[bestandortstypenarrondiertgdf["joinid"]>0][["joinid","geometry","regionid","region"]]
bestandortstypenarrondiertgdf["area"]=bestandortstypenarrondiertgdf["geometry"].area

bestandortstypenarrondiertgdfmerge = bestandortstypenarrondiertgdf.merge(parameterdfjoin, on='joinid',how="left")
len(bestandortstypenarrondiertgdfmerge)
bestandortstypenarrondiertgdfmerge.columns
bestandortstypenarrondiertgdfmerge=bestandortstypenarrondiertgdfmerge[(bestandortstypenarrondiertgdfmerge["joinid"]>0)]
bestandortstypenarrondiertgdfmerge["nais"]=""
bestandortstypenarrondiertgdfmerge.loc[(bestandortstypenarrondiertgdfmerge["regionid"]==1),"nais"]=bestandortstypenarrondiertgdfmerge["NaiS_LFI_JU"]
bestandortstypenarrondiertgdfmerge.loc[(bestandortstypenarrondiertgdfmerge["regionid"]==2),"nais"]=bestandortstypenarrondiertgdfmerge["NaiS_LFI_M/A"]
bestandortstypenarrondiertgdfmerge.loc[(bestandortstypenarrondiertgdfmerge["regionid"]==3),"nais"]=bestandortstypenarrondiertgdfmerge["NaiS_LFI_M/A"]
len(bestandortstypenarrondiertgdfmerge)

bestandortstypenarrondiertgdfmerge.to_file(outdir+"/bestandortstypenarrondiertjoined_rcp85.shp")
print("exported joined  shapefile")
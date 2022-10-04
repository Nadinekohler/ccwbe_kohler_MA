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
import psycopg2
import sqlalchemy
import geoalchemy2
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
thresholdforminimumtotalscore=0.1#0.4
thresholdforminimumtotalscorearve=0.4
thresholdforminimumtotalscorearvegroesser4ha=0.5
thresholdforminimumtotalscorefoehre=0.75
thresholdforminimumtotalscorefoehregroesser4ha=0.6
cellsize=10.0
listetongehalt=[11,12,22,23,33,34,44]
gewichtunglage=5.0 #Nadine: Gewichtung wegen unterschiedlich guten Datengrundlagen?
gewichtungexposition=5.0
gewichtungfeuchte=2.0
gewichtungneigung=5.0
gewichtunggruendigkeit=3.0
gewichtungph=3.0
gewichtungtg=3.0
#gewichtungsonderwald=5.0
gewichtungarve=5.0
gewichtungbergfoehre=5.0
gewichtungwaldfoehre=5.0


#Formparameter Score Funktionen
x_abweichungexposition = np.array([0.0,10.0,20.0,30.0,360.0])
y_abweichungexposition = np.array([1.0,0.9,0.7,0.1,0.1])
f_delta_z_exposition=interp1d(x_abweichungexposition,y_abweichungexposition, kind="linear")
x_flach=[0,0.15,0.5,0.75,1.0,1.25,1.5,1.75,2.0,5.0]
y_flach=[1.0,1.0,0.5,0.4,0.3,0.25,0.2,0.17,0.15,0.0]
f_flach=interp1d(x_flach, y_flach, kind="linear")
x_flachmittel=[0,0.3,1.0,1.25,1.5,1.75,2.0,5.0]
y_flachmittel=[1.0,1.0,0.5,0.4,0.3,0.25,0.18,0.0]
f_flachmittel=interp1d(x_flachmittel, y_flachmittel, kind="linear")
x_mittel=[0.0,0.3,0.8,1.25,1.75,2.0,5.0]
y_mittel=[0.0,1.0,1.0,0.7,0.5,0.4,0.0]
f_mittel = interp1d(x_mittel, y_mittel, kind="linear")
x_mitteltief=[0.0,0.25,0.8,1.2,1.5,2.0,5.0]
y_mitteltief=[0.0,0.0,1.0,1.0,0.8,0.6,0.0]
f_mitteltief = interp1d(x_mitteltief, y_mitteltief, kind="linear")
x_tief=[0.0,1.15,1.2,5.0]
y_tief=[0.0,0.35,1.0,1.0]
f_tief = interp1d(x_tief, y_tief, kind="linear")
x_exposition=[0.0,10.0,20.0,25.0,180.0]
y_exposition=[1.0,0.9, 0.75,0.1,0.1]
f_scoreexposition = interp1d(x_exposition, y_exposition, kind="linear")
x_neig=[0.0,10.0,20.0,30.0,35.0]
y_neig=[1.0,0.5,0.35,0.25,0.1]
f_scorehangneigung=interp1d(x_neig,y_neig,kind="linear")
x_sehrsauer=[1,2,3,3.8,4,5,6,7,8,9]
y_sehrsauer=[1,1,1,1,0.9,0.6,0.5,0.35,0.3,0.25]
f_sehrsauer=interp1d(x_sehrsauer,y_sehrsauer, kind="linear")
x_sehrsauersauer = [1, 2, 3, 3.8, 4.6, 5, 6, 7, 8, 9]
y_sehrsauersauer = [0.4, 0.5, 0.6, 1.0, 1.0, 0.8, 0.6, 0.5, 0.4, 0.3]
f_sehrsauersauer = interp1d(x_sehrsauersauer, y_sehrsauersauer, kind="linear")
x_sauer = [1, 2, 3, 4, 4.5, 5, 6, 7, 8, 9]
y_sauer = [0.1, 0.2, 0.3, 0.8, 1.0, 1.0, 0.7, 0.55, 0.45, 0.4]
f_sauer = interp1d(x_sauer, y_sauer, kind="linear")
x_sauerneutral = [1, 2, 3, 4, 5, 5.5, 6, 7, 8, 9]
y_sauerneutral = [0.1, 0.1, 0.2, 0.6, 1.0, 1.0, 0.85, 0.65, 0.55, 0.45]
f_sauerneutral = interp1d(x_sauerneutral, y_sauerneutral, kind="linear")
x_neutral = [1, 2, 3, 4, 5, 5.5, 6.2, 7, 8, 9]
y_neutral= [0.1, 0.1, 0.1, 0.45, 0.8, 1.0, 1.0, 0.8, 0.6, 0.5]
f_neutral = interp1d(x_neutral, y_neutral, kind="linear")
x_neutralleichtbasisch = [1, 2, 3, 4, 5, 6.2, 7, 8, 9]
y_neutralleichtbasisch = [0.1, 0.1, 0.1, 0.3, 0.6, 1.0, 1.0, 0.75, 0.7]
f_neutralleichtbasisch = interp1d(x_neutralleichtbasisch, y_neutralleichtbasisch, kind="linear")
x_leichtbasisch = [1, 2, 3, 4, 5, 6, 7, 8, 9]
y_leichtbasisch = [0.1, 0.1, 0.1, 0.35, 0.45, 0.75, 1.0, 1.0, 0.8]
f_leichtbasisch = interp1d(x_leichtbasisch, y_leichtbasisch, kind="linear")
x_basisch = [1, 2, 3, 4, 5, 6, 7, 7.6, 8, 9]
y_basisch = [0.1, 0.1, 0.1, 0.1, 0.3, 0.55, 0.8, 1.0, 1.0, 1.0]
f_basisch = interp1d(x_basisch, y_basisch, kind="linear")
x_bodenfeuchte=[1,2,3,4,5,6,7,8,9]
y_sehrtrocken=[1.0,0.8,0.6,0.5,0.3,0.2,0.1,0.1,0.1]
f_sehrtrocken=interp1d(x_bodenfeuchte,y_sehrtrocken, kind="linear")
y_trocken=[0.7,0.8,1,0.8,0.6,0.3,0.2,0.1,0.1]
f_trocken = interp1d(x_bodenfeuchte, y_trocken, kind="linear")
y_normal=[0.2,0.5,0.6,0.8,1,0.8,0.6,0.5,0.2]
f_normal = interp1d(x_bodenfeuchte, y_normal, kind="linear")
y_feucht=[0.1,0.1,0.2,0.3,0.6,0.8,1,0.8,0.7]
f_feucht = interp1d(x_bodenfeuchte, y_feucht, kind="linear")
y_nass=[0.1,0.1,0.1,0.2,0.3,0.5,0.6,0.8,1]
f_nass = interp1d(x_bodenfeuchte, y_nass, kind="linear")
# *************************************************************


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
def scoreregionhoehenstufe(row):
    scoreregiohoehenstufe = np.zeros((nrows, ncols), dtype=np.float32)
    if row['Ju KO']=='x':
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==2)),1,scoreregiohoehenstufe)
    if row['Ju SM']=='x':
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==4)),1,scoreregiohoehenstufe)
    if row['Ju UM']=='x':
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==5)),1,scoreregiohoehenstufe)
    if row['Ju OM']=='x':
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==6)),1,scoreregiohoehenstufe)
    if row['Ju HM']=='x':
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==8)),1,scoreregiohoehenstufe)
    if row['Ju SA']=='x':
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==9)),1,scoreregiohoehenstufe)
    if row['M/A KO']=='x':
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==2)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 2)), 1, scoreregiohoehenstufe)
    if row['M/A SM']=='x':
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==4)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 4)), 1, scoreregiohoehenstufe)
    if row['M/A UM']=='x':
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==5)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 5)), 1, scoreregiohoehenstufe)
    if row['M/A OM']=='x':
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==6)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 6)), 1, scoreregiohoehenstufe)
    if row['M/A HM']=='x':
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==8)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 8)), 1, scoreregiohoehenstufe)
    if row['M/A SA']=='x':
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==9)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 9)), 1, scoreregiohoehenstufe)
    if row['M/A OSA']=='x':
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==10)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 10)), 1, scoreregiohoehenstufe)
    if row['M/A KO']=='m':
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==2)),1,scoreregiohoehenstufe)
    if row['M/A SM']=='m':
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==4)),1,scoreregiohoehenstufe)
    if row['M/A UM']=='m':
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==5)),1,scoreregiohoehenstufe)
    if row['M/A OM']=='m':
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==6)),1,scoreregiohoehenstufe)
    if row['M/A KO']=='a':
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 2)), 1, scoreregiohoehenstufe)
    if row['M/A SM']=='a':
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 4)), 1, scoreregiohoehenstufe)
    if row['M/A UM']=='a':
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 5)), 1, scoreregiohoehenstufe)
    if row['M/A OM']=='a':
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 6)), 1, scoreregiohoehenstufe)
    return scoreregiohoehenstufe
def scoreregionhoehenstufexy(row):
    scoreregiohoehenstufe = np.zeros((nrows, ncols), dtype=np.float32)
    if row['Ju KO'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==2)),1,scoreregiohoehenstufe)
    if row['Ju SM'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==4)),1,scoreregiohoehenstufe)
    if row['Ju UM'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==5)),1,scoreregiohoehenstufe)
    if row['Ju OM'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==6)),1,scoreregiohoehenstufe)
    if row['Ju HM'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==8)),1,scoreregiohoehenstufe)
    if row['Ju SA'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==9)),1,scoreregiohoehenstufe)
    if row['M/A KO'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==2)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 2)), 1, scoreregiohoehenstufe)
    if row['M/A SM'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==4)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 4)), 1, scoreregiohoehenstufe)
    if row['M/A UM'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==5)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 5)), 1, scoreregiohoehenstufe)
    if row['M/A OM'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==6)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 6)), 1, scoreregiohoehenstufe)
    if row['M/A HM'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==8)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 8)), 1, scoreregiohoehenstufe)
    if row['M/A SA'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==9)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 9)), 1, scoreregiohoehenstufe)
    if row['M/A OSA'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==10)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 10)), 1, scoreregiohoehenstufe)
    return scoreregiohoehenstufe
def scoreregionhoehenstufeamxy(row):
    scoreregiohoehenstufe = np.zeros((nrows, ncols), dtype=np.float32)
    if row['Ju KO'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==2)),1,scoreregiohoehenstufe)
    if row['Ju SM'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==4)),1,scoreregiohoehenstufe)
    if row['Ju UM'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==5)),1,scoreregiohoehenstufe)
    if row['Ju OM'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==6)),1,scoreregiohoehenstufe)
    if row['Ju HM'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==8)),1,scoreregiohoehenstufe)
    if row['Ju SA'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==9)),1,scoreregiohoehenstufe)
    if row['M/A KO']=="x":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==2)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 2)), 1, scoreregiohoehenstufe)
    if row['M/A SM']=="x":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==4)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 4)), 1, scoreregiohoehenstufe)
    if row['M/A UM']=="x":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==5)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 5)), 1, scoreregiohoehenstufe)
    if row['M/A OM']=="x":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==6)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 6)), 1, scoreregiohoehenstufe)
    if row['M/A HM']=="x":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==8)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 8)), 1, scoreregiohoehenstufe)
    if row['M/A SA']=="x":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==9)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 9)), 1, scoreregiohoehenstufe)
    if row['M/A OSA']=="x":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==10)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 10)), 1, scoreregiohoehenstufe)
    if row['M/A KO']=="y":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==2)&(gebueschwaldarr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 2)&(gebueschwaldarr>0)), 1, scoreregiohoehenstufe)
    if row['M/A SM']=="y":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==4)&(gebueschwaldarr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 4)&(gebueschwaldarr>0)), 1, scoreregiohoehenstufe)
    if row['M/A UM']=="y":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==5)&(gebueschwaldarr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 5)&(gebueschwaldarr>0)), 1, scoreregiohoehenstufe)
    if row['M/A OM']=="y":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==6)&(gebueschwaldarr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 6)&(gebueschwaldarr>0)), 1, scoreregiohoehenstufe)
    if row['M/A HM']=="y":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==8)&(gebueschwaldarr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 8)&(gebueschwaldarr>0)), 1, scoreregiohoehenstufe)
    if row['M/A SA']=="y":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==9)&(gebueschwaldarr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 9)&(gebueschwaldarr>0)), 1, scoreregiohoehenstufe)
    if row['M/A OSA']=="y":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==10)&(gebueschwaldarr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 10)&(gebueschwaldarr>0)), 1, scoreregiohoehenstufe)
    if row['M/A KO']=="a":
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 2)), 1, scoreregiohoehenstufe)
    if row['M/A SM']=="a":
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 4)), 1, scoreregiohoehenstufe)
    if row['M/A UM']=="a":
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 5)), 1, scoreregiohoehenstufe)
    if row['M/A OM']=="a":
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 6)), 1, scoreregiohoehenstufe)
    if row['M/A HM']=="a":
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 8)), 1, scoreregiohoehenstufe)
    if row['M/A SA']=="a":
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 9)), 1, scoreregiohoehenstufe)
    if row['M/A OSA']=="a":
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 10)), 1, scoreregiohoehenstufe)
    if row['M/A KO']=="m":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==2)),1,scoreregiohoehenstufe)
    if row['M/A SM']=="m":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==4)),1,scoreregiohoehenstufe)
    if row['M/A UM']=="m":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==5)),1,scoreregiohoehenstufe)
    if row['M/A OM']=="m":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==6)),1,scoreregiohoehenstufe)
    if row['M/A HM']=="m":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==8)),1,scoreregiohoehenstufe)
    if row['M/A SA']=="m":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==9)),1,scoreregiohoehenstufe)
    if row['M/A OSA']=="m":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==10)),1,scoreregiohoehenstufe)
    return scoreregiohoehenstufe
def scoreregionhoehenstufeamxyz(row):
    scoreregiohoehenstufe = np.zeros((nrows, ncols), dtype=np.float32)
    if row['Ju KO'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==2)),1,scoreregiohoehenstufe)
    if row['Ju SM'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==4)),1,scoreregiohoehenstufe)
    if row['Ju UM'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==5)),1,scoreregiohoehenstufe)
    if row['Ju OM'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==6)),1,scoreregiohoehenstufe)
    if row['Ju HM'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==8)),1,scoreregiohoehenstufe)
    if row['Ju SA'] in ["x","y"]:
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==9)),1,scoreregiohoehenstufe)
    if row['Ju KO'] =="z":
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==2)&(arvenfoehrenhektararr>0)),1,scoreregiohoehenstufe)
    if row['Ju SM'] =="z":
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==4)&(arvenfoehrenhektararr>0)),1,scoreregiohoehenstufe)
    if row['Ju UM'] =="z":
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==5)&(arvenfoehrenhektararr>0)),1,scoreregiohoehenstufe)
    if row['Ju OM'] =="z":
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==6)&(arvenfoehrenhektararr>0)),1,scoreregiohoehenstufe)
    if row['Ju HM'] =="z":
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==8)&(arvenfoehrenhektararr>0)),1,scoreregiohoehenstufe)
    if row['Ju SA'] =="z":
        scoreregiohoehenstufe=np.where(((regionenarr==1) & (hoehenstufenarr==9)&(arvenfoehrenhektararr>0)),1,scoreregiohoehenstufe)
    if row['M/A KO'] =="z":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==2)&(arvenfoehrenhektararr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 2) & (arvenfoehrenhektararr > 0)), 1,scoreregiohoehenstufe)
    if row['M/A SM'] =="z":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==4)&(arvenfoehrenhektararr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 4) & (arvenfoehrenhektararr > 0)), 1,scoreregiohoehenstufe)
    if row['M/A UM'] =="z":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==5)&(arvenfoehrenhektararr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 5) & (arvenfoehrenhektararr > 0)), 1,scoreregiohoehenstufe)
    if row['M/A OM'] =="z":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==6)&(arvenfoehrenhektararr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr ==3) & (hoehenstufenarr == 6) & (arvenfoehrenhektararr > 0)), 1,scoreregiohoehenstufe)
    if row['M/A HM'] =="z":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==8)&(arvenfoehrenhektararr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 8) & (arvenfoehrenhektararr > 0)), 1,scoreregiohoehenstufe)
    if row['M/A SA'] =="z":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==9)&(arvenfoehrenhektararr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr ==3) & (hoehenstufenarr == 9) & (arvenfoehrenhektararr > 0)), 1,scoreregiohoehenstufe)
    if row['M/A OSA'] =="z":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==9)&(arvenfoehrenhektararr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr ==3) & (hoehenstufenarr == 9) & (arvenfoehrenhektararr > 0)), 1,scoreregiohoehenstufe)
    if row['M/A KO']=="x":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==2)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 2)), 1, scoreregiohoehenstufe)
    if row['M/A SM']=="x":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==4)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 4)), 1, scoreregiohoehenstufe)
    if row['M/A UM']=="x":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==5)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 5)), 1, scoreregiohoehenstufe)
    if row['M/A OM']=="x":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==6)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 6)), 1, scoreregiohoehenstufe)
    if row['M/A HM']=="x":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==8)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 8)), 1, scoreregiohoehenstufe)
    if row['M/A SA']=="x":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==9)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 9)), 1, scoreregiohoehenstufe)
    if row['M/A OSA']=="x":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==10)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 10)), 1, scoreregiohoehenstufe)
    if row['M/A KO']=="y":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==2)&(gebueschwaldarr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 2)&(gebueschwaldarr>0)), 1, scoreregiohoehenstufe)
    if row['M/A SM']=="y":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==4)&(gebueschwaldarr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 4)&(gebueschwaldarr>0)), 1, scoreregiohoehenstufe)
    if row['M/A UM']=="y":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==5)&(gebueschwaldarr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 5)&(gebueschwaldarr>0)), 1, scoreregiohoehenstufe)
    if row['M/A OM']=="y":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==6)&(gebueschwaldarr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 6)&(gebueschwaldarr>0)), 1, scoreregiohoehenstufe)
    if row['M/A HM']=="y":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==8)&(gebueschwaldarr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 8)&(gebueschwaldarr>0)), 1, scoreregiohoehenstufe)
    if row['M/A SA']=="y":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==9)&(gebueschwaldarr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 9)&(gebueschwaldarr>0)), 1, scoreregiohoehenstufe)
    if row['M/A OSA']=="y":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==10)&(gebueschwaldarr>0)),1,scoreregiohoehenstufe)
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 10)&(gebueschwaldarr>0)), 1, scoreregiohoehenstufe)
    if row['M/A KO']=="a":
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 2)), 1, scoreregiohoehenstufe)
    if row['M/A SM']=="a":
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 4)), 1, scoreregiohoehenstufe)
    if row['M/A UM']=="a":
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 5)), 1, scoreregiohoehenstufe)
    if row['M/A OM']=="a":
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 6)), 1, scoreregiohoehenstufe)
    if row['M/A HM']=="a":
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 8)), 1, scoreregiohoehenstufe)
    if row['M/A SA']=="a":
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 9)), 1, scoreregiohoehenstufe)
    if row['M/A OSA']=="a":
        scoreregiohoehenstufe = np.where(((regionenarr == 3) & (hoehenstufenarr == 10)), 1, scoreregiohoehenstufe)
    if row['M/A KO']=="m":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==2)),1,scoreregiohoehenstufe)
    if row['M/A SM']=="m":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==4)),1,scoreregiohoehenstufe)
    if row['M/A UM']=="m":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==5)),1,scoreregiohoehenstufe)
    if row['M/A OM']=="m":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==6)),1,scoreregiohoehenstufe)
    if row['M/A HM']=="m":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==8)),1,scoreregiohoehenstufe)
    if row['M/A SA']=="m":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==9)),1,scoreregiohoehenstufe)
    if row['M/A OSA']=="m":
        scoreregiohoehenstufe=np.where(((regionenarr==2) & (hoehenstufenarr==10)),1,scoreregiohoehenstufe)
    return scoreregiohoehenstufe
def scorearven(row):
    scorearve = np.zeros((nrows, ncols), dtype=np.float32)
    if row['M/A Arve']=='x':
        scorearve=np.where(((regionenarr==2) & (arvenarr==1)),1.0,scorearve)
        scorearve = np.where(((regionenarr == 3) & (arvenarr == 1)), 1.0, scorearve)
    return scorearve
def scorearvenxy(row):
    scorearve = np.zeros((nrows, ncols), dtype=np.float32)
    if row['M/A Arve'] in ['x','y']:
        scorearve=np.where(((regionenarr==2) & (arvenarr==1)),1.0,scorearve)
        scorearve = np.where(((regionenarr == 3) & (arvenarr == 1)), 1.0, scorearve)
    return scorearve
def scorebergfoehren(row):
    scorebergfoehre = np.zeros((nrows, ncols), dtype=np.float32)
    if row['Ju Bfö']=='x':
        scorebergfoehre=np.where(((regionenarr==1) & (bergfoehrenarr==1)),1.0,scorebergfoehre)
    if row['M/A Bfö'] == 'x':
        scorebergfoehre = np.where(((regionenarr == 2) & (bergfoehrenarr == 1)), 1.0, scorebergfoehre)
        scorebergfoehre = np.where(((regionenarr == 3) & (bergfoehrenarr == 1)), 1.0, scorebergfoehre)
    return scorebergfoehre
def scorebergfoehrenxy(row):
    scorebergfoehre = np.zeros((nrows, ncols), dtype=np.float32)
    if row['Ju Bfö'] in ['x','y']:
        scorebergfoehre=np.where(((regionenarr==1) & (bergfoehrenarr==1)),1.0,scorebergfoehre)
    if row['M/A Bfö'] in ['x','y']:
        scorebergfoehre = np.where(((regionenarr == 2) & (bergfoehrenarr == 1)), 1.0, scorebergfoehre)
        scorebergfoehre = np.where(((regionenarr == 3) & (bergfoehrenarr == 1)), 1.0, scorebergfoehre)
    return scorebergfoehre
def scorewaldfoehren(row):
    scorewaldfoehre = np.zeros((nrows, ncols), dtype=np.float32)
    if row['Ju Wfö']=='x':
        scorewaldfoehre=np.where(((regionenarr==1) & (waldfoehrenarr==1)),1.0,scorewaldfoehre)
    if row['M/A Wfö'] == 'x':
        scorewaldfoehre = np.where(((regionenarr == 2) & (waldfoehrenarr == 1)), 1.0, scorewaldfoehre)
        scorewaldfoehre = np.where(((regionenarr == 3) & (waldfoehrenarr == 1)), 1.0, scorewaldfoehre)
    return scorewaldfoehre
def scorewaldfoehrenxy(row):
    scorewaldfoehre = np.zeros((nrows, ncols), dtype=np.float32)
    if row['Ju Wfö'] in ['x','y']:
        scorewaldfoehre=np.where(((regionenarr==1) & (waldfoehrenarr==1)),1.0,scorewaldfoehre)
    if row['M/A Wfö'] in ['x','y']:
        scorewaldfoehre = np.where(((regionenarr == 2) & (waldfoehrenarr == 1)), 1.0, scorewaldfoehre)
        scorewaldfoehre = np.where(((regionenarr == 3) & (waldfoehrenarr == 1)), 1.0, scorewaldfoehre)
    return scorewaldfoehre
def scorehangneigungbe(neigung_von,neigung_bis,neigunguntenscharf,neigungobenscharf):
    scorehangneigungarr = np.zeros((nrows, ncols), dtype=np.float32)
    scorehangneigungarr[:]=0.1
    if neigunguntenscharf!="x" and neigungobenscharf!="x":
        abweichungarr = np.where(((slopearr >= neigung_von) & (slopearr <= neigung_bis) & (slopearr >= 0)), 0.0, 35.0)
        abweichungarr = np.where(((slopearr < neigung_von) & (slopearr > (neigung_von-35.0)) & (slopearr >= 0)), abs(neigung_von-slopearr), abweichungarr)
        abweichungarr = np.where(((slopearr > neigung_bis) & (slopearr < (neigung_bis +35.0)) & (slopearr >= 0)),abs(neigung_bis-slopearr), abweichungarr)
        abweichungarr = np.where((slopearr >= (neigung_bis+35.0)), 35.0, abweichungarr)
        abweichungarr = np.where(((slopearr >= neigung_von) & (slopearr <= neigung_bis) & (slopearr >= 0)), 0.0, abweichungarr)
        abweichungarr = np.where(((abweichungarr > 35.0)), 35.0,abweichungarr)
    elif neigunguntenscharf == "x" and neigungobenscharf == "x":
        abweichungarr = np.where(((slopearr >= neigung_von) & (slopearr <= neigung_bis) & (slopearr >= 0)), 0.0, 35.0)
    elif neigunguntenscharf == "x" and neigungobenscharf != "x":
        abweichungarr = np.where(((slopearr >= neigung_von) & (slopearr <= neigung_bis) & (slopearr >= 0)), 0.0, 35.0)
        abweichungarr = np.where(((slopearr > neigung_bis) & (slopearr < (neigung_bis + 35.0)) & (slopearr >= 0)),abs(neigung_bis - slopearr), abweichungarr)
        abweichungarr = np.where(((slopearr < neigung_von) & (slopearr >= 0)),35.0, abweichungarr)
        abweichungarr = np.where(((slopearr >= neigung_von) & (slopearr <= neigung_bis) & (slopearr >= 0)), 0.0,abweichungarr)
        abweichungarr = np.where(((abweichungarr > 35.0)), 35.0, abweichungarr)
    elif neigunguntenscharf != "x" and neigungobenscharf == "x":
        abweichungarr = np.where(((slopearr >= neigung_von) & (slopearr <= neigung_bis) & (slopearr >= 0)), 0.0, 35.0)
        abweichungarr = np.where(((slopearr < neigung_von) & (slopearr > (neigung_von - 35.0)) & (slopearr >= 0)),abs(neigung_von - slopearr), abweichungarr)
        abweichungarr = np.where(((slopearr > neigung_bis) & (slopearr >= 0)), 35.0, abweichungarr)
        abweichungarr = np.where(((slopearr >= neigung_von) & (slopearr <= neigung_bis) & (slopearr >= 0)), 0.0,abweichungarr)
        abweichungarr = np.where(((abweichungarr > 35.0)), 35.0, abweichungarr)
    scorehangneigungarr = np.where((slopearr >= 0), f_scorehangneigung(abweichungarr),scorehangneigungarr)
    return scorehangneigungarr
def scorelagebe(lagein, lagescharfin):
    lagescorearr=np.zeros((nrows, ncols),dtype=np.float32)
    lagescorearr[:]=0.1
    lagelist=[]
    for lage in str(lagein).strip().split():
        lagelist.append(int(lage))
    if lagescharfin=="x":
        for item in [1,2,3,4]:
            if item in lagelist:
                lagescorearr=np.where((lagearr==int(item)),1.0,lagescorearr)
    else:
        for item in [1, 2, 3, 4]:
            if item in lagelist:
                lagescorearr = np.where((lagearr == int(item)), 1.0, lagescorearr)
            else:
                lagescorearr = np.where((lagearr == int(item)), 0.5, lagescorearr)
    return lagescorearr
def scoregruendigkeitbe(gruendigkeit, gruendigkeitscharf):
    scoregruendigkeitarr = np.zeros((nrows, ncols), dtype=np.float32)
    scoregruendigkeitarr[:] = 0.1
    gruendigkeitlist = []
    for g in str(gruendigkeit).strip().split():
        gruendigkeitlist.append(int(g))
    if gruendigkeitscharf=="x":
        for item in gruendigkeitlist:
            scoregruendigkeitarr = np.where((gruendigkeitarr == int(item)), 1.0, scoregruendigkeitarr)
    else:
        for item in [1,2,3,4,5]:
            if item in gruendigkeitlist:
                scoregruendigkeitarr = np.where((gruendigkeitarr == int(item)), 1.0, scoregruendigkeitarr)
            else:
                scoregruendigkeitarr = np.where((gruendigkeitarr == int(item)), 0.5, scoregruendigkeitarr)
    return scoregruendigkeitarr
def scoreexpositionbe(exp_von, exp_bis, expositionscharf):
    scoreexpositionarr = np.zeros((nrows, ncols), dtype=np.float32)
    scoreexpositionarr[:]=0.1
    if expositionscharf=="x":
        # Nordsektor
        if exp_von >= exp_bis:
            scoreexpositionarr = np.where((expositionarr >= exp_von), 1.0, scoreexpositionarr)
            scoreexpositionarr = np.where(((expositionarr >= 0) & (expositionarr <= exp_bis)), 1.0, scoreexpositionarr)
        # Suedsektor
        elif exp_von <= exp_bis:
            scoreexpositionarr = np.where(((expositionarr >= exp_von) & (expositionarr <= exp_bis)), 1.0,scoreexpositionarr)
    else:
        #Nordsektor
        if exp_von >= exp_bis:
            abweichungarr = abs(exp_von - expositionarr)
            abweichungarr = np.where(abweichungarr > 25.0, 25.0, abweichungarr)
            abweichungarr = np.where(abweichungarr < 0.0, 0.0, abweichungarr)
            scoreexpositionarr = np.where((expositionarr >= exp_von-25.0), f_scoreexposition(abweichungarr), scoreexpositionarr)
            scoreexpositionarr=np.where((expositionarr>=exp_von),1.0,scoreexpositionarr)
            scoreexpositionarr = np.where(((expositionarr >= 0)&(expositionarr>=exp_bis + 25.0)),f_scoreexposition(abweichungarr), scoreexpositionarr)
            scoreexpositionarr = np.where(((expositionarr >= 0)&(expositionarr <= exp_bis)), 1.0, scoreexpositionarr)
        #Suedsektor
        elif exp_von <= exp_bis:
            abweichungarr = abs(exp_von - expositionarr)
            abweichungarr = np.where(abweichungarr > 25.0, 25.0, abweichungarr)
            abweichungarr = np.where(abweichungarr < 0.0, 0.0, abweichungarr)
            scoreexpositionarr = np.where(((expositionarr >= 0) & (expositionarr >= exp_von - 25.0)),f_scoreexposition(abweichungarr), scoreexpositionarr)
            abweichungarr = abs(exp_bis - expositionarr)
            abweichungarr = np.where(abweichungarr > 25.0, 25.0, abweichungarr)
            abweichungarr = np.where(abweichungarr < 0.0, 0.0, abweichungarr)
            scoreexpositionarr = np.where(((expositionarr <= 360.0) & (expositionarr >= exp_bis + 25.0)),f_scoreexposition(abweichungarr), scoreexpositionarr)
            scoreexpositionarr = np.where(((expositionarr >= exp_von) & (expositionarr <= exp_bis)),1.0, scoreexpositionarr)
    return scoreexpositionarr
def scorefeuchtebe(feuchte, feuchtescharf):
    scorefeuchtearr = np.zeros((nrows, ncols), dtype=np.float32)
    scorefeuchtearr[:] = 0.1
    feuchtelist = str(feuchte).strip().split()
    if feuchtescharf=="x":
        for item in feuchtelist:
            scorefeuchtearr = np.where((feuchtearr == int(item)), 1.0, scorefeuchtearr)
    else:
        for item in ["1","2","3","4","5"]:
            if item in feuchtelist:
                scorefeuchtearr = np.where((feuchtearr == int(item)), 1.0, scorefeuchtearr)
            else:
                scorefeuchtearr = np.where((feuchtearr == int(item)), 0.5, scorefeuchtearr)
    return scorefeuchtearr
def scorephbe(ph,phscharf):
    scorepharr = np.zeros((nrows, ncols), dtype=np.float32)
    scorepharr[:] = 0.1
    if ph in ["indiff","9",9]:
        scorepharr = np.where((phcombiarr > 0), 1.0, scorepharr)
    else:
        phanspruch=ph.replace(" ","").replace("bis"," ")
        minph=int(phanspruch.strip().split()[0])
        maxph = int(phanspruch.strip().split()[-1])
        phlist = np.arange(minph, maxph+1,1).tolist()
        if phscharf=="x":
            for item in phlist:
                scorepharr = np.where((phcombiarr == int(item)), 1.0, scorepharr)
        else:
            for item in [1,2,3,4,5,6,7,8]:
                if item in phlist:
                    scorepharr = np.where((phcombiarr == int(item)), 1.0, scorepharr)
                else:
                    scorepharr = np.where((phcombiarr == int(item)), 0.5, scorepharr)
    return scorepharr
def scoretgbe(row):
    scoretgarr = np.zeros((nrows, ncols), dtype=np.float32)
    scoretgarr[:] = 0.1
    #if regionenarr in [1,2]:
    tganspruchJUM=row["TongehaltJuraMittelland"].replace(" ","").replace("bis"," ")
    tganspruchO = row["TongehaltOberland"].replace(" ", "").replace("bis", " ")
    mintgJUM=int(tganspruchJUM.strip().split()[0])
    maxtgJUM = int(tganspruchJUM.strip().split()[-1])
    tglistJUM = np.arange(mintgJUM, maxtgJUM+1,1).tolist()
    mintgO = int(tganspruchO.strip().split()[0])
    maxtgO = int(tganspruchO.strip().split()[-1])
    tglistO = np.arange(mintgO, maxtgO + 1, 1).tolist()
    for item in tglistJUM:
        if item in listetongehalt:
            scoretgarr = np.where(((regionenarr==1)&(tgarr == int(item))), 1.0, scoretgarr)
            scoretgarr = np.where(((regionenarr == 2) & (tgarr == int(item))), 1.0, scoretgarr)
    for item in tglistO:
        if item in listetongehalt:
            scoretgarr = np.where(((regionenarr==3)&(tgarr == int(item))), 1.0, scoretgarr)
    return scoretgarr
def scoresonderwaldbe(sonderwaldin):
    sonderwaldscorearr=np.zeros((nrows, ncols),dtype=np.float32)
    sonderwaldscorearr[:]=0.0
    sonderwaldlist=str(sonderwaldin).replace("*","").strip().split()
    for item in sonderwaldlist:
        sonderwaldscorearr=np.where((sonderwaldarr==int(item)),1.0,sonderwaldscorearr)
    return sonderwaldscorearr
def polygonize(da: xr.DataArray) -> gpd.GeoDataFrame:
    """
    Polygonize a 2D-DataArray into a GeoDataFrame of polygons.

    Parameters
    ----------
    da : xr.DataArray

    Returns
    -------
    polygonized : geopandas.GeoDataFrame
    """
    if da.dims != ("y", "x"):
        raise ValueError('Dimensions must be ("y", "x")')

    values = da.values
    transform = da.attrs.get("transform", None)
    if transform is None:
        raise ValueError("transform is required in da.attrs")
    transform = affine.Affine(*transform)
    shapes = rasterio.features.shapes(values, transform=transform)

    geometries = []
    colvalues = []
    for (geom, colval) in shapes:
        geometries.append(sg.Polygon(geom["coordinates"][0]))
        colvalues.append(colval)

    gdf = gpd.GeoDataFrame({"value": colvalues, "geometry": geometries})
    gdf.crs = da.attrs.get("crs")
    return gdf
# *************************************************************
#end functions
# *************************************************************

#test
#testarr=scorehangneigungbe(70, 80, "","")
#plt.imshow(testarr)
#convertarrtotif((testarr*100).astype(int), outdir + "/" + "testarr.tif", indatatypeint, referenceraster, NODATA_value)
#plt.imshow(testarr)
#testarr=scorelagebe(1,"")
#convertarrtotif((testarr*100).astype(int), outdir + "/" + "testarr.tif", indatatypeint, referenceraster, NODATA_value)
#testarr=scoresonderwaldbe(1,"")
#convertarrtotif((testarr*100).astype(int), outdir + "/" + "testarr.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif((f_scorehangneigung(abweichungarr)*100).astype(int), outdir + "/" + "testscorearr.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif((abweichungarr).astype(int), outdir + "/" + "testabwarr.tif", indatatypeint, referenceraster, NODATA_value)

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
print("read rasters")
#sonderwaldarr=convert_tif_to_array(myworkspace+"/besonderwald.tif")
sonderwaldarr=convert_tif_to_array(myworkspace+"/besonderwald_rcp45.tif")
#felsarr=convert_tif_to_array(myworkspace+"/befels.tif")
lagearr=convert_tif_to_array(myworkspace+"/belage.tif")
#pharr=convert_tif_to_array(myworkspace+"/bebodenreaktionverfeinert.tif")
#phkoboarr=convert_tif_to_array(myworkspace+"/bephkoboclass.tif")
expositionarr=convert_tif_to_array(myworkspace+"/beaspect.tif")
slopearr=convert_tif_to_array(myworkspace+"/beslopeprz10m.tif")
slopearr=np.where(slopearr<0.0,0.0,slopearr)
gruendigkeitarr=convert_tif_to_array(myworkspace+"/bebodengruendigkeitklassifiziert.tif")
feuchtearr=convert_tif_to_array(myworkspace+"/bebodenfeuchte5klassen.tif")
gebueschwaldarr=convert_tif_to_array(myworkspace+"/beshrubforest.tif")
regionenarr=convert_tif_to_array(myworkspace+"/beregionenplus.tif")
hoehenstufenarr=convert_tif_to_array(myworkspace+"/bevegetationshoehenstufen_rcp45.tif")
tgarr=convert_tif_to_array(myworkspace+"/betg.tif")
phcombiarr=convert_tif_to_array(myworkspace+"/bephcombiarr2.tif")
wasserarr=convert_tif_to_array(myworkspace+"/bewasser.tif")
arvenarr=convert_tif_to_array(myworkspace+"/bearven.tif")
np.max(arvenarr)
arvenarr=np.where((arvenarr==3),NODATA_value,arvenarr)
bergfoehrenarr=convert_tif_to_array(myworkspace+"/bebergfoehren.tif")
bergfoehrenarr=np.where((bergfoehrenarr==3),NODATA_value,bergfoehrenarr)
waldfoehrenarr=convert_tif_to_array(myworkspace+"/bewaldfoehren.tif")
waldfoehrenarr=np.where((waldfoehrenarr==3),NODATA_value,waldfoehrenarr)
wniarr=convert_tif_to_array(myworkspace+"/bewni.tif")
np.max(wniarr)
waldarr=convert_tif_to_array(myworkspace+"/bewaldbuffer20mgebueschwald.tif")
arvenfoehrenhektararr=convert_tif_to_array(myworkspace+"/bearvenfoehrenhektar.tif") #Nadine: braucht es diesen Datensatz für Zukunft?
arvenfoehrenhektararr=np.where((arvenfoehrenhektararr==65535),0,arvenfoehrenhektararr)
np.max(arvenfoehrenhektararr)
#loesche Gebueschwald in OM #Nadine: bleibt das so in der Zukunft?
np.max(gebueschwaldarr)
gebueschwaldarr=np.where(((gebueschwaldarr==1)&(hoehenstufenarr==6)),np.min(gebueschwaldarr),gebueschwaldarr)
gebueschwaldarr=np.where(((gebueschwaldarr==2)&(hoehenstufenarr==6)),np.min(gebueschwaldarr),gebueschwaldarr)
aarmassivarr=convert_tif_to_array(myworkspace+"/aarmassiv.tif")
#convertarrtotif(gebueschwaldarr, myworkspace+"/"+"beschrubforest_ohneOM.tif", indatatypeint, referenceraster, NODATA_value)
#phcombiarr=np.where(regionenarr==2,phkoboarr,pharr)
#phcombiarr=np.where((phcombiarr==0),pharr,phcombiarr)
#phcombiarr=np.where((phcombiarr<0),pharr,phcombiarr)
#phcombiarr=np.where((maskarr!=1),NODATA_value,phcombiarr)
#phcombiarr=np.where((wasserarr==1),NODATA_value,phcombiarr)
#convertarrtotif(phcombiarr, myworkspace+"/"+"bephcombiarr.tif", indatatypeint, referenceraster, NODATA_value)
#plt.imshow(phcombiarr)
#del pharr
#del phkoboarr
#*****************************************************************************************************************
#create output array
outarr=np.zeros((nrows, ncols), dtype=int)
outarr[:]=NODATA_value
outscorearr=np.zeros((nrows, ncols), dtype=float)

# ***********
#iteration through parameter table Uebrige Flaechen
print("Uebrige Flaechen")
parameterdf.columns
len(parameterdf)
parameterdfuebrige=parameterdf[((parameterdf["Sonderwald"].astype(str).str.contains("0")))]
parameterdfuebrige=parameterdfuebrige[((~parameterdfuebrige["Sonderwald"].astype(str).str.contains("10")))]
#parameterdfuebrige=parameterdfuebrige[((~parameterdfuebrige["Ju Bfö"].isin(["x","y","m","a","z"])))]
#parameterdfuebrige=parameterdfuebrige[((~parameterdfuebrige["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdfuebrige=parameterdfuebrige[((~parameterdfuebrige["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdfuebrige=parameterdfuebrige[((~parameterdfuebrige["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdfuebrige=parameterdfuebrige[((~parameterdfuebrige["M/A Wfö"].isin(["x","y","m","a","z"])))]
#parameterdfuebrige=parameterdfuebrige[((~parameterdfuebrige["Fels"].isin(["x","s"])))]
parameterdfuebrige=parameterdfuebrige[((~parameterdfuebrige["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
#parameterdfuebrige=parameterdfuebrige[(~parameterdfuebrige["Subregionen"].isin(['WNI']))]
len(parameterdfuebrige)
gewichtunguebrige=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfuebrige.iterrows():
    #print(row["joinid"])
    #WNI Flaechen
    if row["Subregionen"]=="WNI":
        scorewniarr = np.where((wniarr == 1), 1.0, 0.0)
        scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
        scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
        scoregruendigkeitarr = scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
        scoreneigungarr = scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
        scoreexpositionarr = scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
        scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
        scorepharr = scorephbe(row["pH"], row["pH scharf"])
        scoretgarr = scoretgbe(row)
        uebrigetotalscorearr = scorewniarr*scoreregionhoehenstufearr * (gewichtunglage * scorelagearr + gewichtunggruendigkeit * scoregruendigkeitarr + gewichtungneigung * scoreneigungarr + gewichtungexposition * scoreexpositionarr + gewichtungfeuchte * scorefeuchtearr + gewichtungph * scorepharr + gewichtungtg * scoretgarr) / gewichtunguebrige
        outarr = np.where((uebrigetotalscorearr > outscorearr), int(row["joinid"]), outarr)
        outscorearr = np.where((uebrigetotalscorearr > outscorearr), uebrigetotalscorearr, outscorearr)
    else:
        scoreregionhoehenstufearr=scoreregionhoehenstufeamxy(row)
        scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
        scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
        scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
        scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
        scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
        scorepharr = scorephbe(row["pH"], row["pH scharf"])
        scoretgarr = scoretgbe(row)
        #scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
        #scoresonderwaldarr = np.where((sonderwaldarr==0),1.0,0.0)
        uebrigetotalscorearr=scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtunguebrige
        outarr=np.where((uebrigetotalscorearr>outscorearr),int(row["joinid"]),outarr)
        outscorearr=np.where((uebrigetotalscorearr>outscorearr),uebrigetotalscorearr,outscorearr)
outarr=np.where((wasserarr==1),NODATA_value,outarr)
outscorearr=np.where((wasserarr==1),NODATA_value,outscorearr)
outarr=np.where((maskarr!=1),NODATA_value,outarr)
outscorearr=np.where((maskarr!=1),NODATA_value,outscorearr)
#convertarrtotif((outscorearr*100).astype(int), outdir + "/" + "uebrigetotalscorearr.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarr, outdir + "/" + "uebrigeoutarr.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarr,outdir+"/uebrigeoutarr.sav")
#joblib.dump(outscorearr,outdir+"/uebrigeoutscorearr.sav")
del uebrigetotalscorearr
#outarr=joblib.load(outdir+"/uebrigeoutarr.sav")
#outscorearr=joblib.load(outdir+"/uebrigeoutscorearr.sav")

# ***********
#Fels
print("Fels")
outarrfels=np.zeros((nrows, ncols), dtype=int)
outarrfels[:]=NODATA_value
outscorearrfels=np.zeros((nrows, ncols), dtype=float)
parameterdffels=parameterdf[((parameterdf["Fels"].isin(["x","s"]))| (parameterdf["Sonderwald"].astype(str).str.contains("5")))]
parameterdffels=parameterdffels[((~parameterdffels["Sonderwald"].astype(str).str.contains("15")))]
parameterdffels=parameterdffels[((~parameterdffels["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdffels=parameterdffels[((~parameterdffels["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdffels=parameterdffels[((~parameterdffels["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdffels=parameterdffels[((~parameterdffels["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdffels=parameterdffels[((~parameterdffels["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdffels=parameterdffels[((~parameterdffels["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
parameterdffels=parameterdffels[(~parameterdffels["Subregionen"].isin(['WNI']))]
len(parameterdffels)
gewichtungfels=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdffels.iterrows():
    #print(row["joinid"])
    if row["Fels"]=="x":
        scorefelsarr=np.where(((sonderwaldarr==5)&(aarmassivarr<1)),1.0,0.0)
    elif row["Fels"]=="s":
        scorefelsarr=np.where(((sonderwaldarr==5)&(aarmassivarr<1)),0.5,0.0)
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    #scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
    felstotalscorearr=scorefelsarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungfels
    outarrfels = np.where(((felstotalscorearr > thresholdforminimumtotalscore)&(sonderwaldarr==5)&(aarmassivarr<1)&(felstotalscorearr>=outscorearrfels)), int(row["joinid"]), outarrfels)
    outscorearrfels = np.where(((felstotalscorearr > thresholdforminimumtotalscore)&(sonderwaldarr==5)&(aarmassivarr<1)&(felstotalscorearr>=outscorearrfels)), felstotalscorearr, outscorearrfels)
outarrfels=np.where((wasserarr==1),NODATA_value,outarrfels)
outscorearrfels=np.where((wasserarr==1),NODATA_value,outscorearrfels)
outarrfels=np.where((maskarr!=1),NODATA_value,outarrfels)
outscorearrfels=np.where((maskarr!=1),NODATA_value,outscorearrfels)
outarrfels=np.where((sonderwaldarr!=5),NODATA_value,outarrfels)
outscorearrfels=np.where((sonderwaldarr!=5),NODATA_value,outscorearrfels)
#convertarrtotif(outarrfels, outdir + "/" + "outarrfels.tif", indatatypeint, referenceraster,NODATA_value)
#convertarrtotif((outscorearrfels*100).astype(int), outdir + "/" + "outscorearrfels.tif", indatatypeint, referenceraster, NODATA_value)
#joblib.dump(outarrfels,outdir+"/outarrfels.sav")
#joblib.dump(outscorearrfels,outdir+"/outscorearrfels.sav")
del scorefelsarr
del felstotalscorearr
#outarrfels=joblib.load(outdir+"/outarrfels.sav")
#outscorearrfels=joblib.load(outdir+"/outscorearrfels.sav")

print("Fels kristallin")
outarrfelskristallin=np.zeros((nrows, ncols), dtype=int)
outarrfelskristallin[:]=NODATA_value
outscorearrfelskristallin=np.zeros((nrows, ncols), dtype=float)
parameterdffelskristallin=parameterdf[((parameterdf["FelsKristallin"].isin(["x","s"]))| (parameterdf["Sonderwald"].astype(str).str.contains("5")))]
parameterdffelskristallin=parameterdffelskristallin[((~parameterdffelskristallin["Sonderwald"].astype(str).str.contains("15")))]
parameterdffelskristallin=parameterdffelskristallin[((~parameterdffelskristallin["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdffelskristallin=parameterdffelskristallin[((~parameterdffelskristallin["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdffelskristallin=parameterdffelskristallin[((~parameterdffelskristallin["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdffelskristallin=parameterdffelskristallin[((~parameterdffelskristallin["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdffelskristallin=parameterdffelskristallin[((~parameterdffelskristallin["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdffelskristallin=parameterdffelskristallin[((~parameterdffelskristallin["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
parameterdffelskristallin=parameterdffelskristallin[(~parameterdffelskristallin["Subregionen"].isin(['WNI']))]
len(parameterdffelskristallin)
gewichtungfels=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdffelskristallin.iterrows():
    #print(row["joinid"])
    if row["FelsKristallin"]=="x":
        scorefelsarr=np.where(((sonderwaldarr==5)&(aarmassivarr==1)),1.0,0.0)
    elif row["FelsKristallin"]=="s":
        scorefelsarr=np.where(((sonderwaldarr==5)&(aarmassivarr==1)),0.5,0.0)
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    #scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
    felstotalscorearr=scorefelsarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungfels
    outarrfelskristallin = np.where(((felstotalscorearr > thresholdforminimumtotalscore)&(sonderwaldarr==5)&(aarmassivarr==1)&(felstotalscorearr>=outscorearrfelskristallin)), int(row["joinid"]), outarrfelskristallin)
    outscorearrfelskristallin = np.where(((felstotalscorearr > thresholdforminimumtotalscore)&(sonderwaldarr==5)&(aarmassivarr==1)&(felstotalscorearr>=outscorearrfelskristallin)), felstotalscorearr, outscorearrfelskristallin)
outarrfelskristallin=np.where((wasserarr==1),NODATA_value,outarrfelskristallin)
outscorearrfelskristallin=np.where((wasserarr==1),NODATA_value,outscorearrfelskristallin)
outarrfelskristallin=np.where((maskarr!=1),NODATA_value,outarrfelskristallin)
outscorearrfelskristallin=np.where((maskarr!=1),NODATA_value,outscorearrfelskristallin)
outarrfelskristallin=np.where(((sonderwaldarr!=5)&(aarmassivarr==1)),NODATA_value,outarrfelskristallin)
outscorearrfelskristallin=np.where(((sonderwaldarr!=5)&(aarmassivarr==1)),NODATA_value,outscorearrfelskristallin)
#convertarrtotif(outarrfels, outdir + "/" + "outarrfels.tif", indatatypeint, referenceraster,NODATA_value)
#convertarrtotif((outscorearrfels*100).astype(int), outdir + "/" + "outscorearrfels.tif", indatatypeint, referenceraster, NODATA_value)
#joblib.dump(outarrfels,outdir+"/outarrfels.sav")
#joblib.dump(outscorearrfels,outdir+"/outscorearrfels.sav")
del scorefelsarr
del felstotalscorearr
#outarrfels=joblib.load(outdir+"/outarrfels.sav")
#outscorearrfels=joblib.load(outdir+"/outscorearrfels.sav")


# ***********
#iteration through parameter Arve, Waldfoehre, Bergfoehre
#Arve
print("Arve")
outarrarve=np.zeros((nrows, ncols), dtype=int)
outarrarve[:]=NODATA_value
outscorearrarve=np.zeros((nrows, ncols), dtype=float)
parameterdfarven=parameterdf[(parameterdf["M/A Arve"].isin(["x","y"]))]
len(parameterdfarven)
gewichtungsumarve=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfarven.iterrows():
    #print(row["joinid"])
    scorearvearr=scorearvenxy(row)
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxyz(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    #scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
    arvetotalscorearr=scorearvearr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumarve
    outarrarve = np.where(((arvetotalscorearr > thresholdforminimumtotalscore)&(arvenarr==1)&(arvetotalscorearr>=outscorearrarve)), int(row["joinid"]), outarrarve)
    outscorearrarve = np.where(((arvetotalscorearr > thresholdforminimumtotalscore)&(arvenarr==1)&(arvetotalscorearr>=outscorearrarve)), arvetotalscorearr,outscorearrarve)
outarrarve=np.where((wasserarr==1),NODATA_value,outarrarve)
outscorearrarve=np.where((wasserarr==1),NODATA_value,outscorearrarve)
outarrarve=np.where((maskarr!=1),NODATA_value,outarrarve)
outscorearrarve=np.where((maskarr!=1),NODATA_value,outscorearrarve)
outarrarve=np.where((arvenarr!=1),NODATA_value,outarrarve)
outscorearrarve=np.where((arvenarr!=1),NODATA_value,outscorearrarve)
#convertarrtotif((outscorearrarve*100.0).astype(int), outdir + "/" + "outscorearrarve.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarrarve, outdir + "/" + "outarrarve.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarrarve,outdir+"/outarrarve.sav")
#joblib.dump(outscorearrarve,outdir+"/outscorearrarve.sav")
del arvetotalscorearr
del scorearvearr
#outarrarve=joblib.load(outdir+"/outarrarve.sav")
#outscorearrarve=joblib.load(outdir+"/outscorearrarve.sav")



#Bergfoehre
print("Bergfoehre")
outarrbf=np.zeros((nrows, ncols), dtype=int)
outarrbf[:]=NODATA_value
outscorearrbf=np.zeros((nrows, ncols), dtype=float)
parameterdfbergfoehre=parameterdf[((parameterdf["M/A Bfö"].isin(["x","y","a","m"]))| (parameterdf["Ju Bfö"].isin(["x","y"])))]
len(parameterdfbergfoehre)
gewichtungsumbergfoehre=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfbergfoehre.iterrows():
    #print(row["joinid"])
    scorebergfoehrearr=scorebergfoehrenxy(row)
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxyz(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    #scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
    bergfoehretotalscorearr=scorebergfoehrearr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumbergfoehre
    outarrbf = np.where(((bergfoehretotalscorearr > thresholdforminimumtotalscore)&(bergfoehrenarr==1)&(bergfoehretotalscorearr>=outscorearrbf)), int(row["joinid"]), outarrbf)
    outscorearrbf = np.where(((bergfoehretotalscorearr > thresholdforminimumtotalscore)&(bergfoehrenarr==1)&(bergfoehretotalscorearr>=outscorearrbf)), bergfoehretotalscorearr,outscorearrbf)
outarrbf=np.where((wasserarr==1),NODATA_value,outarrbf)
outscorearrbf=np.where((wasserarr==1),NODATA_value,outscorearrbf)
outarrbf=np.where((maskarr!=1),NODATA_value,outarrbf)
outscorearrbf=np.where((maskarr!=1),NODATA_value,outscorearrbf)
outarrbf=np.where((bergfoehrenarr!=1),NODATA_value,outarrbf)
outscorearrbf=np.where((bergfoehrenarr!=1),NODATA_value,outscorearrbf)
#convertarrtotif(outarrbf, outdir + "/" + "outarrbf.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif((outscorearrbf*100).astype(int), outdir + "/" + "outscorearrbf.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarrbf,outdir+"/outarrbf.sav")
#joblib.dump(outscorearrbf,outdir+"/outscorearrbf.sav")
#outarrbf=joblib.load(outdir+"/outarrbf.sav")
#outscorearrbf=joblib.load(outdir+"/outscorearrbf.sav")

#Waldfoehre
print("Waldfoehre")
outarrwf=np.zeros((nrows, ncols), dtype=int)
outarrwf[:]=NODATA_value
outscorearrwf=np.zeros((nrows, ncols), dtype=float)
parameterdfwaldfoehre=parameterdf[((parameterdf["M/A Wfö"].isin(["x","y"])) | (parameterdf["Ju Wfö"].isin(["x","y"])))]
len(parameterdfwaldfoehre)
gewichtungsumwaldfoehre=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfwaldfoehre.iterrows():
    #print(row["joinid"])
    scorewaldfoehrearr=scorewaldfoehrenxy(row)
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxyz(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    #scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
    waldfoehretotalscorearr=scorewaldfoehrearr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumwaldfoehre
    outarrwf = np.where(((waldfoehretotalscorearr > thresholdforminimumtotalscore)&(waldfoehrenarr==1)&(waldfoehretotalscorearr>=outscorearrwf)), int(row["joinid"]), outarrwf)
    outscorearrwf = np.where(((waldfoehretotalscorearr > thresholdforminimumtotalscore)&(waldfoehrenarr==1)&(waldfoehretotalscorearr>=outscorearrwf)), waldfoehretotalscorearr, outscorearrwf)
outarrwf=np.where((wasserarr==1),NODATA_value,outarrwf)
outscorearrwf=np.where((wasserarr==1),NODATA_value,outscorearrwf)
outarrwf=np.where((maskarrbool==True),NODATA_value,outarrwf)
outscorearrwf=np.where((maskarrbool==True),NODATA_value,outscorearrwf)
outarrwf=np.where((waldfoehrenarr!=1),NODATA_value,outarrwf)
outscorearrwf=np.where((waldfoehrenarr!=1),NODATA_value,outscorearrwf)
#convertarrtotif((outscorearrwf*100).astype(int), outdir + "/" + "outscorearrwf.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarrwf, outdir + "/" + "outarrwf.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarrwf,outdir+"/outarrwf.sav")
#joblib.dump(outscorearrwf,outdir+"/outscorearrwf.sav")
#outarrwf=joblib.load(outdir+"/outarrwf.sav")
#outscorearrwf=joblib.load(outdir+"/outscorearrwf.sav")

# ***********
#Sonderwald
print("Sonderwald")
print("6 Auen")
outarrau=np.zeros((nrows, ncols), dtype=int)
outarrau[:]=NODATA_value
outscorearrau=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("6"))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Sonderwald"].astype(str).str.contains("16")))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
parameterdfsonderwald=parameterdfsonderwald[(~parameterdfsonderwald["Subregionen"].isin(['WNI']))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==6),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoresonderwaldarr = np.where((sonderwaldarr == 12), 1.0, scoresonderwaldarr)
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrau=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==6)& (sonderwaldtotalscorearr >= outscorearrau)),int(row["joinid"]),outarrau)
    outscorearrau=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==6)& (sonderwaldtotalscorearr >= outscorearrau)),sonderwaldtotalscorearr,outscorearrau)
    outarrau = np.where(((sonderwaldtotalscorearr > thresholdforminimumtotalscore) & (sonderwaldarr == 12) & (sonderwaldtotalscorearr >= outscorearrau)), int(row["joinid"]), outarrau)
    outscorearrau = np.where(((sonderwaldtotalscorearr > thresholdforminimumtotalscore) & (sonderwaldarr == 12) & (sonderwaldtotalscorearr >= outscorearrau)), sonderwaldtotalscorearr, outscorearrau)
outarrau=np.where((wasserarr==1),NODATA_value,outarrau)
outscorearrau=np.where((wasserarr==1),NODATA_value,outscorearrau)
outarrau=np.where((maskarr!=1),NODATA_value,outarrau)
outscorearrau=np.where((maskarr!=1),NODATA_value,outscorearrau)
outarrau=np.where(((sonderwaldarr==6)|(sonderwaldarr==12)),outarrau,NODATA_value)
outscorearrau=np.where(((sonderwaldarr==6)|(sonderwaldarr==12)),outarrau,NODATA_value)
#convertarrtotif((outscorearrau*100).astype(int), outdir + "/" + "outscorearrau.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarrau, outdir + "/" + "outarrau.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarrau,outdir+"/outarrau.sav")
#joblib.dump(outscorearrau,outdir+"/outscorearrau.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr
#outarrau=joblib.load(outdir+"/outarrau.sav")
#outscorearrau=joblib.load(outdir+"/outscorearrau.sav")

print("2 Bergsturz")
outarrbs=np.zeros((nrows, ncols), dtype=int)
outarrbs[:]=NODATA_value
outscorearrbs=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("2"))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Sonderwald"].astype(str).str.contains("12")))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
parameterdfsonderwald=parameterdfsonderwald[(~parameterdfsonderwald["Subregionen"].isin(['WNI']))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==2),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrbs=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==2)& (sonderwaldtotalscorearr >= outscorearrbs)),int(row["joinid"]),outarrbs)
    outscorearrbs=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==2)& (sonderwaldtotalscorearr >= outscorearrbs)),sonderwaldtotalscorearr,outscorearrbs)
outarrbs=np.where((wasserarr==1),NODATA_value,outarrbs)
outscorearrbs=np.where((wasserarr==1),NODATA_value,outscorearrbs)
outarrbs=np.where((maskarr!=1),NODATA_value,outarrbs)
outscorearrbs=np.where((maskarr!=1),NODATA_value,outscorearrbs)
outarrbs=np.where((sonderwaldarr!=2),NODATA_value,outarrbs)
outscorearrbs=np.where((sonderwaldarr!=2),NODATA_value,outscorearrbs)
#convertarrtotif((outscorearrbs*100).astype(int), outdir + "/" + "outscorearrbergsturz.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarrbs, outdir + "/" + "outarrbergsturz.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarrbs,outdir+"/outarrbs.sav")
#joblib.dump(outscorearrbs,outdir+"/outscorearrbs.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr
#outarrbs=joblib.load(outdir+"/outarrbs.sav")
#outscorearrbs=joblib.load(outdir+"/outscorearrbs.sav")


print("3 Geroell/Schutt")
outarrgeroell=np.zeros((nrows, ncols), dtype=int)
outarrgeroell[:]=NODATA_value
outscorearrgeroell=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("3"))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Sonderwald"].astype(str).str.contains("13")))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
parameterdfsonderwald=parameterdfsonderwald[(~parameterdfsonderwald["Subregionen"].isin(['WNI']))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==3),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrgeroell=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==3)& (sonderwaldtotalscorearr >= outscorearrgeroell)),int(row["joinid"]),outarrgeroell)
    outscorearrgeroell=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==3)& (sonderwaldtotalscorearr >= outscorearrgeroell)),sonderwaldtotalscorearr,outscorearrgeroell)
outarrgeroell=np.where((wasserarr==1),NODATA_value,outarrgeroell)
outscorearrgeroell=np.where((wasserarr==1),NODATA_value,outscorearrgeroell)
outarrgeroell=np.where((maskarr!=1),NODATA_value,outarrgeroell)
outscorearrgeroell=np.where((maskarr!=1),NODATA_value,outscorearrgeroell)
outarrgeroell=np.where((sonderwaldarr!=3),NODATA_value,outarrgeroell)
outscorearrgeroell=np.where((sonderwaldarr!=3),NODATA_value,outscorearrgeroell)
#convertarrtotif((outscorearrgeroell*100).astype(int), outdir + "/" + "outscorearrgeroell.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarrgeroell, outdir + "/" + "outarrgeroell.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarrgeroell,outdir+"/outarrgeroell.sav")
#joblib.dump(outscorearrgeroell,outdir+"/outscorearrgeroell.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr
#outarrgeroell=joblib.load(outdir+"/outarrgeroell.sav")
#outscorearrgeroell=joblib.load(outdir+"/outscorearrgeroell.sav")

print("3 Geroell/Schutt im Kristallin")
outarrgeroellkristallin=np.zeros((nrows, ncols), dtype=int)
outarrgeroellkristallin[:]=NODATA_value
outscorearrgeroellkristallin=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("19"))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
parameterdfsonderwald=parameterdfsonderwald[(~parameterdfsonderwald["Subregionen"].isin(['WNI']))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==19),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrgeroellkristallin=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==3)& (sonderwaldtotalscorearr >= outscorearrgeroellkristallin)),int(row["joinid"]),outarrgeroell)
    outscorearrgeroellkristallin=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==3)& (sonderwaldtotalscorearr >= outscorearrgeroellkristallin)),sonderwaldtotalscorearr,outscorearrgeroell)
outarrgeroellkristallin=np.where((wasserarr==1),NODATA_value,outarrgeroellkristallin)
outscorearrgeroellkristallin=np.where((wasserarr==1),NODATA_value,outscorearrgeroellkristallin)
outarrgeroellkristallin=np.where((maskarr!=1),NODATA_value,outarrgeroellkristallin)
outscorearrgeroellkristallin=np.where((maskarr!=1),NODATA_value,outscorearrgeroellkristallin)
outarrgeroellkristallin=np.where((sonderwaldarr!=3),NODATA_value,outarrgeroellkristallin)
outscorearrgeroellkristallin=np.where((sonderwaldarr!=3),NODATA_value,outscorearrgeroellkristallin)
del sonderwaldtotalscorearr
del scoresonderwaldarr


print("4 Blockschutt")
outarrblockschutt=np.zeros((nrows, ncols), dtype=int)
outarrblockschutt[:]=NODATA_value
outscorearrblockschutt=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("4"))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Sonderwald"].astype(str).str.contains("14")))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
parameterdfsonderwald=parameterdfsonderwald[(~parameterdfsonderwald["Subregionen"].isin(['WNI']))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==4),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrblockschutt=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==4)& (sonderwaldtotalscorearr >= outscorearrblockschutt)),int(row["joinid"]),outarrblockschutt)
    outscorearrblockschutt=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==4)& (sonderwaldtotalscorearr >= outscorearrblockschutt)),sonderwaldtotalscorearr,outscorearrblockschutt)
outarrblockschutt=np.where((wasserarr==1),NODATA_value,outarrblockschutt)
outscorearrblockschutt=np.where((wasserarr==1),NODATA_value,outscorearrblockschutt)
outarrblockschutt=np.where((maskarr!=1),NODATA_value,outarrblockschutt)
outscorearrblockschutt=np.where((maskarr!=1),NODATA_value,outscorearrblockschutt)
outarrblockschutt=np.where((sonderwaldarr!=4),NODATA_value,outarrblockschutt)
outscorearrblockschutt=np.where((sonderwaldarr!=4),NODATA_value,outscorearrblockschutt)
#convertarrtotif((outscorearrblockschutt*100).astype(int), outdir + "/" + "outscorearrblockschutt.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarrblockschutt, outdir + "/" + "outarrblockschutt.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarrblockschutt,outdir+"/outarrblockschutt.sav")
#joblib.dump(outscorearrblockschutt,outdir+"/outscorearrblockschutt.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr
#outarrblockschutt=joblib.load(outdir+"/outarrblockschutt.sav")
#outscorearrblockschutt=joblib.load(outdir+"/outscorearrblockschutt.sav")


print("7 Sumpf")
outarrsumpf=np.zeros((nrows, ncols), dtype=int)
outarrsumpf[:]=NODATA_value
outscorearrsumpf=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("7"))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Sonderwald"].astype(str).str.contains("17")))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
parameterdfsonderwald=parameterdfsonderwald[(~parameterdfsonderwald["Subregionen"].isin(['WNI']))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==7),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrsumpf=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==7)& (sonderwaldtotalscorearr >= outscorearrsumpf)),int(row["joinid"]),outarrsumpf)
    outscorearrsumpf=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==7)& (sonderwaldtotalscorearr >= outscorearrsumpf)),sonderwaldtotalscorearr,outscorearrsumpf)
outarrsumpf=np.where((wasserarr==1),NODATA_value,outarrsumpf)
outscorearrsumpf=np.where((wasserarr==1),NODATA_value,outscorearrsumpf)
outarrsumpf=np.where((maskarr!=1),NODATA_value,outarrsumpf)
outscorearrsumpf=np.where((maskarr!=1),NODATA_value,outscorearrsumpf)
outarrsumpf=np.where((sonderwaldarr!=7),NODATA_value,outarrsumpf)
outscorearrsumpf=np.where((sonderwaldarr!=7),NODATA_value,outscorearrsumpf)
#convertarrtotif((outscorearrsumpf*100).astype(int), outdir + "/" + "outscorearrsumpf.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarrsumpf, outdir + "/" + "outarrsumpf.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarrsumpf,outdir+"/outarrsumpf.sav")
#joblib.dump(outscorearrsumpf,outdir+"/outscorearrsumpf.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr
#outarrsumpf=joblib.load(outdir+"/outarrsumpf.sav")
#outscorearrsumpf=joblib.load(outdir+"/outscorearrsumpf.sav")


print("8 Moor")
outarrmoor=np.zeros((nrows, ncols), dtype=int)
outarrmoor[:]=NODATA_value
outscorearrmoor=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("8"))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
parameterdfsonderwald=parameterdfsonderwald[(~parameterdfsonderwald["Subregionen"].isin(['WNI']))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==8),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrmoor=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==8)& (sonderwaldtotalscorearr >= outscorearrmoor)),int(row["joinid"]),outarrmoor)
    outscorearrmoor=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==8)& (sonderwaldtotalscorearr >= outscorearrmoor)),sonderwaldtotalscorearr,outscorearrmoor)
outarrmoor=np.where((wasserarr==1),NODATA_value,outarrmoor)
outscorearrmoor=np.where((wasserarr==1),NODATA_value,outscorearrmoor)
outarrmoor=np.where((maskarr!=1),NODATA_value,outarrmoor)
outscorearrmoor=np.where((maskarr!=1),NODATA_value,outscorearrmoor)
outarrmoor=np.where((sonderwaldarr!=8),NODATA_value,outarrmoor)
outscorearrmoor=np.where((sonderwaldarr!=8),NODATA_value,outscorearrmoor)
#convertarrtotif((outscorearrmoor*100).astype(int), outdir + "/" + "outscorearrmoor.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarrmoor, outdir + "/" + "outarrmoor.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarrmoor,outdir+"/outarrmoor.sav")
#joblib.dump(outscorearrmoor,outdir+"/outscorearrmoor.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr

print("9 Nadelwaelder auf sumpfigen Standorten")
outarrnadelsumpf=np.zeros((nrows, ncols), dtype=int)
outarrnadelsumpf[:]=NODATA_value
outscorearrnadelsumpf=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("9"))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Sonderwald"].astype(str).str.contains("19")))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Sonderwald"].astype(str).str.contains("12")))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
parameterdfsonderwald=parameterdfsonderwald[(~parameterdfsonderwald["Subregionen"].isin(['WNI']))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==9),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrnadelsumpf=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==9)& (sonderwaldtotalscorearr >= outscorearrnadelsumpf)),int(row["joinid"]),outarrnadelsumpf)
    outscorearrnadelsumpf=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==9)& (sonderwaldtotalscorearr >= outscorearrnadelsumpf)),sonderwaldtotalscorearr,outscorearrnadelsumpf)
outarrnadelsumpf=np.where((wasserarr==1),NODATA_value,outarrnadelsumpf)
outscorearrnadelsumpf=np.where((wasserarr==1),NODATA_value,outscorearrnadelsumpf)
outarrnadelsumpf=np.where((maskarr!=1),NODATA_value,outarrnadelsumpf)
outscorearrnadelsumpf=np.where((maskarr!=1),NODATA_value,outscorearrnadelsumpf)
outarrnadelsumpf=np.where((sonderwaldarr!=9),NODATA_value,outarrnadelsumpf)
outscorearrnadelsumpf=np.where((sonderwaldarr!=9),NODATA_value,outscorearrnadelsumpf)
#convertarrtotif((outscorearrnadelsumpf*100).astype(int), outdir + "/" + "outscorearrnadelsumpf.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarrnadelsumpf, outdir + "/" + "outarrnadelsumpf.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarrnadelsumpf,outdir+"/outarrnadelsumpf.sav")
#joblib.dump(outscorearrnadelsumpf,outdir+"/outscorearrnadelsumpf.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr

print("10 Ueberschwemmbare Flaechen")
outarrflussbuffer=np.zeros((nrows, ncols), dtype=int)
outarrflussbuffer[:]=NODATA_value
outscorearrflussbuffer=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("10"))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
parameterdfsonderwald=parameterdfsonderwald[(~parameterdfsonderwald["Subregionen"].isin(['WNI']))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==10),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrflussbuffer=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==10)& (sonderwaldtotalscorearr >= outscorearrflussbuffer)),int(row["joinid"]),outarrflussbuffer)
    outscorearrflussbuffer=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==10)& (sonderwaldtotalscorearr >= outscorearrflussbuffer)),sonderwaldtotalscorearr,outscorearrflussbuffer)
outarrflussbuffer=np.where((wasserarr==1),NODATA_value,outarrflussbuffer)
outscorearrflussbuffer=np.where((wasserarr==1),NODATA_value,outscorearrflussbuffer)
outarrflussbuffer=np.where((maskarr!=1),NODATA_value,outarrflussbuffer)
outscorearrflussbuffer=np.where((maskarr!=1),NODATA_value,outscorearrflussbuffer)
outarrflussbuffer=np.where((sonderwaldarr!=10),NODATA_value,outarrflussbuffer)
outscorearrflussbuffer=np.where((sonderwaldarr!=10),NODATA_value,outscorearrflussbuffer)
#convertarrtotif((outscorearrflussbuffer*100).astype(int), outdir + "/" + "outscorearrflussbuffer.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarrflussbuffer, outdir + "/" + "outarrflussbuffer.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarrflussbuffer,outdir+"/outarrflussbuffer.sav")
#joblib.dump(outscorearrflussbuffer,outdir+"/outscorearrflussbuffer.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr

#Sonderwald 11 Rissmoraene
print("11 Riss Moraene")
outarrrissmoraene=np.zeros((nrows, ncols), dtype=int)
outarrrissmoraene[:]=NODATA_value
outscorearrrissmoraene=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("11"))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==11),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrrissmoraene=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==11)& (sonderwaldtotalscorearr >= outscorearrrissmoraene)),int(row["joinid"]),outarrrissmoraene)
    outscorearrrissmoraene=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==11)& (sonderwaldtotalscorearr >= outscorearrrissmoraene)),sonderwaldtotalscorearr,outscorearrrissmoraene)
outarrrissmoraene=np.where((wasserarr==1),NODATA_value,outarrrissmoraene)
outscorearrrissmoraene=np.where((wasserarr==1),NODATA_value,outscorearrrissmoraene)
outarrrissmoraene=np.where((maskarr!=1),NODATA_value,outarrrissmoraene)
outscorearrrissmoraene=np.where((maskarr!=1),NODATA_value,outscorearrrissmoraene)
outarrrissmoraene=np.where((sonderwaldarr!=11),NODATA_value,outarrrissmoraene)
outscorearrrissmoraene=np.where((sonderwaldarr!=11),NODATA_value,outscorearrrissmoraene)
#convertarrtotif((outscorearrrissmoraene*100).astype(int), outdir + "/" + "outscorearrrissmoraene.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarrrissmoraene, outdir + "/" + "outarrrissmoraene.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarrrissmoraene,outdir+"/outarrrissmoraene.sav")
#joblib.dump(outscorearrrissmoraene,outdir+"/outscorearrrissmoraene.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr

#Sonderwald 15 Mittelland ausserhalb Rissmoraene
print("15 ausserhalb Riss Moraene")
outarr15=np.zeros((nrows, ncols), dtype=int)
outarr15[:]=NODATA_value
outscorearr15=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("15"))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where(((sonderwaldarr==0)&(regionenarr==2)),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarr15=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==0)&(regionenarr==2)& (sonderwaldtotalscorearr >= outscorearr15)),int(row["joinid"]),outarr15)
    outscorearr15=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==0)&(regionenarr==2)& (sonderwaldtotalscorearr >= outscorearr15)),sonderwaldtotalscorearr,outscorearr15)
outarr15=np.where((wasserarr==1),NODATA_value,outarr15)
outscorearr15=np.where((wasserarr==1),NODATA_value,outscorearr15)
outarr15=np.where((maskarr!=1),NODATA_value,outarr15)
outscorearr15=np.where((maskarr!=1),NODATA_value,outscorearr15)
outarr15=np.where(((sonderwaldarr==0)&(regionenarr==2)),outarr15, NODATA_value)
outscorearr15=np.where(((sonderwaldarr==0)&(regionenarr==2)),outscorearr15,NODATA_value)
#convertarrtotif((outscorearr15*100).astype(int), outdir + "/" + "outscorearr15.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarr15, outdir + "/" + "outarr15.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarr15,outdir+"/outarr15.sav")
#joblib.dump(outscorearr15,outdir+"/outscorearr15.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr


#Sonderwald 16-Bachschuttwald innerhalb Rissmoraene (1R) im Mittelland
print("16 Bachschuttwald innerhalb Rissmoraene (1R) im Mittelland")
outarr16=np.zeros((nrows, ncols), dtype=int)
outarr16[:]=NODATA_value
outscorearr16=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("16"))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==16),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarr16=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==16)& (sonderwaldtotalscorearr >= outscorearr16)),int(row["joinid"]),outarr16)
    outscorearr16=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==16)& (sonderwaldtotalscorearr >= outscorearr16)),sonderwaldtotalscorearr,outscorearr16)
outarr16=np.where((wasserarr==1),NODATA_value,outarr16)
outscorearr16=np.where((wasserarr==1),NODATA_value,outscorearr16)
outarr16=np.where((maskarr!=1),NODATA_value,outarr16)
outscorearr16=np.where((maskarr!=1),NODATA_value,outscorearr16)
outarr16=np.where((sonderwaldarr!=16),NODATA_value,outarr16)
outscorearr16=np.where((sonderwaldarr!=16),NODATA_value,outscorearr16)
#convertarrtotif((outscorearr16*100).astype(int), outdir + "/" + "outscorearr16.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarr16, outdir + "/" + "outarr16.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarr16,outdir+"/outarr16.sav")
#joblib.dump(outscorearr16,outdir+"/outscorearr16.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr


#Sonderwald 17-Bachschuttwald innerhalb Rissmoraene (1R) im Mittelland
print("17 Bachschuttwald ausserhalb Rissmoraene (1W) im Mittelland")
outarr17=np.zeros((nrows, ncols), dtype=int)
outarr17[:]=NODATA_value
outscorearr17=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("17"))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==17),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarr17=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==17)& (sonderwaldtotalscorearr >= outscorearr17)),int(row["joinid"]),outarr17)
    outscorearr17=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==17)& (sonderwaldtotalscorearr >= outscorearr17)),sonderwaldtotalscorearr,outscorearr17)
outarr17=np.where((wasserarr==1),NODATA_value,outarr17)
outscorearr17=np.where((wasserarr==1),NODATA_value,outscorearr17)
outarr17=np.where((maskarr!=1),NODATA_value,outarr17)
outscorearr17=np.where((maskarr!=1),NODATA_value,outscorearr17)
outarr17=np.where((sonderwaldarr!=17),NODATA_value,outarr17)
outscorearr17=np.where((sonderwaldarr!=17),NODATA_value,outscorearr17)
#convertarrtotif((outscorearr17*100).astype(int), outdir + "/" + "outscorearr17.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarr17, outdir + "/" + "outarr17.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarr17,outdir+"/outarr17.sav")
#joblib.dump(outscorearr17,outdir+"/outscorearr17.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr



#Sonderwald 12 Aktive Au
print("12 Aktive Au")
outarraktiveau=np.zeros((nrows, ncols), dtype=int)
outarraktiveau[:]=NODATA_value
outscorearraktiveau=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("12"))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
parameterdfsonderwald=parameterdfsonderwald[(~parameterdfsonderwald["Subregionen"].isin(['WNI']))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==12),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarraktiveau=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==12)& (sonderwaldtotalscorearr >= outscorearraktiveau)),int(row["joinid"]),outarraktiveau)
    outscorearraktiveau=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==12)& (sonderwaldtotalscorearr >= outscorearraktiveau)),sonderwaldtotalscorearr,outscorearraktiveau)
outarraktiveau=np.where((wasserarr==1),NODATA_value,outarraktiveau)
outscorearraktiveau=np.where((wasserarr==1),NODATA_value,outscorearraktiveau)
outarraktiveau=np.where((maskarr!=1),NODATA_value,outarraktiveau)
outscorearraktiveau=np.where((maskarr!=1),NODATA_value,outscorearraktiveau)
outarraktiveau=np.where((sonderwaldarr!=12),NODATA_value,outarraktiveau)
outscorearraktiveau=np.where((sonderwaldarr!=12),NODATA_value,outscorearraktiveau)
#convertarrtotif((outscorearraktiveau*100).astype(int), outdir + "/" + "outscorearraktiveau.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarraktiveau, outdir + "/" + "outarraktiveau.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarraktiveau,outdir+"/outarraktiveau.sav")
#joblib.dump(outscorearraktiveau,outdir+"/outscorearraktiveau.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr

#Sonderwald 1 Bachschutt
print("1 Bachschutt")
outarrbachschutt=np.zeros((nrows, ncols), dtype=int)
outarrbachschutt[:]=NODATA_value
outscorearrbachschutt=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[((parameterdf["Sonderwald"].astype(str).str.contains("1"))&~(parameterdf["Sonderwald"].astype(str).str.contains("10"))&~(parameterdf["Sonderwald"].astype(str).str.contains("11"))&~(parameterdf["Sonderwald"].astype(str).str.contains("12"))&~(parameterdf["Sonderwald"].astype(str).str.contains("13"))&~(parameterdf["Sonderwald"].astype(str).str.contains("14"))&~(parameterdf["Sonderwald"].astype(str).str.contains("19")))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
parameterdfsonderwald=parameterdfsonderwald[(~parameterdfsonderwald["Subregionen"].isin(['WNI']))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==1),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrbachschutt=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==1)& (sonderwaldtotalscorearr >= outscorearrbachschutt)),int(row["joinid"]),outarrbachschutt)
    outscorearrbachschutt=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==1)& (sonderwaldtotalscorearr >= outscorearrbachschutt)),sonderwaldtotalscorearr,outscorearrbachschutt)
outarrbachschutt=np.where((wasserarr==1),NODATA_value,outarrbachschutt)
outscorearrbachschutt=np.where((wasserarr==1),NODATA_value,outscorearrbachschutt)
outarrbachschutt=np.where((maskarr!=1),NODATA_value,outarrbachschutt)
outscorearrbachschutt=np.where((maskarr!=1),NODATA_value,outscorearrbachschutt)
outarrbachschutt=np.where((sonderwaldarr!=1),NODATA_value,outarrbachschutt)
outscorearrbachschutt=np.where((sonderwaldarr!=1),NODATA_value,outscorearrbachschutt)
#convertarrtotif((outscorearrbachschutt*100).astype(int), outdir + "/" + "outscorearrbachschutt.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarrbachschutt, outdir + "/" + "outarrbachschutt.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarrbachschutt,outdir+"/outarrbachschutt.sav")
#joblib.dump(outscorearrbachschutt,outdir+"/outscorearrbachschutt.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr

#Sonderwald 13 Talschuttkegel
print("13 Talschuttkegel")
outarrtalschuttkegel=np.zeros((nrows, ncols), dtype=int)
outarrtalschuttkegel[:]=NODATA_value
outscorearrtalschuttkegel=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("13"))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
parameterdfsonderwald=parameterdfsonderwald[(~parameterdfsonderwald["Subregionen"].isin(['WNI']))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==13),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrtalschuttkegel=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==13)& (sonderwaldtotalscorearr >= outscorearrtalschuttkegel)),int(row["joinid"]),outarrtalschuttkegel)
    outscorearrtalschuttkegel=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==13)& (sonderwaldtotalscorearr >= outscorearrtalschuttkegel)),sonderwaldtotalscorearr,outscorearrtalschuttkegel)
outarrtalschuttkegel=np.where((wasserarr==1),NODATA_value,outarrtalschuttkegel)
outscorearrtalschuttkegel=np.where((wasserarr==1),NODATA_value,outscorearrtalschuttkegel)
outarrtalschuttkegel=np.where((maskarr!=1),NODATA_value,outarrtalschuttkegel)
outscorearrtalschuttkegel=np.where((maskarr!=1),NODATA_value,outscorearrtalschuttkegel)
outarrtalschuttkegel=np.where((sonderwaldarr!=13),NODATA_value,outarrtalschuttkegel)
outscorearrtalschuttkegel=np.where((sonderwaldarr!=13),NODATA_value,outscorearrtalschuttkegel)
#convertarrtotif((outscorearrtalschuttkegel*100).astype(int), outdir + "/" + "outscorearrtalschuttkegel.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarrtalschuttkegel, outdir + "/" + "outarrtalschuttkegel.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarrtalschuttkegel,outdir+"/outarrtalschuttkegel.sav")
#joblib.dump(outscorearrtalschuttkegel,outdir+"/outscorearrtalschuttkegel.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr

#Sonderwald 14
print("14")
outarr14=np.zeros((nrows, ncols), dtype=int)
outarr14[:]=NODATA_value
outscorearr14=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("14"))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdfsonderwald=parameterdfsonderwald[((~parameterdfsonderwald["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
parameterdfsonderwald=parameterdfsonderwald[(~parameterdfsonderwald["Subregionen"].isin(['WNI']))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    #print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==14),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarr14=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==14)& (sonderwaldtotalscorearr >= outscorearr14)),int(row["joinid"]),outarr14)
    outscorearr14=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==14)& (sonderwaldtotalscorearr >= outscorearr14)),sonderwaldtotalscorearr,outscorearr14)
outarr14=np.where((wasserarr==1),NODATA_value,outarr14)
outscorearr14=np.where((wasserarr==1),NODATA_value,outscorearr14)
outarr14=np.where((maskarr!=1),NODATA_value,outarr14)
outscorearr14=np.where((maskarr!=1),NODATA_value,outscorearr14)
outarr14=np.where((sonderwaldarr!=14),NODATA_value,outarr14)
outscorearr14=np.where((sonderwaldarr!=14),NODATA_value,outscorearr14)
#convertarrtotif((outscorearr14*100).astype(int), outdir + "/" + "outscorearr14.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarr14, outdir + "/" + "outarr14.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarr14,outdir+"/outarr14.sav")
#joblib.dump(outscorearr14,outdir+"/outscorearr14.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr




# ***********
#iteration through parameter table Gebueschwald
print("Gebueschwald")
outarrgebuesch=np.zeros((nrows, ncols), dtype=int)
outarrgebuesch[:]=NODATA_value
outscorearrgebuesch=np.zeros((nrows, ncols), dtype=float)
parameterdfgebueschwald=parameterdf[parameterdf["Gebüschwald"]=="LF"]
parameterdfgebueschwald=parameterdfgebueschwald[((~parameterdfgebueschwald["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdfgebueschwald=parameterdfgebueschwald[((~parameterdfgebueschwald["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdfgebueschwald=parameterdfgebueschwald[((~parameterdfgebueschwald["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdfgebueschwald=parameterdfgebueschwald[((~parameterdfgebueschwald["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdfgebueschwald=parameterdfgebueschwald[((~parameterdfgebueschwald["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdfgebueschwald=parameterdfgebueschwald[(~parameterdfgebueschwald["Subregionen"].isin(['WNI']))]
len(parameterdfgebueschwald)
gewichtungsumgebueschwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfgebueschwald.iterrows():
    #print(row["joinid"])
    scoreregionhoehenstufearr=scoreregionhoehenstufeamxy(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    #scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
    scoregebueschwald=np.where((gebueschwaldarr==2),1.0,0.0)
    gebueschwaldtotalscorearr=scoreregionhoehenstufearr*scoregebueschwald*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumgebueschwald
    outarrgebuesch=np.where(((gebueschwaldtotalscorearr>thresholdforminimumtotalscore)&(gebueschwaldarr==2)&(gebueschwaldtotalscorearr>outscorearrgebuesch)),int(row["joinid"]),outarrgebuesch)
    outscorearrgebuesch=np.where(((gebueschwaldtotalscorearr>thresholdforminimumtotalscore)&(gebueschwaldarr==2)&(gebueschwaldtotalscorearr>outscorearrgebuesch)),gebueschwaldtotalscorearr,outscorearrgebuesch)

#MoorLF in Gebueschwald
outarrmoorgebuesch=np.zeros((nrows, ncols), dtype=int)
outarrmoorgebuesch[:]=NODATA_value
outscorearrmoorgebuesch=np.zeros((nrows, ncols), dtype=float)
parameterdfmoorgebueschwald=parameterdf[parameterdf["Gebüschwald"]=="MoorLF"]
len(parameterdfmoorgebueschwald)
gewichtungsummoorgebueschwald=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfmoorgebueschwald.iterrows():
    #print(row["joinid"])
    scoreregionhoehenstufearr=scoreregionhoehenstufeamxy(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    #scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
    scoremoorgebueschwald=np.where(((gebueschwaldarr==2)&(sonderwaldarr==8)),1.0,0.0)
    moorgebueschwaldtotalscorearr=scoreregionhoehenstufearr*scoremoorgebueschwald*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsummoorgebueschwald
    outarrmoorgebuesch=np.where(((moorgebueschwaldtotalscorearr>thresholdforminimumtotalscore)&(gebueschwaldarr==2)&(moorgebueschwaldtotalscorearr>outscorearrgebuesch)),int(row["joinid"]),outarrmoorgebuesch)
    outscorearrmoorgebuesch=np.where(((moorgebueschwaldtotalscorearr>thresholdforminimumtotalscore)&(gebueschwaldarr==2)&(moorgebueschwaldtotalscorearr>outscorearrmoorgebuesch)),moorgebueschwaldtotalscorearr,outscorearrmoorgebuesch)

#AV
print("AV")
parameterdfav=parameterdf[parameterdf["Gebüschwald"]=="AV"]
#idvonav=int(parameterdf[parameterdf["BE"]=="AV"]["joinid"].tolist()[0])
#outarr=np.where((gebueschwaldarr==1),idvonav,outarr)
#outscorearr=np.where((gebueschwaldarr==1),1.0,outscorearr)
for index, row in parameterdfav.iterrows():
    #print(row["joinid"])
    scoreregionhoehenstufearr=scoreregionhoehenstufeamxy(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
    scoregebueschwald=np.where((gebueschwaldarr==1),1.0,0.0)
    gebueschwaldtotalscorearr=scoreregionhoehenstufearr*scoregebueschwald*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumgebueschwald
    outarrgebuesch=np.where(((gebueschwaldtotalscorearr>0)&(gebueschwaldarr==1)&(gebueschwaldtotalscorearr>outscorearrgebuesch)),int(row["joinid"]),outarrgebuesch)
    outscorearrgebuesch=np.where(((gebueschwaldtotalscorearr>0)&(gebueschwaldarr==1)&(gebueschwaldtotalscorearr>outscorearrgebuesch)),gebueschwaldtotalscorearr,outscorearrgebuesch)
    #outscorearr = np.where((gebueschwaldtotalscorearr > outscorearr), gebueschwaldtotalscorearr, outscorearrgebuesch)
outarrgebuesch=np.where((wasserarr==1),NODATA_value,outarrgebuesch)
outscorearrgebuesch=np.where((wasserarr==1),NODATA_value,outscorearrgebuesch)
outarrgebuesch=np.where((maskarr!=1),NODATA_value,outarrgebuesch)
outscorearrgebuesch=np.where((maskarr!=1),NODATA_value,outscorearrgebuesch)
outarrgebuesch=np.where((gebueschwaldarr>0),outarrgebuesch, NODATA_value)
outscorearrgebuesch=np.where((gebueschwaldarr>0),outscorearrgebuesch, NODATA_value)
#convertarrtotif((outscorearrgebuesch*100).astype(int), outdir + "/" + "outscorearrgebuesch.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outarrgebuesch, outdir + "/" + "outarrgebuesch.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarrgebuesch,outdir+"/outarrgebuesch.sav")
#joblib.dump(outscorearrgebuesch,outdir+"/outscorearrgebuesch.sav")
del scoreregionhoehenstufearr
del scorelagearr
del scoregruendigkeitarr
del scoreneigungarr
del scoreexpositionarr
del scorefeuchtearr
del scorepharr
del scoretgarr
del scoresonderwaldarr
del scoregebueschwald
del gebueschwaldtotalscorearr


# ***********
#Kristallin
print("18 Kristallin")
outarrkristallin=np.zeros((nrows, ncols), dtype=int)
outarrkristallin[:]=NODATA_value
outscorearrkristallin=np.zeros((nrows, ncols), dtype=float)
parameterdfkristallin=parameterdf[(parameterdf["kristallin"].isin(["x"]))]
parameterdfkristallin=parameterdfkristallin[((~parameterdfkristallin["Ju Bfö"].isin(["x","y","m","a","z"])))]
parameterdfkristallin=parameterdfkristallin[((~parameterdfkristallin["Ju Wfö"].isin(["x","y","m","a","z"])))]
parameterdfkristallin=parameterdfkristallin[((~parameterdfkristallin["M/A Arve"].isin(["x","y","m","a","z"])))]
parameterdfkristallin=parameterdfkristallin[((~parameterdfkristallin["M/A Bfö"].isin(["x","y","m","a","z"])))]
parameterdfkristallin=parameterdfkristallin[((~parameterdfkristallin["M/A Wfö"].isin(["x","y","m","a","z"])))]
parameterdfkristallin=parameterdfkristallin[((~parameterdfkristallin["Gebüschwald"].isin(["AV","LF","MoorLF"])))]
parameterdfkristallin=parameterdfkristallin[(~parameterdfkristallin["Subregionen"].isin(['WNI']))]
len(parameterdfkristallin)
gewichtungkristallin=gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfkristallin.iterrows():
    #print(row["joinid"])
    if row["kristallin"]=="x":
        scorekristallinarr=np.where((sonderwaldarr==18),1.0,0.0)
    scoreregionhoehenstufearr = scoreregionhoehenstufeamxy(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorelagearr = scorelagebe(row["Lage neu"], row["Lage scharf"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"], row["Gruendigkeit scharf"])
    scoreneigungarr=scorehangneigungbe(float(row['Neigung_von']), float(row['Neigung_bis']), row["Neigung unten scharf"],row["Neigung oben scharf"])
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]),row["Exposition scharf"])
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"], row["Feuchte scharf"])
    scorepharr = scorephbe(row["pH"], row["pH scharf"])
    scoretgarr = scoretgbe(row)
    kristallintotalscorearr=scorekristallinarr*scoreregionhoehenstufearr*(gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungkristallin
    outarrkristallin = np.where(((kristallintotalscorearr > thresholdforminimumtotalscore)&(sonderwaldarr==18)&(kristallintotalscorearr>=outscorearrkristallin)), int(row["joinid"]), outarrkristallin)
    outscorearrkristallin = np.where(((kristallintotalscorearr > thresholdforminimumtotalscore)&(sonderwaldarr==18)&(kristallintotalscorearr>=outscorearrkristallin)), kristallintotalscorearr, outscorearrkristallin)
outarrkristallin=np.where((wasserarr==1),NODATA_value,outarrkristallin)
outscorearrkristallin=np.where((wasserarr==1),NODATA_value,outscorearrkristallin)
outarrkristallin=np.where((maskarr!=1),NODATA_value,outarrkristallin)
outscorearrkristallin=np.where((maskarr!=1),NODATA_value,outscorearrkristallin)
outarrkristallin=np.where((sonderwaldarr!=18),NODATA_value,outarrkristallin)
outscorearrkristallin=np.where((sonderwaldarr!=18),NODATA_value,outscorearrkristallin)
del scorekristallinarr
del kristallintotalscorearr


#Ueberlagerung
print("Ueberlagerung")
outarr=np.where(((outscorearrkristallin>thresholdforminimumtotalscore)&(sonderwaldarr==18)),outarrkristallin,outarr)
outscorearr=np.where(((outscorearrkristallin>thresholdforminimumtotalscore)&(sonderwaldarr==18)),outscorearrkristallin,outscorearr)
outarr=np.where(((outscorearrfels>thresholdforminimumtotalscore)&(sonderwaldarr==5)&(aarmassivarr<1)),outarrfels,outarr)
outscorearr=np.where(((outscorearrfels>thresholdforminimumtotalscore)&(sonderwaldarr==5)&(aarmassivarr<1)),outscorearrfels,outscorearr)
outarr=np.where(((outscorearrfelskristallin>thresholdforminimumtotalscore)&(sonderwaldarr==5)&(aarmassivarr==1)),outarrfelskristallin,outarr)
outscorearr=np.where(((outscorearrfelskristallin>thresholdforminimumtotalscore)&(sonderwaldarr==5)&(aarmassivarr==1)),outscorearrfelskristallin,outscorearr)
#bfarve=np.where((outscorearrarve>outscorearrbf),outarrarve,outarrbf)
#bfarvescore=np.where((outscorearrarve>outscorearrbf),outscorearrarve,outscorearrbf)
#outarr=np.where((bfarvescore>thresholdforminimumtotalscore),bfarve,outarr)
#outscorearr=np.where((bfarvescore>thresholdforminimumtotalscore),bfarvescore,outscorearr)
#outarr = np.where(((outscorearrflussbuffer > thresholdforminimumtotalscore) & (outscorearrflussbuffer > outscorearr) & (sonderwaldarr == 10)), outarrflussbuffer,outarr)
#outscorearr = np.where(((outscorearrflussbuffer > thresholdforminimumtotalscore) & (outscorearrflussbuffer > outscorearr) & (sonderwaldarr == 10)),outscorearrflussbuffer, outscorearr)
outarr = np.where(((outscorearrflussbuffer > thresholdforminimumtotalscore) & (sonderwaldarr == 10)), outarrflussbuffer,outarr)
outscorearr = np.where(((outscorearrflussbuffer > thresholdforminimumtotalscore) & (sonderwaldarr == 10)),outscorearrflussbuffer, outscorearr)
outarr = np.where(((outscorearrrissmoraene > outscorearr) & (sonderwaldarr == 11)), outarrrissmoraene,outarr)
outscorearr = np.where(((outscorearrrissmoraene > outscorearr) & (sonderwaldarr == 11)),outscorearrrissmoraene, outscorearr)
outarr = np.where(((outscorearr15 > outscorearr) & (sonderwaldarr == 0)&(regionenarr==2)), outarr15,outarr)
outscorearr = np.where(((outscorearr15 > outscorearr) & (sonderwaldarr == 0)&(regionenarr==2)),outscorearr15, outscorearr)
outarr = np.where(((outscorearr16 >= outscorearr) & (sonderwaldarr == 0)&(regionenarr==2)), outarr16,outarr)
outscorearr = np.where(((outscorearr16 >= outscorearr) & (sonderwaldarr == 0)&(regionenarr==2)),outscorearr16, outscorearr)
outarr = np.where(((outscorearr17 >= outscorearr) & (sonderwaldarr == 0)&(regionenarr==2)), outarr17,outarr)
outscorearr = np.where(((outscorearr17 >= outscorearr) & (sonderwaldarr == 0)&(regionenarr==2)),outscorearr17, outscorearr)
outarr = np.where(((outscorearrbachschutt > thresholdforminimumtotalscore) & (sonderwaldarr == 1)), outarrbachschutt,outarr)
outscorearr = np.where(((outscorearrbachschutt > thresholdforminimumtotalscore) & (sonderwaldarr == 1)),outscorearrbachschutt, outscorearr)
outarr = np.where(((outscorearrtalschuttkegel > thresholdforminimumtotalscore) & (sonderwaldarr == 13)), outarrtalschuttkegel,outarr)
outscorearr = np.where(((outscorearrtalschuttkegel > thresholdforminimumtotalscore) & (sonderwaldarr == 13)),outscorearrtalschuttkegel, outscorearr)
outarr = np.where(((outscorearr14 > outscorearr) & (sonderwaldarr == 14)),outarr14, outarr)
outscorearr = np.where(((outscorearr14 > outscorearr) & (sonderwaldarr == 14)),outscorearr14, outscorearr)

#Au und aktive Au
outarr=np.where(((outscorearrau>thresholdforminimumtotalscore)&((sonderwaldarr==6)|(sonderwaldarr==12))),outarrau,outarr)
outscorearr=np.where(((outscorearrau>thresholdforminimumtotalscore)&((sonderwaldarr==6)|(sonderwaldarr==12))),outscorearrau,outscorearr)
outarrau=np.where(((outscorearraktiveau>thresholdforminimumtotalscore)&(sonderwaldarr==12)),outarraktiveau,outarrau)
outscorearrau=np.where(((outscorearraktiveau>thresholdforminimumtotalscore)&(sonderwaldarr==12)),outscorearraktiveau,outscorearrau)
outarr=np.where(((outscorearrbs>thresholdforminimumtotalscore)&(sonderwaldarr==2)),outarrbs,outarr)
outscorearr=np.where(((outscorearrbs>thresholdforminimumtotalscore)&(sonderwaldarr==2)),outscorearrbs,outscorearr)
outarr=np.where(((outscorearrgeroell>thresholdforminimumtotalscore)&(sonderwaldarr==3)),outarrgeroell,outarr)
outscorearr=np.where(((outscorearrgeroell>thresholdforminimumtotalscore)&(sonderwaldarr==3)),outscorearrgeroell,outscorearr)
outarr=np.where(((outscorearrgeroellkristallin>thresholdforminimumtotalscore)&(sonderwaldarr==19)),outarrgeroellkristallin,outarr)
outscorearr=np.where(((outscorearrgeroellkristallin>thresholdforminimumtotalscore)&(sonderwaldarr==19)),outscorearrgeroellkristallin,outscorearr)
outarr=np.where(((outscorearrblockschutt>thresholdforminimumtotalscore)&(sonderwaldarr==4)),outarrblockschutt,outarr)
outscorearr=np.where(((outscorearrblockschutt>thresholdforminimumtotalscore)&(sonderwaldarr==4)),outscorearrblockschutt,outscorearr)
outarr=np.where(((outscorearrsumpf>thresholdforminimumtotalscore)&(sonderwaldarr==7)),outarrsumpf,outarr)
outscorearr=np.where(((outscorearrsumpf>thresholdforminimumtotalscore)&(sonderwaldarr==7)),outscorearrsumpf,outscorearr)
outarr=np.where(((outscorearrmoor>thresholdforminimumtotalscore)&(sonderwaldarr==8)),outarrmoor,outarr)
outscorearr=np.where(((outscorearrmoor>thresholdforminimumtotalscore)&(sonderwaldarr==8)),outscorearrmoor,outscorearr)
outarr=np.where(((outscorearrnadelsumpf>thresholdforminimumtotalscore)&(sonderwaldarr==9)),outarrnadelsumpf,outarr)
outscorearr=np.where(((outscorearrnadelsumpf>thresholdforminimumtotalscore)&(sonderwaldarr==9)),outscorearrnadelsumpf,outscorearr)
#Arven
outarr=np.where(((outscorearrarve>thresholdforminimumtotalscore)&(arvenarr==1)&(arvenfoehrenhektararr<=4)&(regionenarr==2)),outarrarve,outarr)
outscorearr=np.where(((outscorearrarve>thresholdforminimumtotalscore)&(arvenarr==1)&(arvenfoehrenhektararr<=4)&(regionenarr==2)),outscorearrarve,outscorearr)
outarr=np.where(((outscorearrarve>thresholdforminimumtotalscore)&(arvenarr==1)&(arvenfoehrenhektararr<=4)&(regionenarr==3)),outarrarve,outarr)
outscorearr=np.where(((outscorearrarve>thresholdforminimumtotalscore)&(arvenarr==1)&(arvenfoehrenhektararr<=4)&(regionenarr==3)),outscorearrarve,outscorearr)
outarr=np.where(((outscorearrarve>outscorearr)&(outscorearrarve>thresholdforminimumtotalscorearvegroesser4ha)&(arvenarr==1)&(arvenfoehrenhektararr>4)&(regionenarr==2)),outarrarve,outarr)
outscorearr=np.where(((outscorearrarve>outscorearr)&(outscorearrarve>thresholdforminimumtotalscorearvegroesser4ha)&(arvenarr==1)&(arvenfoehrenhektararr>4)&(regionenarr==2)),outscorearrarve,outscorearr)
outarr=np.where(((outscorearrarve>outscorearr)&(outscorearrarve>thresholdforminimumtotalscorearvegroesser4ha)&(arvenarr==1)&(arvenfoehrenhektararr>4)&(regionenarr==3)),outarrarve,outarr)
outscorearr=np.where(((outscorearrarve>outscorearr)&(outscorearrarve>thresholdforminimumtotalscorearvegroesser4ha)&(arvenarr==1)&(arvenfoehrenhektararr>4)&(regionenarr==3)),outscorearrarve,outscorearr)
outarr=np.where(((outscorearrarve>thresholdforminimumtotalscore)&(arvenarr==1)&(regionenarr==1)),outarrarve,outarr)
outscorearr=np.where(((outscorearrarve>thresholdforminimumtotalscore)&(arvenarr==1)&(regionenarr==1)),outscorearrarve,outscorearr)
#Bergfoehre
#outarr=np.where(((outscorearrbf>thresholdforminimumtotalscore)&(bergfoehrenarr==1)&(arvenfoehrenhektararr<=4)&(regionenarr==2)),outarrbf,outarr)
#outscorearr=np.where(((outscorearrbf>thresholdforminimumtotalscore)&(bergfoehrenarr==1)&(arvenfoehrenhektararr<=4)&(regionenarr==2)),outscorearrbf,outscorearr)
#outarr=np.where(((outscorearrbf>thresholdforminimumtotalscore)&(bergfoehrenarr==1)&(arvenfoehrenhektararr<=4)&(regionenarr==3)),outarrbf,outarr)
#outscorearr=np.where(((outscorearrbf>thresholdforminimumtotalscore)&(bergfoehrenarr==1)&(arvenfoehrenhektararr<=4)&(regionenarr==3)),outscorearrbf,outscorearr)
outarr=np.where(((outscorearrbf>outscorearr)&(outscorearrbf>thresholdforminimumtotalscorefoehregroesser4ha)&(bergfoehrenarr==1)&(regionenarr==2)),outarrbf,outarr)
outscorearr=np.where(((outscorearrbf>outscorearr)&(outscorearrbf>thresholdforminimumtotalscorefoehregroesser4ha)&(bergfoehrenarr==1)&(regionenarr==2)),outscorearrbf,outscorearr)
outarr=np.where(((outscorearrbf>outscorearr)&(outscorearrbf>thresholdforminimumtotalscorefoehregroesser4ha)&(bergfoehrenarr==1)&(regionenarr==3)),outarrbf,outarr)
outscorearr=np.where(((outscorearrbf>outscorearr)&(outscorearrbf>thresholdforminimumtotalscorefoehregroesser4ha)&(bergfoehrenarr==1)&(regionenarr==3)),outscorearrbf,outscorearr)
#outarr=np.where(((outscorearrbf>outscorearr)&(outscorearrarve>thresholdforminimumtotalscorefoehregroesser4ha)&(bergfoehrenarr==1)&(arvenfoehrenhektararr>4)&(regionenarr==2)),outarrbf,outarr)
#outscorearr=np.where(((outscorearrbf>outscorearr)&(outscorearrarve>thresholdforminimumtotalscorefoehregroesser4ha)&(bergfoehrenarr==1)&(arvenfoehrenhektararr>4)&(regionenarr==2)),outscorearrbf,outscorearr)
#outarr=np.where(((outscorearrbf>outscorearr)&(outscorearrarve>thresholdforminimumtotalscorefoehregroesser4ha)&(bergfoehrenarr==1)&(arvenfoehrenhektararr>4)&(regionenarr==3)),outarrbf,outarr)
#outscorearr=np.where(((outscorearrbf>outscorearr)&(outscorearrarve>thresholdforminimumtotalscorefoehregroesser4ha)&(bergfoehrenarr==1)&(arvenfoehrenhektararr>4)&(regionenarr==3)),outscorearrbf,outscorearr)
#outarr=np.where(((outscorearrbf>thresholdforminimumtotalscore)&(bergfoehrenarr==1)&(regionenarr==1)),outarrbf,outarr)
#outscorearr=np.where(((outscorearrbf>thresholdforminimumtotalscore)&(bergfoehrenarr==1)&(regionenarr==1)),outscorearrbf,outscorearr)
#Waldfoehre
#outarr=np.where(((outscorearrwf>thresholdforminimumtotalscore)&(waldfoehrenarr==1)&(arvenfoehrenhektararr<=4)&(regionenarr==2)),outarrwf,outarr)
#outscorearr=np.where(((outscorearrwf>thresholdforminimumtotalscore)&(waldfoehrenarr==1)&(arvenfoehrenhektararr<=4)&(regionenarr==2)),outscorearrwf,outscorearr)
#outarr=np.where(((outscorearrwf>thresholdforminimumtotalscore)&(waldfoehrenarr==1)&(arvenfoehrenhektararr<=4)&(regionenarr==3)),outarrwf,outarr)
#outscorearr=np.where(((outscorearrwf>thresholdforminimumtotalscore)&(waldfoehrenarr==1)&(arvenfoehrenhektararr<=4)&(regionenarr==3)),outscorearrwf,outscorearr)
#outarr=np.where(((outscorearrwf>outscorearr)&(outscorearrwf>thresholdforminimumtotalscorefoehregroesser4ha)&(waldfoehrenarr==1)&(arvenfoehrenhektararr>4)&(regionenarr==2)),outarrwf,outarr)
#outscorearr=np.where(((outscorearrwf>outscorearr)&(outscorearrwf>thresholdforminimumtotalscorefoehregroesser4ha)&(waldfoehrenarr==1)&(arvenfoehrenhektararr>4)&(regionenarr==2)),outscorearrwf,outscorearr)
#outarr=np.where(((outscorearrwf>outscorearr)&(outscorearrwf>thresholdforminimumtotalscorefoehregroesser4ha)&(waldfoehrenarr==1)&(arvenfoehrenhektararr>4)&(regionenarr==3)),outarrwf,outarr)
#outscorearr=np.where(((outscorearrwf>outscorearr)&(outscorearrwf>thresholdforminimumtotalscorefoehregroesser4ha)&(waldfoehrenarr==1)&(arvenfoehrenhektararr>4)&(regionenarr==3)),outscorearrwf,outscorearr)
outarr=np.where(((outscorearrwf>outscorearr)&(outscorearrwf>thresholdforminimumtotalscorefoehregroesser4ha)&(waldfoehrenarr==1)&(regionenarr==2)),outarrwf,outarr)
outscorearr=np.where(((outscorearrwf>outscorearr)&(outscorearrwf>thresholdforminimumtotalscorefoehregroesser4ha)&(waldfoehrenarr==1)&(regionenarr==2)),outscorearrwf,outscorearr)
outarr=np.where(((outscorearrwf>outscorearr)&(outscorearrwf>thresholdforminimumtotalscorefoehregroesser4ha)&(waldfoehrenarr==1)&(regionenarr==3)),outarrwf,outarr)
outscorearr=np.where(((outscorearrwf>outscorearr)&(outscorearrwf>thresholdforminimumtotalscorefoehregroesser4ha)&(waldfoehrenarr==1)&(regionenarr==3)),outscorearrwf,outscorearr)
outarr=np.where(((outscorearrwf>thresholdforminimumtotalscore)&(waldfoehrenarr==1)&(regionenarr==1)),outarrwf,outarr)
outscorearr=np.where(((outscorearrwf>thresholdforminimumtotalscore)&(waldfoehrenarr==1)&(regionenarr==1)),outscorearrwf,outscorearr)
#Gebueschwald
outarr = np.where(((outscorearrgebuesch > thresholdforminimumtotalscore) & (gebueschwaldarr > 0)), outarrgebuesch,outarr)
outscorearr=np.where(((outscorearrgebuesch>thresholdforminimumtotalscore)&(gebueschwaldarr>0)),outscorearrgebuesch,outscorearr)
outarr = np.where(((outscorearrmoorgebuesch > thresholdforminimumtotalscore) & (gebueschwaldarr > 0)&(sonderwaldarr==8)), outarrmoorgebuesch,outarr)
outscorearr=np.where(((outscorearrmoorgebuesch>thresholdforminimumtotalscore)&(gebueschwaldarr>0)&(sonderwaldarr==8)),outscorearrmoorgebuesch,outscorearr)

#loesche alle 59* in OSA ausserhalb der BFOE und Arven Polygonen
#tempid=parameterdf[parameterdf["BE"]=="59*"]["joinid"]#.tolist()[0]
#for item in tempid:
#    #print(item)
#    outarr = np.where(((outarr==item) & (arvenarr == 1)&(hoehenstufenarr==10)), outarr,0)
#    outscorearr=np.where(((outarr==item) & (arvenarr == 1)&(hoehenstufenarr==10)),outscorearr,0)
#    outarr = np.where(((outarr == item) & (bergfoehrenarr == 1)&(hoehenstufenarr==10)), outarr,0)
#    outscorearr = np.where(((outarr == item) & (bergfoehrenarr == 1)&(hoehenstufenarr==10)), outscorearr,0)

#mask
outscorearrint=(outscorearr*100).astype(int)
outarr=np.where((wasserarr==1),NODATA_value,outarr)
outscorearr=np.where((wasserarr==1),NODATA_value,outscorearr)
outscorearrint=np.where((wasserarr==1),0,outscorearrint)
outarr=np.where((maskarr!=1),NODATA_value,outarr)
outscorearr=np.where((maskarr!=1),NODATA_value,outscorearr)
outscorearrint=np.where((maskarr!=1),0,outscorearrint)
outarr=np.where((waldarr==1),outarr,NODATA_value)
outscorearr=np.where((waldarr==1),outscorearr,NODATA_value)
outscorearrint=np.where((waldarr==1),outscorearrint,0)

#write output
#convertarrtotif(outscorearr, outdir + "/" + "outscorearr.tif", indatatype, referenceraster, NODATA_value)
#convertarrtotif(outarr, outdir + "/" + "outarr.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarr,outdir+"/outarr_final.sav")
#joblib.dump(outscorearr,outdir+"/outscorearr_final.sav")
#joblib.dump(outscorearrint,outdir+"/outscorearrint_final.sav")
convertarrtotif(outarr, outdir+"/"+"bestandortstypen_rcp45.tif", 3, referenceraster, NODATA_value)
#convertarrtotif(outscorearr, outdir+"/"+"bestandortstypenscore.tif", indatatype, referenceraster, NODATA_value)
convertarrtotif(outscorearrint, outdir+"/"+"bestandortstypenscoreinteger_rcp45.tif", indatatypeint, referenceraster, NODATA_value)
#plt.imshow(outarr)
print("modelling done ...")

#Arrondierung
print("Arrondierung ....")
#outarr=convert_tif_to_array(outdir+"/"+"bestandortstypen.tif")
arrondiertarr=np.zeros((nrows, ncols), dtype=int)
arrondierbar_joinidlist=parameterdf[parameterdf["arrondieren"]=="x"]["joinid"].unique().tolist()
outarrarrondiert=outarr.copy()
i=1#i=360
j=1#j=2742
while i<nrows-1:
    j=1
    while j<ncols-1:
        joinid=outarr[i,j]
        #wasser=wasserarr[i,j]
        sw=sonderwaldarr[i,j]
        reg=regionenarr[i,j]
        lage=lagearr[i,j]
        gebuesch=gebueschwaldarr[i,j]
        arve=arvenarr[i,j]
        bf=bergfoehrenarr[i,j]
        wf=waldfoehrenarr[i,j]
        wni=wniarr[i,j]
        if joinid>0 and joinid in arrondierbar_joinidlist and sw<1 and gebuesch<1 and arve<1 and bf<1 and wf<1 and wni<1:
            # count same neighbors
            anzgleichenachbarn = 0
            if outarr[i, j + 1] == joinid:
                anzgleichenachbarn += 1
            if outarr[i + 1, j + 1] == joinid:
                anzgleichenachbarn += 1
            if outarr[i + 1, j] == joinid:
                anzgleichenachbarn += 1
            if outarr[i + 1, j - 1] == joinid:
                anzgleichenachbarn += 1
            if outarr[i, j - 1] == joinid:
                anzgleichenachbarn += 1
            if outarr[i - 1, j - 1] == joinid:
                anzgleichenachbarn += 1
            if outarr[i - 1, j] == joinid:
                anzgleichenachbarn += 1
            if outarr[i - 1, j + 1] == joinid:
                anzgleichenachbarn += 1
            #neighborslist
            # select joinid to be used for generalization
            joinidlist = []
            if outarr[i, j + 1] >0:
                joinidlist.append(outarr[i, j + 1])
            if outarr[i + 1, j + 1] >0:
                joinidlist.append(outarr[i + 1, j + 1])
            if outarr[i + 1, j] >0:
                joinidlist.append(outarr[i + 1, j])
            if outarr[i + 1, j - 1] >0:
                joinidlist.append(outarr[i + 1, j - 1])
            if outarr[i, j - 1] >0:
                joinidlist.append(outarr[i, j - 1])
            if outarr[i - 1, j - 1] >0:
                joinidlist.append(outarr[i - 1, j - 1])
            if outarr[i - 1, j] >0:
                joinidlist.append(outarr[i - 1, j])
            if outarr[i - 1, j + 1] >0:
                joinidlist.append(outarr[i - 1, j + 1])
            #while -9999 in joinidlist:
            #    joinidlist.remove(-9999)
            arrondierbarejoinidlist=joinidlist.copy()
            for arrondierbar in arrondierbar_joinidlist:
                if arrondierbar in arrondierbarejoinidlist:
                    arrondierbarejoinidlist.remove(arrondierbar)
            if len(arrondierbarejoinidlist) > 0:
                joinidtobeusedforgeneralization = max(set(arrondierbarejoinidlist), key=arrondierbarejoinidlist.count)#min(joinidlist)
            else:
                if len(joinidlist) > 0:
                    # check joinid with maximum neighbors
                    joinidtobeusedforgeneralization = max(set(joinidlist), key=joinidlist.count)
                else:
                    joinidtobeusedforgeneralization = joinid
            if anzgleichenachbarn==0:
                if lage==4 and reg==1:
                    outarrarrondiert[i, j]=joinid
                else:
                    outarrarrondiert[i,j]=joinidtobeusedforgeneralization
                    arrondiertarr[i,j]=1
        j+=1
    i+=1
convertarrtotif(outarrarrondiert, outdir+"/"+"bestandortstypenarrondiert_rcp45.tif", 3, referenceraster, NODATA_value)
convertarrtotif(arrondiertarr, outdir+"/"+"bearrondiert_rcp45.tif", indatatypeint, referenceraster, NODATA_value)

np.sum(outarrarrondiert)==np.sum(outarr)

#convert to shapefile
#outarr.dtype
#print("convert raster to shapefile and join parameterfile to shapefile ....")
# create new shapefile with the create_shp function
#shp_driver = ogr.GetDriverByName("ESRI Shapefile")
#shp_dataset = shp_driver.CreateDataSource(outdir+"/bestandortstypen.shp")
#spat_ref = osr.SpatialReference()
#proj = referencetifraster.GetProjectionRef()
#spat_ref.ImportFromWkt(proj)
#dst_layer =shp_dataset.CreateLayer("besto",spat_ref, ogr.wkbPolygon)
## create new field to define values
#new_field = ogr.FieldDefn("joinid", ogr.OFTInteger)
#dst_layer.CreateField(new_field)
## Polygonize(band, hMaskBand[optional]=None, destination lyr, field ID, papszOptions=[], callback=None)
#raster=gdal.Open(outdir+"/"+"bestandortstypen.tif")
#raster_band=raster.GetRasterBand(1)
#gdal.Polygonize(raster_band, None, dst_layer, 0, [], callback=None)
#time.sleep(1200)
#shp_dataset.Destroy()
#Alternative?:
#os.system('python3 -m gdal_polygonize '+outdir+'/bestandortstypen.tif -b 1 -f "ESRI Shapefile" bestandortstypen joinid')
# create projection file
#with open(outdir+"/bestandortstypen.prj", "w") as prj:
#    prj.write(int(spat_ref.GetAuthorityCode(None)))
#prj.close()
#eventuell Warteschlaufe einbauen weil gdal kein Signal zurueckgibt wann Befehl fertig ausgefuehrt ist

#open shapefile and join values from parameter file
#inraster = xr.open_rasterio(outdir+"/"+"bestandortstypen.tif").squeeze('band', drop=True)
#bestandortstypengdf=polygonize(inraster)
#bestandortstypengdf=gpd.read_file(outdir+"/"+"bestandortstypen_intsct_region.shp")

#join parameter table
bestandortstypengdf=gpd.read_file(outdir+"/"+"bestandortstypen_rcp45.shp")
bestandortstypengdf["region"]=""
bestandortstypengdf.loc[bestandortstypengdf["regionid"]==1,"region"]="Berner Jura"
bestandortstypengdf.loc[bestandortstypengdf["regionid"]==2,"region"]="Mittelland"
bestandortstypengdf.loc[bestandortstypengdf["regionid"]==3,"region"]="Oberland"

bestandortstypengdf.dtypes
#bestandortstypengdf=bestandortstypengdf.astype({'value': 'int64'})
bestandortstypengdf.columns
len(bestandortstypengdf)
#bestandortstypengdf=bestandortstypengdf.rename(columns={"value":"joinid"})
#bestandortstypengdf=bestandortstypengdf.rename(columns={"gridcode":"joinid"})
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

bestandortstypengdfmerge.to_file(outdir+"/bestandortstypenjoined_rcp45.shp")
print("exported joined  shapefile")

#clip shapefile with forest mask
#waldgdf=gpd.read_file(myworkspace+"/bewald.shp")
#waldgdf.crs
#len(waldgdf)
#bestandortstypengdfmergeclip=gpd.clip(bestandortstypengdfmerge, waldgdf,keep_geom_type=False)
#bestandortstypengdfmergeclip.to_file(outdir+"/bestandortstypenjoinedclipwald.shp")
#print("shapefile clipped to forest cover")

#aggregate areas
bestandortstypengdfmergeclip=gpd.read_file(outdir+"/"+"bestandortstypenjoinedclipwald_rcp45.shp")
bestandortstypengdfmergeJURA=bestandortstypengdfmergeclip[bestandortstypengdfmergeclip["regionid"]==1]
bestandortstypengdfmergeMittelland=bestandortstypengdfmergeclip[bestandortstypengdfmergeclip["regionid"]==2]
bestandortstypengdfmergeAlpen=bestandortstypengdfmergeclip[bestandortstypengdfmergeclip["regionid"]==3]

#areastatistics=bestandortstypengdfmerge.groupby(["region","BE"]).agg({'area': 'sum'})
#areastatistics["hektar"]=areastatistics["area"]/10000.0
areastatisticsJura=bestandortstypengdfmergeJURA.groupby(["BE"]).agg({'area': 'sum'})
areastatisticsMittelland=bestandortstypengdfmergeMittelland.groupby(["BE"]).agg({'area': 'sum'})
areastatisticsAlpen=bestandortstypengdfmergeAlpen.groupby(["BE"]).agg({'area': 'sum'})
areastatisticsJura["hektar"]=areastatisticsJura["area"]/10000.0
areastatisticsMittelland["hektar"]=areastatisticsMittelland["area"]/10000.0
areastatisticsAlpen["hektar"]=areastatisticsAlpen["area"]/10000.0
#areastatisticsJura=areastatisticsJura.rename_axis(index='BE', columns="index")
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

areastatisticsJura.to_excel(outdir+"/areastatisticsJura_rcp45.xlsx")
areastatisticsMittelland.to_excel(outdir+"/areastatisticsMittelland_rcp45.xlsx")
areastatisticsAlpen.to_excel(outdir+"/areastatisticsAlpen_rcp45.xlsx")
#areastatistics.to_excel(outdir+"/areastatistics.xlsx")

#arrondiertes file
bestandortstypenarrondiertgdf=gpd.read_file(outdir+"/"+"bestandortstypenarrondiert_rcp45.shp")
bestandortstypenarrondiertgdf["region"]=""
bestandortstypenarrondiertgdf.loc[bestandortstypenarrondiertgdf["regionid"]==1,"region"]="Berner Jura"
bestandortstypenarrondiertgdf.loc[bestandortstypenarrondiertgdf["regionid"]==2,"region"]="Mittelland"
bestandortstypenarrondiertgdf.loc[bestandortstypenarrondiertgdf["regionid"]==3,"region"]="Oberland"

bestandortstypenarrondiertgdf.dtypes
#bestandortstypengdf=bestandortstypengdf.astype({'value': 'int64'})
bestandortstypenarrondiertgdf.columns
len(bestandortstypenarrondiertgdf)
#bestandortstypengdf=bestandortstypengdf.rename(columns={"value":"joinid"})
#bestandortstypengdf=bestandortstypengdf.rename(columns={"gridcode":"joinid"})
bestandortstypenarrondiertgdf=bestandortstypenarrondiertgdf[bestandortstypenarrondiertgdf["joinid"]>0][["joinid","geometry","regionid","region"]]
bestandortstypenarrondiertgdf["area"]=bestandortstypenarrondiertgdf["geometry"].area
#bestandortstypengdf=bestandortstypengdf.astype({'joinid': 'int64'})
#parameterdf.columns
#parameterdf.dtypes
#parameterdf=parameterdf.astype({'joinid': 'int64'})
#parameterdf.dtypes
#parameterdfjoin=parameterdf[["joinid","NrBE","BE","NaiS_LFI_JU","NaiS_LFI_M/A","Anforderungsprofil NaiS"]]
bestandortstypenarrondiertgdfmerge = bestandortstypenarrondiertgdf.merge(parameterdfjoin, on='joinid',how="left")
len(bestandortstypenarrondiertgdfmerge)
bestandortstypenarrondiertgdfmerge.columns
bestandortstypenarrondiertgdfmerge=bestandortstypenarrondiertgdfmerge[(bestandortstypenarrondiertgdfmerge["joinid"]>0)]
bestandortstypenarrondiertgdfmerge["nais"]=""
bestandortstypenarrondiertgdfmerge.loc[(bestandortstypenarrondiertgdfmerge["regionid"]==1),"nais"]=bestandortstypenarrondiertgdfmerge["NaiS_LFI_JU"]
bestandortstypenarrondiertgdfmerge.loc[(bestandortstypenarrondiertgdfmerge["regionid"]==2),"nais"]=bestandortstypenarrondiertgdfmerge["NaiS_LFI_M/A"]
bestandortstypenarrondiertgdfmerge.loc[(bestandortstypenarrondiertgdfmerge["regionid"]==3),"nais"]=bestandortstypenarrondiertgdfmerge["NaiS_LFI_M/A"]
len(bestandortstypenarrondiertgdfmerge)
#clip shapefile with forest mask
#waldgdf=gpd.read_file(myworkspace+"/bewaldbuffer20m.shp")
#waldgdf.crs
#len(waldgdf)
#bestandortstypengdfmergeclip=gpd.clip(bestandortstypengdfmerge, waldgdf,keep_geom_type=False)
##bestandortstypengdfmergeclip.to_file(outdir+"/bestandortstypenjoinedclipwald_mitsturztrajektorien.shp")
#bestandortstypengdfmergeclip.to_file(outdir+"/bestandortstypenjoinedclipwald_ohnesturztrajektorien.shp")
#print("shapefile clipped to forest cover")
#bestandortstypengdfmerge.to_file(outdir+"/bestandortstypenjoined_mitsturztrajektorien.shp")
bestandortstypenarrondiertgdfmerge.to_file(outdir+"/bestandortstypenarrondiertjoined_rcp45.shp")
print("exported joined  shapefile")
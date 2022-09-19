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
#myworkspace="D:/CCWBE/GIS"
myworkspace="C:/DATA/projects/CCWBE/GIS"
referenceraster=myworkspace+"/bedem10m.tif"
codespace="C:/DATA/develops/ccwbe"
#outdir=myworkspace+"/out20220112_mitSturztrajektorien"
outdir=myworkspace+"/Modellergebnisse"
#model parameter file
parameterdf=pd.read_excel(codespace+"/"+"Anhang1_Parameter_Waldstandorte_BE_20220128V2.xlsx", dtype="str", engine='openpyxl')
parameterdf.columns
parameterdf=parameterdf.rename(columns={"Nr. BE (Achtung, z.T. doppelte Nummern)":"NrBE","Sonderwald (Kat. 1 und 5 weglassen; 3* = Schutt/Geröll bei Bach)": "Sonderwald", "x = Einheit v.a. auf Sturztrajektorien vorkommend (doppelt gewichten bei Sturztraj.)": "Sturztrajektorien",'nur Einheiten mit "x" oder "s" auf Fels modellieren (x = doppelt gewichten, s = nur halb gewichten)':"Fels"})
parameterdf=parameterdf.rename(columns={"Korrekturen Tongehalt Jura, Mittelland":"TongehaltJuraMittelland","Korrekturen Tongehalt Oberland, basierend auf den Korrekturen Jura":"TongehaltOberland"})
len(parameterdf)
parameterdf.dtypes
parameterdf=parameterdf.astype({"Sonderwald":str})
NODATA_value=-9999
thresholdforminimumtotalscore=0.0
cellsize=10.0
listetongehalt=[11,12,22,23,33,34,44]
gewichtunghoehe=5.0
gewichtunglage=5.0
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
x_hoehendifferenz = np.array([-210.0, -200.0, 0, 200.0, 210.0])
y_hoehendifferenz = np.array([0.0,0.56,1.0,0.56,0.0])
f_scorehoehe = interp1d(x_hoehendifferenz, y_hoehendifferenz, kind="linear")
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
x_ns=[0.0,1000.0,2500.0]
y_ns=[1.0,0.35,0.1]
f_scoreniederschlag=interp1d(x_ns,y_ns,kind="linear")
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
    return scoreregiohoehenstufe
def scoreregionhoehenstufexy(row):
    scoreregiohoehenstufe = np.zeros((nrows, ncols), dtype=np.float32)
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
def scorehangneigungbe(neigung_von, neigung_bis):
    scorehangneigungarr = np.zeros((nrows, ncols), dtype=np.float32)
    if neigung_von > 35.0:
        abweichungarr = abs(neigung_von - slopearr)
        abweichungarr = np.where(abweichungarr > 35.0, 35.0, abweichungarr)
        abweichungarr = np.where(abweichungarr < 0.0, 0.0, abweichungarr)
        scorehangneigungarr = np.where(((slopearr >= (neigung_von - 35.0)) & (slopearr < neigung_von) & (slopearr >= 0)),f_scorehangneigung(abweichungarr), scorehangneigungarr)
    else:
        abweichungarr = abs(neigung_von - slopearr)
        abweichungarr = np.where(abweichungarr > 35.0, 35.0, abweichungarr)
        abweichungarr = np.where(abweichungarr < 0.0, 0.0, abweichungarr)
        scorehangneigungarr = np.where(((slopearr >= 0.0) & (slopearr < neigung_von)),f_scorehangneigung(abweichungarr), scorehangneigungarr)
    scorehangneigungarr = np.where(((slopearr > 0) & (slopearr <= neigung_von - 35.0)), 0.1, scorehangneigungarr)
    abweichungarr = abs(neigung_bis - slopearr)
    abweichungarr = np.where(abweichungarr > 35.0, 35.0, abweichungarr)
    abweichungarr = np.where(abweichungarr < 0.0, 0.0, abweichungarr)
    scorehangneigungarr = np.where(((slopearr > neigung_bis) & (slopearr < neigung_bis+35.0)), f_scorehangneigung(abweichungarr),scorehangneigungarr)
    scorehangneigungarr = np.where(((slopearr > neigung_bis + 35.0)), 0.1, scorehangneigungarr)
    scorehangneigungarr=np.where(((slopearr>=neigung_von)&(slopearr<=neigung_bis)),1.0,scorehangneigungarr)
    return scorehangneigungarr
def scorelagebe(lagein):
    lagescorearr=np.zeros((nrows, ncols),dtype=np.float32)
    lagescorearr[:]=0.1
    lagelist=str(lagein).strip().split()
    for item in lagelist:
        lagescorearr=np.where((lagearr==int(item)),1.0,lagescorearr)
    return lagescorearr
def scorehoehebe(hoehe_min, hoehe_max):
    scorehoehearr = np.zeros((nrows, ncols), dtype=np.float32)
    scorehoehearr=np.where((dhmarr<hoehe_min),0.1,scorehoehearr)
    scorehoehearr = np.where((dhmarr > hoehe_max), 0.1, scorehoehearr)
    scorehoehearr = np.where(((dhmarr >= hoehe_min)&(dhmarr <= hoehe_max)), 1.0, scorehoehearr)
    return scorehoehearr
def scoregruendigkeitbe(gruendigkeit):
    scoregruendigkeitarr = np.zeros((nrows, ncols), dtype=np.float32)
    scoregruendigkeitarr[:] = 0.1
    gruendigkeitlist = str(gruendigkeit).strip().split()
    for item in gruendigkeitlist:
        scoregruendigkeitarr = np.where((gruendigkeitarr == int(item)), 1.0, scoregruendigkeitarr)
    return scoregruendigkeitarr
def scoreexpositionbe(exp_von, exp_bis):
    scoreexpositionarr = np.zeros((nrows, ncols), dtype=np.float32)
    scoreexpositionarr[:]=0.1
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
def scorefeuchtebe(feuchte):
    scorefeuchtearr = np.zeros((nrows, ncols), dtype=np.float32)
    scorefeuchtearr[:] = 0.1
    feuchtelist = str(feuchte).strip().split()
    for item in feuchtelist:
        scorefeuchtearr = np.where((feuchtearr == int(item)), 1.0, scorefeuchtearr)
    return scorefeuchtearr
def scorephbe(ph):
    scorepharr = np.zeros((nrows, ncols), dtype=np.float32)
    scorepharr[:] = 0.1
    if ph=="indiff":
        scorepharr = np.where((phcombiarr > 0), 1.0, scorepharr)
    else:
        phanspruch=ph.replace(" ","").replace("bis"," ")
        minph=int(phanspruch.strip().split()[0])
        maxph = int(phanspruch.strip().split()[-1])
        phlist = np.arange(minph, maxph+1,1).tolist()
        for item in phlist:
            scorepharr = np.where((phcombiarr == int(item)), 1.0, scorepharr)
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
np.min(dhmarr)
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
sonderwaldarr=convert_tif_to_array(myworkspace+"/besonderwald.tif")
#sonderwaldarr=convert_tif_to_array(myworkspace+"/besonderwald_ohneSturztrajektorien.tif")
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
hoehenstufenarr=convert_tif_to_array(myworkspace+"/bevegetationshoehenstufen.tif")
tgarr=convert_tif_to_array(myworkspace+"/betg.tif")
phcombiarr=convert_tif_to_array(myworkspace+"/bephcombiarr.tif")
wasserarr=convert_tif_to_array(myworkspace+"/beseen.tif")
arvenarr=convert_tif_to_array(myworkspace+"/bearven.tif")
bergfoehrenarr=convert_tif_to_array(myworkspace+"/bebergfoehren.tif")
waldfoehrenarr=convert_tif_to_array(myworkspace+"/bewaldfoehren.tif")
waldarr=convert_tif_to_array(myworkspace+"/bewaldbuffer20mgebueschwald.tif")
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
parameterdfuebrige=parameterdf[((parameterdf["Sonderwald"].astype(str).str.contains("0")))]
gewichtunguebrige=gewichtunghoehe+gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfuebrige.iterrows():
    print(row["joinid"])
    scoreregionhoehenstufearr=scoreregionhoehenstufe(row)
    scorehoehearr=scorehoehebe(float(row["Hoehe_min"]), float(row["Hoehe_max"]))
    scorelagearr = scorelagebe(row["Lage neu"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"])
    scoreneigungarr=scorehangneigungbe(np.float(row['Neigung_von']), np.float(row['Neigung_bis']))
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]))
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"])
    scorepharr = scorephbe(row["pH"])
    scoretgarr = scoretgbe(row)
    #scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
    #scoresonderwaldarr = np.where((sonderwaldarr==0),1.0,0.0)
    uebrigetotalscorearr=scoreregionhoehenstufearr*(gewichtunghoehe*scorehoehearr+gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtunguebrige
    outarr=np.where((uebrigetotalscorearr>outscorearr),int(row["joinid"]),outarr)
    outscorearr=np.where((uebrigetotalscorearr>outscorearr),uebrigetotalscorearr,outscorearr)
outarr=np.where((wasserarr==1),NODATA_value,outarr)
outscorearr=np.where((wasserarr==1),NODATA_value,outscorearr)
outarr=np.where((maskarr!=1),NODATA_value,outarr)
outscorearr=np.where((maskarr!=1),NODATA_value,outscorearr)
convertarrtotif((outscorearr*100).astype(int), outdir + "/" + "uebrigetotalscorearr.tif", indatatypeint, referenceraster, NODATA_value)
convertarrtotif(outarr, outdir + "/" + "uebrigeoutarr.tif", indatatypeint, referenceraster,NODATA_value)
joblib.dump(outarr,outdir+"/uebrigeoutarr.sav")
joblib.dump(outscorearr,outdir+"/uebrigeoutscorearr.sav")
del uebrigetotalscorearr
#outarr=joblib.load(outdir+"/uebrigeoutarr.sav")
#outscorearr=joblib.load(outdir+"/uebrigeoutscorearr.sav")

# ***********
#Fels
print("Fels")
outarrfels=np.zeros((nrows, ncols), dtype=int)
outarrfels[:]=NODATA_value
outscorearrfels=np.zeros((nrows, ncols), dtype=float)
parameterdffels=parameterdf[((parameterdf["Fels"].isin(["x","s"])))]
len(parameterdffels)
gewichtungfels=gewichtunghoehe+gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdffels.iterrows():
    print(row["joinid"])
    if row["Fels"]=="x":
        scorefelsarr=np.where((sonderwaldarr==5),1.0,0.0)
    elif row["Fels"]=="s":
        scorefelsarr=np.where((sonderwaldarr==5),0.5,0.0)
    scoreregionhoehenstufearr = scoreregionhoehenstufe(row)
    #scorearvearr=scorearven(row)
    #scorebergfoehrearr = scorebergfoehren(row)
    #scorewaldfoehrearr = scorewaldfoehren(row)
    scorehoehearr=scorehoehebe(float(row["Hoehe_min"]), float(row["Hoehe_max"]))
    scorelagearr = scorelagebe(row["Lage neu"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"])
    scoreneigungarr=scorehangneigungbe(np.float(row['Neigung_von']), np.float(row['Neigung_bis']))
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]))
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"])
    scorepharr = scorephbe(row["pH"])
    scoretgarr = scoretgbe(row)
    #scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
    felstotalscorearr=scorefelsarr*scoreregionhoehenstufearr*(gewichtunghoehe*scorehoehearr+gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungfels
    outarrfels = np.where(((felstotalscorearr > thresholdforminimumtotalscore)&(sonderwaldarr==5)&(felstotalscorearr>=outscorearrfels)), int(row["joinid"]), outarrfels)
    outscorearrfels = np.where(((felstotalscorearr > thresholdforminimumtotalscore)&(sonderwaldarr==5)&(felstotalscorearr>=outscorearrfels)), felstotalscorearr, outscorearrfels)
outarrfels=np.where((wasserarr==1),NODATA_value,outarrfels)
outscorearrfels=np.where((wasserarr==1),NODATA_value,outscorearrfels)
outarrfels=np.where((maskarr!=1),NODATA_value,outarrfels)
outscorearrfels=np.where((maskarr!=1),NODATA_value,outscorearrfels)
outarrfels=np.where((sonderwaldarr!=5),NODATA_value,outarrfels)
outscorearrfels=np.where((sonderwaldarr!=5),NODATA_value,outscorearrfels)
convertarrtotif(outarrfels, outdir + "/" + "outarrfels.tif", indatatypeint, referenceraster,NODATA_value)
convertarrtotif((outscorearrfels*100).astype(int), outdir + "/" + "outscorearrfels.tif", indatatypeint, referenceraster, NODATA_value)
joblib.dump(outarrfels,outdir+"/outarrfels.sav")
joblib.dump(outscorearrfels,outdir+"/outscorearrfels.sav")
del scorefelsarr
del felstotalscorearr

# ***********
#iteration through parameter Arve, Waldfoehre, Bergfoehre
#Arve
print("Arve")
outarrarve=np.zeros((nrows, ncols), dtype=int)
outarrarve[:]=NODATA_value
outscorearrarve=np.zeros((nrows, ncols), dtype=float)
parameterdfarven=parameterdf[(parameterdf["M/A Arve"].isin(["x","y"]))]
len(parameterdfarven)
gewichtungsumarve=gewichtunghoehe+gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfarven.iterrows():
    print(row["joinid"])
    scorearvearr=scorearvenxy(row)
    scoreregionhoehenstufearr = scoreregionhoehenstufexy(row)
    scorehoehearr=scorehoehebe(float(row["Hoehe_min"]), float(row["Hoehe_max"]))
    scorelagearr = scorelagebe(row["Lage neu"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"])
    scoreneigungarr=scorehangneigungbe(np.float(row['Neigung_von']), np.float(row['Neigung_bis']))
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]))
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"])
    scorepharr = scorephbe(row["pH"])
    scoretgarr = scoretgbe(row)
    #scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
    arvetotalscorearr=scorearvearr*scoreregionhoehenstufearr*(gewichtunghoehe*scorehoehearr+gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumarve
    outarrarve = np.where(((arvetotalscorearr > thresholdforminimumtotalscore)&(arvenarr==1)&(arvetotalscorearr>=outscorearrarve)), int(row["joinid"]), outarrarve)
    outscorearrarve = np.where(((arvetotalscorearr > thresholdforminimumtotalscore)&(arvenarr==1)&(arvetotalscorearr>=outscorearrarve)), arvetotalscorearr,outscorearrarve)
outarrarve=np.where((wasserarr==1),NODATA_value,outarrarve)
outscorearrarve=np.where((wasserarr==1),NODATA_value,outscorearrarve)
outarrarve=np.where((maskarr!=1),NODATA_value,outarrarve)
outscorearrarve=np.where((maskarr!=1),NODATA_value,outscorearrarve)
outarrarve=np.where((arvenarr!=1),NODATA_value,outarrarve)
outscorearrarve=np.where((arvenarr!=1),NODATA_value,outscorearrarve)
convertarrtotif((outscorearrarve*100.0).astype(int), outdir + "/" + "outscorearrarve.tif", indatatypeint, referenceraster, NODATA_value)
convertarrtotif(outarrarve, outdir + "/" + "outarrarve.tif", indatatypeint, referenceraster,NODATA_value)
joblib.dump(outarrarve,outdir+"/outarrarve.sav")
joblib.dump(outscorearrarve,outdir+"/outscorearrarve.sav")
del arvetotalscorearr
del scorearvearr


#Bergfoehre
print("Bergfoehre")
outarrbf=np.zeros((nrows, ncols), dtype=int)
outarrbf[:]=NODATA_value
outscorearrbf=np.zeros((nrows, ncols), dtype=float)
parameterdfbergfoehre=parameterdf[((parameterdf["M/A Bfö"].isin(["x","y"]))| (parameterdf["Ju Bfö"].isin(["x","y"])))]
len(parameterdfbergfoehre)
gewichtungsumbergfoehre=gewichtunghoehe+gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfbergfoehre.iterrows():
    print(row["joinid"])
    scorebergfoehrearr=scorebergfoehrenxy(row)
    scoreregionhoehenstufearr = scoreregionhoehenstufexy(row)
    scorehoehearr=scorehoehebe(float(row["Hoehe_min"]), float(row["Hoehe_max"]))
    scorelagearr = scorelagebe(row["Lage neu"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"])
    scoreneigungarr=scorehangneigungbe(np.float(row['Neigung_von']), np.float(row['Neigung_bis']))
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]))
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"])
    scorepharr = scorephbe(row["pH"])
    scoretgarr = scoretgbe(row)
    #scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
    bergfoehretotalscorearr=scorebergfoehrearr*scoreregionhoehenstufearr*(gewichtunghoehe*scorehoehearr+gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumbergfoehre
    outarrbf = np.where(((bergfoehretotalscorearr > thresholdforminimumtotalscore)&(bergfoehrenarr==1)&(bergfoehretotalscorearr>=outscorearrbf)), int(row["joinid"]), outarrbf)
    outscorearrbf = np.where(((bergfoehretotalscorearr > thresholdforminimumtotalscore)&(bergfoehrenarr==1)&(bergfoehretotalscorearr>=outscorearrbf)), bergfoehretotalscorearr,outscorearrbf)
outarrbf=np.where((wasserarr==1),NODATA_value,outarrbf)
outscorearrbf=np.where((wasserarr==1),NODATA_value,outscorearrbf)
outarrbf=np.where((maskarr!=1),NODATA_value,outarrbf)
outscorearrbf=np.where((maskarr!=1),NODATA_value,outscorearrbf)
outarrbf=np.where((bergfoehrenarr!=1),NODATA_value,outarrbf)
outscorearrbf=np.where((bergfoehrenarr!=1),NODATA_value,outscorearrbf)
convertarrtotif(outarrbf, outdir + "/" + "outarrbf.tif", indatatypeint, referenceraster, NODATA_value)
convertarrtotif((outscorearrbf*100).astype(int), outdir + "/" + "outscorearrbf.tif", indatatypeint, referenceraster,NODATA_value)
joblib.dump(outarrbf,outdir+"/outarrbf.sav")
joblib.dump(outscorearrbf,outdir+"/outscorearrbf.sav")

#Waldfoehre
print("Waldfoehre")
outarrwf=np.zeros((nrows, ncols), dtype=int)
outarrwf[:]=NODATA_value
outscorearrwf=np.zeros((nrows, ncols), dtype=float)
parameterdfwaldfoehre=parameterdf[((parameterdf["M/A Wfö"].isin(["x","y"])) | (parameterdf["Ju Wfö"].isin(["x","y"])))]
len(parameterdfwaldfoehre)
gewichtungsumwaldfoehre=gewichtunghoehe+gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfwaldfoehre.iterrows():
    print(row["joinid"])
    scorewaldfoehrearr=scorewaldfoehrenxy(row)
    scoreregionhoehenstufearr = scoreregionhoehenstufexy(row)
    scorehoehearr=scorehoehebe(float(row["Hoehe_min"]), float(row["Hoehe_max"]))
    scorelagearr = scorelagebe(row["Lage neu"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"])
    scoreneigungarr=scorehangneigungbe(np.float(row['Neigung_von']), np.float(row['Neigung_bis']))
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]))
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"])
    scorepharr = scorephbe(row["pH"])
    scoretgarr = scoretgbe(row)
    #scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
    waldfoehretotalscorearr=scorewaldfoehrearr*scoreregionhoehenstufearr*(gewichtunghoehe*scorehoehearr+gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumwaldfoehre
    outarrwf = np.where(((waldfoehretotalscorearr > thresholdforminimumtotalscore)&(waldfoehrenarr==1)&(waldfoehretotalscorearr>=outscorearrwf)), int(row["joinid"]), outarrwf)
    outscorearrwf = np.where(((waldfoehretotalscorearr > thresholdforminimumtotalscore)&(waldfoehrenarr==1)&(waldfoehretotalscorearr>=outscorearrwf)), waldfoehretotalscorearr, outscorearrwf)
outarrwf=np.where((wasserarr==1),NODATA_value,outarrwf)
outscorearrwf=np.where((wasserarr==1),NODATA_value,outscorearrwf)
outarrwf=np.where((maskarrbool==True),NODATA_value,outarrwf)
outscorearrwf=np.where((maskarrbool==True),NODATA_value,outscorearrwf)
outarrwf=np.where((waldfoehrenarr!=1),NODATA_value,outarrwf)
outscorearrwf=np.where((waldfoehrenarr!=1),NODATA_value,outscorearrwf)
convertarrtotif((outscorearrwf*100).astype(int), outdir + "/" + "outscorearrwf.tif", indatatypeint, referenceraster, NODATA_value)
convertarrtotif(outarrwf, outdir + "/" + "outarrwf.tif", indatatypeint, referenceraster,NODATA_value)
joblib.dump(outarrwf,outdir+"/outarrwf.sav")
joblib.dump(outscorearrwf,outdir+"/outscorearrwf.sav")
#outarrwf=joblib.load(outdir+"/outarrwf.sav")
#outscorearrwf=joblib.load(outdir+"/outscorearrwf.sav")

## ***********
##Sturztrajektorien
#print("Sturz")
#parameterdfsturz=parameterdf[(parameterdf["Sturztrajektorien"]=="x")]
#len(parameterdfsturz)
#gewichtungfels=gewichtunghoehe+gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
#for index, row in parameterdfsturz.iterrows():
#    print(row["joinid"])
#    scoresturzarr=np.where((sonderwaldarr==1),1.0,0.0)
#    scoreregionhoehenstufearr = scoreregionhoehenstufe(row)
#    scorearvearr=scorearven(row)
#    scorebergfoehrearr = scorebergfoehren(row)
#    scorewaldfoehrearr = scorewaldfoehren(row)
#    scorehoehearr=scorehoehebe(float(row["Hoehe_min"]), float(row["Hoehe_max"]))
#    scorelagearr = scorelagebe(row["Lage neu"])
#    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"])
#    scoreneigungarr=scorehangneigungbe(np.float(row['Neigung_von']), np.float(row['Neigung_bis']))
#    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]))
#    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"])
#    scorepharr = scorephbe(row["pH"])
#    scoretgarr = scoretgbe(row)
#    scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
#    sturztotalscorearr=scoresturzarr*scoreregionhoehenstufearr*scoresonderwaldarr*(gewichtunghoehe*scorehoehearr+gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungfels
#    outarr = np.where((sturztotalscorearr > thresholdforminimumtotalscore), int(row["joinid"]), outarr)
#    outscorearr = np.where((sturztotalscorearr > thresholdforminimumtotalscore), sturztotalscorearr,outscorearr)
#    #outarr=np.where(((sturztotalscorearr>thresholdforminimumtotalscore)&(sturztotalscorearr>=outscorearr)),int(row["joinid"]),outarr)
#    #outscorearr=np.where(((sturztotalscorearr>thresholdforminimumtotalscore)&(sturztotalscorearr>=outscorearr)),sturztotalscorearr,outscorearr)
#outarr=np.where((wasserarr==1),NODATA_value,outarr)
#outscorearr=np.where((wasserarr==1),NODATA_value,outscorearr)
#outarr=np.where((maskarrbool==True),NODATA_value,outarr)
#outscorearr=np.where((maskarrbool==True),NODATA_value,outscorearr)
##sturztotalscorearr=np.where((maskarrbool==True),NODATA_value,sturztotalscorearr)
##convertarrtotif(sturztotalscorearr, outdir + "/" + "sturztotalscorearr.tif", indatatype, referenceraster, NODATA_value)
##convertarrtotif(outarr, outdir + "/" + "sturztotalscorearr.tif", indatatypeint, referenceraster,NODATA_value)
#joblib.dump(outarr,outdir+"/outarr_6.sav")
#joblib.dump(outscorearr,outdir+"/outscorearr_6.sav")
#del sturztotalscorearr
#del scoresturzarr

# ***********
#Sonderwald
print("Sonderwald")
print("6 Auen")
outarrau=np.zeros((nrows, ncols), dtype=int)
outarrau[:]=NODATA_value
outscorearrau=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("6"))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunghoehe+gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==6),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufe(row)
    scorearvearr=scorearven(row)
    scorebergfoehrearr = scorebergfoehren(row)
    scorewaldfoehrearr = scorewaldfoehren(row)
    scorehoehearr=scorehoehebe(float(row["Hoehe_min"]), float(row["Hoehe_max"]))
    scorelagearr = scorelagebe(row["Lage neu"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"])
    scoreneigungarr=scorehangneigungbe(np.float(row['Neigung_von']), np.float(row['Neigung_bis']))
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]))
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"])
    scorepharr = scorephbe(row["pH"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunghoehe*scorehoehearr+gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrau=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==6)& (sonderwaldtotalscorearr >= outscorearrau)),int(row["joinid"]),outarrau)
    outscorearrau=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==6)& (sonderwaldtotalscorearr >= outscorearrau)),sonderwaldtotalscorearr,outscorearrau)
outarrau=np.where((wasserarr==1),NODATA_value,outarrau)
outscorearrau=np.where((wasserarr==1),NODATA_value,outscorearrau)
outarrau=np.where((maskarr!=1),NODATA_value,outarrau)
outscorearrau=np.where((maskarr!=1),NODATA_value,outscorearrau)
outarrau=np.where((sonderwaldarr!=6),NODATA_value,outarrau)
outscorearrau=np.where((sonderwaldarr!=6),NODATA_value,outscorearrau)
convertarrtotif((outscorearrau*100).astype(int), outdir + "/" + "outscorearrau.tif", indatatypeint, referenceraster, NODATA_value)
convertarrtotif(outarrau, outdir + "/" + "outarrau.tif", indatatypeint, referenceraster,NODATA_value)
joblib.dump(outarrau,outdir+"/outarrau.sav")
joblib.dump(outscorearrau,outdir+"/outscorearrau.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr

print("2 Bergsturz")
outarrbs=np.zeros((nrows, ncols), dtype=int)
outarrbs[:]=NODATA_value
outscorearrbs=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("2"))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunghoehe+gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==2),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufe(row)
    scorearvearr=scorearven(row)
    scorebergfoehrearr = scorebergfoehren(row)
    scorewaldfoehrearr = scorewaldfoehren(row)
    scorehoehearr=scorehoehebe(float(row["Hoehe_min"]), float(row["Hoehe_max"]))
    scorelagearr = scorelagebe(row["Lage neu"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"])
    scoreneigungarr=scorehangneigungbe(np.float(row['Neigung_von']), np.float(row['Neigung_bis']))
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]))
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"])
    scorepharr = scorephbe(row["pH"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunghoehe*scorehoehearr+gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrbs=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==2)& (sonderwaldtotalscorearr >= outscorearrbs)),int(row["joinid"]),outarrbs)
    outscorearrbs=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==2)& (sonderwaldtotalscorearr >= outscorearrbs)),sonderwaldtotalscorearr,outscorearrbs)
outarrbs=np.where((wasserarr==1),NODATA_value,outarrbs)
outscorearrbs=np.where((wasserarr==1),NODATA_value,outscorearrbs)
outarrbs=np.where((maskarr!=1),NODATA_value,outarrbs)
outscorearrbs=np.where((maskarr!=1),NODATA_value,outscorearrbs)
outarrbs=np.where((sonderwaldarr!=2),NODATA_value,outarrbs)
outscorearrbs=np.where((sonderwaldarr!=2),NODATA_value,outscorearrbs)
convertarrtotif((outscorearrbs*100).astype(int), outdir + "/" + "outscorearrbergsturz.tif", indatatypeint, referenceraster, NODATA_value)
convertarrtotif(outarrbs, outdir + "/" + "outarrbergsturz.tif", indatatypeint, referenceraster,NODATA_value)
joblib.dump(outarrbs,outdir+"/outarrbs.sav")
joblib.dump(outscorearrbs,outdir+"/outscorearrbs.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr

print("3 Geroell/Schutt")
outarrgeroell=np.zeros((nrows, ncols), dtype=int)
outarrgeroell[:]=NODATA_value
outscorearrgeroell=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("3"))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunghoehe+gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==3),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufe(row)
    scorearvearr=scorearven(row)
    scorebergfoehrearr = scorebergfoehren(row)
    scorewaldfoehrearr = scorewaldfoehren(row)
    scorehoehearr=scorehoehebe(float(row["Hoehe_min"]), float(row["Hoehe_max"]))
    scorelagearr = scorelagebe(row["Lage neu"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"])
    scoreneigungarr=scorehangneigungbe(np.float(row['Neigung_von']), np.float(row['Neigung_bis']))
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]))
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"])
    scorepharr = scorephbe(row["pH"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunghoehe*scorehoehearr+gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrgeroell=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==3)& (sonderwaldtotalscorearr >= outscorearrgeroell)),int(row["joinid"]),outarrgeroell)
    outscorearrgeroell=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==3)& (sonderwaldtotalscorearr >= outscorearrgeroell)),sonderwaldtotalscorearr,outscorearrgeroell)
outarrgeroell=np.where((wasserarr==1),NODATA_value,outarrgeroell)
outscorearrgeroell=np.where((wasserarr==1),NODATA_value,outscorearrgeroell)
outarrgeroell=np.where((maskarr!=1),NODATA_value,outarrgeroell)
outscorearrgeroell=np.where((maskarr!=1),NODATA_value,outscorearrgeroell)
outarrgeroell=np.where((sonderwaldarr!=3),NODATA_value,outarrgeroell)
outscorearrgeroell=np.where((sonderwaldarr!=3),NODATA_value,outscorearrgeroell)
convertarrtotif((outscorearrgeroell*100).astype(int), outdir + "/" + "outscorearrgeroell.tif", indatatypeint, referenceraster, NODATA_value)
convertarrtotif(outarrgeroell, outdir + "/" + "outarrgeroell.tif", indatatypeint, referenceraster,NODATA_value)
joblib.dump(outarrgeroell,outdir+"/outarrgeroell.sav")
joblib.dump(outscorearrgeroell,outdir+"/outscorearrgeroell.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr

print("4 Blockschutt")
outarrblockschutt=np.zeros((nrows, ncols), dtype=int)
outarrblockschutt[:]=NODATA_value
outscorearrblockschutt=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("4"))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunghoehe+gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==4),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufe(row)
    scorearvearr=scorearven(row)
    scorebergfoehrearr = scorebergfoehren(row)
    scorewaldfoehrearr = scorewaldfoehren(row)
    scorehoehearr=scorehoehebe(float(row["Hoehe_min"]), float(row["Hoehe_max"]))
    scorelagearr = scorelagebe(row["Lage neu"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"])
    scoreneigungarr=scorehangneigungbe(np.float(row['Neigung_von']), np.float(row['Neigung_bis']))
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]))
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"])
    scorepharr = scorephbe(row["pH"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunghoehe*scorehoehearr+gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrblockschutt=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==4)& (sonderwaldtotalscorearr >= outscorearrblockschutt)),int(row["joinid"]),outarrblockschutt)
    outscorearrblockschutt=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==4)& (sonderwaldtotalscorearr >= outscorearrblockschutt)),sonderwaldtotalscorearr,outscorearrblockschutt)
outarrblockschutt=np.where((wasserarr==1),NODATA_value,outarrblockschutt)
outscorearrblockschutt=np.where((wasserarr==1),NODATA_value,outscorearrblockschutt)
outarrblockschutt=np.where((maskarr!=1),NODATA_value,outarrblockschutt)
outscorearrblockschutt=np.where((maskarr!=1),NODATA_value,outscorearrblockschutt)
outarrblockschutt=np.where((sonderwaldarr!=4),NODATA_value,outarrblockschutt)
outscorearrblockschutt=np.where((sonderwaldarr!=4),NODATA_value,outscorearrblockschutt)
convertarrtotif((outscorearrblockschutt*100).astype(int), outdir + "/" + "outscorearrblockschutt.tif", indatatypeint, referenceraster, NODATA_value)
convertarrtotif(outarrblockschutt, outdir + "/" + "outarrblockschutt.tif", indatatypeint, referenceraster,NODATA_value)
joblib.dump(outarrblockschutt,outdir+"/outarrblockschutt.sav")
joblib.dump(outscorearrblockschutt,outdir+"/outscorearrblockschutt.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr

print("7 Sumpf")
outarrsumpf=np.zeros((nrows, ncols), dtype=int)
outarrsumpf[:]=NODATA_value
outscorearrsumpf=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("7"))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunghoehe+gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==7),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufe(row)
    scorearvearr=scorearven(row)
    scorebergfoehrearr = scorebergfoehren(row)
    scorewaldfoehrearr = scorewaldfoehren(row)
    scorehoehearr=scorehoehebe(float(row["Hoehe_min"]), float(row["Hoehe_max"]))
    scorelagearr = scorelagebe(row["Lage neu"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"])
    scoreneigungarr=scorehangneigungbe(np.float(row['Neigung_von']), np.float(row['Neigung_bis']))
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]))
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"])
    scorepharr = scorephbe(row["pH"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunghoehe*scorehoehearr+gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrsumpf=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==7)& (sonderwaldtotalscorearr >= outscorearrsumpf)),int(row["joinid"]),outarrsumpf)
    outscorearrsumpf=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==7)& (sonderwaldtotalscorearr >= outscorearrsumpf)),sonderwaldtotalscorearr,outscorearrsumpf)
outarrsumpf=np.where((wasserarr==1),NODATA_value,outarrsumpf)
outscorearrsumpf=np.where((wasserarr==1),NODATA_value,outscorearrsumpf)
outarrsumpf=np.where((maskarr!=1),NODATA_value,outarrsumpf)
outscorearrsumpf=np.where((maskarr!=1),NODATA_value,outscorearrsumpf)
outarrsumpf=np.where((sonderwaldarr!=7),NODATA_value,outarrsumpf)
outscorearrsumpf=np.where((sonderwaldarr!=7),NODATA_value,outscorearrsumpf)
convertarrtotif((outscorearrsumpf*100).astype(int), outdir + "/" + "outscorearrsumpf.tif", indatatypeint, referenceraster, NODATA_value)
convertarrtotif(outarrsumpf, outdir + "/" + "outarrsumpf.tif", indatatypeint, referenceraster,NODATA_value)
joblib.dump(outarrsumpf,outdir+"/outarrsumpf.sav")
joblib.dump(outscorearrsumpf,outdir+"/outscorearrsumpf.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr

print("8 Moor")
outarrmoor=np.zeros((nrows, ncols), dtype=int)
outarrmoor[:]=NODATA_value
outscorearrmoor=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("8"))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunghoehe+gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==8),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufe(row)
    scorearvearr=scorearven(row)
    scorebergfoehrearr = scorebergfoehren(row)
    scorewaldfoehrearr = scorewaldfoehren(row)
    scorehoehearr=scorehoehebe(float(row["Hoehe_min"]), float(row["Hoehe_max"]))
    scorelagearr = scorelagebe(row["Lage neu"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"])
    scoreneigungarr=scorehangneigungbe(np.float(row['Neigung_von']), np.float(row['Neigung_bis']))
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]))
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"])
    scorepharr = scorephbe(row["pH"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunghoehe*scorehoehearr+gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrmoor=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==8)& (sonderwaldtotalscorearr >= outscorearrmoor)),int(row["joinid"]),outarrmoor)
    outscorearrmoor=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==8)& (sonderwaldtotalscorearr >= outscorearrmoor)),sonderwaldtotalscorearr,outscorearrmoor)
outarrmoor=np.where((wasserarr==1),NODATA_value,outarrmoor)
outscorearrmoor=np.where((wasserarr==1),NODATA_value,outscorearrmoor)
outarrmoor=np.where((maskarr!=1),NODATA_value,outarrmoor)
outscorearrmoor=np.where((maskarr!=1),NODATA_value,outscorearrmoor)
outarrmoor=np.where((sonderwaldarr!=8),NODATA_value,outarrmoor)
outscorearrmoor=np.where((sonderwaldarr!=8),NODATA_value,outscorearrmoor)
convertarrtotif((outscorearrmoor*100).astype(int), outdir + "/" + "outscorearrmoor.tif", indatatypeint, referenceraster, NODATA_value)
convertarrtotif(outarrmoor, outdir + "/" + "outarrmoor.tif", indatatypeint, referenceraster,NODATA_value)
joblib.dump(outarrmoor,outdir+"/outarrmoor.sav")
joblib.dump(outscorearrmoor,outdir+"/outscorearrmoor.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr

print("9 Nadelwaelder auf sumpfigen Standorten")
outarrnadelsumpf=np.zeros((nrows, ncols), dtype=int)
outarrnadelsumpf[:]=NODATA_value
outscorearrnadelsumpf=np.zeros((nrows, ncols), dtype=float)
parameterdfsonderwald=parameterdf[(parameterdf["Sonderwald"].astype(str).str.contains("9"))]
len(parameterdfsonderwald)
gewichtungsumsonderwald=gewichtunghoehe+gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfsonderwald.iterrows():
    print(row["joinid"])
    scoresonderwaldarr=np.where((sonderwaldarr==9),1.0,0.0)#scoresonderwaldbe(row["Sonderwald"].replace("0","").replace(" ",""))
    scoreregionhoehenstufearr = scoreregionhoehenstufe(row)
    scorearvearr=scorearven(row)
    scorebergfoehrearr = scorebergfoehren(row)
    scorewaldfoehrearr = scorewaldfoehren(row)
    scorehoehearr=scorehoehebe(float(row["Hoehe_min"]), float(row["Hoehe_max"]))
    scorelagearr = scorelagebe(row["Lage neu"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"])
    scoreneigungarr=scorehangneigungbe(np.float(row['Neigung_von']), np.float(row['Neigung_bis']))
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]))
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"])
    scorepharr = scorephbe(row["pH"])
    scoretgarr = scoretgbe(row)
    sonderwaldtotalscorearr=scoresonderwaldarr*scoreregionhoehenstufearr*(gewichtunghoehe*scorehoehearr+gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumsonderwald
    outarrnadelsumpf=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==9)& (sonderwaldtotalscorearr >= outscorearrnadelsumpf)),int(row["joinid"]),outarrnadelsumpf)
    outscorearrnadelsumpf=np.where(((sonderwaldtotalscorearr>thresholdforminimumtotalscore)&(sonderwaldarr==9)& (sonderwaldtotalscorearr >= outscorearrnadelsumpf)),sonderwaldtotalscorearr,outscorearrnadelsumpf)
outarrnadelsumpf=np.where((wasserarr==1),NODATA_value,outarrnadelsumpf)
outscorearrnadelsumpf=np.where((wasserarr==1),NODATA_value,outscorearrnadelsumpf)
outarrnadelsumpf=np.where((maskarr!=1),NODATA_value,outarrnadelsumpf)
outscorearrnadelsumpf=np.where((maskarr!=1),NODATA_value,outscorearrnadelsumpf)
outarrnadelsumpf=np.where((sonderwaldarr!=9),NODATA_value,outarrnadelsumpf)
outscorearrnadelsumpf=np.where((sonderwaldarr!=9),NODATA_value,outscorearrnadelsumpf)
convertarrtotif((outscorearrnadelsumpf*100).astype(int), outdir + "/" + "outscorearrnadelsumpf.tif", indatatypeint, referenceraster, NODATA_value)
convertarrtotif(outarrnadelsumpf, outdir + "/" + "outarrnadelsumpf.tif", indatatypeint, referenceraster,NODATA_value)
joblib.dump(outarrnadelsumpf,outdir+"/outarrnadelsumpf.sav")
joblib.dump(outscorearrnadelsumpf,outdir+"/outscorearrnadelsumpf.sav")
del sonderwaldtotalscorearr
del scoresonderwaldarr

# ***********
#iteration through parameter table Gebueschwald
print("Gebueschwald")
outarrgebuesch=np.zeros((nrows, ncols), dtype=int)
outarrgebuesch[:]=NODATA_value
outscorearrgebuesch=np.zeros((nrows, ncols), dtype=float)
parameterdfgebueschwald=parameterdf[parameterdf["Gebüschwald"]=="LF"]
len(parameterdfgebueschwald)
gewichtungsumgebueschwald=gewichtunghoehe+gewichtunglage+gewichtungexposition+gewichtungfeuchte+gewichtungneigung+gewichtunggruendigkeit+gewichtungph+gewichtungtg
for index, row in parameterdfgebueschwald.iterrows():
    print(row["joinid"])
    scoreregionhoehenstufearr=scoreregionhoehenstufexy(row)
    scorehoehearr=scorehoehebe(float(row["Hoehe_min"]), float(row["Hoehe_max"]))
    scorelagearr = scorelagebe(row["Lage neu"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"])
    scoreneigungarr=scorehangneigungbe(np.float(row['Neigung_von']), np.float(row['Neigung_bis']))
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]))
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"])
    scorepharr = scorephbe(row["pH"])
    scoretgarr = scoretgbe(row)
    #scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
    scoregebueschwald=np.where((gebueschwaldarr==2),1.0,0.0)
    gebueschwaldtotalscorearr=scoreregionhoehenstufearr*scoregebueschwald*(gewichtunghoehe*scorehoehearr+gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumgebueschwald
    outarrgebuesch=np.where(((gebueschwaldtotalscorearr>thresholdforminimumtotalscore)&(gebueschwaldarr==2)&(gebueschwaldtotalscorearr>outscorearrgebuesch)),int(row["joinid"]),outarrgebuesch)
    outscorearrgebuesch=np.where(((gebueschwaldtotalscorearr>thresholdforminimumtotalscore)&(gebueschwaldarr==2)&(gebueschwaldtotalscorearr>outscorearrgebuesch)),gebueschwaldtotalscorearr,outscorearrgebuesch)
#AV
print("AV")
parameterdfav=parameterdf[parameterdf["Gebüschwald"]=="AV"]
#idvonav=int(parameterdf[parameterdf["BE"]=="AV"]["joinid"].tolist()[0])
#outarr=np.where((gebueschwaldarr==1),idvonav,outarr)
#outscorearr=np.where((gebueschwaldarr==1),1.0,outscorearr)
for index, row in parameterdfav.iterrows():
    print(row["joinid"])
    scoreregionhoehenstufearr=scoreregionhoehenstufexy(row)
    scorehoehearr=scorehoehebe(float(row["Hoehe_min"]), float(row["Hoehe_max"]))
    scorelagearr = scorelagebe(row["Lage neu"])
    scoregruendigkeitarr=scoregruendigkeitbe(row["Gruendigkeit"])
    scoreneigungarr=scorehangneigungbe(np.float(row['Neigung_von']), np.float(row['Neigung_bis']))
    scoreexpositionarr=scoreexpositionbe(float(row["Exposition_von"]), float(row["Exposition_bis"]))
    scorefeuchtearr = scorefeuchtebe(row["Feuchte neu"])
    scorepharr = scorephbe(row["pH"])
    scoretgarr = scoretgbe(row)
    scoresonderwaldarr = scoresonderwaldbe(row["Sonderwald"])
    scoregebueschwald=np.where((gebueschwaldarr==1),1.0,0.0)
    gebueschwaldtotalscorearr=scoreregionhoehenstufearr*scoregebueschwald*(gewichtunghoehe*scorehoehearr+gewichtunglage*scorelagearr+gewichtunggruendigkeit*scoregruendigkeitarr+gewichtungneigung*scoreneigungarr+gewichtungexposition*scoreexpositionarr+gewichtungfeuchte*scorefeuchtearr+gewichtungph*scorepharr+gewichtungtg*scoretgarr)/gewichtungsumgebueschwald
    outarrgebuesch=np.where(((gebueschwaldtotalscorearr>0)&(gebueschwaldarr==1)&(gebueschwaldtotalscorearr>outscorearrgebuesch)),int(row["joinid"]),outarrgebuesch)
    outscorearrgebuesch=np.where(((gebueschwaldtotalscorearr>0)&(gebueschwaldarr==1)&(gebueschwaldtotalscorearr>outscorearrgebuesch)),gebueschwaldtotalscorearr,outscorearrgebuesch)
    #outscorearr = np.where((gebueschwaldtotalscorearr > outscorearr), gebueschwaldtotalscorearr, outscorearrgebuesch)
outarrgebuesch=np.where((wasserarr==1),NODATA_value,outarrgebuesch)
outscorearrgebuesch=np.where((wasserarr==1),NODATA_value,outscorearrgebuesch)
outarrgebuesch=np.where((maskarr!=1),NODATA_value,outarrgebuesch)
outscorearrgebuesch=np.where((maskarr!=1),NODATA_value,outscorearrgebuesch)
outarrgebuesch=np.where((gebueschwaldarr>0),outarrgebuesch, NODATA_value)
outscorearrgebuesch=np.where((gebueschwaldarr>0),outarrgebuesch, NODATA_value)
convertarrtotif((outscorearrgebuesch*100).astype(int), outdir + "/" + "outscorearrgebuesch.tif", indatatypeint, referenceraster, NODATA_value)
convertarrtotif(outarrgebuesch, outdir + "/" + "outarrgebuesch.tif", indatatypeint, referenceraster,NODATA_value)
joblib.dump(outarrgebuesch,outdir+"/outarrgebuesch.sav")
joblib.dump(outscorearrgebuesch,outdir+"/outscorearrgebuesch.sav")
del scoreregionhoehenstufearr
del scorehoehearr
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

#Ueberlagerung
outarr=np.where((outscorearrfels>thresholdforminimumtotalscore),outarrfels,outarr)
outscorearr=np.where((outscorearrfels>thresholdforminimumtotalscore),outscorearrfels,outscorearr)
bfarve=np.where((outscorearrarve>outscorearrbf),outarrarve,outarrbf)
bfarvescore=np.where((outscorearrarve>outscorearrbf),outscorearrarve,outscorearrbf)
outarr=np.where((bfarvescore>thresholdforminimumtotalscore),bfarve,outarr)
outscorearr=np.where((bfarvescore>thresholdforminimumtotalscore),bfarvescore,outscorearr)
outarr=np.where((outscorearrwf>thresholdforminimumtotalscore),outarrwf,outarr)
outscorearr=np.where((outscorearrwf>thresholdforminimumtotalscore),outscorearrwf,outscorearr)
outarr=np.where((outscorearrau>thresholdforminimumtotalscore),outarrau,outarr)
outscorearr=np.where((outscorearrau>thresholdforminimumtotalscore),outscorearrau,outscorearr)
outarr=np.where((outscorearrbs>thresholdforminimumtotalscore),outarrbs,outarr)
outscorearr=np.where((outscorearrbs>thresholdforminimumtotalscore),outscorearrbs,outscorearr)
outarr=np.where((outscorearrgeroell>thresholdforminimumtotalscore),outarrgeroell,outarr)
outscorearr=np.where((outscorearrgeroell>thresholdforminimumtotalscore),outscorearrgeroell,outscorearr)
outarr=np.where((outscorearrblockschutt>thresholdforminimumtotalscore),outarrblockschutt,outarr)
outscorearr=np.where((outscorearrblockschutt>thresholdforminimumtotalscore),outscorearrblockschutt,outscorearr)
outarr=np.where((outscorearrsumpf>thresholdforminimumtotalscore),outarrsumpf,outarr)
outscorearr=np.where((outscorearrsumpf>thresholdforminimumtotalscore),outscorearrsumpf,outscorearr)
outarr=np.where((outscorearrmoor>thresholdforminimumtotalscore),outarrmoor,outarr)
outscorearr=np.where((outscorearrmoor>thresholdforminimumtotalscore),outscorearrmoor,outscorearr)
outarr=np.where((outscorearrnadelsumpf>thresholdforminimumtotalscore),outarrnadelsumpf,outarr)
outscorearr=np.where((outscorearrnadelsumpf>thresholdforminimumtotalscore),outscorearrnadelsumpf,outscorearr)
outarr=np.where((outscorearrgebuesch>thresholdforminimumtotalscore),outarrgebuesch,outarr)
outscorearr=np.where((outscorearrgebuesch>thresholdforminimumtotalscore),outscorearrgebuesch,outscorearr)

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
joblib.dump(outarr,outdir+"/outarr_final.sav")
joblib.dump(outscorearr,outdir+"/outscorearr_final.sav")
joblib.dump(outscorearrint,outdir+"/outscorearrint_final.sav")
convertarrtotif(outarr, outdir+"/"+"bestandortstypen.tif", indatatypeint, referenceraster, NODATA_value)
#convertarrtotif(outscorearr, outdir+"/"+"bestandortstypenscore.tif", indatatype, referenceraster, NODATA_value)
convertarrtotif(outscorearrint, outdir+"/"+"bestandortstypenscoreinteger.tif", indatatypeint, referenceraster, NODATA_value)
#plt.imshow(outarr)
print("modelling done ...")

#convert to shapefile
outarr.dtype
print("convert raster to shapefile and join parameterfile to shapefile ....")
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
bestandortstypengdf=gpd.read_file(outdir+"/"+"bestandortstypen.shp")
bestandortstypengdf.dtypes
#bestandortstypengdf=bestandortstypengdf.astype({'value': 'int64'})
bestandortstypengdf.columns
len(bestandortstypengdf)
#bestandortstypengdf=bestandortstypengdf.rename(columns={"value":"joinid"})
bestandortstypengdf=bestandortstypengdf.rename(columns={"gridcode":"joinid"})
bestandortstypengdf=bestandortstypengdf[bestandortstypengdf["joinid"]>0]
bestandortstypengdf["area"]=bestandortstypengdf["geometry"].area
#bestandortstypengdf=bestandortstypengdf.astype({'joinid': 'int64'})
parameterdf.columns
parameterdf.dtypes
parameterdf=parameterdf.astype({'joinid': 'int64'})
parameterdf.dtypes
parameterdfjoin=parameterdf[["joinid","NrBE","BE","NaiS_LFI_JU","NaiS_LFI_M/A","Anforderungsprofil NaiS"]]
bestandortstypengdfmerge = bestandortstypengdf.merge(parameterdfjoin, on='joinid',how="left")
len(bestandortstypengdfmerge)
bestandortstypengdfmerge.columns
bestandortstypengdfmerge=bestandortstypengdfmerge[(bestandortstypengdfmerge["joinid"]>0)]
len(bestandortstypengdfmerge)
#clip shapefile with forest mask
#waldgdf=gpd.read_file(myworkspace+"/bewaldbuffer20m.shp")
#waldgdf.crs
#len(waldgdf)
#bestandortstypengdfmergeclip=gpd.clip(bestandortstypengdfmerge, waldgdf,keep_geom_type=False)
##bestandortstypengdfmergeclip.to_file(outdir+"/bestandortstypenjoinedclipwald_mitsturztrajektorien.shp")
#bestandortstypengdfmergeclip.to_file(outdir+"/bestandortstypenjoinedclipwald_ohnesturztrajektorien.shp")
#print("shapefile clipped to forest cover")
#bestandortstypengdfmerge.to_file(outdir+"/bestandortstypenjoined_mitsturztrajektorien.shp")
bestandortstypengdfmerge.to_file(outdir+"/bestandortstypenjoined.shp")
print("exported joined  shapefile")
#aggreagte areas
areastatistics=bestandortstypengdfmerge.groupby("BE").agg({'area': 'sum'})
areastatistics.to_excel(outdir+"/areastatistics.xlsx")

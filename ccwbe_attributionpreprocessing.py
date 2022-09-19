import numpy as np
import pandas as pd
import joblib
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
import joblib
from osgeo import osr, gdal
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(2056) #LV95
gtiff_driver=gdal.GetDriverByName("GTiff")


#functions
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

#input workspaces
codeworkspace="C:/DATA/develops/ccwbe"
projectspace="C:/DATA/projects/CCWBE"

#read excel files
naismatrixdf=pd.read_excel(codeworkspace+"/"+"Matrix_Baum_inkl_collin_20210412_mit AbkuerzungenCLEAN.xlsx", dtype="str", engine='openpyxl')
projectionswegedf=pd.read_excel(codeworkspace+"/"+"L_Projektionswege_im_Klimawandel_18022020_export.xlsx", dtype="str", engine='openpyxl')
#naiseinheitenunique=pd.read_excel(projectspace+"/import/"+"nais_einheiten_unique_SG_mf.xlsx", dtype="str", engine='openpyxl')

#read the rasters
#reference tif raster
print("read reference raster")
referenceraster=projectspace+"/GIS/bedem10m.tif"
referencetifraster=gdal.Open(referenceraster)
referencetifrasterband=referencetifraster.GetRasterBand(1)
referencerasterProjection=referencetifraster.GetProjection()
ncols=referencetifrasterband.XSize
nrows=referencetifrasterband.YSize
indatatype=referencetifrasterband.DataType
#indatatypeint=gdal.Open(myworkspace+"/regionen.tif").GetRasterBand(1).DataType
#dhmarr=convert_tif_to_array("D:/CCW20/GIS/dhm25.tif")
NODATA_value=-9999

sloperaster=projectspace+"/GIS/beslopeprz10m.tif"
radiationraster=projectspace+"/GIS/beradyy10m.tif"
lageraster=projectspace+"/GIS/belage.tif"
hsraster=projectspace+"/GIS/bevegetationshoehenstufen.tif"
#slopearr=convert_tif_to_array(projectspace+"/GIS/sgslpprc2m.tif")
#if np.min(slopearr)<NODATA_value:
#    slopearr=np.where(slopearr==np.min(slopearr),NODATA_value,slopearr)


#read shapefile
#stok_gdf=gpd.read_file(projectspace+"/GIS/Modellergebnisse/bestandortstypenjoined.shp")
stok_gdf=gpd.read_file(projectspace+"/GIS/Modellergebnisse/bestandortstypenarrondiertjoined.shp")
#stok_gdf=gpd.read_file(projectspace+"/GIS/stok_gdf_attributed.shp")
len(stok_gdf)
stok_gdf.crs
stok_gdf.set_crs(2056, inplace=True, allow_override=True)
#stok_gdf.plot()
stok_gdf.columns
#change column names
stok_gdf["nais1"]=""
stok_gdf["naisue"]=""
stok_gdf["naismosaic"]=""
stok_gdf["id"]=0
stok_gdf["mo"]=0
stok_gdf["ue"]=0
stok_gdf["id"]=stok_gdf.index

#read other shapefiles
#Tannenareale
taheute=gpd.read_file(projectspace+"/GIS/Tannenareale.shp")
taheute.crs
taheute.columns
#taheute.plot()
taheute.rename(columns={"Code_Ta": "taheute"}, inplace=True)
taheute.drop(columns=['Areal_de', 'Areal_fr', 'Areal_it', 'Areal_en','Shape_Leng','Shape_Area'], inplace=True)
#overlay spatial join
stok_gdfta=gpd.sjoin(stok_gdf,taheute, how='left', op="intersects")
stok_gdfta.drop(columns=['index_right'], inplace=True)
len(stok_gdfta)
stok_gdftagrouped=stok_gdfta[["id","taheute"]].groupby(by=["id"]).min()
#stok_gdftagrouped["joinid"]=stok_gdftagrouped.index
len(stok_gdftagrouped)
stok_gdftagrouped.columns
stok_gdf.columns
stok_gdf=stok_gdf.merge(stok_gdftagrouped, on='id', how='left')
len(stok_gdf)
np.max(stok_gdftagrouped["taheute"])
#stok_gdf.to_file(projectspace+"/GIS/Modellergebnisse/stok_gdf_attributed.shp")
del taheute
del stok_gdftagrouped
del stok_gdfta
#Standortregionen
storeg=gpd.read_file(projectspace+"/GIS/Waldstandortsregionen.shp")
storeg.crs
storeg.columns
#taheute.plot()
storeg.rename(columns={"Subcode": "storeg"}, inplace=True)
storeg.drop(columns=['Region_de', 'Region_fr', 'Region_it', 'Region_en', 'Code', 'Code_Bu', 'Code_Fi', 'Shape_Leng', 'Shape_Area'], inplace=True)
#overlay spatial join
#stok_gdfta=gpd.sjoin_nearest(stok_gdf, taheute, how='left', max_distance=500, distance_col=None)#lsuffix='left', rsuffix='right'
stok_gdfstoreg=gpd.sjoin(stok_gdf,storeg, how='left', op="intersects")
len(stok_gdfstoreg)
stok_gdfstoreggrouped=stok_gdfstoreg[["id","storeg"]].groupby(by=["id"]).min()
#stok_gdftagrouped["joinid"]=stok_gdftagrouped.index
len(stok_gdfstoreggrouped)
stok_gdfstoreggrouped.columns
stok_gdf.columns
stok_gdf=stok_gdf.merge(stok_gdfstoreggrouped, on='id', how='left')#left_on='joinid', right_on='joinid',
len(stok_gdf)
#stok_gdf.to_file(projectspace+"/GIS/Modellergebnisse/stok_gdf_attributed.shp")
del storeg
del stok_gdfstoreggrouped
del stok_gdfstoreg
#Hoehenstufen19611990
hsheute=gpd.read_file(projectspace+"/GIS/vegetationshoehenstufen19611990ensemble_LV95_Bern.shp")
len(hsheute)
#hsheute.plot()


#attribute shapefile
#mean slope in percent
#stok_gdf["meanslopeprc"]=0
#zonstatslope=zonal_stats(stok_gdf, sloperaster,stats="count min mean max median")
zonstatslope=zonal_stats(stok_gdf, sloperaster,stats="mean", nodata=None, all_touched=True)
zonstatslopedf = pd.DataFrame(zonstatslope)
zonstatslopedf.rename(columns={"mean": "meanslopeprc"}, inplace=True)
zonstatslopedf["id"]=zonstatslopedf.index
del zonstatslope

stok_gdf=stok_gdf.merge(zonstatslopedf, on='id', how='left')
len(stok_gdf)
stok_gdf.columns
#stok_gdf.drop(columns=['meanslopeprc_x', 'meanslopeprc_y'], inplace=True)
stok_gdf["slpprzrec"]=0
stok_gdf.loc[stok_gdf["meanslopeprc"]>=70.0,"slpprzrec"]=4
stok_gdf.loc[((stok_gdf["meanslopeprc"]>=60.0)&(stok_gdf["meanslopeprc"]<70.0)),"slpprzrec"]=3
stok_gdf.loc[((stok_gdf["meanslopeprc"]>=20.0)&(stok_gdf["meanslopeprc"]<60.0)),"slpprzrec"]=2
stok_gdf.loc[stok_gdf["meanslopeprc"]<20.0,"slpprzrec"]=1
stok_gdf.columns
del zonstatslopedf

#Lage
#kuppen
#kuppen=gpd.read_file(projectspace+"/GIS/szkuppen.shp")
#kuppen.crs
#kuppen.columns
#stok_gdf["lage"]=0
#stok_gdflage=gpd.sjoin(stok_gdf,kuppen, how='left', op="intersects")#op="within")
#len(stok_gdflage)
#stok_gdflage.loc[stok_gdflage["gridcode"]!=4,["gridcode"]]=0
#stok_gdf.loc[stok_gdflage["gridcode"]==4,["lage"]]=4
##ebene
#stok_gdf.loc[stok_gdf["meanslopeprc"]<10.0,"lage"]=1
##mulden
#mulden=gpd.read_file(projectspace+"/GIS/szmulden.shp")
#mulden.crs
##mulden.set_crs(2056, inplace=True)
#mulden.columns
#stok_gdflage=gpd.sjoin(stok_gdf,mulden, how='left', op="within")
#len(stok_gdflage)
#np.max(stok_gdflage["gridcode"])
#stok_gdf.loc[stok_gdflage["gridcode"]==2,["lage"]]=2
##hang
#stok_gdf.loc[stok_gdf["lage"]==0,"lage"]=3
#np.min(stok_gdf["lage"])
##stok_gdf.to_file(projectspace+"/GIS/Modellergebnisse/stok_gdf_attributed.shp")
#del stok_gdflage
#del kuppen
#del mulden

#Lage
#stok_gdf.drop(columns=['lage'], inplace=True)
#stok_gdf["lage"]=0
zonstatlage=zonal_stats(stok_gdf, lageraster,stats="mean", nodata=None, all_touched=True)
zonstatlagedf = pd.DataFrame(zonstatlage)
len(zonstatlagedf)
#Hang
zonstatlagedf.loc[zonstatlagedf["mean"]<=3.5,"lage"]=3
#Mulden
zonstatlagedf.loc[zonstatlagedf["mean"]<=2.5,"lage"]=2
#Eben
zonstatlagedf.loc[zonstatlagedf["mean"]<=1.5,"lage"]=1
#Kuppen
zonstatlagedf.loc[zonstatlagedf["mean"]>3.5,"lage"]=4
zonstatlagedf.loc[pd.isna(zonstatlagedf["mean"])==True,"lage"]=3
zonstatlagedf["id"]=zonstatlagedf.index
zonstatlagedf.drop(columns=['mean'], inplace=True)
zonstatlagedf=zonstatlagedf.astype({'lage': 'int64'})#.dtypes
zonstatlagedf.dtypes
stok_gdf=stok_gdf.merge(zonstatlagedf, on='id', how='left')
stok_gdf.loc[stok_gdf["meanslopeprc"]<10.0,"lage"]=1

#radiation
#stok_gdf["rad"]=0
zonstatrad=zonal_stats(stok_gdf, radiationraster,stats="mean", nodata=None, all_touched=True)
zonstatraddf = pd.DataFrame(zonstatrad)
zonstatraddf.rename(columns={"mean": "rad"}, inplace=True)
zonstatraddf["id"]=zonstatraddf.index
del zonstatrad
stok_gdf=stok_gdf.merge(zonstatraddf, on='id', how='left')
len(stok_gdf)
stok_gdf.columns
stok_gdf["radiation"]=0
stok_gdf.loc[stok_gdf["rad"]<750412.5805,"radiation"]=-1 #10% quantile
stok_gdf.loc[stok_gdf["rad"]>1297563.512,"radiation"]=1 #90% quantile
stok_gdf.columns
#stok_gdf.to_file(projectspace+"/GIS/Modellergebnisse/stok_gdf_attributed.shp")
del zonstatraddf

#hoehenstufen heute
#stok_gdf.drop(columns=['hsmodcod',"hsmod"], inplace=True)
#stok_gdf["lage"]=0
#stok_gdf.drop(columns=['hsmodcod',"hsmod"], inplace=True)
zonstaths=zonal_stats(stok_gdf, hsraster,stats="mean", nodata=None, all_touched=True)
zonstathsdf = pd.DataFrame(zonstaths)
len(zonstathsdf)
#osa
zonstathsdf.loc[zonstathsdf["mean"]>9.5,"hsmodcod"]=10
#sa
zonstathsdf.loc[zonstathsdf["mean"]<=9.5,"hsmodcod"]=9
#hm
zonstathsdf.loc[zonstathsdf["mean"]<=8.5,"hsmodcod"]=8
#om
zonstathsdf.loc[zonstathsdf["mean"]<=7.5,"hsmodcod"]=6
#um
zonstathsdf.loc[zonstathsdf["mean"]<=5.5,"hsmodcod"]=5
#sm
zonstathsdf.loc[zonstathsdf["mean"]<=4.5,"hsmodcod"]=4
#co
zonstathsdf.loc[zonstathsdf["mean"]<=2.5,"hsmodcod"]=2
#nan
zonstathsdf.loc[pd.isna(zonstathsdf["mean"])==True,"hsmodcod"]=0
zonstathsdf.drop(columns=['mean'], inplace=True)
zonstathsdf["id"]=zonstathsdf.index
zonstathsdf=zonstathsdf.astype({'hsmodcod': 'int64'})#.dtypes
zonstathsdf.dtypes
stok_gdf=stok_gdf.merge(zonstathsdf, on='id', how='left')
#stok_gdf.drop(columns=["lage_y", "lage_x"], inplace=True)
#stok_gdf["lage"]=stok_gdf["lage_y"]
#stok_gdf.columns

#Lage
#stok_gdf["lage"]=0
#zonstatlage=zonal_stats(stok_gdf, lageraster,stats="mean", nodata=None, all_touched=True)
#zonstatlagedf = pd.DataFrame(zonstatlage)
#len(zonstatlagedf)
##Hang
#zonstatlagedf.loc[zonstatlagedf["mean"]<=3.5,"lage"]=3
##Mulden
#zonstatlagedf.loc[zonstatlagedf["mean"]<=2.5,"lage"]=2
##Eben
#zonstatlagedf.loc[zonstatlagedf["mean"]<=1.5,"lage"]=1
##Kuppen
#zonstatlagedf.loc[zonstatlagedf["mean"]>3.5,"lage"]=4
#zonstatlagedf.loc[pd.isna(zonstatlagedf["mean"])==True,"lage"]=3
#zonstatlagedf["id"]=zonstatlagedf.index
#zonstatlagedf.drop(columns=['mean'], inplace=True)
#zonstatlagedf=zonstatlagedf.astype({'lage': 'int64'})#.dtypes
#zonstatlagedf.dtypes
#stok_gdf=stok_gdf.merge(zonstatlagedf, on='id', how='left')
#stok_gdf.loc[stok_gdf["meanslopeprc"]<10.0,"lage"]=1


#hsheute.columns#.tolist()
#hsheute.rename(columns={"Code": "hsmodcod"}, inplace=True)
#hsheute.drop(columns=['Id', 'gridcode','HS_de', 'HS_fr', 'HS_it', 'HS_en', 'Subcode','Kommentar','flaeche'], inplace=True)
#len(stok_gdf)
##hsheute.plot()
##spatial join, attribution of vegetation belts to forest polygons
#stok_gdfhs=gpd.sjoin(stok_gdf,hsheute, how='left', op="intersects")
#len(stok_gdfhs)
#stok_gdfhsgrouped=stok_gdfhs[["joinid","hsmodcod"]].groupby(by=["joinid"]).min()
#stok_gdftagrouped["joinid"]=stok_gdftagrouped.index
#len(stok_gdfhsgrouped)
#stok_gdfhsgrouped.columns
#stok_gdf.columns
#stok_gdf=stok_gdf.merge(stok_gdfhsgrouped, on='joinid', how='left')#left_on='joinid', right_on='joinid',
#len(stok_gdf)
#del stok_gdfhs
#del stok_gdfhsgrouped
np.min(stok_gdf["hsmodcod"])
stok_gdf["tahs"]=""
stok_gdf.loc[stok_gdf["hsmodcod"]==2,"tahs"]="collin"
stok_gdf.loc[stok_gdf["hsmodcod"]==4,"tahs"]="submontan"
stok_gdf.loc[stok_gdf["hsmodcod"]==5,"tahs"]="untermontan"
stok_gdf.loc[stok_gdf["hsmodcod"]==6,"tahs"]="obermontan"
stok_gdf.loc[stok_gdf["hsmodcod"]==8,"tahs"]="hochmontan"
stok_gdf.loc[stok_gdf["hsmodcod"]==9,"tahs"]="subalpin"
stok_gdf.loc[stok_gdf["hsmodcod"]==10,"tahs"]="obersubalpin"
stok_gdf["hsmodcod"].unique().tolist()
stok_gdf.loc[pd.isna(stok_gdf["hsmodcod"])==True,"hsmodcod"]=0
stok_gdf.dtypes
stok_gdf.astype({'hsmodcod': 'int64'})#.dtypes
#stok_gdf.to_file(projectspace+"/GIS/Modellergebnisse/stok_gdf_attributed.shp")
#stok_gdf.to_file(projectspace+"/GIS/Modellergebnisse/stok_gdf_arrondiert_attributed.shp")
#stok_gdf.drop(columns=['hsmod'], inplace=True)



#uebersetzung von NAIS Kombi in NAIS ta und taue
allenaiseinheiteninmodellierung=stok_gdf["nais"].unique().tolist()
len(allenaiseinheiteninmodellierung)

stok_gdf["ta"]=""#tree app
stok_gdf["taue"]=""#tree app uebergang
stok_gdf["tauehs"]=stok_gdf["tahs"]#tree app uebergang hoehenstufe
for naiskombi in allenaiseinheiteninmodellierung:
    if "(" in naiskombi:
        stok_gdf.loc[stok_gdf["nais"] == naiskombi, "ue"] = 1
        naiskombilist=naiskombi.replace("("," ").replace(")","").strip().split()
        stok_gdf.loc[stok_gdf["nais"] == naiskombi, "ta"] = naiskombilist[0]
        stok_gdf.loc[stok_gdf["nais"] == naiskombi, "taue"] = naiskombilist[1]
    elif "/" in naiskombi:
        stok_gdf.loc[stok_gdf["nais"] == naiskombi, "mo"] = 1
        naiskombilist=naiskombi.replace("/"," ").strip().split()
        stok_gdf.loc[stok_gdf["nais"] == naiskombi, "ta"] = naiskombilist[0]
        stok_gdf.loc[stok_gdf["nais"] == naiskombi, "taue"] = naiskombilist[1]
    else:
        stok_gdf.loc[stok_gdf["nais"] == naiskombi, "ta"] = naiskombi

stok_gdf.columns
stok_gdf["radiation"].unique().tolist()
stok_gdf["slpprzrec"].unique().tolist()
stok_gdf["lage"].unique().tolist()
stok_gdf["tahs"].unique().tolist()
stok_gdf["ta"].unique().tolist()
stok_gdf["taue"].unique().tolist()
stok_gdf["tauehs"].unique().tolist()

#stok_gdf.to_file(projectspace+"/GIS/Modellergebnisse/stok_gdf_attributed_nais.shp")
stok_gdf.to_file(projectspace+"/GIS/Modellergebnisse/stok_gdf_arrondiert_attributed_nais.shp")

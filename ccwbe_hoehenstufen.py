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
codeworkspace="C:/DATA/develops/ccwsg"
projectspace="C:/DATA/projects/CCWSG"
db_connection_url = "postgres://postgres:pw@localhost:5432/pythonspatial";
engine = create_engine(db_connection_url)
#conn=psycopg2.connect(db_connection_url)
#conn = psycopg2.connect(host="localhost", port = 5432, database="pythonspatial", user="postgres", password="mypassword")
#conn = psycopg2.connect("dbname=pythonspatial port=5432 user=postgres password=mypassword")
conn = psycopg2.connect(dbname="pythonspatial", host="localhost", user="postgres", password="pw")
cur=conn.cursor()

#read excel files
naismatrixdf=pd.read_excel(codeworkspace+"/"+"Matrix_Baum_inkl_collin_20210412_mit AbkuerzungenCLEAN.xlsx", dtype="str", engine='openpyxl')
projectionswegedf=pd.read_excel(codeworkspace+"/"+"L_Projektionswege_im_Klimawandel_18022020_export.xlsx", dtype="str", engine='openpyxl')
naiseinheitenunique=pd.read_excel(projectspace+"/import/"+"nais_einheiten_unique_SG_mf.xlsx", dtype="str", engine='openpyxl')

#read the rasters
#reference tif raster
print("read reference raster")
referenceraster=projectspace+"/GIS/sgslpprc2m.tif"
referencetifraster=gdal.Open(referenceraster)
referencetifrasterband=referencetifraster.GetRasterBand(1)
referencerasterProjection=referencetifraster.GetProjection()
ncols=referencetifrasterband.XSize
nrows=referencetifrasterband.YSize
indatatype=referencetifrasterband.DataType
#indatatypeint=gdal.Open(myworkspace+"/regionen.tif").GetRasterBand(1).DataType
#dhmarr=convert_tif_to_array("D:/CCW20/GIS/dhm25.tif")
NODATA_value=-9999

sloperaster=projectspace+"/GIS/sgslpprc2m.tif"
radiationraster=projectspace+"/GIS/sgglobradjw.tif"
#slopearr=convert_tif_to_array(projectspace+"/GIS/sgslpprc2m.tif")
#if np.min(slopearr)<NODATA_value:
#    slopearr=np.where(slopearr==np.min(slopearr),NODATA_value,slopearr)


#read shapefile
stok_gdf=gpd.read_file(projectspace+"/GIS/stok_gdf.shp")
#stok_gdf=gpd.read_file(projectspace+"/GIS/stok_gdf_attributed.shp")
len(stok_gdf)
stok_gdf.crs
#stok_gdf.plot()
stok_gdf.columns
#change column names (sg___ are the St Gallen units)
stok_gdf.rename(columns={"nais1": "sg1", "naisueberg": "sgue", "naismosaic":"sgmosaic"}, inplace=True)
stok_gdf["nais1"]=""
stok_gdf["naisue"]=""
stok_gdf["naismosaic"]=""
stok_gdf["joinid"]=0
stok_gdf["joinid"]=stok_gdf.index

#read other shapefiles
#Tannenareale
taheute=gpd.read_file(projectspace+"/import/Tannenareale.shp")
taheute.crs
taheute.columns
#taheute.plot()
taheute.rename(columns={"Code_Ta": "taheute"}, inplace=True)
taheute.drop(columns=['Areal_de', 'Areal_fr', 'Areal_it', 'Areal_en','Shape_Leng','Shape_Area'], inplace=True)
#overlay spatial join
#stok_gdfta=gpd.sjoin_nearest(stok_gdf, taheute, how='left', max_distance=500, distance_col=None)#lsuffix='left', rsuffix='right'
stok_gdfta=gpd.sjoin(stok_gdf,taheute, how='left', op="intersects")
len(stok_gdfta)
stok_gdftagrouped=stok_gdfta[["joinid","taheute"]].groupby(by=["joinid"]).min()
#stok_gdftagrouped["joinid"]=stok_gdftagrouped.index
len(stok_gdftagrouped)
stok_gdftagrouped.columns
stok_gdf.columns
stok_gdf=stok_gdf.merge(stok_gdftagrouped, on='joinid', how='left')#left_on='joinid', right_on='joinid',
len(stok_gdf)
np.max(stok_gdftagrouped["taheute"])
stok_gdf.to_file(projectspace+"/GIS/stok_gdf_attributed.shp")
del taheute
del stok_gdftagrouped
del stok_gdfta
#Standortregionen
storeg=gpd.read_file(projectspace+"/import/Waldstandortsregionen.shp")
storeg.crs
storeg.columns
#taheute.plot()
storeg.rename(columns={"Subcode": "storeg"}, inplace=True)
storeg.drop(columns=['Region_de', 'Region_fr', 'Region_it', 'Region_en', 'Code', 'Code_Bu', 'Code_Fi', 'Shape_Leng', 'Shape_Area'], inplace=True)
#overlay spatial join
#stok_gdfta=gpd.sjoin_nearest(stok_gdf, taheute, how='left', max_distance=500, distance_col=None)#lsuffix='left', rsuffix='right'
stok_gdfstoreg=gpd.sjoin(stok_gdf,storeg, how='left', op="intersects")
len(stok_gdfstoreg)
stok_gdfstoreggrouped=stok_gdfstoreg[["joinid","storeg"]].groupby(by=["joinid"]).min()
#stok_gdftagrouped["joinid"]=stok_gdftagrouped.index
len(stok_gdfstoreggrouped)
stok_gdfstoreggrouped.columns
stok_gdf.columns
stok_gdf=stok_gdf.merge(stok_gdfstoreggrouped, on='joinid', how='left')#left_on='joinid', right_on='joinid',
len(stok_gdf)
stok_gdf.to_file(projectspace+"/GIS/stok_gdf_attributed.shp")
del storeg
del stok_gdfstoreggrouped
del stok_gdfstoreg
#Hoehenstufen19611990
hsheute=gpd.read_file(projectspace+"/GIS/vegetationshoehenstufen19611990clipSGAIAR.shp")
len(hsheute)
#hsheute.plot()


#attribute shapefile
#mean slope in percent
stok_gdf["meanslopeprc"]=0
#zonstatslope=zonal_stats(stok_gdf, referenceraster,stats="count min mean max median")
zonstatslope=zonal_stats(stok_gdf, referenceraster,stats="mean")
i=0
while i < len(stok_gdf):
    stok_gdf.loc[i,"meanslopeprc"]=zonstatslope[i]["mean"]
    i+=1
stok_gdf["slpprzrec"]=0
stok_gdf.loc[stok_gdf["meanslopeprc"]>=70.0,"slpprzrec"]=4
stok_gdf.loc[((stok_gdf["meanslopeprc"]>=60.0)&(stok_gdf["meanslopeprc"]<70.0)),"slpprzrec"]=3
stok_gdf.loc[((stok_gdf["meanslopeprc"]>=20.0)&(stok_gdf["meanslopeprc"]<60.0)),"slpprzrec"]=2
stok_gdf.loc[stok_gdf["meanslopeprc"]<20.0,"slpprzrec"]=1
stok_gdf.columns
del zonstatslope

#for index, row in stok_gdf.iterrows():


#Lage
#kuppen
kuppen=gpd.read_file(projectspace+"/GIS/sgkuppen.shp")
kuppen.crs
kuppen.columns
stok_gdf["lage"]=0
stok_gdflage=gpd.sjoin(stok_gdf,kuppen, how='left', op="within")
len(stok_gdflage)
stok_gdflage.loc[stok_gdflage["gridcode"]!=4,["gridcode"]]=0
stok_gdf.loc[stok_gdflage["gridcode"]==4,["lage"]]=4
#ebene
stok_gdf.loc[stok_gdf["meanslopeprc"]<10.0,"lage"]=1
#mulden
mulden=gpd.read_file(projectspace+"/GIS/sgmuldenLV95.shp")
mulden.crs
#mulden.set_crs(2056, inplace=True)
mulden.columns
mulden.plot()
stok_gdflage=gpd.sjoin(stok_gdf,mulden, how='left', op="within")
len(stok_gdflage)
np.max(stok_gdflage["gridcode"])
stok_gdf.loc[stok_gdflage["gridcode"]==2,["lage"]]=2
#hang
stok_gdf.loc[stok_gdf["lage"]==0,"lage"]=3
np.min(stok_gdf["lage"])
stok_gdf.to_file(projectspace+"/GIS/stok_gdf_attributed.shp")
del stok_gdflage

#radiation
stok_gdf["rad"]=0
#zonstatslope=zonal_stats(stok_gdf, referenceraster,stats="count min mean max median")
zonstatrad=zonal_stats(stok_gdf, radiationraster,stats="mean")
i=0
while i < len(stok_gdf):
    stok_gdf.loc[i,"rad"]=zonstatrad[i]["mean"]
    i+=1
stok_gdf["radiation"]=0
stok_gdf.loc[stok_gdf["rad"]>=147.0,"radiation"]=1 #10% quantile
stok_gdf.loc[stok_gdf["rad"]<=112.0,"radiation"]=-1 #90% quantile
stok_gdf.columns
stok_gdf.to_file(projectspace+"/GIS/stok_gdf_attributed.shp")
del zonstatrad

#hoehenstufen heute
#sqlstatement='SELECT id, "HS_de" AS hsmodheu,"Code" AS hsmodcod,"Subcode" AS hsmodsub,geom FROM public.vegetationshoehenstufen19611990owfix WHERE "HS_de" NOT IN ('+"'-'"+');'
#hsheute=gpd.read_postgis(sqlstatement, engine, geom_col='geom', crs=None, index_col=None, coerce_float=True, parse_dates=None, params=None, chunksize=None)
#hsheute.set_index('id')
hsheute.columns#.tolist()
hsheute.rename(columns={"Code": "hsmodcod"}, inplace=True)
hsheute.drop(columns=['id', 'HS_de', 'HS_fr', 'HS_it', 'HS_en', 'Subcode'], inplace=True)
len(stok_gdf)
#hsheute.plot()
#spatial join, attribution of vegetation belts to forest polygons
stok_gdfhs=gpd.sjoin(stok_gdf,hsheute, how='left', op="intersects")
len(stok_gdfhs)
stok_gdfhsgrouped=stok_gdfhs[["joinid","hsmodcod"]].groupby(by=["joinid"]).min()
#stok_gdftagrouped["joinid"]=stok_gdftagrouped.index
len(stok_gdfhsgrouped)
stok_gdfhsgrouped.columns
stok_gdf.columns
stok_gdf=stok_gdf.merge(stok_gdfhsgrouped, on='joinid', how='left')#left_on='joinid', right_on='joinid',
len(stok_gdf)
del stok_gdfhs
del stok_gdfhsgrouped
stok_gdf["hsmod"]=""
stok_gdf.loc[stok_gdf["hsmodcod"]==2,"hsmod"]="collin"
stok_gdf.loc[stok_gdf["hsmodcod"]==4,"hsmod"]="submontan"
stok_gdf.loc[stok_gdf["hsmodcod"]==5,"hsmod"]="untermontan"
stok_gdf.loc[stok_gdf["hsmodcod"]==6,"hsmod"]="obermontan"
stok_gdf.loc[stok_gdf["hsmodcod"]==8,"hsmod"]="hochmontan"
stok_gdf.loc[stok_gdf["hsmodcod"]==9,"hsmod"]="subalpin"
stok_gdf.loc[stok_gdf["hsmodcod"]==2,"hsmod"]="obersubalpin"
stok_gdf["hsmodcod"].unique().tolist()
stok_gdf.loc[pd.isna(stok_gdf["hsmodcod"])==True,"hsmodcod"]=0
stok_gdf.dtypes
stok_gdf.astype({'hsmodcod': 'int64'})#.dtypes
stok_gdf.to_file(projectspace+"/GIS/stok_gdf_attributed.shp")

#uebersetzung von SG in NAIS
for index, row in naiseinheitenunique.iterrows():
    sg1=row["SG"]
    stok_gdf.loc[stok_gdf["sg1"] == sg1, "nais1"] = row["NaiS"]
    stok_gdf.loc[stok_gdf["sgue"] == sg1, "naisue"] = row["NaiS"]
    stok_gdf.loc[stok_gdf["sgmosaic"] == sg1, "naismosaic"] = row["NaiS"]
stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "19(49)", "nais1"] = "19f"
stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "26h(18w)", "nais1"] = "26w"
stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "9a(10w)", "nais1"] = "9w"
stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "8(26)", "nais1"] = "8S"
stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "8S(8*)", "nais1"] = "8b"
#cases with constraints Bedingungen
stok_gdf.loc[((stok_gdf["sg1"] == "72")&(stok_gdf["storeg"] == "1")), "nais1"] = "72"
stok_gdf.loc[((stok_gdf["sg1"] == "72")&(stok_gdf["storeg"] == "2")), "nais1"] = "59"
stok_gdf.loc[((stok_gdf["sgue"] == "72")&(stok_gdf["storeg"] == "1")), "naisue"] = "72"
stok_gdf.loc[((stok_gdf["sgue"] == "72")&(stok_gdf["storeg"] == "2")), "naisue"] = "59"
stok_gdf.loc[((stok_gdf["sgmosaic"] == "72")&(stok_gdf["storeg"] == "1")), "naismosaic"] = "72"
stok_gdf.loc[((stok_gdf["sgmosaic"] == "72")&(stok_gdf["storeg"] == "2")), "naismosaic"] = "59"
stok_gdf.loc[((stok_gdf["sg1"] == "72L")&(stok_gdf["storeg"] == "1")), "nais1"] = "72G"
stok_gdf.loc[((stok_gdf["sg1"] == "72L")&(stok_gdf["storeg"] == "2")), "nais1"] = "59G"
stok_gdf.loc[((stok_gdf["sgue"] == "72L")&(stok_gdf["storeg"] == "1")), "naisue"] = "72G"
stok_gdf.loc[((stok_gdf["sgue"] == "72L")&(stok_gdf["storeg"] == "2")), "naisue"] = "59G"
stok_gdf.loc[((stok_gdf["sgmosaic"] == "72L")&(stok_gdf["storeg"] == "1")), "naismosaic"] = "72G"
stok_gdf.loc[((stok_gdf["sgmosaic"] == "72L")&(stok_gdf["storeg"] == "2")), "naismosaic"] = "59G"
stok_gdf.loc[((stok_gdf["sg1"] == "72Lae")&(stok_gdf["storeg"] == "1")), "nais1"] = "72Lä"
stok_gdf.loc[((stok_gdf["sg1"] == "72Lae")&(stok_gdf["storeg"] == "2")), "nais1"] = "59Lä"
stok_gdf.loc[((stok_gdf["sgue"] == "72Lae")&(stok_gdf["storeg"] == "1")), "naisue"] = "72Lä"
stok_gdf.loc[((stok_gdf["sgue"] == "72Lae")&(stok_gdf["storeg"] == "2")), "naisue"] = "59Lä"
stok_gdf.loc[((stok_gdf["sgmosaic"] == "72Lae")&(stok_gdf["storeg"] == "1")), "naismosaic"] = "72Lä"
stok_gdf.loc[((stok_gdf["sgmosaic"] == "72Lae")&(stok_gdf["storeg"] == "2")), "naismosaic"] = "59Lä"
stok_gdf.loc[((stok_gdf["sg1"] == "53")&(stok_gdf["hsmod"] == "subalpin")), "nais1"] = "53"
stok_gdf.loc[((stok_gdf["sg1"] == "53")&(stok_gdf["hsmod"].isin(["obermontan","hochmontan"]))), "nais1"] = "53Ta"
stok_gdf.loc[((stok_gdf["sg1"] == "57")&(stok_gdf["meanslopep"] <60)), "nais1"] = "57V"
stok_gdf.loc[((stok_gdf["sg1"] == "57")&(stok_gdf["meanslopep"] >=60)), "nais1"] = "57C"
stok_gdf.loc[((stok_gdf["sg1"] == "60*")&(stok_gdf["hsmod"] == "subalpin")), "nais1"] = "60*"
stok_gdf.loc[((stok_gdf["sg1"] == "60*")&(stok_gdf["hsmod"] == "hochmontan")), "nais1"] = "60*Ta"
stok_gdf.loc[((stok_gdf["sg1"] == "60*L")&(stok_gdf["hsmod"] == "subalpin")), "nais1"] = "60*G"
stok_gdf.loc[((stok_gdf["sg1"] == "60*L")&(stok_gdf["hsmod"] == "hochmontan")), "nais1"] = "60*TaG"

check1=stok_gdf[(pd.isna(stok_gdf["nais1"])==True)][["DTWGEINHEI","sg1"]]
checkue=stok_gdf[((pd.isna(stok_gdf["naisue"])==True)&(pd.isna(stok_gdf["sgue"])==False))][["DTWGEINHEI","sgue"]]
checkmosaic=stok_gdf[((pd.isna(stok_gdf["naismosaic"])==True)&(pd.isna(stok_gdf["sgmosaic"])==False))][["DTWGEINHEI","sgmosaic"]]
len(checkmosaic)
checkmosaic.sgmosaic.unique()


stok_gdf.columns

#attribution of altitudinal vegetation belts from the classification table
#doubthless cases without constraints
stok_gdf["hs1"]=""
stok_gdf["hsue"]=""
stok_gdf["hsmo"]=""
naiseinheitenunique_doubthless=naiseinheitenunique[((pd.isna(naiseinheitenunique["Bedingung"])==True)&(pd.isna(naiseinheitenunique["hs1"])==False))]
hslist=naiseinheitenunique_doubthless["hs1"].unique().tolist()
hslist
for index, row in naiseinheitenunique_doubthless.iterrows():
    sg1=row["SG"]
    stok_gdf.loc[stok_gdf["sg1"] == sg1, "hs1"] = row["hs1"]
    stok_gdf.loc[stok_gdf["sgue"] == sg1, "hsue"] = row["hs1"]
    stok_gdf.loc[stok_gdf["sgmosaic"] == sg1, "hsmo"] = row["hs1"]
stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "19(49)", "hs1"] = "om"
stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "26h(18w)", "hs1"] = "om"
stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "9a(10w)", "hs1"] = "sm"
stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "8(26)", "hs1"] = "um"
stok_gdf.loc[stok_gdf["DTWGEINHEI"] == "8S(8*)", "hs1"] = "um"
#two or more vegetation belts possible
naiseinheitenunique_2hs=naiseinheitenunique[((pd.isna(naiseinheitenunique["Bedingung"])==True)&(pd.isna(naiseinheitenunique["hs1"])==True)&(pd.isna(naiseinheitenunique["hs2"])==False))]
hslist=naiseinheitenunique_2hs["hs2"].unique().tolist()
hslist
stok_gdf.columns
#main forest type
#'sm um'
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=="sm um"]["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="submontan")), "hs1"] = "sm"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=="sm um"]["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hs1"] = "um"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=="sm um"]["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin"]))), "hs1"] = "sm"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=="sm um"]["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["obermontan","hochmontan","subalpin"]))), "hs1"] = "um"
#'sm um om'
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um om']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="submontan")), "hs1"] = "sm"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um om']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hs1"] = "um"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um om']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="obermontan")), "hs1"] = "om"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um om']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin"]))), "hs1"] = "sm"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um om']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["hochmontan","subalpin"]))), "hs1"] = "om"
#'um om'
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om   ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="obermontan")), "hs1"] = "om"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om   ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hs1"] = "um"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om   ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan"]))), "hs1"] = "um"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om   ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["hochmontan","subalpin"]))), "hs1"] = "om"
#'om hm sa'
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="obermontan")), "hs1"] = "om"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="hochmontan")), "hs1"] = "hm"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="subalpin")), "hs1"] = "sa"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan"]))), "hs1"] = "om"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["","obersubalpin"]))), "hs1"] = "sa"
#'om hm'
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="obermontan")), "hs1"] = "om"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="hochmontan")), "hs1"] = "hm"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan"]))), "hs1"] = "om"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["subalpin","obersubalpin",""]))), "hs1"] = "hm"
#'co sm um'
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='co sm um']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="collin")), "hs1"] = "co"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='co sm um']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="submontan")), "hs1"] = "sm"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='co sm um']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hs1"] = "um"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='co sm um']["NaiS"].unique().tolist()))), "hs1"] = "um"
#'hm sa'
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="hochmontan")), "hs1"] = "hm"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="subalpin")), "hs1"] = "sa"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan","obermontan"]))), "hs1"] = "hm"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["obersubalpin",""]))), "hs1"] = "sa"
#'um om hm'
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hs1"] = "um"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="obermontan")), "hs1"] = "om"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="hochmontan")), "hs1"] = "hm"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan"]))), "hs1"] = "um"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["subalpin","obersubalpin",""]))), "hs1"] = "hm"
#'sm um  '
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um  ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="submontan")), "hs1"] = "sm"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um  ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hs1"] = "um"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um  ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin"]))), "hs1"] = "sm"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um  ']["NaiS"].unique().tolist()))), "hs1"] = "um"
#'sm um'
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan"]))), "hs1"] = "sm"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["untermontan", "obermontan", "hochmontan", "subalpin",""]))), "hs1"] = "um"
#'hm sa osa'
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa osa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="hochmontan")), "hs1"] = "hm"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa osa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="subalpin")), "hs1"] = "sa"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa osa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["obersubalpin",""]))), "hs1"] = "osa"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa osa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan","obermontan"]))), "hs1"] = "hm"
#fill remainders
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(["57V","57C", "60*", "53"]))), "hs1"] = "sa"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(["60*Ta","60*TaG"]))), "hs1"] = "hm"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(["59Lä"]))&(stok_gdf["hsmod"].isin(["subalpin", "hochmontan","obermontan","untermontan","submontan"]))), "hs1"] = "sa"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(["59Lä"]))&(stok_gdf["hsmod"].isin(["obersubalpin",""]))), "hs1"] = "osa"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(["72","59"]))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan","obermontan", "hochmontan","subalpin"]))), "hs1"] = "sa"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(["72","59"]))&(stok_gdf["hsmod"].isin(["obersubalpin",""]))), "hs1"] = "osa"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(["53Ta"]))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan","obermontan"]))), "hs1"] = "om"
stok_gdf.loc[((stok_gdf["hs1"]=="")&(stok_gdf["nais1"].isin(["53Ta"]))&(stok_gdf["hsmod"].isin(["hochmontan","subalpin","obersubalpin",""]))), "hs1"] = "hm"
#test1=stok_gdf.loc[((pd.isna(stok_gdf["hs1"])==True)&(stok_gdf["nais1"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="submontan"))]

#uebergang forest type
#'sm um'
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=="sm um"]["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="submontan")), "hsue"] = "sm"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=="sm um"]["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hsue"] = "um"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=="sm um"]["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin"]))), "hsue"] = "sm"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=="sm um"]["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["obermontan","hochmontan","subalpin"]))), "hsue"] = "um"
#'sm um om'
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um om']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="submontan")), "hsue"] = "sm"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um om']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hsue"] = "um"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um om']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="obermontan")), "hsue"] = "om"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um om']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin"]))), "hsue"] = "sm"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um om']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["hochmontan","subalpin"]))), "hsue"] = "om"
#'um om'
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om   ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="obermontan")), "hsue"] = "om"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om   ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hsue"] = "um"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om   ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan"]))), "hsue"] = "um"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om   ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["hochmontan","subalpin"]))), "hsue"] = "om"
#'om hm sa'
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="obermontan")), "hsue"] = "om"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="hochmontan")), "hsue"] = "hm"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="subalpin")), "hsue"] = "sa"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan"]))), "hsue"] = "om"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["","obersubalpin"]))), "hsue"] = "sa"
#'om hm'
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="obermontan")), "hsue"] = "om"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="hochmontan")), "hsue"] = "hm"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan"]))), "hsue"] = "om"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["subalpin","obersubalpin",""]))), "hsue"] = "hm"
#'co sm um'
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='co sm um']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="collin")), "hsue"] = "co"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='co sm um']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="submontan")), "hsue"] = "sm"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='co sm um']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hsue"] = "um"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='co sm um']["NaiS"].unique().tolist()))), "hsue"] = "um"
#'hm sa'
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="hochmontan")), "hsue"] = "hm"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="subalpin")), "hsue"] = "sa"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan","obermontan"]))), "hsue"] = "hm"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["obersubalpin",""]))), "hsue"] = "sa"
#'um om hm'
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hsue"] = "um"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="obermontan")), "hsue"] = "om"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="hochmontan")), "hsue"] = "hm"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan"]))), "hsue"] = "um"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["subalpin","obersubalpin",""]))), "hsue"] = "hm"
#'sm um  '
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um  ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="submontan")), "hsue"] = "sm"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um  ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hsue"] = "um"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um  ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin"]))), "hsue"] = "sm"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um  ']["NaiS"].unique().tolist()))), "hsue"] = "um"
#'sm um'
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan"]))), "hsue"] = "sm"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["untermontan", "obermontan", "hochmontan", "subalpin",""]))), "hsue"] = "um"
#'hm sa osa'
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa osa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="hochmontan")), "hsue"] = "hm"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa osa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="subalpin")), "hsue"] = "sa"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa osa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["obersubalpin",""]))), "hsue"] = "osa"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa osa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan","obermontan"]))), "hsue"] = "hm"
#fill remainders
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(["57V","57C", "60*", "53"]))), "hsue"] = "sa"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(["60*Ta","60*TaG"]))), "hsue"] = "hm"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(["59Lä"]))&(stok_gdf["hsmod"].isin(["subalpin", "hochmontan","obermontan","untermontan","submontan"]))), "hsue"] = "sa"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(["59Lä"]))&(stok_gdf["hsmod"].isin(["obersubalpin",""]))), "hsue"] = "osa"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(["72","59"]))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan","obermontan", "hochmontan","subalpin"]))), "hsue"] = "sa"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(["72","59"]))&(stok_gdf["hsmod"].isin(["obersubalpin",""]))), "hsue"] = "osa"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(["53Ta"]))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan","obermontan"]))), "hsue"] = "om"
stok_gdf.loc[((stok_gdf["hsue"]=="")&(stok_gdf["naisue"].isin(["53Ta"]))&(stok_gdf["hsmod"].isin(["hochmontan","subalpin","obersubalpin",""]))), "hsue"] = "hm"

#mosaic forest type
#'sm um'
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=="sm um"]["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="submontan")), "hsmo"] = "sm"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=="sm um"]["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hsmo"] = "um"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=="sm um"]["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin"]))), "hsmo"] = "sm"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=="sm um"]["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["obermontan","hochmontan","subalpin"]))), "hsmo"] = "um"
#'sm um om'
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um om']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="submontan")), "hsmo"] = "sm"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um om']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hsmo"] = "um"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um om']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="obermontan")), "hsmo"] = "om"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um om']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin"]))), "hsmo"] = "sm"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um om']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["hochmontan","subalpin"]))), "hsmo"] = "om"
#'um om'
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om   ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="obermontan")), "hsmo"] = "om"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om   ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hsmo"] = "um"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om   ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan"]))), "hsmo"] = "um"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om   ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["hochmontan","subalpin"]))), "hsmo"] = "om"
#'om hm sa'
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="obermontan")), "hsmo"] = "om"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="hochmontan")), "hsmo"] = "hm"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="subalpin")), "hsmo"] = "sa"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan"]))), "hsmo"] = "om"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["","obersubalpin"]))), "hsmo"] = "sa"
#'om hm'
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="obermontan")), "hsmo"] = "om"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="hochmontan")), "hsmo"] = "hm"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan"]))), "hsmo"] = "om"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["subalpin","obersubalpin",""]))), "hsmo"] = "hm"
#'co sm um'
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='co sm um']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="collin")), "hsmo"] = "co"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='co sm um']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="submontan")), "hsmo"] = "sm"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='co sm um']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hsmo"] = "um"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='co sm um']["NaiS"].unique().tolist()))), "hsmo"] = "um"
#'hm sa'
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="hochmontan")), "hsmo"] = "hm"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="subalpin")), "hsmo"] = "sa"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan","obermontan"]))), "hsmo"] = "hm"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["obersubalpin",""]))), "hsmo"] = "sa"
#'um om hm'
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hsmo"] = "um"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="obermontan")), "hsmo"] = "om"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="hochmontan")), "hsmo"] = "hm"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan"]))), "hsmo"] = "um"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='um om hm']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["subalpin","obersubalpin",""]))), "hsmo"] = "hm"
#'sm um  '
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um  ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="submontan")), "hsmo"] = "sm"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um  ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="untermontan")), "hsmo"] = "um"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um  ']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin"]))), "hsmo"] = "sm"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um  ']["NaiS"].unique().tolist()))), "hsmo"] = "um"
#'sm um'
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan"]))), "hsmo"] = "sm"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='sm um']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["untermontan", "obermontan", "hochmontan", "subalpin",""]))), "hsmo"] = "um"
#'hm sa osa'
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa osa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="hochmontan")), "hsmo"] = "hm"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa osa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"]=="subalpin")), "hsmo"] = "sa"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa osa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["obersubalpin",""]))), "hsmo"] = "osa"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(naiseinheitenunique_2hs[naiseinheitenunique_2hs["hs2"]=='hm sa osa']["NaiS"].unique().tolist()))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan","obermontan"]))), "hsmo"] = "hm"
#fill remainders
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(["57V","57C", "60*", "53"]))), "hsmo"] = "sa"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(["60*Ta","60*TaG"]))), "hsmo"] = "hm"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(["59Lä"]))&(stok_gdf["hsmod"].isin(["subalpin", "hochmontan","obermontan","untermontan","submontan"]))), "hsmo"] = "sa"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(["59Lä"]))&(stok_gdf["hsmod"].isin(["obersubalpin",""]))), "hsmo"] = "osa"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(["72","59"]))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan","obermontan", "hochmontan","subalpin"]))), "hsmo"] = "sa"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(["72","59"]))&(stok_gdf["hsmod"].isin(["obersubalpin",""]))), "hsmo"] = "osa"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(["53Ta"]))&(stok_gdf["hsmod"].isin(["collin","submontan","untermontan","obermontan"]))), "hsmo"] = "om"
stok_gdf.loc[((stok_gdf["hsmo"]=="")&(stok_gdf["naismosaic"].isin(["53Ta"]))&(stok_gdf["hsmod"].isin(["hochmontan","subalpin","obersubalpin",""]))), "hsmo"] = "hm"





#check empty values
stok_gdf["hs1"].unique().tolist()
checknohs=stok_gdf[stok_gdf["hs1"]==""][["DTWGEINHEI","sg1","nais1", "hs1","hsmod"]]
checknohs=stok_gdf[stok_gdf["hs1"]==""][["nais1","hsmod"]]
len(checknohs)
checknohsunique=checknohs.groupby(by=["nais1","hsmod"])
len(checknohsunique)
checknohs["nais1"].unique().tolist()
checknohsunique["nais1"].unique().tolist()

#hoehenstufe heute definitif
stok_gdf["hsheudef"]=""
stok_gdf.loc[stok_gdf["hs1"] == "co","hsheudef"]="collin"
stok_gdf.loc[stok_gdf["hs1"] == "sm","hsheudef"]="submontan"
stok_gdf.loc[stok_gdf["hs1"] == "um","hsheudef"]="untermontan"
stok_gdf.loc[stok_gdf["hs1"] == "om","hsheudef"]="obermontan"
stok_gdf.loc[stok_gdf["hs1"] == "hm","hsheudef"]="hochmontan"
stok_gdf.loc[stok_gdf["hs1"] == "sa","hsheudef"]="subalpin"
stok_gdf.loc[stok_gdf["hs1"] == "osa","hsheudef"]="obersubalpin"

stok_gdf.to_file(projectspace+"/GIS/stok_gdf_attributed.shp")

#export for monika to refine
stok_gdf.columns
stok_gdf.to_postgis(name="sg_stok_gdf", con=engine)
sqlstatement='SELECT "DTWGEINHEI",mosaic,uebergang,sg1,sgue,sgmosaic,nais1,naisue,naismosaic, hs1,hsue, hsmo FROM public.sg_stok_gdf GROUP BY "DTWGEINHEI",mosaic,uebergang,sg1,sgue,sgmosaic,nais1,naisue,naismosaic, hs1,hsue, hsmo;'
checkallunique=pd.read_sql_query(sqlstatement,con=engine)
len(checkallunique)
checkallunique.to_excel(projectspace+"/export/checkallunique.xlsx")
checkallunique_reduced=checkallunique[((checkallunique["uebergang"]==1) | (checkallunique["mosaic"]==1))]
checkallunique_reduced["tocheck"]=0
checkallunique_reduced.loc[((checkallunique_reduced["uebergang"]==1) & (checkallunique_reduced["hs1"]!=checkallunique_reduced["hsue"])),"tocheck"]=1
checkallunique_reduced.loc[((checkallunique_reduced["mosaic"]==1) & (checkallunique_reduced["hs1"]!=checkallunique_reduced["hsmo"])),"tocheck"]=1
checkallunique_reduced=checkallunique_reduced[checkallunique_reduced["tocheck"]==1]
len(checkallunique_reduced)
checkallunique_reduced.to_excel(projectspace+"/export/checkallunique_reduced.xlsx")
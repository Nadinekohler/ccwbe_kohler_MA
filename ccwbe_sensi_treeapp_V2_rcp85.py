import numpy as np
import pandas as pd
import joblib
import fiona
import geopandas as gpd
import os
import shapefile
import shapely
#import pyshp
from osgeo import ogr
import psycopg2
import sqlalchemy
import geoalchemy2
from sqlalchemy import create_engine
import xlrd
import openpyxl

#input data
codeworkspace="E:/Masterarbeit/ccwbe_kohler_MA/ccwbe_kohler_MA"
projectspace="E:/Masterarbeit/GIS"
naismatrixdf=pd.read_excel(codeworkspace+"/"+"Matrix_Baum_inkl_collin_20210412_mit AbkuerzungenCLEAN.xlsx", dtype="str", engine='openpyxl')
#projectionswegedf=pd.read_excel(codeworkspace+"/"+"L_Projektionswege_im_Klimawandel_18022020_export.xlsx", dtype="str", engine='openpyxl')
#gr_tree_abbreviations_df=pd.read_excel(codeworkspace+"/"+"Baumarten_LFI_export.xls", dtype=str)
#gr_tree_abbreviations_extract_df=gr_tree_abbreviations_df[gr_tree_abbreviations_df["Abkürzung_BK"].notnull()]
#climatescenario="rcp45"
climatescenario="rcp85"

#*************************************
#functions


def heuteempfohlen(naismatrixdf,sto_heute, sto_zukunft):
    treelist=[]
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf=naismatrixdf[naismatrixdf[sto_heute].isin(["a","b","c"])]
        extrdf2=extrdf[extrdf[sto_zukunft].isin(["a","b"])]
        extrdf3=extrdf2[extrdf2["grtreeid"].notnull()]
        treelist=extrdf3["grtreeid"].unique().tolist()#).replace("[","").replace("]","").replace(",","").replace("'","")
        if "" in treelist:
            treelist.remove("")
    else:
        treelist=["notinnaismatrix"]
    return treelist
def heutebedingtempfohlen(naismatrixdf,sto_heute, sto_zukunft):
    treelist=[]
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf=naismatrixdf[naismatrixdf[sto_heute].isin(["a","b","c"])]
        extrdf2=extrdf[extrdf[sto_zukunft]=="c"]
        extrdf3=extrdf2[extrdf2["grtreeid"].notnull()]
        treelist=extrdf3["grtreeid"].unique().tolist()
        if "" in treelist:
            treelist.remove("")
    else:
        treelist=["notinnaismatrix"]
    return treelist
def heutegefaehrdet(naismatrixdf,sto_heute, sto_zukunft):
    treelist=[]
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf=naismatrixdf[naismatrixdf[sto_heute].isin(["a","b","c"])]
        extrdf2=extrdf[extrdf[sto_zukunft]!="a"]
        extrdf3 = extrdf2[extrdf2[sto_zukunft] != "b"]
        extrdf4 = extrdf3[extrdf3[sto_zukunft] != "c"]
        extrdf5=extrdf4[extrdf4["grtreeid"].notnull()]
        treelist=extrdf5["grtreeid"].unique().tolist()
        if "" in treelist:
            treelist.remove("")
    else:
        treelist=["notinnaismatrix"]
    return treelist
def heuteachtung(naismatrixdf,sto_heute, sto_zukunft):
    treelist = []
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf = naismatrixdf[naismatrixdf[sto_heute].isin(["a", "b", "c"])]
        extrdf2 = extrdf[extrdf[sto_zukunft].isin(["a", "b", "c"])]
        if len(extrdf2)>0 and "Ailanthus altissima" in extrdf2["Namelat"].unique().tolist():
            treelist = ["Ailanthus altissima"]
    else:
        treelist=["notinnaismatrix"]
    return treelist
def zukunftempfohlen(naismatrixdf,sto_heute, sto_zukunft):
    treelist=[]
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf=naismatrixdf[naismatrixdf[sto_zukunft].isin(["a","b"])]
        extrdf2 = extrdf[extrdf[sto_heute] != "a"]
        extrdf3 = extrdf2[extrdf2[sto_heute] != "b"]
        extrdf4 = extrdf3[extrdf3[sto_heute] != "c"]
        treelist=extrdf4["grtreeid"].unique().tolist()
        if "" in treelist:
            treelist.remove("")
    else:
        treelist=["notinnaismatrix"]
    return treelist
def zukunftbedingtempfohlen(naismatrixdf,sto_heute, sto_zukunft):
    treelist=[]
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf=naismatrixdf[naismatrixdf[sto_zukunft]=="c"]
        extrdf2 = extrdf[extrdf[sto_heute] != "a"]
        extrdf3 = extrdf2[extrdf2[sto_heute] != "b"]
        extrdf4 = extrdf3[extrdf3[sto_heute] != "c"]
        treelist=extrdf4["grtreeid"].unique().tolist()
        if "" in treelist:
            treelist.remove("")
    else:
        treelist=["notinnaismatrix"]
    return treelist
def zukunftachtung(naismatrixdf,sto_heute, sto_zukunft):
    treelist = []
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf = naismatrixdf[naismatrixdf[sto_zukunft].isin(["a", "b", "c"])]
        extrdf2 = extrdf[extrdf[sto_heute] != "a"]
        extrdf3 = extrdf2[extrdf2[sto_heute] != "b"]
        extrdf4 = extrdf3[extrdf3[sto_heute] != "c"]
        if len(extrdf4)>0 and "Ailanthus altissima" in extrdf4["Namelat"].unique().tolist():
            treelist = ["Ailanthus altissima"]
    else:
        treelist=["notinnaismatrix"]
    return treelist
def logikUebergang(x,y):
    u=""
    if x=="a":
        if y=="a":
            u="a"
        elif y=="b":
            u="a"
        elif y=="c":
            u="b"
        elif y in ["","ex"]:
            u="c"
    elif x=="b":
        if y=="a":
            u="b"
        elif y=="b":
            u="b"
        elif y=="c":
            u="b"
        elif y in ["","ex"]:
            u="c"
    elif x=="c":
        if y=="a":
            u="b"
        elif y=="b":
            u="c"
        elif y=="c":
            u="c"
        elif y in ["","ex"]:
            u=""
    elif x=="ex":
        if y=="a":
            u="c"
        elif y=="b":
            u="c"
        elif y=="c":
            u=""
        elif y in ["","ex"]:
            u=""
    elif x=="":
        if y=="a":
            u="c"
        elif y=="b":
            u="c"
        elif y=="c":
            u=""
        elif y in ["","ex"]:
            u=""
    return u
def uebergangstandortbedeutung(baumart, standort1column, standort2column):
    outue=""
    bedeutung1=str(naismatrix_gr_df.loc[naismatrix_gr_df[naismatrix_gr_df["grtreeid"] == baumart].index, str(standort1column)].values[0])
    bedeutung2=str(naismatrix_gr_df.loc[naismatrix_gr_df[naismatrix_gr_df["grtreeid"] == baumart].index, str(standort2column)].values[0])
    if bedeutung1 in ["a"] and bedeutung2 in ["a", "b"]:
        outue="a"
    elif bedeutung1 in ["a"] and bedeutung2 in ["c"]:
        outue="b"
    elif bedeutung1 in ["a"] and bedeutung2 not in ["a","b","c"]:
        outue="c"
    elif bedeutung1 in ["b"] and bedeutung2 in ["a","b","c"]:
        outue="b"
    elif bedeutung1 in ["b"] and bedeutung2 not in ["a","b","c"]:
        outue="c"
    elif bedeutung1 in ["c"] and bedeutung2 in ["a"]:
        outue="b"
    elif bedeutung1 in ["c"] and bedeutung2 in ["b","c"]:
        outue="c"
    elif bedeutung1 in ["c"] and bedeutung2 not in ["a","b","c"]:
        outue="ex"
    elif bedeutung1 not in ["a","b","c"] and bedeutung2 in ["a","b"]:
        outue="c"
    elif bedeutung1 not in ["a","b","c"] and bedeutung2 in ["c"]:
        outue="ex"
    elif bedeutung1 not in ["a","b","c"] and bedeutung2 not in ["a","b","c"]:
        outue="ex"
    return outue
#*************************************


#******************************************************************************************************
#Baumartenempfehlungen
#******************************************************************************************************
grtreeid_list=naismatrixdf["Abkuerzung"].unique().tolist()
len(grtreeid_list)
grtreeid_list.sort()
gr_treetypes_LFI=grtreeid_list.copy()
for item in ["BUL", "FUL", "KA",""]:#"ES"
    if item in gr_treetypes_LFI:
        gr_treetypes_LFI.remove(item)
len(gr_treetypes_LFI)
joblib.dump(gr_treetypes_LFI, projectspace+"gr_treetypes_LFI.sav")

naismatrix_gr_df = naismatrixdf[naismatrixdf["Abkuerzung"].isin(gr_treetypes_LFI)]
len(naismatrix_gr_df)
joblib.dump(naismatrix_gr_df, projectspace+"naismatrix_gr_df.sav")
ausnahmenausserhalbbuchenareal=['21*', '23*', '25a', '25as', '25b', '25f', '25au', '26', '26h','29A','29C','33a', '33b', '33m', '34a', '34b', '35Q', '40Pt', '40PBlt','42C', '42V', '42t', '46', '46*', '47', '47D', '47M', '47*', '48','91']
buchenarealstoreg=['1','2a','5a','5b', 'J','M','Me']
ausnahmenausserhalbbuchenarealstoreg=['2b','3','4']
buchenausschlusshoehenstufenzukunft=['collin', 'hochmontan','subalpin', 'obersubalpin']
naisstandortstypeninmatrixlist=naismatrix_gr_df.columns.tolist()[8:-1]
ausnahmentannenreliktareal=['21*','23','24','24*','24*Fe','25a','25as','25b','25f','25au','26','26h','26w','27h','27*','33a','33b','33m','34a','34b','35Q','40P','40PBl','40Pt','40PBlt','42V','42t','47H']

#Baumartenbedeutungen
print("Berechne Baumartenbedeutungen ...")
#create a copy of the combinations data frame
combinations_df_bedeutung=combinations_df.copy()
layercolumnslist=combinations_df_bedeutung.columns.tolist()
for col in gr_treetypes_LFI:
    #print(col)
    combinations_df_bedeutung[col+"heu1"]=""
    combinations_df_bedeutung[col + "heu2"] = ""
for col in gr_treetypes_LFI:
    #print(col)
    combinations_df_bedeutung[col+"zuk1"]=""
    combinations_df_bedeutung[col + "zuk2"] = ""

#kein Uebergang
print("kein Uebergang ...")
for standorttyp in naisstandortstypeninmatrixlist:
    #print(standorttyp)
    for baumart in gr_treetypes_LFI:
        baumartbedeutung=naismatrix_gr_df.loc[naismatrix_gr_df[naismatrix_gr_df["Abkuerzung"]==baumart].index,standorttyp].values[0]
        if baumartbedeutung in ["a", "b","c"]:
            combinations_df_bedeutung.loc[combinations_df_bedeutung[combinations_df_bedeutung["ta"]==standorttyp].index, baumart + "heu1"] = baumartbedeutung
            combinations_df_bedeutung.loc[combinations_df_bedeutung[combinations_df_bedeutung["taue"] == standorttyp].index, baumart + "heu2"] = baumartbedeutung
            combinations_df_bedeutung.loc[combinations_df_bedeutung[combinations_df_bedeutung["naiszuk1"] == standorttyp].index, baumart + "zuk1"] = baumartbedeutung
            combinations_df_bedeutung.loc[combinations_df_bedeutung[combinations_df_bedeutung["naiszuk2"] == standorttyp].index, baumart + "zuk2"] = baumartbedeutung
#Uebergang
print("Uebergang ...")
for baumart in gr_treetypes_LFI:
    #print(baumart)
    combinations_df_bedeutung[baumart+"heuUE"]=""
for baumart in gr_treetypes_LFI:
    #print(baumart)
    combinations_df_bedeutung[baumart+"zukUE"]=""
for baumart in gr_treetypes_LFI:
    #print(baumart)
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart+"heu1"].isin(["a"])) & (combinations_df_bedeutung[baumart+"heu2"].isin(["a", "b"])))].index, baumart+"heuUE"] = "a"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "zuk1"].isin(["a"])) & (
        combinations_df_bedeutung[baumart + "zuk2"].isin(["a", "b"])))].index, baumart + "zukUE"] = "a"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "heu1"].isin(["a"])) & (
        combinations_df_bedeutung[baumart + "heu2"].isin(["c"])))].index, baumart + "heuUE"] = "b"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "zuk1"].isin(["a"])) & (
        combinations_df_bedeutung[baumart + "zuk2"].isin(["c"])))].index, baumart + "zukUE"] = "b"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "heu1"].isin(["a"])) & (
        combinations_df_bedeutung[baumart + "heu2"].isin(["", "ex"])))].index, baumart + "heuUE"] = "c"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "zuk1"].isin(["a"])) & (
        combinations_df_bedeutung[baumart + "zuk2"].isin(["", "ex"])))].index, baumart + "zukUE"] = "c"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "heu1"].isin(["b"])) & (
        combinations_df_bedeutung[baumart + "heu2"].isin(["a", "b", "c"])))].index, baumart + "heuUE"] = "b"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "zuk1"].isin(["b"])) & (
        combinations_df_bedeutung[baumart + "zuk2"].isin(["a", "b", "c"])))].index, baumart + "zukUE"] = "b"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "heu1"].isin(["b"])) & (
        combinations_df_bedeutung[baumart + "heu2"].isin(["", "ex"])))].index, baumart + "heuUE"] = "c"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "zuk1"].isin(["b"])) & (
        combinations_df_bedeutung[baumart + "zuk2"].isin(["", "ex"])))].index, baumart + "zukUE"] = "c"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "heu1"].isin(["c"])) & (
        combinations_df_bedeutung[baumart + "heu2"].isin(["a"])))].index, baumart + "heuUE"] = "b"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "zuk1"].isin(["c"])) & (
        combinations_df_bedeutung[baumart + "zuk2"].isin(["a"])))].index, baumart + "zukUE"] = "b"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "heu1"].isin(["c"])) & (
        combinations_df_bedeutung[baumart + "heu2"].isin(["b", "c"])))].index, baumart + "heuUE"] = "c"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "zuk1"].isin(["c"])) & (
        combinations_df_bedeutung[baumart + "zuk2"].isin(["b", "c"])))].index, baumart + "zukUE"] = "c"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "heu1"].isin(["", "ex"])) & (
        combinations_df_bedeutung[baumart + "heu2"].isin(["a", "b"])))].index, baumart + "heuUE"] = "c"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "zuk1"].isin(["", "ex"])) & (
        combinations_df_bedeutung[baumart + "zuk2"].isin(["a", "b"])))].index, baumart + "zukUE"] = "c"

#correct beech vaules in excemption areas
baumart = "BU"
for index, row in combinations_df_bedeutung.iterrows():
    if row["storeg"] in ausnahmenausserhalbbuchenarealstoreg and row["ta"] in ausnahmenausserhalbbuchenareal:
        combinations_df_bedeutung.loc[index, baumart + "heu1"] = ""
        if row["ue"]==1:
            combinations_df_bedeutung.loc[index, baumart + "heuUE"] = ""
    if row["storeg"] in ausnahmenausserhalbbuchenarealstoreg and row["taue"] in ausnahmenausserhalbbuchenareal:
        combinations_df_bedeutung.loc[index, baumart + "heu2"] = ""
        if row["ue"]==1:
            combinations_df_bedeutung.loc[index, baumart + "heuUE"] = ""
    if row["storeg"] in ausnahmenausserhalbbuchenarealstoreg and row["hszukcor"] in ["collin", "hochmontan","subalpin", "obersubalpin"] and row["naiszuk1"] in ausnahmenausserhalbbuchenareal:
        combinations_df_bedeutung.loc[index, baumart + "zuk1"] = ""
        if row["ue"]==1:
            combinations_df_bedeutung.loc[index, baumart + "zukUE"] = ""
    if row["storeg"] in ausnahmenausserhalbbuchenarealstoreg and row["hszukcor"] in ["collin", "hochmontan","subalpin", "obersubalpin"] and row["naiszuk2"] in ausnahmenausserhalbbuchenareal:
        combinations_df_bedeutung.loc[index, baumart + "zuk2"] = ""
        if row["ue"]==1:
            combinations_df_bedeutung.loc[index, baumart + "zukUE"] = ""

#correct TA in excemption areas
baumart = 'TA'
for index, row in combinations_df_bedeutung.iterrows():
    if row["taheute"] == 3 and row["ta"] in ausnahmentannenreliktareal:
        combinations_df_bedeutung.loc[index, baumart + "heu1"] = ""
        if row["ue"]==1:
            combinations_df_bedeutung.loc[index, baumart + "heuUE"] = ""
    if row["subcode"] == 3 and row["ta"] in ausnahmentannenreliktareal:
        combinations_df_bedeutung.loc[index, baumart + "heu1"] = ""
        if row["ue"]==1:
            combinations_df_bedeutung.loc[index, baumart + "heuUE"] = ""
    if row["taheute"] == 3 and row["taue"] in ausnahmentannenreliktareal:
        combinations_df_bedeutung.loc[index, baumart + "heu2"] = ""
        if row["ue"]==1:
            combinations_df_bedeutung.loc[index, baumart + "heuUE"] = ""
    if row["subcode"] == 3 and row["taue"] in ausnahmentannenreliktareal:
        combinations_df_bedeutung.loc[index, baumart + "heu2"] = ""
        if row["ue"]==1:
            combinations_df_bedeutung.loc[index, baumart + "heuUE"] = ""

#rename column TUL-->TU
#combinations_df_bedeutung.rename(columns = {'TULheute1':'TUheute1'}, inplace = True)
#combinations_df_bedeutung.rename(columns = {'TULheute2':'TUheute2'}, inplace = True)
#combinations_df_bedeutung.rename(columns = {'TULzukunft1':'TUzukunft1'}, inplace = True)
#combinations_df_bedeutung.rename(columns = {'TULzukunft2':'TUzukunft2'}, inplace = True)
#combinations_df_bedeutung.rename(columns = {'TULheuteUE':'TUheuteUE'}, inplace = True)
#combinations_df_bedeutung.rename(columns = {'TULzukunftUE':'TUzukunftUE'}, inplace = True)

#combinations_df_bedeutung.to_csv(projectspace+"/"+climatescenario.lower()+"_combinations_df_baumartenbedeutungen.csv")
joblib.dump(combinations_df_bedeutung, projectspace+climatescenario.lower()+"_combinations_df_baumartenbedeutungen.sav")
#combinations_df_bedeutung.to_sql("grnaistahsstoregclip6190"+climatescenario+"_baumartenbedeutungen", engine)
#combinations_df_bedeutung.to_postgis(name="sg_"+climatescenario+'_baumartenbedeutungen', con=engine)
#combinations_df_bedeutung.to_file(projectspace+"/"+"sg_"+climatescenario+"_baumartenbedeutungen.shp")
#combinations_df_bedeutung.to_file(projectspace+"/"+"sg_"+climatescenario+"_baumartenbedeutungen.gpkg", layer="sg_"+climatescenario+"_baumartenbedeutungen", driver="GPKG")
#sqlstatement='SELECT * FROM public.grnaistahsstoregclip6190'+climatescenario+'_zukuenftigestandorte;'
#combinations_df=pd.read_sql_query(sqlstatement,con=engine)
#sqlstatement='SELECT * FROM public.grnaistahsstoregclip6190'+climatescenario+'_baumartenbedeutungen;'
#combinations_df_bedeutung=pd.read_sql_query(sqlstatement,con=engine)
#gr_treetypes_LFI=joblib.load(projectspace+"/"+"gr_treetypes_LFI.sav")
len(combinations_df_bedeutung)
len(combinations_df)

#iterate and calculate Baumartenempfehlungen
print("Berechne Baumartenempfehlungen ...")
#add columns to main layer
combinations_df_baumartenempfehlung=combinations_df_bedeutung.copy()
layercolumnslist=combinations_df_baumartenempfehlung.columns.tolist()
for col in gr_treetypes_LFI:
    combinations_df_baumartenempfehlung[col]=-999

for col in gr_treetypes_LFI:
    #print(col)
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"]==0)&(combinations_df_baumartenempfehlung[col+"zuk1"].isin(["a","b"]))&(combinations_df_baumartenempfehlung[col+"heu1"].isin(["a","b","c"]))),col]=1
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"]==0) & (combinations_df_baumartenempfehlung[col + "zuk1"].isin(["c"])) & (combinations_df_baumartenempfehlung[col + "heu1"].isin(["a", "b", "c"]))), col] = 2
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"]==0) & (~combinations_df_baumartenempfehlung[col + "zuk1"].isin(["a", "b","c"])) & (combinations_df_baumartenempfehlung[col + "heu1"].isin(["a", "b", "c"]))), col] = 3
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"]==0) & (combinations_df_baumartenempfehlung[col + "zuk1"].isin(["a", "b"])) & (~combinations_df_baumartenempfehlung[col + "heu1"].isin(["a", "b", "c"]))), col] = 4
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"]==0) & (combinations_df_baumartenempfehlung[col + "zuk1"].isin(["c"])) & (~combinations_df_baumartenempfehlung[col + "heu1"].isin(["a", "b", "c"]))), col] = 5
    #uebergang
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"] == 1) & (combinations_df_baumartenempfehlung[col + "zukUE"].isin(["a", "b"])) & (combinations_df_baumartenempfehlung[col + "heuUE"].isin(["a", "b", "c"]))), col] = 1
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"] == 1) & (combinations_df_baumartenempfehlung[col + "zukUE"].isin(["c"])) & (combinations_df_baumartenempfehlung[col + "heuUE"].isin(["a", "b", "c"]))), col] = 2
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"] == 1) & (~combinations_df_baumartenempfehlung[col + "zukUE"].isin(["a", "b", "c"])) & (combinations_df_baumartenempfehlung[col + "heuUE"].isin(["a", "b", "c"]))), col] = 3
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"] == 1) & (combinations_df_baumartenempfehlung[col + "zukUE"].isin(["a", "b"])) & (~combinations_df_baumartenempfehlung[col + "heuUE"].isin(["a", "b", "c"]))), col] = 4
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"] == 1) & (combinations_df_baumartenempfehlung[col + "zukUE"].isin(["c"])) & (~combinations_df_baumartenempfehlung[col + "heuUE"].isin(["a", "b", "c"]))), col] = 5

layercolumnslist=combinations_df_baumartenempfehlung.columns.tolist()

#joblib.dump(gr_treetypes_LFI, projectspace+"/"+"gr_treetypes_LFI.sav")
for col in gr_treetypes_LFI:
    #print(col)
    combinations_df_baumartenempfehlung.loc[combinations_df_baumartenempfehlung[col].isna()==True, col]=-999
    if (col + "heu1") in layercolumnslist:
        combinations_df_baumartenempfehlung.drop(columns=col+ "heu1", axis=1, inplace=True)
    if (col + "heu2") in layercolumnslist:
        combinations_df_baumartenempfehlung.drop(columns=col+ "heu2", axis=1, inplace=True)
    if (col + "zuk1") in layercolumnslist:
        combinations_df_baumartenempfehlung.drop(columns=col+ "zuk1", axis=1, inplace=True)
    if (col + "zuk2") in layercolumnslist:
        combinations_df_baumartenempfehlung.drop(columns=col+ "zuk2", axis=1, inplace=True)
    if (col + "heuUE") in layercolumnslist:
        combinations_df_baumartenempfehlung.drop(columns=col+ "heuUE", axis=1, inplace=True)
    if (col + "zukUE") in layercolumnslist:
        combinations_df_baumartenempfehlung.drop(columns=col+ "zukUE", axis=1, inplace=True)

#save
#combinations_df_baumartenempfehlung.to_csv(projectspace+"/"+climatescenario.lower()+"_combinations_df_baumartenempfehlungen.csv")
joblib.dump(combinations_df_baumartenempfehlung, projectspace+"be_"+climatescenario.lower()+"_baumartenempfehlungen.sav")
#combinations_df_baumartenempfehlung.to_sql("li"+climatescenario+"_baumartenempfehlungen", engine)
#combinations_df_baumartenempfehlung.to_postgis(name="sg_"+climatescenario+'_baumartenempfehlungen', con=engine)


#******************************************************************************************************
#Sensitive Standorte
#******************************************************************************************************
print("Berechne Sensitive Standorte ...")
combinations_df_senstivestandorte=combinations_df_bedeutung.copy()
combinations_df_senstivestandorte["sensi3ba"]=-9999
combinations_df_senstivestandorte["sensi4ba"]=-9999
combinations_df_senstivestandorte["lenzukab"]=-9999
combinations_df_senstivestandorte["lenheua"]=-9999
combinations_df_senstivestandorte["lenheub"]=-9999
for index, row in combinations_df_senstivestandorte.iterrows():
    #if index%10000==0:
    #    print(index)
    #print(row["joinstr"])
    uebergang=row["ue"]
    baumartenzukunftablist=[]
    baumartenheutealist = []
    baumartenheuteblist = []
    sensitiverstandort3=row["sensi3ba"]
    sensitiverstandort4=row["sensi4ba"]
    if uebergang==0:
        for baumart in gr_treetypes_LFI:
            if row[baumart+"zuk1"] in ["a","b"]:
                baumartenzukunftablist.append(baumart)
        for baumartheutea in baumartenzukunftablist:
            if row[baumartheutea+"heu1"] =="a":
                baumartenheutealist.append(baumartheutea)
        for baumartheuteb in baumartenzukunftablist:
            if row[baumartheuteb + "heu1"] == "b":
                baumartenheuteblist.append(baumartheuteb)
    elif uebergang==1:
        for baumart in gr_treetypes_LFI:
            if row[baumart+"zukUE"] in ["a", "b"]:
                baumartenzukunftablist.append(baumart)
        for baumartheutea in baumartenzukunftablist:
            if row[baumartheutea+"heuUE"] =="a":
                baumartenheutealist.append(baumartheutea)
        for baumartheuteb in baumartenzukunftablist:
            if row[baumartheuteb + "heuUE"] == "b":
                baumartenheuteblist.append(baumartheuteb)
    if len(baumartenheutealist)>0:
        sensitiverstandort3 = 0
        sensitiverstandort4 = 0
    if len(baumartenheutealist)==0 and len(baumartenheuteblist)>=3:
        sensitiverstandort3 = 1
    elif len(baumartenheutealist)==0 and len(baumartenheuteblist)<3:
        sensitiverstandort3 = 2
    if len(baumartenheutealist)==0 and len(baumartenheuteblist)>=4:
        sensitiverstandort4 = 1
    elif len(baumartenheutealist)==0 and len(baumartenheuteblist)<4:
        sensitiverstandort4 = 2
    combinations_df_senstivestandorte.loc[index, "lenzukab"] = len(baumartenheutealist)
    combinations_df_senstivestandorte.loc[index, "lenheua"] = len(baumartenheutealist)
    combinations_df_senstivestandorte.loc[index, "lenheub"] = len(baumartenheuteblist)
    combinations_df_senstivestandorte.loc[index, "sensi3ba"]=sensitiverstandort3
    combinations_df_senstivestandorte.loc[index, "sensi4ba"] = sensitiverstandort4

#delete columns not needed anymore
columnstodelete=[]
for col in gr_treetypes_LFI:
    #print(col)
    columnstodelete.append(col)
    columnstodelete.append(col+"heu1")
    columnstodelete.append(col + "heu2")
    columnstodelete.append(col + "zuk1")
    columnstodelete.append(col + "zuk2")
    columnstodelete.append(col + "heuUE")
    columnstodelete.append(col + "zukUE")
for col in columnstodelete:
    if col in combinations_df_senstivestandorte.columns.tolist():
        combinations_df_senstivestandorte.drop(columns=col, axis=1, inplace=True)
#layercolumnslist=combinations_df_senstivestandorte.columns.tolist()

#write the output
print("write the output ...")
combinations_df_senstivestandorte.columns
joblib.dump(combinations_df_senstivestandorte, projectspace+"/sg_"+climatescenario.lower()+"_sensitivestandorte.sav")
combinations_df_senstivestandorte.to_file(projectspace+"be_"+climatescenario+"_sensitivestandorte.shp")
#combinations_df_senstivestandorte.to_file(projectspace+"/"+"sg_"+climatescenario+"_sensitivestandorte.gpkg", layer="sg_"+climatescenario+"_sensitivestandorte", driver="GPKG")
combinations_df.columns
#combinations_df.to_file(projectspace+"/Modellergebnisse/"+"be_"+climatescenario+"_zukuenftigestandorte.shp")
#combinations_df.to_file(projectspace+"/"+"sg_"+climatescenario+"_zukuenftigestandorte.gpkg", layer="sg_"+climatescenario+"_zukuenftigestandorte", driver="GPKG")
#combinations_df=joblib.load(projectspace+"/Modellergebnisse/"+climatescenario.lower()+"_combinations_df_futureSTO.sav")
#combinations_df_bedeutung.to_file(projectspace+"/"+"sg_"+climatescenario+"_baumartenbedeutungen.shp")
#combinations_df_bedeutung.to_file(projectspace+"/"+"sg_"+climatescenario+"_baumartenbedeutungen.gpkg", layer="sg_"+climatescenario+"_baumartenbedeutungen", driver="GPKG")
combinations_df_baumartenempfehlung.columns
combinations_df_baumartenempfehlung.to_file(projectspace+"be_"+climatescenario+"_baumartenempfehlungen.shp")
#combinations_df_baumartenempfehlung.to_file(projectspace+"/"+"sg_"+climatescenario+"_baumartenempfehlungen.gpkg", layer="sg_"+climatescenario+"_baumartenempfehlungen", driver="GPKG")




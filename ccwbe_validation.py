import os
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from osgeo import osr, gdal
import fiona
import geopandas as gpd
import os
#import shapefile
import shapely
#import pyshp
from osgeo import ogr
import xlrd
import openpyxl
import shapely.geometry as sg

# *************************************************************
#environment settings
#myworkspace="D:/CCWBE/GIS"
myworkspace="C:/DATA/projects/CCWBE/GIS"
codespace="C:/DATA/develops/ccwbe"
outdir=myworkspace+"/Modellergebnisse"


#Vergleich mit NAIS_LFI
mod_intsct_naislfi=gpd.read_file(outdir+"/"+"bestandortstypenjoined_intsct_naislfi.shp")
mod_intsct_naislfi.columns
mod_intsct_naislfi.crs
len(mod_intsct_naislfi)
mod_intsct_naislfi["nais1"]=""
mod_intsct_naislfi["nais2"]=""
mod_intsct_naislfi["nais3"]=mod_intsct_naislfi["NAIS_TYPC"]

#join nais codes
naisuebersetzungdf=pd.read_excel(codespace+"/"+"UebersetzungNAIScodeNAISstandortstyp.xlsx", dtype="str", engine='openpyxl')
for index, row in naisuebersetzungdf.iterrows():
    naiscode=row["NaisCode"].replace(" ","")
    naistyp=row["NaisSTO"].replace(" ","")
    mod_intsct_naislfi.loc[mod_intsct_naislfi["NAIS_TYP"]==naiscode, "nais1"] = naistyp
    mod_intsct_naislfi.loc[mod_intsct_naislfi["NAISTYPUEB"] == naiscode, "nais2"] = naistyp

mod_intsct_naislfi=mod_intsct_naislfi[((mod_intsct_naislfi ["NAIS_TYPC"].isna()==False)&(mod_intsct_naislfi ["Anforderun"].isna()==False))]
mod_intsct_naislfi["hit"]=0
for index, row in mod_intsct_naislfi.iterrows():
    if row["nais1"] in str(row["Anforderun"]).strip().split():
        mod_intsct_naislfi.loc[index, "hit"]=1
    if row["nais2"] in str(row["Anforderun"]).strip().split():
        mod_intsct_naislfi.loc[index, "hit"]=1
    if row["nais3"] in str(row["Anforderun"]).strip().split():
        mod_intsct_naislfi.loc[index, "hit"]=1
print("hits: "+str(len(mod_intsct_naislfi[mod_intsct_naislfi["hit"]==1]))+ " of "+ str(len(mod_intsct_naislfi)))
validationJU=mod_intsct_naislfi[(mod_intsct_naislfi ["region"]=="Berner Jura")]
validationM=mod_intsct_naislfi[(mod_intsct_naislfi ["region"]=="Mittelland")]
validationA=mod_intsct_naislfi[(mod_intsct_naislfi ["region"]=="Oberland")]
hitrateJU=sum(validationJU[validationJU["hit"]==1]["area"])/sum(validationJU["area"])
print("hitrate NAiS LFI Jura: "+str(hitrateJU*100))
hitrateM=sum(validationM[validationM["hit"]==1]["area"])/sum(validationM["area"])
print("hitrate NAiS LFI Mittelland: "+str(hitrateM*100))
hitrateA=sum(validationA[validationA["hit"]==1]["area"])/sum(validationA["area"])
print("hitrate NAiS LFI Oberland: "+str(hitrateA*100))
mod_intsct_naislfi.to_file(outdir+"/"+"bestandortstypenjoined_intsct_naislfi_hits.shp")

#Excel file mit den Uebersetzungen der Berner Standortkartierung in vereinfachte Berner Einheiten
uebersetzungdf=pd.read_excel(codespace+"/"+"StandortskarteBern_AWN_BE_uniqueentriesEINHEIT_bh.xlsx", dtype="str", engine='openpyxl')
uebersetzungdf=uebersetzungdf.rename(columns={"EINHEIT2":"BEvereinf"})
uebersetzungdf.columns
uebersetzungdf.dtypes
#model parameter file
parameterdf=pd.read_excel(codespace+"/"+"Anhang1_Parameter_Waldstandorte_BE_20220515.xlsx", dtype="str", engine='openpyxl')
parameterdf.columns
parameterdf=parameterdf.rename(columns={"Nr. BE (Achtung, z.T. doppelte Nummern)":"NrBE","Sonderwald (Kat. 1 und 5 weglassen; 3* = Schutt/Geröll bei Bach)": "Sonderwald", "x = Einheit v.a. auf Sturztrajektorien vorkommend (doppelt gewichten bei Sturztraj.)": "Sturztrajektorien",'nur Einheiten mit "x" oder "s" auf Fels modellieren (x = doppelt gewichten, s = nur halb gewichten)':"Fels"})
parameterdf=parameterdf.rename(columns={"Korrekturen Tongehalt Jura, Mittelland":"TongehaltJuraMittelland","Korrekturen Tongehalt Oberland, basierend auf den Korrekturen Jura":"TongehaltOberland"})
len(parameterdf)
parameterdf.dtypes

#Kartierung Bern
kartierungbern=gpd.read_file(myworkspace+"/"+"KAWA_STAO_STA.shp")
len(kartierungbern)
#Join Uebersetzungstabelle an Kartierung Bern
kartierungbern = kartierungbern.merge(uebersetzungdf, on='EINHEIT',how="left")
kartierungbern=kartierungbern[["EINHEIT","BEvereinf","geometry"]]
kartierungbern.columns
#join NaiS-Typ an Berner Kartierung
parameterdf=parameterdf[['BE','NaiS_LFI_JU', 'NaiS_LFI_M/A']]
parameterdf=parameterdf.rename(columns={'BE':'BEvereinf','NaiS_LFI_JU':'kartJU', 'NaiS_LFI_M/A':'kartMA'})
kartierungbern = kartierungbern.merge(parameterdf, on='BEvereinf',how="left")
kartierungbern.columns
#kartierungbern.to_file(myworkspace+"/"+"kartierungbern_joined.shp")

#Read Modellierung intersected Kartierung BE
mod_intsct_kartbern=gpd.read_file(outdir+"/"+"bestandortstypenjoined_intsct_kartierungbern.shp")
mod_intsct_kartbern.columns
mod_intsct_kartbern=mod_intsct_kartbern[['joinid', 'area', 'BE', 'NaiS_LFI_J','NaiS_LFI_M', 'Anforderun', 'region', 'EINHEIT','BEvereinf', 'kartJU', 'kartMA','geometry']]
mod_intsct_kartbern=mod_intsct_kartbern.rename(columns={"NaiS_LFI_J":"modJU", "NaiS_LFI_M":"modMA"})
#update area
mod_intsct_kartbern["area"]=mod_intsct_kartbern["geometry"].area

#zwei Spalten fuer den hit/nicht-hit
mod_intsct_kartbern["hitJU"]=0
mod_intsct_kartbern["hitMA"]=0
mod_intsct_kartbern["hit"]=0
mod_intsct_kartbern.columns
len(mod_intsct_kartbern)
#check ob Kartierung Bern vereinfacht uebersetzt in Nais in Anforderungsprofil ist
mod_intsct_kartbern=mod_intsct_kartbern[mod_intsct_kartbern["kartMA"].isna()==False]
mod_intsct_kartbern=mod_intsct_kartbern[mod_intsct_kartbern["kartJU"].isna()==False]
for index, row in mod_intsct_kartbern.iterrows():
    kartMA=str(row["kartMA"]).replace("("," ").replace(")","").replace("/"," ").strip().split()
    kartJU=str(row["kartJU"]).replace("(", " ").replace(")", "").replace("/", " ").strip().split()
    for item in kartMA:
        if item!=None and item.lower() in str(row["Anforderun"]).lower().strip().split():
            mod_intsct_kartbern.loc[index, "hitMA"]=1
            mod_intsct_kartbern.loc[index, "hit"] = 1
    for item in kartJU:
        if item!=None and item.lower() in str(row["Anforderun"]).lower().strip().split():
            mod_intsct_kartbern.loc[index, "hitJU"]=1
            mod_intsct_kartbern.loc[index, "hit"] = 1
#flaechengewichtung der hits
mod_intsct_kartbern["hitMAweight"]=mod_intsct_kartbern["area"]*mod_intsct_kartbern["hitMA"]
mod_intsct_kartbern["hitJUweight"]=mod_intsct_kartbern["area"]*mod_intsct_kartbern["hitJU"]
validationJU=mod_intsct_kartbern[((mod_intsct_kartbern ["region"]=="Berner Jura")&(mod_intsct_kartbern ["kartJU"].isna()==False)&(mod_intsct_kartbern ["Anforderun"].isna()==False))]
validationM=mod_intsct_kartbern[((mod_intsct_kartbern ["region"]=="Mittelland")&(mod_intsct_kartbern ["kartMA"].isna()==False)&(mod_intsct_kartbern ["Anforderun"].isna()==False))]
validationA=mod_intsct_kartbern[((mod_intsct_kartbern ["region"]=="Oberland")&(mod_intsct_kartbern ["kartMA"].isna()==False)&(mod_intsct_kartbern ["Anforderun"].isna()==False))]
hitrateJU=sum(validationJU["hitJUweight"])/sum(validationJU["area"])
print("hitrate Kartierung Bern Jura: "+str(hitrateJU*100))
hitrateM=sum(validationM["hitMAweight"])/sum(validationM["area"])
print("hitrate Kartierung Bern Mittelland: "+str(hitrateM*100))
hitrateA=sum(validationA["hitMAweight"])/sum(validationA["area"])
print("hitrate Kartierung Bern Alpen: "+str(hitrateA*100))
mod_intsct_kartbern.to_file(outdir+"/"+"bestandortstypenjoined_intsct_kartierungbern_hits.shp")

#Standortkarte Luzern
mod_intsct_kartluzern=gpd.read_file(outdir+"/"+"bestandortstypenjoined_intsct_kartierungluzern.shp")
mod_intsct_kartluzern["area"]=mod_intsct_kartluzern["geometry"].area
mod_intsct_kartluzern.columns
mod_intsct_kartluzern ["hit"]=0
len(mod_intsct_kartluzern)
for index, row in mod_intsct_kartluzern.iterrows():
    if row["NAIS1"]!=None and row["NAIS1"].lower() in str(row["Anforderun"]).lower().strip().split():
        mod_intsct_kartluzern.loc[index, "hit"]=1
    if row["NAIS2"]!=None and row["NAIS2"].lower() in str(row["Anforderun"]).lower().strip().split():
        mod_intsct_kartluzern.loc[index, "hit"]=1
    if row["STO1_TXT"]!=None and row["STO1_TXT"].lower() in str(row["Anforderun"]).lower().strip().split():
        mod_intsct_kartluzern.loc[index, "hit"]=1
    if row["STO2_TXT"]!=None and row["STO2_TXT"].lower() in str(row["Anforderun"]).lower().strip().split():
        mod_intsct_kartluzern.loc[index, "hit"]=1
    if row["STO3_TXT"]!=None and row["STO3_TXT"].lower() in str(row["Anforderun"]).lower().strip().split():
        mod_intsct_kartluzern.loc[index, "hit"]=1
    if row["STO4_TXT"]!=None and row["STO4_TXT"].lower() in str(row["Anforderun"]).lower().strip().split():
        mod_intsct_kartluzern.loc[index, "hit"]=1

flaechemithit=np.sum(mod_intsct_kartluzern[mod_intsct_kartluzern["hit"]==1]["area"])
flaechetotal=np.sum(mod_intsct_kartluzern["area"])
hitrateLU=flaechemithit/flaechetotal*100
print("hitrate Kartierung LU: "+str(hitrateLU))
mod_intsct_kartluzern.to_file(outdir+"/"+"bestandortstypenjoined_intsct_kartierungluzern_hits.shp")

#Standortkarte Jura
mod_intsct_kartjura=gpd.read_file(outdir+"/"+"bestandortstypenjoined_intsct_kartierungjura.shp")
mod_intsct_kartjura["area"]=mod_intsct_kartjura["geometry"].area
mod_intsct_kartjura=mod_intsct_kartjura[mod_intsct_kartjura["nais1"]!="_"]
mod_intsct_kartjura.columns
mod_intsct_kartjura["hit"]=0
len(mod_intsct_kartjura)
for index, row in mod_intsct_kartjura.iterrows():
    if row["nais1"].lower() in str(row["Anforderun"]).lower().strip().split():
        mod_intsct_kartjura.loc[index, "hit"]=1
    if row["naisue"].lower() in str(row["Anforderun"]).lower().strip().split():
        mod_intsct_kartjura.loc[index, "hit"]=1
flaechemithit=np.sum(mod_intsct_kartjura[mod_intsct_kartjura["hit"]==1]["area"])
flaechetotal=np.sum(mod_intsct_kartjura["area"])
hitrateJU=flaechemithit/flaechetotal*100
print("hitrate Kartierung JU: "+str(hitrateJU))
mod_intsct_kartjura[['geometry','BE','NaiS_LFI_J', 'Anforderun','nais1', 'naisue','hit']].to_file(outdir+"/"+"bestandortstypenjoined_intsct_kartierungjura_hits.shp")
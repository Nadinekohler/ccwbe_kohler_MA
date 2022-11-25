# Titel: Anhängen der Parameter an die Modellierung der zukünftigen Standorttypen via joinid

# Autorin: Nadine KOhler
# Stand: 25.11.2022

# Masterarbeit:
# Die Entwicklung des Waldes im Kanton Bern basierend auf der klimabedingten Verschiebung der Vegetationshöhenstufen
# Eine partizipative Modellierung von Berner Waldstandorttypen für die Periode 2070-99


# Wichtig!
# Bevor dieses Skript gerechnet werden kann, muss die Modellierung "ccwbe_standorthinweiskarteV2_rcp85" und die Schritte in der ArcMap Toolbox "postprocessing2_rcp85" durchgerechnet worden sein.
# In der Toolbox werden die TIF's aus der Modellierung in Shapefiles umgewandelt und die Regionen den joinids zugeschrieben. Hier werden dann weitere wichtige Parameter aus der Parametertabelle den joinids angehängt.

# *************************************************************
# Import Module

import pandas as pd
import geopandas as gpd
import shapefile

# *************************************************************
# Definition Arbeitsumgebung
print("define workspace")
myworkspace="E:/Masterarbeit/GIS/Modellergebnisse_221118"
myresults="E:/Masterarbeit/GIS/Modellergebnisse_221118"
codespace="E:/Masterarbeit/Parametertabelle"
outdir=myresults

# *************************************************************
# Link zur Parametertabelle

print("read parameter table")
parameterdf=pd.read_excel(codespace+"/"+"Parametertabelle_2070-99_Waldstandorte_BE_221118.xlsx", dtype="str", engine='openpyxl')
parameterdf.columns

# *************************************************************
# Einlesen der Shapefiles

print("read shapefiles")
bestandortstypengdf=(myresults+"/bestandortstypen_rcp85.shp")
bestandortstypenarrondiertgdf=(myresults+"/bestandortstypenarrondiert_rcp85.shp")

# *************************************************************
# Anhängen der Parameter an die Standorttypen

print("join parameter table to Shapefile")
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
parameterdfjoin=parameterdf[["joinid","NrBE","BE","NaiS_LFI_JU","NaiS_LFI_M/A","BE_zukunft","Anford_kol"]]
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
print("exported joined shapefile")

# *************************************************************
# Anhängen der Parameter an das arrondierte Shapefile

print("join parameter to cleaned Shapefile")
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
print("exported clean and joined shapefile")

# *************************************************************
# Berechnung der Arealstatistik

print("calculate area statistics")
bestandortstypengdfmergeJURA=bestandortstypengdfmerge[bestandortstypengdfmerge["regionid"]==1]
bestandortstypengdfmergeMittelland=bestandortstypengdfmerge[bestandortstypengdfmerge["regionid"]==2]
bestandortstypengdfmergeAlpen=bestandortstypengdfmerge[bestandortstypengdfmerge["regionid"]==3]

areastatisticsJura=bestandortstypengdfmergeJURA.groupby(["BE_zukunft"]).agg({'area': 'sum'})
areastatisticsMittelland=bestandortstypengdfmergeMittelland.groupby(["BE_zukunft"]).agg({'area': 'sum'})
areastatisticsAlpen=bestandortstypengdfmergeAlpen.groupby(["BE_zukunft"]).agg({'area': 'sum'})
areastatisticsJura["hektar"]=areastatisticsJura["area"]/10000.0
areastatisticsMittelland["hektar"]=areastatisticsMittelland["area"]/10000.0
areastatisticsAlpen["hektar"]=areastatisticsAlpen["area"]/10000.0

areastatisticsJura["BEeinheit"] = areastatisticsJura.index
areastatisticsMittelland["BEeinheit"] = areastatisticsMittelland.index
areastatisticsAlpen["BEeinheit"] = areastatisticsAlpen.index

haeufigkeitdf=pd.read_excel(codespace+"/"+"Haeufigkeit_Schaetzung_def_20220314.xlsx", dtype="str", engine='openpyxl') #Was passiert mit den Kollinen Einheiten?
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
areastatisticsAlpen=areastatisticsAlpen.merge(joinA[["BEeinheit","Priorisierung Alpen"]], on='BEeinheit',how="left")

areastatisticsJura.to_excel(outdir+"/areastatisticsJura_rcp85.xlsx")
areastatisticsMittelland.to_excel(outdir+"/areastatisticsMittelland_rcp85.xlsx")
areastatisticsAlpen.to_excel(outdir+"/areastatisticsAlpen_rcp85.xlsx")
print("exported excel")

print("model finished")
# Titel: xx

# Autorin: Nadine KOhler
# Stand: 25.11.2022

# Masterarbeit:
# Die Entwicklung des Waldes im Kanton Bern basierend auf der klimabedingten Verschiebung der Vegetationshöhenstufen
# Eine partizipative Modellierung von Berner Waldstandorttypen für die Periode 2070-99


# *************************************************************
# Schritt 1: Import Module
import pandas as pd
import geopandas as gpd
import shapefile
import fiona
from pySankey.sankey import sankey
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

# *************************************************************
# Schritt 2: Definition Arbeitsumgebung
print("define workspace")
myresults="E:/Masterarbeit/GIS/Modellergebnisse_221206"
myworkspace="E:/Masterarbeit/GIS"
mycodespace="E:/Masterarbeit/ccwbe_kohler_MA/ccwbe_kohler_MA"
outdir="E:/Masterarbeit/Chord_diagrams/Auswertungen"

einheitendf=pd.read_excel(mycodespace+"/"+"Nodes_Chord_diagram.xlsx")
einheitendf.columns
einheitendf=pd.DataFrame(einheitendf,columns=['Berner Einheiten'])
einheitendf

# *************************************************************
# MITTELLAND


# *************************************************************
# Schritt 3: Einlesen der Shapefiles
print("Shapefiles Standorttypen einlesen, Header rows umbennenen")

BEdire45ML=gpd.read_file(myresults+"/"+"bedire45ML.shp", dtype="str")
BEtree45ML=gpd.read_file(myresults+"/"+"betree45ML.shp", dtype="str")
BEdire85ML=gpd.read_file(myresults+"/"+"bedire85ML.shp", dtype="str")
BEtree85ML=gpd.read_file(myresults+"/"+"betree85ML.shp", dtype="str")
BEheuteML=gpd.read_file(myresults+"/"+"beheuteML.shp", dtype="str")


BEheuteML=BEheuteML.rename(columns={"BE":"BE_heuteML","nais":"naisheuteML", "area":"areaheuteML"})
BEheuteML.columns
BEdire85ML=BEdire85ML.rename(columns={"BE_zukunft":"BEdire85ML", "nais":"nais85ML","Anford_kol":"Anford_kol85ML", "area":"areadire85ML"})
BEdire85ML.columns
BEtree85ML=BEtree85ML.rename(columns={"naisheute":"naisheute85tree","naiszukunf":"naiszukunft85tree","hszukunft":"hszukunft85","bezukunft":"BEtree85ML", "area":"areatree85ML"})
BEtree85ML.columns
BEdire45ML=BEdire45ML.rename(columns={"BE_zukunft":"BEdire45ML", "nais":"nais45ML","Anford_kol":"Anford_kol45ML", "area":"areadire45ML"})
BEdire45ML.columns
BEtree45ML=BEtree45ML.rename(columns={"naisheute":"naisheute45tree","naiszukunf":"naiszukunft45tree","hszukunft":"hszukunft45","bezukunft":"BEtree45ML", "area":"areatree45ML"})
BEtree45ML.columns

# *************************************************************
# Schritt 9: Flächenstatistik nach Regionen
print("Mittelland")
BEheuteML.columns
BEheuteML["area_heuteML"]=""
BEheuteML.columns
BEheuteML["area_heuteML"]=BEheuteML["geometry"].area
areastatheuteML=BEheuteML.groupby(["BE_heuteML"]).agg({'area_heuteML': 'sum'})
areastatheuteML["ha_heuteML"]=areastatheuteML["area_heuteML"]/10000.0
areastatheuteML["BEeinheit"] = areastatheuteML.index
areastatheuteML

BEtree85ML.columns
BEtree85ML["area_TA85ML"]=""
BEtree85ML.columns
BEtree85ML["area_TA85ML"]=BEtree85ML["geometry"].area
areastatrcp85_treeML=BEtree85ML.groupby(["BEtree85ML"]).agg({'area_TA85ML': 'sum'})
areastatrcp85_treeML["ha_TA85ML"]=areastatrcp85_treeML["area_TA85ML"]/10000.0
areastatrcp85_treeML["BEeinheit"] = areastatrcp85_treeML.index
areastatrcp85_treeML

BEdire85ML.columns
BEdire85ML["area_dire85ML"]=""
BEdire85ML.columns
BEdire85ML["area_dire85ML"]=BEdire85ML["geometry"].area
areastatrcp85_direML=BEdire85ML.groupby(["BEdire85ML"]).agg({'area_dire85ML': 'sum'})
areastatrcp85_direML["ha_dire85ML"]=areastatrcp85_direML["area_dire85ML"]/10000.0
areastatrcp85_direML["BEeinheit"] = areastatrcp85_direML.index
areastatrcp85_direML

BEtree45ML.columns
BEtree45ML["area_TA45ML"]=""
BEtree45ML.columns
BEtree45ML["area_TA45ML"]=BEtree45ML["geometry"].area
areastatrcp45_treeML=BEtree45ML.groupby(["BEtree45ML"]).agg({'area_TA45ML': 'sum'})
areastatrcp45_treeML["ha_TA45ML"]=areastatrcp45_treeML["area_TA45ML"]/10000.0
areastatrcp45_treeML["BEeinheit"] = areastatrcp45_treeML.index
areastatrcp45_treeML

BEdire45ML.columns
BEdire45ML["area_dire45ML"]=""
BEdire45ML.columns
BEdire45ML["area_dire45ML"]=BEdire45ML["geometry"].area
areastatrcp45_direML=BEdire45ML.groupby(["BEdire45ML"]).agg({'area_dire45ML': 'sum'})
areastatrcp45_direML["ha_dire45ML"]=areastatrcp45_direML["area_dire45ML"]/10000.0
areastatrcp45_direML["BEeinheit"] = areastatrcp45_direML.index
areastatrcp45_direML

print("Arealstatistik pro Region und Einheit für alle Szenarien")
#areastatJURAmerge=pd.merge(areastatheuteJura,areastatrcp45direJura,areastatrcp85direJura,areastatrcp45_treeJURA,areastatrcp85_treeJURA, on="BEeinheit", how="left") #many to many?
einheitendfML=einheitendf.merge(areastatheuteML, left_on='Berner Einheiten', right_on="BEeinheit", how="left")
einheitendfML.columns
einheitendfML.drop(columns=["BEeinheit"], inplace=True)
einheitendfML.columns
einheitendfML=einheitendfML.merge(areastatrcp45_treeML,left_on='Berner Einheiten', right_on="BEeinheit", how="left") #many to many?
einheitendfML.drop(columns=["BEeinheit"], inplace=True)
einheitendfML=einheitendfML.merge(areastatrcp45_direML, left_on='Berner Einheiten', right_on="BEeinheit", how="left") #many to many?
einheitendfML.drop(columns=["BEeinheit"], inplace=True)
einheitendfML=einheitendfML.merge(areastatrcp85_treeML,left_on='Berner Einheiten', right_on="BEeinheit", how="left") #many to many?
einheitendfML.drop(columns=["BEeinheit"], inplace=True)
einheitendfML=einheitendfML.merge(areastatrcp85_direML, left_on='Berner Einheiten', right_on="BEeinheit", how="left") #many to many?
einheitendfML.drop(columns=["BEeinheit"], inplace=True)
einheitendfML.columns


einheitendfML.loc[einheitendfML["area_heuteML"].isna()==True,"area_heuteML"]="-"
einheitendfML.loc[einheitendfML["ha_heuteML"].isna()==True,"ha_heuteML"]="-"

einheitendfML.loc[einheitendfML["area_TA45ML"].isna()==True,"area_TA45ML"]="-"
einheitendfML.loc[einheitendfML["ha_TA45ML"].isna()==True,"ha_TA45ML"]="-"

einheitendfML.loc[einheitendfML["area_dire45ML"].isna()==True,"area_dire45ML"]="-"
einheitendfML.loc[einheitendfML["ha_dire45ML"].isna()==True,"ha_dire45ML"]="-"

einheitendfML.loc[einheitendfML["area_TA85ML"].isna()==True,"area_TA85ML"]="-"
einheitendfML.loc[einheitendfML["ha_TA85ML"].isna()==True,"ha_TA85ML"]="-"

einheitendfML.loc[einheitendfML["area_dire85ML"].isna()==True,"area_dire85ML"]="-"
einheitendfML.loc[einheitendfML["ha_dire85ML"].isna()==True,"ha_dire85ML"]="-"

einheitendfML.columns
einheitendfML=pd.DataFrame(einheitendfML,columns=['Berner Einheiten', 'ha_heuteML', 'ha_TA45ML','ha_dire45ML','ha_TA85ML','ha_dire85ML'])
einheitendfML.columns
einheitendfML=einheitendfML.rename(columns={"ha_heuteML":"Fläche heute","ha_TA45ML":"Fläche RCP4.5 TreeApp","ha_dire45ML":"Fläche RCP4.5 direkt","ha_TA85ML":"Fläche RCP8.5 TreeApp","ha_dire85ML":"Fläche RCP8.5 direkt"})
einheitendfML.columns

einheitendfML.to_excel(outdir+"/areastatML.xlsx")

# *************************************************************
#JURA


# *************************************************************
# Schritt 3: Einlesen der Shapefiles
print("Shapefiles Standorttypen einlesen, Header rows umbennenen")

BEdire45JU=gpd.read_file(myresults+"/"+"bedire45JURA.shp", dtype="str")
BEtree45JU=gpd.read_file(myresults+"/"+"betree45JURA.shp", dtype="str")
BEdire85JU=gpd.read_file(myresults+"/"+"bedire85JURA.shp", dtype="str")
BEtree85JU=gpd.read_file(myresults+"/"+"betree85JURA.shp", dtype="str")
BEheuteJU=gpd.read_file(myresults+"/"+"beheuteJURA.shp", dtype="str")


BEheuteJU=BEheuteJU.rename(columns={"BE":"BE_heuteJU","nais":"naisheuteJU", "area":"areaheuteJU"})
BEheuteJU.columns
BEdire85JU=BEdire85JU.rename(columns={"BE_zukunft":"BEdire85JU", "nais":"nais85JU","Anford_kol":"Anford_kol85JU", "area":"areadire85JU"})
BEdire85JU.columns
BEtree85JU=BEtree85JU.rename(columns={"naisheute":"naisheute85tree","naiszukunf":"naiszukunft85tree","hszukunft":"hszukunft85","bezukunft":"BEtree85JU", "area":"areatree85JU"})
BEtree85JU.columns
BEdire45JU=BEdire45JU.rename(columns={"BE_zukunft":"BEdire45JU", "nais":"nais45JU","Anford_kol":"Anford_kol45JU", "area":"areadire45JU"})
BEdire45JU.columns
BEtree45JU=BEtree45JU.rename(columns={"naisheute":"naisheute45tree","naiszukunf":"naiszukunft45tree","hszukunft":"hszukunft45","bezukunft":"BEtree45JU", "area":"areatree45JU"})
BEtree45JU.columns

# *************************************************************
# Schritt 9: Flächenstatistik nach Regionen
print("Jura")
BEheuteJU.columns
BEheuteJU["area_heuteJU"]=""
BEheuteJU.columns
BEheuteJU["area_heuteJU"]=BEheuteJU["geometry"].area
areastatheuteJU=BEheuteJU.groupby(["BE_heuteJU"]).agg({'area_heuteJU': 'sum'})
areastatheuteJU["ha_heuteJU"]=areastatheuteJU["area_heuteJU"]/10000.0
areastatheuteJU["BEeinheit"] = areastatheuteJU.index
areastatheuteJU

BEtree85JU.columns
BEtree85JU["area_TA85JU"]=""
BEtree85JU.columns
BEtree85JU["area_TA85JU"]=BEtree85JU["geometry"].area
areastatrcp85_treeJU=BEtree85JU.groupby(["BEtree85JU"]).agg({'area_TA85JU': 'sum'})
areastatrcp85_treeJU["ha_TA85JU"]=areastatrcp85_treeJU["area_TA85JU"]/10000.0
areastatrcp85_treeJU["BEeinheit"] = areastatrcp85_treeJU.index
areastatrcp85_treeJU

BEdire85JU.columns
BEdire85JU["area_dire85JU"]=""
BEdire85JU.columns
BEdire85JU["area_dire85JU"]=BEdire85JU["geometry"].area
areastatrcp85_direJU=BEdire85JU.groupby(["BEdire85JU"]).agg({'area_dire85JU': 'sum'})
areastatrcp85_direJU["ha_dire85JU"]=areastatrcp85_direJU["area_dire85JU"]/10000.0
areastatrcp85_direJU["BEeinheit"] = areastatrcp85_direJU.index
areastatrcp85_direJU

BEtree45JU.columns
BEtree45JU["area_TA45JU"]=""
BEtree45JU.columns
BEtree45JU["area_TA45JU"]=BEtree45JU["geometry"].area
areastatrcp45_treeJU=BEtree45JU.groupby(["BEtree45JU"]).agg({'area_TA45JU': 'sum'})
areastatrcp45_treeJU["ha_TA45JU"]=areastatrcp45_treeJU["area_TA45JU"]/10000.0
areastatrcp45_treeJU["BEeinheit"] = areastatrcp45_treeJU.index
areastatrcp45_treeJU

BEdire45JU.columns
BEdire45JU["area_dire45JU"]=""
BEdire45JU.columns
BEdire45JU["area_dire45JU"]=BEdire45JU["geometry"].area
areastatrcp45_direJU=BEdire45JU.groupby(["BEdire45JU"]).agg({'area_dire45JU': 'sum'})
areastatrcp45_direJU["ha_dire45JU"]=areastatrcp45_direJU["area_dire45JU"]/10000.0
areastatrcp45_direJU["BEeinheit"] = areastatrcp45_direJU.index
areastatrcp45_direJU

#areastatrcp85_direJU.to_excel(myresults+"/"+"areastatrcp85_direJU.xlsx")


print("Arealstatistik pro Region und Einheit für alle Szenarien")
#areastatJURAmerge=pd.merge(areastatheuteJura,areastatrcp45direJura,areastatrcp85direJura,areastatrcp45_treeJURA,areastatrcp85_treeJURA, on="BEeinheit", how="left") #many to many?
einheitendfJU=einheitendf.merge(areastatheuteJU, left_on='Berner Einheiten', right_on="BEeinheit", how="left")
einheitendfJU.columns
einheitendfJU.drop(columns=["BEeinheit"], inplace=True)
einheitendfJU=einheitendfJU.merge(areastatrcp45_treeJU,left_on='Berner Einheiten', right_on="BEeinheit", how="left") #many to many?
einheitendfJU.drop(columns=["BEeinheit"], inplace=True)
einheitendfJU=einheitendfJU.merge(areastatrcp45_direJU, left_on='Berner Einheiten', right_on="BEeinheit", how="left") #many to many?
einheitendfJU.drop(columns=["BEeinheit"], inplace=True)
einheitendfJU=einheitendfJU.merge(areastatrcp85_treeJU,left_on='Berner Einheiten', right_on="BEeinheit", how="left") #many to many?
einheitendfJU.drop(columns=["BEeinheit"], inplace=True)
einheitendfJU=einheitendfJU.merge(areastatrcp85_direJU, left_on='Berner Einheiten', right_on="BEeinheit", how="left") #many to many?
einheitendfJU.drop(columns=["BEeinheit"], inplace=True)
einheitendfJU.columns


einheitendfJU.loc[einheitendfJU["area_heuteJU"].isna()==True,"area_heuteJU"]="-"
einheitendfJU.loc[einheitendfJU["ha_heuteJU"].isna()==True,"ha_heuteJU"]="-"

einheitendfJU.loc[einheitendfJU["area_TA45JU"].isna()==True,"area_TA45JU"]="-"
einheitendfJU.loc[einheitendfJU["ha_TA45JU"].isna()==True,"ha_TA45JU"]="-"

einheitendfJU.loc[einheitendfJU["area_dire45JU"].isna()==True,"area_dire45JU"]="-"
einheitendfJU.loc[einheitendfJU["ha_dire45JU"].isna()==True,"ha_dire45JU"]="-"

einheitendfJU.loc[einheitendfJU["area_TA85JU"].isna()==True,"area_TA85JU"]="-"
einheitendfJU.loc[einheitendfJU["ha_TA85JU"].isna()==True,"ha_TA85JU"]="-"

einheitendfJU.loc[einheitendfJU["area_dire85JU"].isna()==True,"area_dire85JU"]="-"
einheitendfJU.loc[einheitendfJU["ha_dire85JU"].isna()==True,"ha_dire85JU"]="-"

einheitendfJU.columns
einheitendfJU=pd.DataFrame(einheitendfJU,columns=['Berner Einheiten', 'ha_heuteJU', 'ha_TA45JU','ha_dire45JU','ha_TA85JU','ha_dire85JU'])
einheitendfJU.columns
einheitendfJU=einheitendfJU.rename(columns={"ha_heuteJU":"Fläche heute","ha_TA45JU":"Fläche RCP4.5 TreeApp","ha_dire45JU":"Fläche RCP4.5 direkt","ha_TA85JU":"Fläche RCP8.5 TreeApp","ha_dire85JU":"Fläche RCP8.5 direkt"})
einheitendfJU.columns


#areastatALpenmerge=pd.merge(areastatheuteALPS,areastatrcp45direALPS,areastatrcp85direALPS,areastatrcp45_treeALPS,areastatrcp85_treeALPS, on="BEeinheit", how="left") #many to many?

einheitendfJU.to_excel(outdir+"/areastatJURA.xlsx")

# *************************************************************
#ALPEN

# *************************************************************
# Schritt 3: Einlesen der Shapefiles
print("Shapefiles Standorttypen einlesen, Header rows umbennenen")

BEdire45AL=gpd.read_file(myresults+"/"+"bedire45ALPS.shp", dtype="str")
BEtree45AL=gpd.read_file(myresults+"/"+"betree45ALPS.shp", dtype="str")
BEdire85AL=gpd.read_file(myresults+"/"+"bedire85ALPS.shp", dtype="str")
BEtree85AL=gpd.read_file(myresults+"/"+"betree85ALPS.shp", dtype="str")
BEheuteAL=gpd.read_file(myresults+"/"+"beheuteALPS.shp", dtype="str")


BEheuteAL=BEheuteAL.rename(columns={"BE":"BE_heuteAL","nais":"naisheuteAL", "area":"areaheuteAL"})
BEheuteAL.columns
BEdire85AL=BEdire85AL.rename(columns={"BE_zukunft":"BEdire85AL", "nais":"nais85AL","Anford_kol":"Anford_kol85AL", "area":"areadire85AL"})
BEdire85AL.columns
BEtree85AL=BEtree85AL.rename(columns={"naisheute":"naisheute85tree","naiszukunf":"naiszukunft85tree","hszukunft":"hszukunft85","bezukunft":"BEtree85AL", "area":"areatree85AL"})
BEtree85AL.columns
BEdire45AL=BEdire45AL.rename(columns={"BE_zukunft":"BEdire45AL", "nais":"nais45AL","Anford_kol":"Anford_kol45AL", "area":"areadire45AL"})
BEdire45AL.columns
BEtree45AL=BEtree45AL.rename(columns={"naisheute":"naisheute45tree","naiszukunf":"naiszukunft45tree","hszukunft":"hszukunft45","bezukunft":"BEtree45AL", "area":"areatree45AL"})
BEtree45AL.columns

# *************************************************************
# Schritt 9: Flächenstatistik nach Regionen
print("Alpen")
BEheuteAL.columns
BEheuteAL["area_heuteAL"]=""
BEheuteAL.columns
BEheuteAL["area_heuteAL"]=BEheuteAL["geometry"].area
areastatheuteAL=BEheuteAL.groupby(["BE_heuteAL"]).agg({'area_heuteAL': 'sum'})
areastatheuteAL["ha_heuteAL"]=areastatheuteAL["area_heuteAL"]/10000.0
areastatheuteAL["BEeinheit"] = areastatheuteAL.index
areastatheuteAL

BEtree85AL.columns
BEtree85AL["area_TA85AL"]=""
BEtree85AL.columns
BEtree85AL["area_TA85AL"]=BEtree85AL["geometry"].area
areastatrcp85_treeAL=BEtree85AL.groupby(["BEtree85AL"]).agg({'area_TA85AL': 'sum'})
areastatrcp85_treeAL["ha_TA85AL"]=areastatrcp85_treeAL["area_TA85AL"]/10000.0
areastatrcp85_treeAL["BEeinheit"] = areastatrcp85_treeAL.index
areastatrcp85_treeAL

BEdire85AL.columns
BEdire85AL["area_dire85AL"]=""
BEdire85AL.columns
BEdire85AL["area_dire85AL"]=BEdire85AL["geometry"].area
areastatrcp85_direAL=BEdire85AL.groupby(["BEdire85AL"]).agg({'area_dire85AL': 'sum'})
areastatrcp85_direAL["ha_dire85AL"]=areastatrcp85_direAL["area_dire85AL"]/10000.0
areastatrcp85_direAL["BEeinheit"] = areastatrcp85_direAL.index
areastatrcp85_direAL

BEtree45AL.columns
BEtree45AL["area_TA45AL"]=""
BEtree45AL.columns
BEtree45AL["area_TA45AL"]=BEtree45AL["geometry"].area
areastatrcp45_treeAL=BEtree45AL.groupby(["BEtree45AL"]).agg({'area_TA45AL': 'sum'})
areastatrcp45_treeAL["ha_TA45AL"]=areastatrcp45_treeAL["area_TA45AL"]/10000.0
areastatrcp45_treeAL["BEeinheit"] = areastatrcp45_treeAL.index
areastatrcp45_treeAL

BEdire45AL.columns
BEdire45AL["area_dire45AL"]=""
BEdire45AL.columns
BEdire45AL["area_dire45AL"]=BEdire45AL["geometry"].area
areastatrcp45_direAL=BEdire45AL.groupby(["BEdire45AL"]).agg({'area_dire45AL': 'sum'})
areastatrcp45_direAL["ha_dire45AL"]=areastatrcp45_direAL["area_dire45AL"]/10000.0
areastatrcp45_direAL["BEeinheit"] = areastatrcp45_direAL.index
areastatrcp45_direAL

print("Arealstatistik pro Region und Einheit für alle Szenarien")
#areastatJURAmerge=pd.merge(areastatheuteJura,areastatrcp45direJura,areastatrcp85direJura,areastatrcp45_treeJURA,areastatrcp85_treeJURA, on="BEeinheit", how="left") #many to many?
einheitendfAL=einheitendf.merge(areastatheuteAL, left_on='Berner Einheiten', right_on="BEeinheit", how="left")
einheitendfAL.columns
einheitendfAL.drop(columns=["BEeinheit"], inplace=True)
einheitendfAL=einheitendfAL.merge(areastatrcp45_treeAL,left_on='Berner Einheiten', right_on="BEeinheit", how="left") #many to many?
einheitendfAL.drop(columns=["BEeinheit"], inplace=True)
einheitendfAL=einheitendfAL.merge(areastatrcp45_direAL, left_on='Berner Einheiten', right_on="BEeinheit", how="left") #many to many?
einheitendfAL.drop(columns=["BEeinheit"], inplace=True)
einheitendfAL=einheitendfAL.merge(areastatrcp85_treeAL,left_on='Berner Einheiten', right_on="BEeinheit", how="left") #many to many?
einheitendfAL.drop(columns=["BEeinheit"], inplace=True)
einheitendfAL=einheitendfAL.merge(areastatrcp85_direAL, left_on='Berner Einheiten', right_on="BEeinheit", how="left") #many to many?
einheitendfAL.drop(columns=["BEeinheit"], inplace=True)
einheitendfAL.columns


einheitendfAL.loc[einheitendfAL["area_heuteAL"].isna()==True,"area_heuteAL"]="-"
einheitendfAL.loc[einheitendfAL["ha_heuteAL"].isna()==True,"ha_heuteAL"]="-"

einheitendfAL.loc[einheitendfAL["area_TA45AL"].isna()==True,"area_TA45AL"]="-"
einheitendfAL.loc[einheitendfAL["ha_TA45AL"].isna()==True,"ha_TA45AL"]="-"

einheitendfAL.loc[einheitendfAL["area_dire45AL"].isna()==True,"area_dire45AL"]="-"
einheitendfAL.loc[einheitendfAL["ha_dire45AL"].isna()==True,"ha_dire45AL"]="-"

einheitendfAL.loc[einheitendfAL["area_TA85AL"].isna()==True,"area_TA85AL"]="-"
einheitendfAL.loc[einheitendfAL["ha_TA85AL"].isna()==True,"ha_TA85AL"]="-"

einheitendfAL.loc[einheitendfAL["area_dire85AL"].isna()==True,"area_dire85AL"]="-"
einheitendfAL.loc[einheitendfAL["ha_dire85AL"].isna()==True,"ha_dire85AL"]="-"

einheitendfAL.columns
einheitendfAL=pd.DataFrame(einheitendfAL,columns=['Berner Einheiten', 'ha_heuteAL', 'ha_TA45AL','ha_dire45AL','ha_TA85AL','ha_dire85AL'])
einheitendfAL.columns
einheitendfAL=einheitendfAL.rename(columns={"ha_heuteAL":"Fläche heute","ha_TA45AL":"Fläche RCP4.5 TreeApp","ha_dire45AL":"Fläche RCP4.5 direkt","ha_TA85AL":"Fläche RCP8.5 TreeApp","ha_dire85AL":"Fläche RCP8.5 direkt"})
einheitendfAL.columns

einheitendfAL.to_excel(outdir+"/areastatALPS.xlsx")



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
outdir=myresults

# *************************************************************
# Schritt 3: Einlesen der Shapefiles
print("Shapefiles Standorttypen einlesen, Header rows umbennenen")
#BEheute=gpd.read_file(myworkspace+"/"+"bestandortstypenarrondiertjoined.shp", dtype="str")
BEheute=gpd.read_file(myworkspace+"/"+"bestandortstypenjoined.shp", dtype="str")
BErcp45_tree=gpd.read_file(myworkspace+"/"+"be_rcp45_zukuenftigestandorteCLEAN.shp", dtype="str")
BErcp85_tree=gpd.read_file(myworkspace+"/"+"be_rcp85_zukuenftigestandorteCLEAN.shp", dtype="str")
BErcp45_dire=gpd.read_file(myresults+"/"+"bestandortstypenarrondiertjoined_rcp45.shp", dtype="str")
BErcp85_dire=gpd.read_file(myresults+"/"+"bestandortstypenarrondiertjoined_rcp85.shp", dtype="str")

BEheute.columns
BEheute=pd.DataFrame(BEheute, columns=['BE','nais','regionid','region','geometry','Anforderun','HS_heute','HS_rcp45','HS_rcp85'])
BEheute.columns
BErcp45_dire.columns
BErcp45_dire=pd.DataFrame(BErcp45_dire, columns=['BE_zukunft', 'nais', 'regionid','region','geometry','Anford_kol','HS_heute','HS_rcp45','HS_rcp85'])
BErcp85_dire=pd.DataFrame(BErcp85_dire, columns=['BE_zukunft','nais','regionid','region','geometry','Anford_kol','HS_heute','HS_rcp45','HS_rcp85'])

BEheute=BEheute.rename(columns={"BE":"BE_heute","nais":"naisheute"})
BEheute.columns
BErcp45_dire=BErcp45_dire.rename(columns={"BE_zukunft":"BEzukunft45dire", "nais":"naisrcp45","Anford_kol":"Anford_kol45"})
BErcp45_dire.columns
BErcp85_dire=BErcp85_dire.rename(columns={"BE_zukunft":"BEzukunft85dire", "nais":"naisrcp85", "Anford_kol":"Anford_kol85"})
BErcp85_dire.columns
BErcp45_tree=BErcp45_tree.rename(columns={"naisheute":"naisheute45tree","hsheute":"hsheute45tree","naiszukunf":"naiszukunft45tree","hszukunft":"hszukunft45tree","bezukunft":"bezukunft45tree"})
BErcp45_tree.columns
BErcp85_tree=BErcp85_tree.rename(columns={"naisheute":"naisheute85tree","hsheute":"hsheute85tree","naiszukunf":"naiszukunft85tree","hszukunft":"hszukunft85tree","bezukunft":"bezukunft85tree"})
BErcp85_tree.columns

# *************************************************************
# Schritt 4: Fehlende Attributte (Regionen und Höhenstufen) den Shapefiles anhängen --> Overlay?
#print("Regionen der Durchstichmethode anfügen")
# Regionid an TreeApp Datensätze anhängen
#Regionen=gpd.read_file(myworkspace+"/"+"kantonbernplusregionalisierungunionsinglepart.shp", dtype="str")
#BErcp45_tree_regionen=gpd.overlay(BErcp45_tree,Regionen,how='union')
#BErcp45_tree_regionen.columns
#BErcp85_tree_regionen=gpd.overlay(BErcp85_tree,Regionen,how='union')
#BErcp85_tree_regionen.columns

# *************************************************************
# Schritt 5: Alle Höhenstufen überlagern in einen Datensatz
#print("Vegetationshöhenstufen einlesen und umbenennen"
#vegheute=gpd.read_file(myworkspace+"/"+"vegetationshoehenstufen19611990owclipkantonbernplus.shp", dtype="str")
#vegheute=pd.DataFrame(vegheute, columns=['HS_de','Code','Subcode','geometry'])
#vegheute=vegheute.rename(columns={"HS_de":"HS_heute","Code":"Codeheute","Subcode":"Subcodeheute"})
#vegheute.columns

#vegrcp45=gpd.read_file(myworkspace+"/"+"bevegetationshoehenstufen20702099rcp45singlepart.shp", dtype="str")
#vegrcp45=pd.DataFrame(vegheute, columns=['HS_de','Code','Subcode','geometry'])
#vegrcp45=vegrcp45.rename(columns={"HS_de":"HS_rcp45","Code":"Code_rcp45","Subcode":"Subcodercp45"})
#vegrcp45.columns

#vegrcp85=gpd.read_file(myworkspace+"/"+"bevegetationshoehenstufen20702099rcp85singlepart.shp", dtype="str")
#vegrcp85=pd.DataFrame(vegheute, columns=['HS_de','Code','Subcode','geometry'])
#vegrcp85=vegrcp85.rename(columns={"HS_de":"HS_rcp85","Code":"Code_rcp85","Subcode":"Subcodercp85"})
#vegrcp85.columns

# Ein Datensatz (vegall) mit allen Höhenstufen bilden --> funktioniert noch nicht...--> AttributeError: 'DataFrame' object has no attribute 'crs'
#vegheutercp45=gpd.overlay(vegheute,vegrcp45, how="union",)
#vegall=gpd.overlay(vegheutercp45, vegrcp85, how="union")
#vegall.columns

#print("Alle Höhenstufen direkten Methoden anfügen")
#BEheuteveg=gpd.overlay(BEheute,vegall,how="union")
#BErcp45_direveg=gpd.overlay(BErcp45_dire,vegall,how="union")
#BErcp85_direveg=gpd.overlay(BErcp85_dire,vegall,how="union")

# *************************************************************
# Schritt 6: Excels nach Regionen bilden --> prüfen mit den COlumns!!
#BEheuteMittelland=BEheute[BEheute["regionid"]==2]

#BEheuteJURA.to_excel(outdir+"/BEheuteJura.csv")
#BEheuteMittelland.to_file(outdir+"/BEheuteMittelland.csv")
#BEheuteAlpen.to_file(outdir+"/BEheuteAlpen.csv")
#print("exported subset excel files BEheute")

print("Excels nach Regionen bilden")
BEheuteJURA=BEheute[BEheute.regionid == 1]
BEheuteMittelland=BEheute[BEheute.regionid == 2]
BEheuteAlpen=BEheute[BEheute.regionid == 3]

# BErcp45_dire
BErcp45_dire.columns
BErcp45_direJURA=BErcp45_dire[BErcp45_dire.regionid == 1]
BErcp45_direMittelland=BErcp45_dire[BErcp45_dire.regionid == 2]
BErcp45_direAlpen=BErcp45_dire[BErcp45_dire.regionid == 3]

# BErcp85_dire
BErcp85_direJURA=BErcp85_dire[BErcp85_dire.regionid == 1]
BErcp85_direMittelland=BErcp85_dire[BErcp85_dire.regionid == 2]
BErcp85_direAlpen=BErcp85_dire[BErcp85_dire.regionid == 3]

# BErcp45_tree
BErcp45_treeJURA=BErcp45_tree[BErcp45_tree.regionid == 1]
BErcp45_treeMittelland=BErcp45_tree[BErcp45_tree.regionid == 2]
BErcp45_treeAlpen=BErcp45_tree[BErcp45_tree.regionid == 3]

# BErcp85_tree
BErcp85_treeJURA=BErcp85_tree[BErcp85_tree.regionid == 1]
BErcp85_treeMittelland=BErcp85_tree[BErcp85_tree.regionid == 2]
BErcp85_treeAlpen=BErcp85_tree[BErcp85_tree.regionid == 3]

# *************************************************************
# Schritt 7: Überlagerung der Shapes für die Sankey Diagramme

print("geopandas overlay Einheiten heute mit der direkten Methode") #für die Sankey Diagramme
#Einheitenheuteundrcp45direJURA=gpd.overlay(BEheuteJURA,BErcp45_direJURA,how='union')
#Einheitenheuteundrcp85direJURA=gpd.overlay(BEheuteJURA,BErcp85_direJURA,how='union')

#Einheitenheuteundrcp45direML=gpd.overlay(BEheuteMittelland,BErcp45_direMittelland,how='union')
Einheitenheuteundrcp85direML=gpd.overlay(BEheuteMittelland,BErcp85_direMittelland,how='union')

#Einheitenheuteundrcp45direALPS=gpd.overlay(BEheuteAlpen,BErcp45_direAlpen,how='union')
Einheitenheuteundrcp85direALPS=gpd.overlay(BEheuteAlpen,BErcp85_direAlpen,how='union')

print("geopandas overlay Einheiten heute mit der Durchstichmethode") #für die Sankey Diagramme
#Einheitenheuteundrcp45treeJURA=gpd.overlay(BEheuteJURA,BErcp45_treeJURA,how='union')
#Einheitenheuteundrcp85treeJURA=gpd.overlay(BEheuteJURA,BErcp85_treeJURA,how='union')

#Einheitenheuteundrcp45treeML=gpd.overlay(BEheuteMittelland,BErcp45_treeMittelland,how='union')
Einheitenheuteundrcp85treeML=gpd.overlay(BEheuteMittelland,BErcp85_treeMittelland,how='union')

#Einheitenheuteundrcp45treeALPS=gpd.overlay(BEheuteAlpen,BErcp45_treeAlpen,how='union')
Einheitenheuteundrcp85treeALPS=gpd.overlay(BEheuteAlpen,BErcp85_treeAlpen,how='union')

####
# Fläche berechnen!!!
# --> Attribut "flaeche"



# *************************************************************
# Schritt 10: Sankey Diagram: Für Mittelland und Alpen pro Höhenstufe, einmal mit und einmal ohne Sonderwald

# Definiere Normale und SW Einheiten
parameterdf=pd.read_excel(mycodespace+"/"+"Parametertabelle_2070-99_Waldstandorte_BE_221118.xlsx", dtype="str", engine='openpyxl')
parameterdf.columns

allnormal=parameterdf[((parameterdf["Sonderwald"].astype(str).str.contains("0"))&(~parameterdf["Sonderwald"].astype(str).str.contains("1"))&(~parameterdf["Sonderwald"].astype(str).str.contains("2"))&(~parameterdf["Sonderwald"].astype(str).str.contains("3"))&(~parameterdf["Sonderwald"].astype(str).str.contains("4"))&(~parameterdf["Sonderwald"].astype(str).str.contains("5"))&(~parameterdf["Sonderwald"].astype(str).str.contains("6"))&(~parameterdf["Sonderwald"].astype(str).str.contains("7"))&(~parameterdf["Sonderwald"].astype(str).str.contains("8"))&(~parameterdf["Sonderwald"].astype(str).str.contains("9"))&(~parameterdf["Sonderwald"].astype(str).str.contains("10")))]
allnormaltolist=allnormal["BE"].unique().tolist()

allSW=parameterdf[((~parameterdf["Sonderwald"].astype(str).str.contains("0"))|(parameterdf["Sonderwald"].astype(str).str.contains("1"))|(parameterdf["Sonderwald"].astype(str).str.contains("2"))|(parameterdf["Sonderwald"].astype(str).str.contains("3"))|(parameterdf["Sonderwald"].astype(str).str.contains("4"))|(parameterdf["Sonderwald"].astype(str).str.contains("5"))|(parameterdf["Sonderwald"].astype(str).str.contains("6"))|(parameterdf["Sonderwald"].astype(str).str.contains("7"))|(parameterdf["Sonderwald"].astype(str).str.contains("8"))|(parameterdf["Sonderwald"].astype(str).str.contains("9"))|(parameterdf["Sonderwald"].astype(str).str.contains("10")))]
allSWtolist=allSW["BE"].unique().tolist()

# Make subset with vegetation belt
print("Mittelland submontan und untermontan")
sankeysubmontandirekt45ML=Einheitenheuteundrcp45direML[Einheitenheuteundrcp45direML.Code_heute == 4]
sankeysubmontandirekt45ML.head(5)
sankeyunterontandirekt45ML=Einheitenheuteundrcp45direML[Einheitenheuteundrcp45direML.Code_heute == 5]

sankeysubmontandirekt85ML=Einheitenheuteundrcp85direML[Einheitenheuteundrcp85direML.Code_heute == 4]
sankeyuntermontandirekt85ML=Einheitenheuteundrcp85direML[Einheitenheuteundrcp85direML.Code_heute == 5]

sankeysubmontantree45ML=Einheitenheuteundrcp45treeML[Einheitenheuteundrcp45treeML.Code_heute == 4]
sankeyunterontantree45ML=Einheitenheuteundrcp45treeML[Einheitenheuteundrcp45treeML.Code_heute == 5]

sankeysubmontantree85ML=Einheitenheuteundrcp85treeML[Einheitenheuteundrcp85treeML.Code_heute == 4]
sankeyuntermontantree85ML=Einheitenheuteundrcp85treeML[Einheitenheuteundrcp85treeML.Code_heute == 5]

# Make subset with vegetation belt
print("Mittelland subalpin und obersubalpin")
sankeysubalpindirekt45ML=Einheitenheuteundrcp45direML[Einheitenheuteundrcp45direML.Code_heute == 9]
sankeyobersubalpindirekt45ML=Einheitenheuteundrcp45direML[Einheitenheuteundrcp45direML.Code_heute == 10]

sankeysubalpindirekt85ML=Einheitenheuteundrcp85direML[Einheitenheuteundrcp85direML.Code_heute == 9]
sankeyobersubalpindirekt85ML=Einheitenheuteundrcp85direML[Einheitenheuteundrcp85direML.Code_heute == 10]

sankeysubalpintree45ML=Einheitenheuteundrcp45treeML[Einheitenheuteundrcp45treeML.Code_heute == 9]
sankeyobersubalpintree45ML=Einheitenheuteundrcp45treeML[Einheitenheuteundrcp45treeML.Code_heute == 10]

sankeysubalpintree85ML=Einheitenheuteundrcp85treeML[Einheitenheuteundrcp85treeML.Code_heute == 9]
sankeyobersubalpintree85ML=Einheitenheuteundrcp85treeML[Einheitenheuteundrcp85treeML.Code_heute == 10]


print("Alpen submontan und untermontan")
sankeysubmontandirekt45ALPS=Einheitenheuteundrcp45direALPS[Einheitenheuteundrcp45direALPS.Code_heute == 4]
sankeyunterontandirekt45ALPS=Einheitenheuteundrcp45direALPS[Einheitenheuteundrcp45direALPS.Code_heute == 5]

sankeysubmontandirekt85ALPS=Einheitenheuteundrcp85direALPS[Einheitenheuteundrcp85direALPS.Code_heute == 4]
sankeyuntermontandirekt85ALPS=Einheitenheuteundrcp85direALPS[Einheitenheuteundrcp85direALPS.Code_heute == 5]

sankeysubmontantree45ALPS=Einheitenheuteundrcp45treeALPS[Einheitenheuteundrcp45treeALPS.Code_heute == 4]
sankeyunterontantree45ALPS=Einheitenheuteundrcp45treeALPS[Einheitenheuteundrcp45treeALPS.Code_heute == 5]

sankeysubmontantree85ALPS=Einheitenheuteundrcp85treeALPS[Einheitenheuteundrcp85treeALPS.Code_heute == 4]
sankeyuntermontantree85ALPS=Einheitenheuteundrcp85treeALPS[Einheitenheuteundrcp85treeALPS.Code_heute == 5]

# Make subset with vegetation belt
print("Alpen subalpin und obersubalpin")
sankeysubalpindirekt45ALPS=Einheitenheuteundrcp45direALPS[Einheitenheuteundrcp45direALPS.Code_heute == 9]
sankeyobersubalpindirekt45ALPS=Einheitenheuteundrcp45direALPS[Einheitenheuteundrcp45direALPS.Code_heute == 10]

sankeysubalpindirekt85ALPS=Einheitenheuteundrcp85direALPS[Einheitenheuteundrcp85direALPS.Code_heute == 9]
sankeyobersubalpindirekt85ALPS=Einheitenheuteundrcp85direALPS[Einheitenheuteundrcp85direALPS.Code_heute == 10]

sankeysubalpintree45ALPS=Einheitenheuteundrcp45treeALPS[Einheitenheuteundrcp45treeALPS.Code_heute == 9]
sankeyobersubalpintree45ALPS=Einheitenheuteundrcp45treeALPS[Einheitenheuteundrcp45treeALPS.Code_heute == 10]

sankeysubalpintree85ALPS=Einheitenheuteundrcp85treeALPS[Einheitenheuteundrcp85treeALPS.Code_heute == 9]
sankeyobersubalpintree85ALPS=Einheitenheuteundrcp85treeALPS[Einheitenheuteundrcp85treeALPS.Code_heute == 10]

# Sankey Diagramme mit Sonderwald und normalen Einheiten
print("sankey diagrams: submontan Mittelland")
print("sankeysubmontandirekt85ML")
sankeysubmontandirekt85MLSonderwald=sankeysubmontandirekt85ML[sankeysubmontandirekt85ML["BE_heute"].isin(allSWtolist)]
sankeysubmontandirekt85MLSonderwald
#sankeysubmontandirekt45MLSonderwald.sort_values(by='Code_rcp85', ascending=False)
sankeysubmontandirekt85MLnormaleEinheiten=sankeysubmontandirekt85ML[sankeysubmontandirekt85ML["BE_heute"].isin(allnormaltolist)]
sankeysubmontandirekt85MLnormaleEinheiten
#datanormal.sort_values(by='Code_rcp85', ascending=False)

print("draw basic Sankey Diagram")
sankey(left=sankeysubmontandirekt85MLSonderwald["BE"], right=sankeysubmontandirekt85MLSonderwald["BE_rcp85"], leftWeight=sankeysubmontandirekt85MLSonderwald["flaeche"], rightWeight=sankeysubmontandirekt85MLSonderwald["flaeche"], figure_name=["Submontane Sonderwaldstandorte im Mittelland, neue Methode"], aspect=4, fontsize=8)
sankey(left=sankeysubmontandirekt85MLnormaleEinheiten["BE"], right=sankeysubmontandirekt85MLnormaleEinheiten["BE_rcp85"], leftWeight=sankeysubmontandirekt85MLnormaleEinheiten["flaeche"], rightWeight=sankeysubmontandirekt85MLnormaleEinheiten["flaeche"], figure_name=["Submontane Standorte im Mittelland, neue Methode"], aspect=4, fontsize=8)


print("sankeysubmontantree45ML")
sankeysubmontantree45MLSonderwald=sankeysubmontantree45ML[sankeysubmontantree45ML["BE_heute"].isin(allSWtolist)]
sankeysubmontantree45MLSonderwald
#sankeysubmontandirekt45MLSonderwald.sort_values(by='Code_rcp85', ascending=False)
sankeysubmontantree45MLnormaleEinheiten=sankeysubmontantree45ML[sankeysubmontantree45ML["BE_heute"].isin(allnormaltolist)]
sankeysubmontantree45MLnormaleEinheiten
#datanormal.sort_values(by='Code_rcp85', ascending=False)

print("draw basic Sankey Diagram")
sankey(left=sankeysubmontantree45MLSonderwald["BE"], right=sankeysubmontantree45MLSonderwald["BE_rcp85"], leftWeight=sankeysubmontantree45MLSonderwald["flaeche"], rightWeight=sankeysubmontantree45MLSonderwald["flaeche"], figure_name=["Submontane Sonderwaldstandorte im Mittelland, Durchstichmethode"], aspect=4, fontsize=8)
sankey(left=sankeysubmontantree45MLnormaleEinheiten["BE"], right=sankeysubmontantree45MLnormaleEinheiten["BE_rcp85"], leftWeight=sankeysubmontantree45MLnormaleEinheiten["flaeche"], rightWeight=sankeysubmontantree45MLnormaleEinheiten["flaeche"], figure_name=["Submontane Standorte im Mittelland, Durchstichmethode"], aspect=4, fontsize=8)

# *************************************************************
# Schritt 8: Überlagerung der Shapes für die geometrische Analyse

print("geopandas overlay Einheiten der beiden zukünftigen Methoden")
Einheitenrcp45JURA=gpd.overlay(BErcp45_direJURA,BErcp45_treeJURA,how='intersection')
Einheitenrcp85JURA=gpd.overlay(BErcp85_direJURA,BErcp85_treeJURA,how='intersection')

Einheitenrcp45ML=gpd.overlay(BErcp45_direMittelland,BErcp45_treeMittelland,how='intersection')
Einheitenrcp85ML=gpd.overlay(BErcp85_direMittelland,BErcp85_treeMittelland,how='intersection')

Einheitenrcp45ALPS=gpd.overlay(BErcp45_direAlpen,BErcp45_treeAlpen,how='intersection')
Einheitenrcp85ALPS=gpd.overlay(BErcp85_direAlpen,BErcp85_treeAlpen,how='intersection')


# *************************************************************
# Schritt 9: Flächenstatistik nach Regionen

print("area stat Jura Durchstichmethode")
BErcp45_treeJURA.columns # BE heute =='xx' prüfen...stimmt so noch nicht!
BErcp45_treeJURA["area_TA45JU"]=""
BErcp45_treeJURA["area_TA45JU"]=BErcp45_treeJURA["geometry"].area
areastatrcp45_treeJURA=BErcp45_treeJURA.groupby(["xx"]).agg({'area_TA45JU': 'sum'})
areastatrcp45_treeJURA["ha_TA45JU"]=areastatrcp45_treeJURA["area"]/10000.0
areastatrcp45_treeJURA["BEeinheit"] = areastatrcp45_treeJURA.index

BErcp85_treeJURA.columns
BErcp85_treeJURA["area_TA85JU"]=""
BErcp85_treeJURA["area_TA85JU"]=BErcp85_treeJURA["geometry"].area
areastatrcp85_treeJURA=BErcp85_treeJURA.groupby(["xx"]).agg({'area_TA85JU': 'sum'})
areastatrcp85_treeJURA["ha_TA85JU"]=areastatrcp85_treeJURA["area"]/10000.0
areastatrcp85_treeJURA["BEeinheit"] = areastatrcp85_treeJURA.index

print("area stat Mittelland Durchstichmethode")
BErcp45_treeMittelland.columns # BE heute =='xx' prüfen...stimmt so noch nicht!
BErcp45_treeMittelland["area_TA45ML"]=""
BErcp45_treeMittelland["area_TA45ML"]=BErcp45_treeMittelland["geometry"].area
areastatrcp45_treeML=BErcp45_treeMittelland.groupby(["xx"]).agg({'area_TA45ML': 'sum'})
areastatrcp45_treeML["ha_TA45ML"]=areastatrcp45_treeML["area"]/10000.0
areastatrcp45_treeML["BEeinheit"] = areastatrcp45_treeML.index

BErcp85_treeMittelland.columns
BErcp85_treeMittelland["area_TA85ML"]=""
BErcp85_treeMittelland["area_TA85ML"]=BErcp45_treeJURA["geometry"].area
areastatrcp85_treeML=BErcp85_treeMittelland.groupby(["xx"]).agg({'area_TA85ML': 'sum'})
areastatrcp85_treeML["ha_TA85ML"]=areastatrcp85_treeML["area"]/10000.0
areastatrcp85_treeML["BEeinheit"] = areastatrcp85_treeML.index

print("area stat Alpen Durchstichmethode")
BErcp45_treeAlpen.columns # BE heute =='xx' prüfen...stimmt so noch nicht!
BErcp45_treeAlpen["area_TA45AL"]=""
BErcp45_treeAlpen["area_TA45AL"]=BErcp45_treeAlpen["geometry"].area
areastatrcp45_treeALPS=BErcp45_treeAlpen.groupby(["xx"]).agg({'area_TA45AL': 'sum'})
areastatrcp45_treeALPS["ha_TA45AL"]=areastatrcp45_treeALPS["area"]/10000.0
areastatrcp45_treeALPS["BEeinheit"] = areastatrcp45_treeALPS.index

BErcp85_treeMittelland.columns
BErcp85_treeAlpen["area_TA85AL"]=""
BErcp85_treeAlpen["area_TA85AL"]=BErcp85_treeAlpen["geometry"].area
areastatrcp85_treeALPS=BErcp85_treeAlpen.groupby(["xx"]).agg({'area_TA85AL': 'sum'})
areastatrcp85_treeALPS["ha_TA85AL"]=areastatrcp85_treeALPS["area"]/10000.0
areastatrcp85_treeALPS["BEeinheit"] = areastatrcp85_treeALPS.index

#print("export area stats der Durchstichmethode to excel")
#areastatrcp45_treeJURA.to_excel(outdir+"/areastatrcp45_treeJURA.xlsx")
#areastatrcp85_treeJURA.to_excel(outdir+"/areastatrcp85_treeJURA.xlsx")
#areastatrcp45_treeML.to_excel(outdir+"/areastatrcp45_treeML.xlsx")
#areastatrcp85_treeML.to_excel(outdir+"/areastatrcp85_treeML.xlsx")
#areastatrcp45_treeALPS.to_excel(outdir+"/areastatrcp45_treeALPS.xlsx")
#areastatrcp85_treeALPS.to_excel(outdir+"/areastatrcp85_treeALPS.xlsx")

print("vorhandene Flächenstatistiken reinladen, Header rows umbenennen"
areastatheuteJura=pd.read.excel(myworkspace+"/"+"areastatisticsJura.xlsx", dtype="str", engine='openpyxl'))
areastatheuteJura=pd.DataFrame(areastatheuteJura, columns=['BEeinheit','area','hektar'])
areastatheuteJura=areastatheuteJura.rename(columns={"area":"area_diheuJU", "hektar":"ha_diheuJU"})
areastatheuteJura.columns

areastatrcp45direJura=pd.read.excel(myresults+"/"+"areastatisticsJura_rcp45.xlsx", dtype="str", engine='openpyxl'))
areastatrcp45direJura=pd.DataFrame(areastatrcp45direJura, columns=['BEeinheit','area','hektar'])
areastatrcp45direJura=areastatrcp45direJura.rename(columns={"area":"area_di45JU", "hektar":"ha_di45JU"})
areastatrcp45direJura.columns

areastatrcp85direJura=pd.read.excel(myresults+"/"+"areastatisticsJura_rcp85.xlsx", dtype="str", engine='openpyxl'))
areastatrcp85direJura=pd.DataFrame(areastatrcp85direJura, columns=['BEeinheit','area','hektar'])
areastatrcp85direJura=areastatrcp85direJura.rename(columns={"area":"area_di85JU", "hektar":"ha_di85JU"})
areastatrcp85direJura.columns

areastatheuteML=pd.read.excel(myworkspace+"/"+"areastatisticsMittelland.xlsx", dtype="str", engine='openpyxl'))
areastatheuteML=pd.DataFrame(areastatheuteML, columns=['BEeinheit','area','hektar'])
areastatheuteML=areastatheuteML.rename(columns={"area":"area_diheuML", "hektar":"ha_diheuML"})
areastatheuteML.columns

areastatrcp45direML=pd.read.excel(myresults+"/"+"areastatisticsMittelland_rcp45.xlsx", dtype="str", engine='openpyxl'))
areastatrcp45direML=pd.DataFrame(areastatrcp45direML, columns=['BEeinheit','area','hektar'])
areastatrcp45direML=areastatrcp45direML.rename(columns={"area":"area_di45ML", "hektar":"ha_di45ML"})
areastatrcp45direML.columns

areastatrcp85direML=pd.read.excel(myresults+"/"+"areastatisticsMittelland_rcp85.xlsx", dtype="str", engine='openpyxl'))
areastatrcp85direML=pd.DataFrame(areastatrcp85direML, columns=['BEeinheit','area','hektar'])
areastatrcp85direML=areastatrcp85direML.rename(columns={"area":"area_di85ML", "hektar":"ha_di85ML"})
areastatrcp85direML.columns

areastatheuteALPS=pd.read.excel(myworkspace+"/"+"areastatisticsAlpen.xlsx", dtype="str", engine='openpyxl'))
areastatheuteALPS=pd.DataFrame(areastatheuteALPS, columns=['BEeinheit','area','hektar'])
areastatheuteALPS=areastatheuteALPS.rename(columns={"area":"area_diheuAL", "hektar":"ha_diheuAL"})
areastatheuteALPS.columns

areastatrcp45direALPS=pd.read.excel(myresults+"/"+"areastatisticsAlpen_rcp45.xlsx", dtype="str", engine='openpyxl'))
areastatrcp45direALPS=pd.DataFrame(areastatrcp45direALPS, columns=['BEeinheit','area','hektar'])
areastatrcp45direALPS=areastatrcp45direALPS.rename(columns={"area":"area_di45AL", "hektar":"ha_di45AL"})
areastatrcp45direALPS.columns

areastatrcp85direALPS=pd.read.excel(myresults+"/"+"areastatisticsAlpen_rcp85.xlsx", dtype="str", engine='openpyxl'))
areastatrcp85direALPS=pd.DataFrame(areastatrcp85direALPS, columns=['BEeinheit','area','hektar'])
areastatrcp85direALPS=areastatrcp85direALPS.rename(columns={"area":"area_di85AL", "hektar":"ha_di85AL"})
areastatrcp85direALPS.columns

print("Arealstatistik pro Region und Einheit für alle Szenarien")
areastatJURAmerge=pd.merge(areastatheuteJura,areastatrcp45direJura,areastatrcp85direJura,areastatrcp45_treeJURA,areastatrcp85_treeJURA, on="BEeinheit", how="left") #many to many?
areastatMittellandmerge=pd.merge(areastatheuteML,areastatrcp45direML,areastatrcp85direML,areastatrcp45_treeML,areastatrcp85_treeML, on="BEeinheit", how="left") #many to many?
areastatALpenmerge=pd.merge(areastatheuteALPS,areastatrcp45direALPS,areastatrcp85direALPS,areastatrcp45_treeALPS,areastatrcp85_treeALPS, on="BEeinheit", how="left") #many to many?

areastatJURAmerge.to_excel(outdir+"/areastatJURA.xlsx")
areastatMittellandmerge.to_excel(outdir+"/areastatML.xlsx")
areastatALpenmerge.to_excel(outdir+"/areastatALPS.xlsx")








# Jura
#Beispiel:
#joinJuraheute=areastatheuteJura[["BE_heute","area"]].groupby(["BE_heute"]).agg({'area': 'sum'})
#joinJuraheute["BE_heute"]=joinJuraheute.index

#joinJuraheute=areastatheuteJura[["xx","xx"]].groupby(["xx"]).agg({'xx': 'sum'})
#joinJuraheute["xx"]=joinJuraheute.index
#
#joinJurarcp45dire=areastatrcp45direJura[["xx","xx"]].groupby(["xx"]).agg({'xx': 'sum'})
#joinJurarcp45dire["xx"]=joinJuraheute.index
#
#joinJurarcp85dire=areastatrcp85direJura[["xx","xx"]].groupby(["xx"]).agg({'xx': 'sum'})
#joinJurarcp45dire["xx"]=joinJuraheute.index
#
#joinJurarco45tree=areastatrcp45_treeJURA[["xx","xx"]].groupby(["xx"]).agg({'xx': 'sum'})
#joinJurarco45tree["xx"]=joinJuraheute.index
#
#joinJurarco85tree=areastatrcp85_treeJURA[["xx","xx"]].groupby(["xx"]).agg({'xx': 'sum'})
#joinJurarco85tree["xx"]=joinJuraheute.index
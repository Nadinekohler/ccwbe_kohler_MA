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

# *************************************************************
# Schritt 2: Definition Arbeitsumgebung
print("define workspace")
myresults="E:/Masterarbeit/GIS/Modellergebnisse_221026"
myworkspace="E:/Masterarbeit/GIS"
codespace="E:/Masterarbeit/Parametertabelle"
outdir=myresults

# *************************************************************
# Schritt 3: Einlesen der Shapefiles
print("Shapefiles einlesen")
BEheute=gpd.read_file(myworkspace+"/"+"bestandortstypenarrondiertjoined.shp", dtype="str")
BErcp45_tree=gpd.read_file(myworkspace+"/"+"be_rcp45_zukuenftigestandorteCLEAN.shp", dtype="str")
BErcp85_tree=gpd.read_file(myworkspace+"/"+"be_rcp85_zukuenftigestandorteCLEAN.shp", dtype="str")
BErcp45_dire=gpd.read_file(myresults+"/"+"bestandortstypenarrondiertjoined_rcp45.shp", dtype="str")
BErcp85_dire=gpd.read_file(myresults+"/"+"bestandortstypenarrondiertjoined_rcp85.shp", dtype="str")

BEheute=pd.DataFrame(BEheute, columns=['BE','nais','regionid','region','geometry','Anforderun'])
BErcp45_dire=pd.DataFrame(BErcp45_dire, columns=['BE_zukunft','regionid','region','geometry','Anford_kol'])
BErcp85_dire=pd.DataFrame(BErcp85_dire, columns=['BE_zukunft','regionid','region','geometry','Anford_kol'])
BErcp45_dire.columns
BErcp85_dire.columns

vegheute=gpd.read_file(myworkspace+"/"+"vegetationshoehenstufen19611990owclipkantonbernplus.shp", dtype="str")
vegheute=pd.DataFrame(vegheute, columns=['HS_de','Code','Subcode'])
vegheute.columns
vegrcp45=gpd.read_file(myworkspace+"/"+"bevegetationshoehenstufen20702099rcp45singlepart.shp", dtype="str")
vegrcp45=pd.DataFrame(vegheute, columns=['HS_de','Code','Subcode'])
vegrcp45.columns
vegrcp85=gpd.read_file(myworkspace+"/"+"bevegetationshoehenstufen20702099rcp85singlepart.shp", dtype="str")
vegrcp85=pd.DataFrame(vegheute, columns=['HS_de','Code','Subcode'])
vegrcp85.columns


# Rename header rows
BEheute=BEheute.rename(columns={"BE":"BE_heute","nais":"naisheute"})
BEheute.columns
BErcp45_dire=BErcp45_dire.rename(columns={"BE_zukunft":"BEzukunft45", "Anford_kol":"Anford_kol45"})
BErcp45_dire.columns
BErcp85_dire=BErcp85_dire.rename(columns={"BE_zukunft":"BEzukunft85", "Anford_kol":"Anford_kol85"})
BErcp85_dire.columns
BErcp45_tree=BErcp45_tree.rename(columns={"naisheute":"naisheute45tree","hsheute":"hsheute45tree","naiszukunft":"naiszukunf45tree","hszukunft":"hszukunft45tree","bezukunft":"bezukunft45tree"})
BErcp45_tree.columns
BErcp85_tree=BErcp85_tree.rename(columns={"naisheute":"naisheute85tree","hsheute":"hsheute85tree","naiszukunft":"naiszukunf85tree","hszukunft":"hszukunft85tree","bezukunft":"bezukunft85tree"})
BErcp85_tree.columns

vegheute=vegheute.rename(columns={"HS_de":"HS_heute","Code":"Codeheute","Subcode":"Subcodeheute"})
vegheute.columns
vegrcp45=vegrcp45.rename(columns={"HS_de":"HS_rcp45","Code":"Code_rcp45","Subcode":"Subcodercp45"})
vegrcp45.columns
vegrcp85=vegrcp85.rename(columns={"HS_de":"HS_rcp85","Code":"Code_rcp85","Subcode":"Subcodercp85"})
vegrcp85.columns



# *************************************************************
# Schritt 4: Fehlende Attributte (Regionen und Höhenstufen) den Shapefiles anhängen --> Overlay?
print("Regionen der Durchstichmethode anfügen")

# Regionid an TreeApp RCP 45 anfügen --> bestandortstypenjoinedarrondiert.shp verwenden, dort ist die regionid drin und dann mit Overlay, union? Nachher alle neuen Attributte löschen und nur noch regionid hinzunehmen?
BErcp45_treereg=gpd.overlay(BErcp45_tree,BEheute,how='union')
BErcp45_treereg=pd.DataFrame(BErcp45_treereg, columns=['naisheute45TA','hsheute45TA','naiszukunf','hszukunft45TA','geometry','bezukunft45TA','regionid'])


# Regionid an TreeApp RCP 85 anfügen --> siehe oben



print("Alle Höhenstufen den heutigen Einheiten und jenen der direkten Methode anfügen")
BEheuteveghs=gpd.overlay(BEheute,vegheute,how="union")

# *************************************************************
# Schritt 5: Shapefiles nach Regionen bilden
print("Einheiten von heute nach Regionen exportieren")
BEheuteJURA=BEheute[BEheute["regionid"]==1]
BEheuteMittelland=BEheute[BEheute["regionid"]==2]
BEheuteAlpen=BEheute[BEheute["regionid"]==3]

BEheuteJURA.to_file(outdir+"/BEheuteJura.shp")
BEheuteMittelland.to_file(outdir+"/BEheuteMittelland.shp")
BEheuteAlpen.to_file(outdir+"/BEheuteAlpen.shp")
print("exported subset shapefiles BEheute")

print("Einheiten der direkten Methode nach Regionen exportieren")
# BErcp45_dire
BErcp45_direJURA=BEheute[BEheute["regionid"]==1]
BErcp45_direMittelland=BEheute[BEheute["regionid"]==2]
BErcp45_direAlpen=BEheute[BEheute["regionid"]==3]

BErcp45_direJURA.to_file(outdir+"/BErcp45_direJURA.shp")
BErcp45_direMittelland.to_file(outdir+"/BErcp45_direMittelland.shp")
BErcp45_direAlpen.to_file(outdir+"/BErcp45_direAlpen.shp")
print("exported subset shapefiles BErcp45_dire")

# BErcp85_dire
BErcp85_direJURA=BEheute[BEheute["regionid"]==1]
BErcp85_direMittelland=BEheute[BEheute["regionid"]==2]
BErcp85_direAlpen=BEheute[BEheute["regionid"]==3]

BErcp85_direJURA.to_file(outdir+"/BErcp85_direJURA.shp")
BErcp85_direMittelland.to_file(outdir+"/BErcp85_direMittelland.shp")
BErcp85_direAlpen.to_file(outdir+"/BErcp85_direAlpen.shp")
print("exported subset shapefiles BErcp85_dire")

print("Einheiten der Durchstichmethode nach Regionen exportieren")
# BErcp45_tree
BErcp45_treeJURA=BErcp45_treeJURA[BErcp45_treeJURA["regionid"]==1]
BErcp45_treeMittelland=BErcp45_treeMittelland[BErcp45_treeMittelland["regionid"]==2]
BErcp45_treeAlpen=BErcp45_treeAlpen[BErcp45_treeAlpen["regionid"]==3]

BErcp45_treeJURA.to_file(outdir+"/BErcp45_treeJURA.shp")
BErcp45_treeMittelland.to_file(outdir+"/BErcp45_treeMittelland.shp")
BErcp45_treeAlpen.to_file(outdir+"/BErcp45_treeAlpen.shp")
print("exported subset shapefiles BErcp45_tree")

# BErcp85_tree
BErcp85_treeJURA=BErcp85_treeJURA[BErcp85_treeJURA["regionid"]==1]
BErcp85_treeMittelland=BErcp85_treeMittelland[BErcp85_treeMittelland["regionid"]==2]
BErcp85_treeAlpen=BErcp85_treeAlpen[BErcp85_treeAlpen["regionid"]==3]

BErcp85_treeJURA.to_file(outdir+"/BErcp85_treeJURA.shp")
BErcp85_treeMittelland.to_file(outdir+"/BErcp85_treeMittelland.shp")
BErcp85_treeAlpen.to_file(outdir+"/BErcp85_treeAlpen.shp")
print("exported subset shapefiles BErcp85_tree")

# *************************************************************
# Schritt 6: Überlagerung der Shapes für die Sankey Diagramme

print("geopandas overlay Einheiten heute mit der direkten Methode") #für die Sankey Diagramme
Einheitenheuteundrcp45direJURA=gpd.overlay(BEheuteJURA,BErcp45_direJURA,how='union')
Einheitenheuteundrcp85direJURA=gpd.overlay(BEheuteJURA,BErcp85_direJURA,how='union')

Einheitenheuteundrcp45direML=gpd.overlay(BEheuteMittelland,BErcp45_direMittelland,how='union')
Einheitenheuteundrcp85direML=gpd.overlay(BEheuteMittelland,BErcp85_direMittelland,how='union')

Einheitenheuteundrcp45direALPS=gpd.overlay(BEheuteAlpen,BErcp45_direAlpen,how='union')
Einheitenheuteundrcp85direALPS=gpd.overlay(BEheuteAlpen,BErcp85_direAlpen,how='union')

print("geopandas overlay Einheiten heute mit der Durchstichmethode") #für die Sankey Diagramme
Einheitenheuteundrcp45treeJURA=gpd.overlay(BEheuteJURA,BErcp45_treeJURA,how='union')
Einheitenheuteundrcp85treeJURA=gpd.overlay(BEheuteJURA,BErcp85_treeJURA,how='union')

Einheitenheuteundrcp45treeML=gpd.overlay(BEheuteMittelland,BErcp45_treeMittelland,how='union')
Einheitenheuteundrcp85treeML=gpd.overlay(BEheuteMittelland,BErcp85_treeMittelland,how='union')

Einheitenheuteundrcp45treeALPS=gpd.overlay(BEheuteAlpen,BErcp45_treeAlpen,how='union')
Einheitenheuteundrcp85treeALPS=gpd.overlay(BEheuteAlpen,BErcp85_treeAlpen,how='union')

# *************************************************************
# Schritt 7: Überlagerung der Shapes für die geometrische Analyse

print("geopandas overlay Einheiten der beiden zukünftigen Methoden")
Einheitenrcp45JURA=gpd.overlay(BErcp45_direJURA,BErcp45_treeJURA,how='intersection')
Einheitenrcp85JURA=gpd.overlay(BErcp85_direJURA,BErcp85_treeJURA,how='intersection')

Einheitenrcp45ML=gpd.overlay(BErcp45_direMittelland,BErcp45_treeMittelland,how='intersection')
Einheitenrcp85ML=gpd.overlay(BErcp85_direMittelland,BErcp85_treeMittelland,how='intersection')

Einheitenrcp45ALPS=gpd.overlay(BErcp45_direAlpen,BErcp45_treeAlpen,how='intersection')
Einheitenrcp85ALPS=gpd.overlay(BErcp85_direAlpen,BErcp85_treeAlpen,how='intersection')


# *************************************************************
# Schritt 8: Flächenstatistik nach Regionen --> das brauche ich nur für die Modellierung der Durchstichmethode zu machen, bei den anderen werden diese schon modelliert!

print("area stat Jura Durchstichmethode")
BErcp45_treeJURA["area"]=""
BErcp45_treeJURA["area"]=BErcp45_treeJURA["geometry"].area
areastatrcp45_treeJURA=BEheuteJURA.groupby(["BE_heute"]).agg({'area': 'sum'}) #BE heute etc. prüfen...stimmt so noch nicht!
areastatrcp45_treeJURA["hektar"]=areastatrcp45_treeJURA["area"]/10000.0
areastatrcp45_treeJURA["BEeinheit"] = areastatrcp45_treeJURA.index

BErcp85_treeJURA["area"]=""
BErcp85_treeJURA["area"]=BErcp45_treeJURA["geometry"].area
areastatrcp85_treeJURA=BEheuteJURA.groupby(["BE_heute"]).agg({'area': 'sum'})
areastatrcp85_treeJURA["hektar"]=areastatrcp85_treeJURA["area"]/10000.0
areastatrcp85_treeJURA["BEeinheit"] = areastatrcp85_treeJURA.index

print("area stat Mittelland Durchstichmethode")
BErcp45_treeMittelland["area"]=""
BErcp45_treeMittelland["area"]=BErcp45_treeJURA["geometry"].area
areastatrcp45_treeML=BEheuteJURA.groupby(["BE_heute"]).agg({'area': 'sum'})
areastatrcp45_treeML["hektar"]=areastatrcp45_treeML["area"]/10000.0
areastatrcp45_treeML["BEeinheit"] = areastatrcp45_treeML.index

print("area stat Mittelland Durchstichmethode")
BErcp85_treeMittelland["area"]=""
BErcp85_treeMittelland["area"]=BErcp45_treeJURA["geometry"].area
areastatrcp85_treeML=BEheuteJURA.groupby(["BE_heute"]).agg({'area': 'sum'})
areastatrcp85_treeML["hektar"]=areastatrcp85_treeML["area"]/10000.0
areastatrcp85_treeML["BEeinheit"] = areastatrcp85_treeML.index

print("area stat Alpen Durchstichmethode")
BErcp45_treeAlpen["area"]=""
BErcp45_treeAlpen["area"]=BErcp45_treeJURA["geometry"].area
areastatrcp45_treeALPS=BEheuteJURA.groupby(["BE_heute"]).agg({'area': 'sum'})
areastatrcp45_treeALPS["hektar"]=areastatrcp45_treeALPS["area"]/10000.0
areastatrcp45_treeALPS["BEeinheit"] = areastatrcp45_treeALPS.index

print("area stat Alpen Durchstichmethode")
BErcp85_treeAlpen["area"]=""
BErcp85_treeAlpen["area"]=BErcp45_treeJURA["geometry"].area
areastatrcp85_treeALPS=BEheuteJURA.groupby(["BE_heute"]).agg({'area': 'sum'})
areastatrcp85_treeALPS["hektar"]=areastatrcp85_treeALPS["area"]/10000.0
areastatrcp85_treeALPS["BEeinheit"] = areastatrcp85_treeALPS.index

#print("export area stats der Durchstichmethode to excel")
#areastatrcp45_treeJURA.to_excel(outdir+"/areastatrcp45_treeJURA.xlsx")
#areastatrcp85_treeJURA.to_excel(outdir+"/areastatrcp85_treeJURA.xlsx")
#areastatrcp45_treeML.to_excel(outdir+"/areastatrcp45_treeML.xlsx")
#areastatrcp85_treeML.to_excel(outdir+"/areastatrcp85_treeML.xlsx")
#areastatrcp45_treeALPS.to_excel(outdir+"/areastatrcp45_treeALPS.xlsx")
#areastatrcp85_treeALPS.to_excel(outdir+"/areastatrcp85_treeALPS.xlsx")

# *************************************************************
# Schritt 9: Flächenstatistik pro Einheit und allen Szenarien

areastatheuteJura=pd.read.excel(myworkspace+"/"+"areastatisticsJura.xlsx", dtype="str", engine='openpyxl'))
areastatrcp45direJura=pd.read.excel(myresults+"/"+"areastatisticsJura_rcp45.xlsx", dtype="str", engine='openpyxl'))
areastatrcp85direJura=pd.read.excel(myresults+"/"+"areastatisticsJura_rcp85.xlsx", dtype="str", engine='openpyxl'))
areastatheuteML=pd.read.excel(myworkspace+"/"+"areastatisticsMittelland.xlsx", dtype="str", engine='openpyxl'))
areastatrcp45direML=pd.read.excel(myresults+"/"+"areastatisticsMittelland_rcp45.xlsx", dtype="str", engine='openpyxl'))
areastatrcp85direML=pd.read.excel(myresults+"/"+"areastatisticsMittelland_rcp85.xlsx", dtype="str", engine='openpyxl'))
areastatheuteALPS=pd.read.excel(myworkspace+"/"+"areastatisticsAlpen.xlsx", dtype="str", engine='openpyxl'))
areastatrcp45direALPS=pd.read.excel(myresults+"/"+"areastatisticsAlpen_rcp45.xlsx", dtype="str", engine='openpyxl'))
areastatrcp85direALPS=pd.read.excel(myresults+"/"+"areastatisticsAlpen_rcp85.xlsx", dtype="str", engine='openpyxl'))


# Jura

joinJuraheute=areastatheuteJura[["BE_heute","area"]].groupby(["BE_heute"]).agg({'area': 'sum'})
joinJuraheute["BE_heute"]=joinJuraheute.index

joinJurarcp45dire=areastatrcp45direJura[["BE_heute","area"]].groupby(["BE_heute"]).agg({'area': 'sum'})
joinJurarcp45dire["BE_heute"]=joinJuraheute.index

joinJurarcp85dire=areastatrcp85direJura[["BE_heute","area"]].groupby(["BE_heute"]).agg({'area': 'sum'})
joinJurarcp45dire["BE_heute"]=joinJuraheute.index


areatatJURAmerge=areastatheuteJura.merge(joinJuraheute[["BE_heute", "area"]])

# Mittelland
# ...


# Alpen
# ...

#areastatisticsJura=areastatisticsJura.merge(joinJura[["BEeinheit","Priorisierung Jura"]], on='BEeinheit',how="left")


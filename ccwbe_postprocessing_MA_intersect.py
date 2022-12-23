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

BEdire85ML=gpd.read_file(myresults+"/"+"bercp85MLintersect.shp", dtype="str")
BEdire85ML.columns

BEdire85ML=pd.DataFrame(BEdire85ML, columns=['naiszukunf','bezukunft','flaeche','nais','HS_rcp45','Anford_kol'])
BEdire85ML.columns

BEdire85ML

#Hit Rate wo BE_zukunft mit bezukunft, oder Anforderungsprofile zutrifft --> welche Einheiten muss ich verwenden

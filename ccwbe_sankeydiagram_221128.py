# Title: Berechnung eines Chord-Diagrammes

# Author: Nadine Kohler
# Stand: 28.11.2022

# Thesis:
## Die Entwicklung des Waldes im Kanton Bern basierend auf der klimabedingten Verschiebung der Vegetationshöhenstufen
## Eine partizipative Modellierung von Berner Waldstandorttypen für die Periode 2070-99


# Modules
import pandas as pd
from pySankey.sankey import sankey
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

# Environment settings
myworkspace="E:/Masterarbeit/GIS/Modellergebnisse_221206"
mycodespace="E:/Masterarbeit/ccwbe_kohler_MA/ccwbe_kohler_MA"
myresults="E:/Masterarbeit/Chord_diagrams/Auswertungen"
outdir=myresults

# Read Excel
print("read data")
#data = pd.read_csv(myworkspace+"/"+"sttypenintrsct_Jura_HS_heute85.csv",low_memory=False)
dfdata = pd.read_table(myworkspace+"/"+"beMLintrctheutercp85.txt", sep=',',low_memory=False)
dfdata.columns
dfdata.head(5)

# Define important columns
data=pd.DataFrame(dfdata, columns=['BE','BE_zukunft','flaeche','HS_heute','HS_rcp45','HS_rcp85'])
print(data.head(5))
data.columns
data.dtypes

# Make subset with vegetation belt
subset_data=data[data.HS_heute == 4]
subset_data.head(5)
print(subset_data)

parameterdf=pd.read_excel(mycodespace+"/"+"Parametertabelle_2070-99_Waldstandorte_BE_221118.xlsx", dtype="str", engine='openpyxl')
parameterdf.columns
allSW=parameterdf[((~parameterdf["Sonderwald"].astype(str).str.contains("0"))|(parameterdf["Sonderwald"].astype(str).str.contains("1"))|(parameterdf["Sonderwald"].astype(str).str.contains("2"))|(parameterdf["Sonderwald"].astype(str).str.contains("3"))|(parameterdf["Sonderwald"].astype(str).str.contains("4"))|(parameterdf["Sonderwald"].astype(str).str.contains("5"))|(parameterdf["Sonderwald"].astype(str).str.contains("6"))|(parameterdf["Sonderwald"].astype(str).str.contains("7"))|(parameterdf["Sonderwald"].astype(str).str.contains("8"))|(parameterdf["Sonderwald"].astype(str).str.contains("9"))|(parameterdf["Sonderwald"].astype(str).str.contains("10")))]
allSWtolist=allSW["BE"].unique().tolist()
dataSW=subset_data[subset_data["BE"].isin(allSWtolist)]
dataSW
dataSW.sort_values(by='HS_rcp85', ascending=False)

allnormal=parameterdf[((parameterdf["Sonderwald"].astype(str).str.contains("0"))&(~parameterdf["Sonderwald"].astype(str).str.contains("1"))&(~parameterdf["Sonderwald"].astype(str).str.contains("2"))&(~parameterdf["Sonderwald"].astype(str).str.contains("3"))&(~parameterdf["Sonderwald"].astype(str).str.contains("4"))&(~parameterdf["Sonderwald"].astype(str).str.contains("5"))&(~parameterdf["Sonderwald"].astype(str).str.contains("6"))&(~parameterdf["Sonderwald"].astype(str).str.contains("7"))&(~parameterdf["Sonderwald"].astype(str).str.contains("8"))&(~parameterdf["Sonderwald"].astype(str).str.contains("9"))&(~parameterdf["Sonderwald"].astype(str).str.contains("10")))]
allnormaltolist=allnormal["BE"].unique().tolist()
datanormal=subset_data[subset_data["BE"].isin(allnormaltolist)]
datanormal
datanormal.sort_values(by='HS_rcp85', ascending=False)

# Draw Basic Sankey Diagram
print("define source, target and area")
#sankey(left=sm_data["BE"], right=sm_data["BE_rcp85"], leftWeight=sm_data["flaeche"], rightWeight=sm_data["flaeche"], figure_name=["Test"], aspect=4, fontsize=8)
sankey(left=dataSW["BE"], right=dataSW["BE_zukunft"], leftWeight=dataSW["flaeche"], rightWeight=dataSW["flaeche"], figure_name=["Sonderwaldstandorte Jura im Submontan"], aspect=4, fontsize=8)
sankey(left=datanormal["BE"], right=datanormal["BE_zukunft"], leftWeight=datanormal["flaeche"], rightWeight=datanormal["flaeche"], figure_name=["Waldstandorte Jura im Jura"], aspect=4, fontsize=8)
#sankey(left=datanormal["BE"], right=datanormal["BE_rcp85"].sort_values(by='Code_rcp85', ascending=False), leftWeight=datanormal["flaeche"], rightWeight=datanormal["flaeche"], figure_name=["Waldstandorte Jura im Jura"], aspect=4, fontsize=8)


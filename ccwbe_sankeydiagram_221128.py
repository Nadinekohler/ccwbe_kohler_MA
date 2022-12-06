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
#import plotly
#import plotly.graph_objects as go
#import plotly.express as pex
#import os


# Environment settings
myworkspace="E:/Masterarbeit/Chord_diagrams/1_Durchlauf"
mycodespace="E:/Masterarbeit/ccwbe_kohler_MA/ccwbe_kohler_MA"

# Read Excel
print("read data")
#data = pd.read_csv(myworkspace+"/"+"sttypenintrsct_Jura_HS_heute85.csv",low_memory=False)
dfdata = pd.read_csv(myworkspace+"/"+"Test_direkt_jura.csv", sep=';')
dfdata.columns
dfdata.head(5)

# Define important columns
data=pd.DataFrame(dfdata, columns=['BE','BE_rcp45','BE_rcp85','flaeche','Code_heute','Code_rcp45','Code_rcp85'])
print(data.head(5))
data.columns
data.dtypes

# Make subset with vegetation belt
subset_data=data[data.Code_heute == 4] #AND SW = 0
subset_data.head(5)
print(subset_data)

parameterdf=pd.read_excel(mycodespace+"/"+"Parametertabelle_2070-99_Waldstandorte_BE_221118.xlsx", dtype="str", engine='openpyxl')
parameterdf.columns
allSW=parameterdf[parameterdf["Sonderwald"] != 0]
allSWtolist=allSW["BE"].unique().tolist()
dataSW=subset_data[subset_data["BE"].isin(allSWtolist)]
dataSW

allnormal=parameterdf[parameterdf["Sonderwald"] == 0]
allnormaltolist=allnormal["BE"].unique().tolist()
datanormal=subset_data[subset_data["BE"].isin(allnormaltolist)]
datanormal

viridis=plt.colormaps['viridis']
colors = ["#ffffcc", "#a1dab4", "#41b6c4", "#2c7fb8", "#253494"]
my_cmap = ListedColormap(colors, name="my_cmap")


# Draw Basic Sankey Diagram with normal Einheiten
print("define source, target and area")
#sankey(left=sm_data["BE"], right=sm_data["BE_rcp85"], leftWeight=sm_data["flaeche"], rightWeight=sm_data["flaeche"], figure_name=["Test"], aspect=4, fontsize=8)
sankey(left=dataSW["BE"], right=dataSW["BE_rcp85"], leftWeight=dataSW["flaeche"], rightWeight=dataSW["flaeche"], figure_name=["Test"], aspect=4, fontsize=8)
#sankey(left=datanormal["BE"], right=datanormal["BE_rcp85"], leftWeight=datanormal["flaeche"], rightWeight=datanormal["flaeche"], figure_name=["Test"], aspect=4, fontsize=8)






# sort descending for the future scenario --> How can I sort within sm_data and not making a new list?
#sm_data_sorted=sm_data.Code_rcp45.sort_values(ascending=False)
#print(sm_data_sorted)

# Define group colors for vegetation belt --> doesn't work
#colors = {
#    for 2 in Code_rcp45: "#f71b1b",
#   for 4 in Code_rcp45: "#1b7ef7",
#}

#hs_all=sm_data.Code_heute.tolist() + sm_data.Code_rcp45.tolist() + sm_data.Code_rcp85.tolist()
#hs_rcp45=sm_data.Code_rcp45.tolist()
#print(hs_rcp45)


# Save the figure --> doesn't work
#print("export diagram")
#fig.savefig(myworkspace+"test.png", bbox_inches="tight", dpi=150)
## Get current figure
#print("show sankey diagram")
#fig = plt.gcf()
## Format diagram
#print("adjust format")
## Set size
#fig.set_size_inches(6, 6)
## Set background to white
#fig.set_facecolor("w")
#fig.update_layout(title_text="Veränderung der Standorttypen", font_size=10)

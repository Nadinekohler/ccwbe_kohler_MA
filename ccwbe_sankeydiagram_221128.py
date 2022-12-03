# Title: Berechnung eines Chord-Diagrammes

# Author: Nadine Kohler
# Stand: 28.11.2022

# Thesis:
## Die Entwicklung des Waldes im Kanton Bern basierend auf der klimabedingten Verschiebung der Vegetationshöhenstufen
## Eine partizipative Modellierung von Berner Waldstandorttypen für die Periode 2070-99


# Environment settings
myworkspace="E:/Masterarbeit/Chord_diagrams/1_Durchlauf"
mycodespace="E:/Masterarbeit/ccwbe_kohler_MA/ccwbe_kohler_MA"

# Modules
import pandas as pd
from pySankey.sankey import sankey
import matplotlib.pyplot as plt
import plotly
import plotly.graph_objects as go
import plotly.express as pex
import os


# Read Excel
print("read data")
#data = pd.read_csv(myworkspace+"/"+"sttypenintrsct_Jura_HS_heute85.csv",low_memory=False)
dfdata = pd.read_csv(myworkspace+"/"+"Test_direkt_jura.csv", dtype=str)
dfdata.columns
dfdata.head(5)


data=pd.DataFrame(dfdata, columns=['BE','BE_rcp45','BE_rcp85','flaeche','Code_heute','Code_rcp45','Code_rcp85'],dtype=str)
print(data.head(5))
data.columns


# Draw Sankey Diagram
print("define source, target and area")
sankey(left=data["BE"], right=data["BE_rcp85"], leftWeight=data["flaeche"], rightWeight=data["flaeche"], aspect=20, fontsize=9)
#sankey(left=data["hsheute"], right=data["hszukunft"], leftWeight=data["BE"], rightWeight=data["BE_zukunft"], aspect=20, fontsize=9)
#sankey(left=data[source_indices], right=data[target_indices], leftWeight=data[source_flaeche], rightWeight=data[target_flaeche], aspect=20, fontsize=9)

# Get current figure
print("show sankey diagram")
fig = plt.gcf()

# Format diagram
print("adjust format")
# Set size
fig.set_size_inches(6, 6)

# Set background to white
fig.set_facecolor("w")

fig.update_layout(title_text="Veränderung der Standorttypen", font_size=10)

# Save the figure
print("export diagram")
fig.savefig(myworkspace+"test.png", bbox_inches="tight", dpi=150)
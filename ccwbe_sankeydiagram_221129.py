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
import plotly.io
import pandas as pd
from pySankey.sankey import sankey
import matplotlib.pyplot as plt
import plotly
import plotly.graph_objects as go
import plotly.express as pex
import os



# Read Excel
print("read data")
dfdata = pd.read_csv(myworkspace+"/"+"Test_direkt_jura.csv", sep=";", low_memory=False)
dfdata.columns
dfdata.head(5)

data=pd.DataFrame(dfdata, columns=['BE','BE_rcp45','BE_rcp85','flaeche','Code_heute','Code_rcp45','Code_rcp85'])
data.head(5)

# Define all chart nodes
all_nodes=data.BE.values.tolist() + data.BE_rcp45.values.tolist() + data.BE_rcp85.values.tolist()
all_nodes

#Define vegetation belts
all_hs=data.Code_heute.tolist() + data.Code_rcp45.tolist() + data.Code_rcp85.tolist()

# Indices of sources and targets
source_indices = [all_nodes.index(BE) for BE in data.BE]
target_indices = [all_nodes.index(BE_rcp45) for BE_rcp45 in data.BE_rcp45]


fig = go.Figure(data=[go.Sankey(
                        # Define nodes
                        node = dict(
                          label = all_hs,
                          color = (for 2 in all_hs["black"]), (for 4 in all_hs["orange"]), (for 5 in all_hs["purple"]),(for 6 in all_hs["yellow"]),(for 8 in all_hs["blue"]),(for 9 in all_hs["green"]),(for 10 in all_hs["red"]),
                        ),

                        # Add links
                        link = dict(
                          source =  source_indices,
                          target =  target_indices,
                          value =  data.flaeche,
                        )
                    )
                ])

fig.update_layout(title_text="test",
                  font_size=10)


plotly.io.write_image(fig,myworkspace + "test.jpeg")
if not os.path.exists("images"):
    os.mkdir("images")
fig.write_image("images/test.jpeg")
# Title: Berechnung eines Chord-Diagrammes

# Author: Nadine Kohler
# Stand: 28.11.2022

# Thesis:
## Die Entwicklung des Waldes im Kanton Bern basierend auf der klimabedingten Verschiebung der Vegetationshöhenstufen
## Eine partizipative Modellierung von Berner Waldstandorttypen für die Periode 2070-99


# Environment settings
import plotly.io

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
data = pd.read_csv(myworkspace+"/"+"sttypenintrsct_Jura_HS_heute85.csv", low_memory=False)
data.columns


# Define all chart nodes
all_nodes=data.BE.values.tolist() + data.BE_zukunft.values.tolist()

# Indices of sources and destinations
source_indices = [all_nodes.index(BE) for BE in data.BE]
target_indices = [all_nodes.index(BE_zukunft) for BE_zukunft in data.BE_zukunft]


fig = go.Figure(data=[go.Sankey(
                        # Define nodes
                        node = dict(
                          label =  all_nodes,
                          color =  "black"
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

fig



plotly.io.write_image(fig,myworkspace + "test.jpeg")
if not os.path.exists("images"):
    os.mkdir("images")
fig.write_image("images/test.jpeg")
# Titel: Berechnung eines Chord-Diagrammes

# Autorin: Nadine KOhler
# Stand: 25.11.2022

# Masterarbeit:
# Die Entwicklung des Waldes im Kanton Bern basierend auf der klimabedingten Verschiebung der Vegetationshöhenstufen
# Eine partizipative Modellierung von Berner Waldstandorttypen für die Periode 2070-99


#environment settings
myworkspace="E:/Masterarbeit/Chord_diagrams/1_Durchlauf"
mycodespace="E:/Masterarbeit/ccwbe_kohler_MA/ccwbe_kohler_MA"


#Module:
import pandas as pd
import holoviews as hv
from holoviews import opts, dim
import holoviews.plotting.bokeh
hv.extension('bokeh')
hv.output(size=200)
import matplotlib
import bokeh
import selenium
from bokeh.io import show, export_png


#Excel-Tabellen:
#dfdata = pd.read_excel(myworkspace+"/"+"sttypenintrsct_Jura_heute85.xlsx")
dfdata = pd.read_excel(myworkspace+"/"+"Test.xlsx", dtype=str)
dfdata.columns

data=pd.DataFrame(dfdata, columns=['BE','BE_zukunft','flaeche'])
print(data.head(5))
data.columns

# Node-Data
node_data = pd.read_excel(mycodespace+"/"+"Nodes_Chord_diagram.xlsx", dtype=str)
print(node_data.head(5))
#add node labels
nodes=hv.Dataset(pd.DataFrame(node_data['Berner Einheiten']),'index')
nodes.columns


#create chord object
chord=hv.Chord((data, nodes)).select(value=(5, None))

chord.opts(opts.Chord(cmap='Category20', edge_cmap='Category20', edge_color=dim('BE').astype(str), labels='nodes', node_color=dim('index').astype(str)))
bokeh.io.show(chord)

#export
#bokeh.io.export_png(chord,myworkspace+'chord_jura_rcp45.png')
bokeh.io.export_png(chord,myworkspace+'test.png')
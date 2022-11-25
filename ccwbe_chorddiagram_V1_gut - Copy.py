
#Mein Skript:
#Titel: Chord diagram
#Autorin: Nadine Kohler

#environment settings
#myworkspace="E:/Masterarbeit/GIS/Modellergebnisse_221026"
#outdir="E:/Masterarbeit/Chord_diagrams"

myworkspace="E:/Masterarbeit/Chord_diagrams/1_Durchlauf"
outdir="E:/Masterarbeit/Chord_diagrams/1_Durchlauf"

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
dfdata = pd.read_excel(myworkspace+"/"+"sttypenintrsct_Jura_heute85.xlsx")
dfdata.columns

data=pd.DataFrame(dfdata, columns=['BE','BE_zukunft','flaeche'])
print(data.head(5))
data.columns

# Node-Data
node_data = pd.read_excel(myworkspace+"/"+"Nodes_Chord_diagram.xlsx")
print(node_data.head(5))

#add node labels
nodes=hv.Dataset(pd.DataFrame(node_data['Berner Einheiten']),'index')

#create chord object
chord=hv.Chord((data, nodes)).select(value=(5, None))

#costomization of chart
chord.opts(opts.Chord(cmap='Category20', edge_cmap='Category20', edge_color=dim('BE').str(), labels='nodes', node_color=dim('index').str()))
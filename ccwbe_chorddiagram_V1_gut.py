
#Mein Skript:
#Titel: Chord diagram
#Autorin: Nadine Kohler

#environment settings
myworkspace="E:/Masterarbeit/Chord_diagrams/1_Durchlauf"
outdir="E:/Masterarbeit/Chord_diagrams/1_Durchlauf"

#Module:
import pandas as pd
import numpy as np
import holoviews as hv
from holoviews import opts, dim
import matplotlib
import bokeh
import selenium
from bokeh.io import show, export_png


#Excel-Tabellen:
dfdata = pd.read_excel(myworkspace+"/"+"Test.xlsx", dtype=str)
#dfedges = pd.read_excel(myworkspace+"/"+"Nodes_Chord_diagram.xlsx", dtype=str)
dfdata.columns

# Names of the features.
names = pd.read_excel(myworkspace+"/"+"Nodes_Chord_diagram.xlsx")
print(names.head(5))

hv.Chord(names)

#Output Definitionen
hv.extension('matplotlib')
hv.output(fig='png',size=300)


#Definitionen
#edges=pd.DataFrame(dfedges)
#print(edges.head(5))

data=pd.DataFrame(dfdata, columns=['BE','BE_zukunft','flaeche'])
print(data.head(5))

hv.Chord(data)

nodes=hv.Dataset(pd.DataFrame(data),'index')
nodes.data.head()

chord = hv.Chord((data)).select(value=(5, None))
chord.opts(opts.Chord(cmap='Category20', edge_cmap='Category20', labels=['data'], node_color=dim('data').str())) #edge_color=dim('source').str(),

bokeh.io.show(chord)

#write output
chord.background_fill_color = None
chord.border_fill_color = None
hv.save(chord, 'test_chord.png', fmt='png')
chord

#export_png(chord, filename="test.png")
print("modelling done ...")




#"BE_chord_Jura_rcp45.html")
#"BE_chord_Jura_rcp85.html")
#"BE_chord_ML_rcp45.html")
#"BE_chord_ML_rcp85.html")
#"BE_chord_Alpen_rcp45.html")
#"BE_chord_Alpen_rcp85.html")


show(chord)




#colormap = ["#444444", "#a6cee3", "#1f78b4", "#b2df8a", "#33a02c", "#fb9a99", "#e31a1c", "#fdbf6f", "#ff7f00", "#cab2d6", "#6a3d9a"]

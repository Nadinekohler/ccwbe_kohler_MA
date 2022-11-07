
#Code for creating the Chord Diagram with Python
#Author: Nadine
# *************************************************************

#environment settings
myworkspace="E:/Masterarbeit/Chord_diagrams"
outdir=myworkspace
# *************************************************************

#importing Pandas library and packages

import pandas as pd
import holoviews as hv
from holoviews import opts, dim
import matplotlib
import bokeh
from bokeh.io import show

#Anhand Beispiel les miserables:

from bokeh.sampledata.les_mis import data

#hv.extension('bokeh')
#hv.output(size=200)

hv.extension('matplotlib')
hv.output(fig='svg',size=200)

links=pd.DataFrame(data['links'])
print(links.head(3))
hv.Chord(links)

nodes=hv.Dataset(pd.DataFrame(data['nodes']), 'index')
nodes.data.head()

chord = hv.Chord((links, nodes)).select(value=(5, None))
chord.opts(opts.Chord(cmap='Category20', edge_cmap='Category20', edge_color=dim('source').str(), labels='name', node_color=dim('index').str()))



#Code for creating the Chord Diagram with Python
#Author: Nadine


# *************************************************************
#environment settings
myworkspace="E:/Masterarbeit/GIS"
referenceraster=myworkspace+"/bedem10m.tif"
codespace="E:/Masterarbeit/Parametertabelle"
#outdir=myworkspace+"/out20220112_mitSturztrajektorien"
outdir=myworkspace
#model parameter file
parameterdf=pd.read_excel(codespace+"/"+"Anhang1_Parameter_Waldstandorte_BE_erweitert_220929.xlsx", dtype="str", engine='openpyxl')
parameterdf.columns

# *************************************************************
#importing Pandas library
import pandas as pd
import bokeh
import bkcharts
from bkcharts import output_file, Chord
from bokeh.io import show
from bokeh.sampledata.les_mis import data

nodes = data['nodes']
links = data['links']

nodes_df = pd.DataFrame(nodes)
links_df = pd.DataFrame(links)

source_data = links_df.merge(nodes_df, how='left', left_on='source', right_index=True)
source_data = source_data.merge(nodes_df, how='left', left_on='target', right_index=True)
source_data = source_data[source_data["value"] > 5]

chord_from_df = Chord(source_data, source="name_x", target="name_y", value="value")
output_file('chord_from_df.html', mode="inline")
show(chord_from_df)
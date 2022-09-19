import numpy as np
import arcpy
from pandas import Series, DataFrame
import pandas as pd
arcpy.CheckOutExtension("Spatial")
from pylab import *
import matplotlib.pyplot as plt


def gridasciitonumpyarrayfloat(ingridfilefullpath):
    i=0
    row = 0
    headerstr=''
    infile=open(ingridfilefullpath, "r")
    for line in infile:
        if i==0:
            ncols=int(line.strip().split()[-1])
            headerstr+=line
        elif i==1:
            nrows=int(line.strip().split()[-1])
            headerstr += line
        elif i==2:
            xllcorner=float(line.strip().split()[-1])
            headerstr += line
        elif i==3:
            yllcorner=float(line.strip().split()[-1])
            headerstr += line
        elif i==4:
            cellsize=float(line.strip().split()[-1])
            headerstr += line
        elif i==5:
            NODATA_value=float(line.strip().split()[-1])
            arr=np.zeros((nrows, ncols), dtype=float)
            arr[:,:]=NODATA_value
            headerstr += line.replace("\n","")
        elif i>5 and i<nrows:
            col=0
            while col<ncols:
                for item in line.strip().split():
                    arr[row,col]=float(item)
                    col+=1
            row+=1
        i+=1
    infile.close()
    return arr, ncols, nrows, xllcorner, yllcorner, cellsize, NODATA_value, headerstr
def gridasciitonumpyarrayint(ingridfilefullpath):
    i=0
    row = 0
    headerstr=''
    infile=open(ingridfilefullpath, "r")
    for line in infile:
        if i==0:
            ncols=int(line.strip().split()[-1])
            headerstr+=line
        elif i==1:
            nrows=int(line.strip().split()[-1])
            headerstr += line
        elif i==2:
            xllcorner=float(line.strip().split()[-1])
            headerstr += line
        elif i==3:
            yllcorner=float(line.strip().split()[-1])
            headerstr += line
        elif i==4:
            cellsize=float(line.strip().split()[-1])
            headerstr += line
        elif i==5:
            NODATA_value=float(line.strip().split()[-1])
            arr=np.zeros((nrows, ncols), dtype=int)
            arr[:,:]=NODATA_value
            headerstr += line.replace("\n","")
        elif i>5 and i<nrows:
            col=0
            while col<ncols:
                for item in line.strip().split():
                    arr[row,col]=float(item)
                    col+=1
            row+=1
        i+=1
    infile.close()
    return arr, ncols, nrows, xllcorner, yllcorner, cellsize, NODATA_value, headerstr
def convert_tif_to_array(intifraster):
    inras = gdal.Open(intifraster)
    inband = inras.GetRasterBand(1)
    outarr = inband.ReadAsArray()
    return outarr

#inputfiles
myworkspace = "D:/CCWBE"
tempdir="D:/temp/tempFGB.gdb"
arcpy.env.workspace = tempdir
kantonPG="D:/CCWBE/GIS/kantonbernplus.shp"
demraster=arcpy.Raster(myworkspace+"/GIS/"+"bedem10m.tif")
sloperaster=arcpy.Raster(myworkspace+"/GIS/"+"beslopeprz10m.tif")
flowaccraster=arcpy.Raster(myworkspace+"/GIS/"+"beflowacc10mfill.tif")
felsraster=arcpy.Raster(myworkspace+"/GIS/"+"befels.tif")
maskraster=arcpy.Raster(myworkspace+"/GIS/"+"bemask.tif")
demarr=arcpy.RasterToNumPyArray(demraster)
slopearr=arcpy.RasterToNumPyArray(sloperaster)
flaccarr=arcpy.RasterToNumPyArray(flowaccraster)
maskarr=arcpy.RasterToNumPyArray(maskraster)
felsarr=arcpy.RasterToNumPyArray(felsraster)
demasc, ncols, nrows, xllcorner, yllcorner, cellsize, NODATA_value, headerstr=gridasciitonumpyarrayfloat(myworkspace+"/GIS/"+"bedem10m.asc")

refraster=demraster
arcpy.env.cellSize = refraster
arcpy.env.extent = refraster
arcpy.env.snapRaster = refraster
arcpy.env.Mask = refraster
arcpy.env.overwriteOutput = True
#cellsize=refraster.meanCellWidth
cellsize=10.0
lowerLeft = arcpy.Point(refraster.extent.XMin,refraster.extent.YMin)


#Gelaendedivergenz
srn=2 #min radius in cells
srx=20 #max radius in pixels
inc = 1 #increment
rad = srn
cnt=0

while rad<=srx:
    print rad
    outfocalstat=arcpy.sa.FocalStatistics(demraster, arcpy.sa.NbrCircle(rad,"CELL"),"MEAN", "DATA")
    outfocalstat.save(tempdir + "/" + "outfocalstat"+str(rad))
    exp=demraster-outfocalstat
    exp.save(tempdir+"/"+"exp"+str(rad))
    outzonstatmean=arcpy.sa.ZonalStatistics(kantonPG,"FID",exp, "MEAN","DATA")
    outzonstatmean.save(tempdir+"/"+"outzonstatmean")
    outzonstatstd = arcpy.sa.ZonalStatistics(kantonPG, "FID", exp, "STD", "DATA")
    outzonstatstd.save(tempdir + "/" + "outzonstatstd")
    expnrm=100.0*((exp-outzonstatmean)/outzonstatstd)
    expnrm.save(tempdir + "/" + "expnrm" + str(rad))
    rad=rad+inc
    cnt=cnt+1

if rad>srx:
    rad=srx
srd=rad-inc
ctl=cnt-1
cth=cnt+1

#maxgelaendedivergenz=expnrm
tmpcnt=arcpy.Raster(tempdir + "/" + "expnrm" + str(rad))

while srd>=srn:
    print rad
    expnrm= arcpy.Raster(tempdir + "/" + "expnrm" + str(srd))
    outabs=arcpy.sa.Abs(expnrm)
    outabs.save(tempdir + "/" + "outabs")
    tmpctl=arcpy.sa.Con(outabs,expnrm,tmpcnt, '"VALUE">120')
    tmpctl.save(tempdir + "/begeldiv" + str(rad))
    rad=rad-inc
    srd=srd-inc
    tmpcnt =arcpy.Raster(tempdir + "/" + "expnrm" + str(rad))
    cth=cnt
    cnt=cnt-1
    ctl=ctl-1
#out
out1=tmpcnt
out2=arcpy.sa.FocalStatistics(tmpcnt, arcpy.sa.NbrCircle(2,"CELL"),"MEAN", "DATA")
out2.save(tempdir + "/tmpout2")


#reclassify
reclarr=arcpy.RasterToNumPyArray(out2)
#reclarr=arcpy.RasterToNumPyArray(arcpy.Raster(tempdir + "/tmpout2"))
gelarr=reclarr.copy()
i=0
j=0
rows=np.shape(reclarr)[0]
cols=np.shape(reclarr)[1]
np.shape(reclarr)==np.shape(gelarr)
while i<rows:
    j=0
    while j<cols:
        if reclarr[i,j]<-200:
            gelarr[i, j]=1 #Ebene
        elif reclarr[i,j]>=-200 and reclarr[i,j]<-100:
            gelarr[i, j]=2 #Hangfuss/Mulde
        elif reclarr[i,j]>=-100 and reclarr[i,j]<=200:
            gelarr[i, j]=3 #Hang
        elif reclarr[i, j] > 200:
            gelarr[i, j] = 4  # Kuppe
        else:
            gelarr[i, j] = 0
        n=0
        if i>=1 and i <= rows-1 and j >=1 and j <= cols-1:
            if reclarr[i-1, j-1]==4:
                n+=1
            if reclarr[i-1, j]==4:
                n+=1
            if reclarr[i-1, j+1]==4:
                n+=1
            if reclarr[i, j-1]==4:
                n+=1
            if reclarr[i, j+1]==4:
                n+=1
            if reclarr[i+1, j-1]==4:
                n+=1
            if reclarr[i+1, j]==4:
                n+=1
            if reclarr[i+1, j+1]==4:
                n+=1
            if n>=5:
                gelarr[i, j] = 4
        j+=1
    i+=1
#plt.imshow(gelarr)
#reconvert array to raster
#outrecl = arcpy.NumPyArrayToRaster(gelarr, lowerLeft, cellsize)
#outrecl.save(myworkspace+"/GIS/"+"/ligeldivrecl.tif")#+ str(rad))
#Verfeinerung Gelaendedivergenz
#gelarr=reclarr.copy()#arcpy.RasterToNumPyArray(outrecl)
#outarr=gelarr.copy()
rows=np.shape(gelarr)[0]
cols=np.shape(gelarr)[1]
outarr=np.zeros((rows,cols),dtype=int)
#outarr[0, :] = NODATA_value
#outarr[-1, :] = NODATA_value
#outarr[:, 0] = NODATA_value
#outarr[:, -1] = NODATA_value
np.shape(gelarr)
np.shape(demarr)
np.shape(slopearr)
np.shape(flaccarr)
#plt.imshow(demarr)
#plt.imshow(flaccarr)

i=1
j=1
while i < rows-1:
    print(i)
    j=1
    while j < cols-1:
        if gelarr[i,j] in [1,2,3,4]:
            outarr[i,j]=gelarr[i,j]
        #Kuppe bereinigen 0
        #if (flaccarr[i,j]*cellsize*cellsize)<100:
        #    outarr[i,j]=4
        # Kuppen bereinigen 1
        z=demarr[i,j]
        n=0
        if demarr[i-1,j-1]<z:
            n+=1
        if demarr[i-1,j]<z:
            n+=1
        if demarr[i-1, j + 1] < z:
            n += 1
        if demarr[i,j+1]<z:
            n+=1
        if demarr[i+1,j+1]<z:
            n+=1
        if demarr[i+1,j]<z:
            n+=1
        if demarr[i+1,j-1]<z:
            n+=1
        if demarr[i,j-1]<z:
            n+=1
        if n>=6 and gelarr[i, j] == 4:
            outarr[i-1,j-1]=4
            outarr[i-1, j] = 4
            outarr[i-1, j+1] = 4
            outarr[i, j+1] = 4
            outarr[i+1, j+1] = 4
            outarr[i+1, j] = 4
            outarr[i+1, j-1] = 4
            outarr[i, j-1] = 4
        # Kuppen bereinigen 2
        anzkuppen = 0
        sumneig=0.0
        if gelarr[i-1,j-1]==4:
            anzkuppen+=1
        if gelarr[i-1,j]==4:
            anzkuppen+=1
        if gelarr[i-1, j + 1]==4:
            anzkuppen += 1
        if gelarr[i,j+1]==4:
            anzkuppen+=1
        if gelarr[i+1,j+1]==4:
            anzkuppen+=1
        if gelarr[i+1,j]==4:
            anzkuppen+=1
        if gelarr[i+1,j-1]==4:
            anzkuppen+=1
        if gelarr[i,j-1]==4:
            anzkuppen+=1
        sumneig = slopearr[i-1,j-1]+slopearr[i-1,j]+slopearr[i-1, j+1]+slopearr[i,j+1]+slopearr[i+1,j+1]+slopearr[i+1,j]+slopearr[i+1,j-1]+slopearr[i,j-1]
        if anzkuppen>0 and sumneig>=100:
            outarr[i,j]=4

        # Ebene bereinigen 1
        if slopearr[i,j]<10:
            outarr[i,j]=1
        # Ebene bereinigen 2
        neigungsmittelwert = (slopearr[i,j]+slopearr[i-1,j-1]+slopearr[i-1,j]+slopearr[i-1, j+1]+slopearr[i,j+1]+slopearr[i+1,j+1]+slopearr[i+1,j]+slopearr[i+1,j-1]+slopearr[i,j-1])/9.0
        if gelarr[i,j]==4 and neigungsmittelwert <20:
            outarr[i, j]=1
        #Mulden bereinigen
        if (flaccarr[i,j]*cellsize*cellsize)>=50000.0 and slopearr[i,j]>10 and slopearr[i,j]<30:
            outarr[i,j]=2
        if outarr[i,j] >4:
            outarr[i,j]=0
        if outarr[i,j] <0:
            outarr[i,j]=0
        #Mask raster
        if maskarr[i,j] !=1:
            outarr[i,j]=0
        if outarr[i,j] ==0:
            outarr[i,j]=1
        j += 1
    i += 1

#1 Ebene
#2 Hangfuss/Mulde
#3 Hang
#4 Kuppe
i=1
j=1
while i < rows-1:
    print(i)
    j=1
    while j < cols-1:
        # loesche Ebenen in der Nachbarschaft von  Fels
        n = 0
        if outarr[i - 1, j - 1] == 1:
            n += 1
        if outarr[i - 1, j] == 1:
            n += 1
        if outarr[i - 1, j + 1] == 1:
            n += 1
        if outarr[i, j + 1] == 1:
            n += 1
        if outarr[i + 1, j + 1] == 1:
            n += 1
        if outarr[i + 1, j] == 1:
            n += 1
        if outarr[i + 1, j - 1] == 1:
            n += 1
        if outarr[i, j - 1] == 1:
            n += 1
        if outarr == 3 and n > 0:
            outarr = 2

        # loesche Mulden in Fels
        if felsarr[i,j]==1 and outarr[i,j]==2:
            outarr[i,j]=3
        # loesche Ebenen in Fels
        if felsarr[i, j] == 1 and outarr[i, j] == 1:
            outarr[i, j] = 3
        #Ausscheidung von Hangfusslagen am Rand von Ebenen
        n = 0
        if outarr[i - 1, j - 1]==1:
            n += 1
        if outarr[i - 1, j]==1:
            n += 1
        if outarr[i - 1, j + 1]==1:
            n += 1
        if outarr[i, j + 1]==1:
            n += 1
        if outarr[i + 1, j + 1]==1:
            n += 1
        if outarr[i + 1, j]==1:
            n += 1
        if outarr[i + 1, j - 1]==1:
            n += 1
        if outarr[i, j - 1]==1:
            n += 1
        if outarr==3 and n>0:
            outarr=2
        j += 1
    i += 1


plt.imshow(outarr)
#reconvert array to raster
np.savetxt(myworkspace+"/GIS/"+"begeldivcorrected2.asc", outarr, delimiter=' ',newline='\n', header=headerstr, comments='')
outraster = arcpy.NumPyArrayToRaster(outarr, lowerLeft, cellsize)
#outraster.save(myworkspace+"/GIS/"+"begeldivc2")
outraster.save(myworkspace+"/GIS/"+"begeldivcorrected2.tif")


print "done .."


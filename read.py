import time as currenttime
start_time = currenttime.time()
import Nio
import Ngl
import numpy,sys,os, math

cdf_file = Nio.open_file("data/test.nc","r")
#print(cdf_file.dimensions)
#print(cdf_file.attributes.keys())
#print(cdf_file.rank)
#print(cdf_file.variables)
#print(cdf_file)
#print(Ngl.pynglpath('rangs'))

#Assign variables
lat  = cdf_file.variables["latitude"]  # Latitude
lon  = cdf_file.variables["longitude"]  # Longitude
Z    = cdf_file.variables["z"]    # Geopotential height
fcrs = cdf_file.variables["FCRS"] # Fine dust particles
ccrs = cdf_file.variables["CCRS"] # Coarse dust particles
time = cdf_file.variables["time"]
X = cdf_file.variables["X"]
Y = cdf_file.variables["Y"]

#############Code refactoring

def plotter(targetVariable, outputType, outputName, time, layer, plotTitle, palette):
    #pyNgl setup
    wkres = Ngl.Resources()
    wkres.wkWidth = wkres.wkHeight = 5000
    wks = Ngl.open_wks(outputType, f"./outputs/{outputName}",wkres)
    resources = Ngl.Resources()
    #Plot settings

    maxVariable = int(math.ceil(numpy.amax(targetVariable[:,layer,:,:]) / 100.0)) * 100
    if palette:
        resources.cnFillPalette = palette 
    resources.cnFillOn = True
    resources.cnLinesOn = False
    resources.cnLineLabelsOn = False # Hide in-plot labels
    resources.cnLevelSelectionMode = "ManualLevels"
    resources.cnRasterModeOn = True
    resources.cnMinLevelValF = 100
    resources.cnMaxLevelValF = maxVariable
    resources.cnLevelSpacingF = int(maxVariable/8)
    resources.tiMainString = plotTitle
    #Projection settings
    resources.mpProjection = "LambertConformal"
    resources.mpLambertParallel1F = cdf_file.attributes['P_ALP'] #45
    resources.mpLambertParallel2F = cdf_file.attributes['P_BET'] #22
    resources.mpLambertMeridianF = cdf_file.attributes['P_GAM'] #20
    #resources.mpDataBaseVersion    = "HighRes"
    resources.mpDataBaseVersion = "MediumRes"
    #Set view window boundaries
    resources.mpLimitMode = "Corners"
    resources.mpLeftCornerLatF = lat[0,0]
    resources.mpLeftCornerLonF = lon[0,0]
    resources.mpRightCornerLatF = lat[-1,-1]
    resources.mpRightCornerLonF = lon[-1,-1]
    resources.tfDoNDCOverlay = True
    resources.tmXTOn = False
    resources.tmXBOn = False
    resources.tmYROn = False
    resources.tmYLOn = False
    Ngl.contour_map(wks,targetVariable[time,layer,:,:],resources)
    Ngl.destroy(wks)

layer = 10
time = 0
palette = 'test'

while time < 1:
    name = f"time {time}"
    plotTitle = f"Layer: {layer} / Time: {time}h"
    plotter(ccrs, 'png', name, time, layer, plotTitle,palette)
    time +=1

cdf_file.close()
print(f"--- {float(currenttime.time() - start_time):.4f} seconds ---")
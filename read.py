import Nio
import Ngl
import numpy,sys,os

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

def plotter(targetVariable, outputType, outputName, time, layer, plotTitle):
    #pyNgl setup
    wks = Ngl.open_wks(outputType,outputName)
    resources = Ngl.Resources()
    #Plot settings
    resources.mpFillOn              = True         # Turn on map fill.
    resources.mpFillAreaSpecifiers  = ["Water","Land","AllNational"]
    resources.mpSpecifiedFillColors = [17,18,17]
    resources.mpAreaMaskingOn       = True            # Indicate we want to
    resources.mpMaskAreaSpecifiers  = "Africa"  # mask land.
    resources.mpPerimOn             = True            # Turn on a perimeter.
    #resources.mpGridMaskMode        = "MaskLand"      # Mask grid over land.
    resources.cnFillDrawOrder       = "PreDraw"       # Draw contours first.

    ic = Ngl.new_color(wks,0.75,0.75,0.75) #set colormap
    resources.cnFillOn = True
    resources.cnLinesOn = False
    resources.cnLineLabelsOn = False # Hide in-plot labels
    resources.cnRasterModeOn = True
    resources.tiMainString = plotTitle
    #Projection settings
    resources.mpProjection = "LambertConformal"
    resources.mpLambertParallel1F = 45
    resources.mpLambertParallel2F = 22
    resources.mpLambertMeridianF = 20
    resources.mpDataBaseVersion    = "HighRes"
    #View window boundaries
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

plotter(ccrs, 'x11', 'def test', 0, 0, 'title')
cdf_file.close()
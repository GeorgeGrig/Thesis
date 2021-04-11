import Nio
import Ngl
import numpy,sys,os

#print(Nio.__version__)

#print(Ngl.__version__)

cdf_file = Nio.open_file("data/test.nc","r")
#print(cdf_file.dimensions)
#print(cdf_file.attributes.keys())
#print(cdf_file.rank)
#print(cdf_file.variables)
#print(cdf_file)


#Assign variables
lat  = cdf_file.variables["latitude"]  # Latitude
lon  = cdf_file.variables["longitude"]  # Longitude
Z    = cdf_file.variables["z"]    # Geopotential height
fcrs = cdf_file.variables["FCRS"] # Fine dust particles
ccrs = cdf_file.variables["CCRS"] # Coarse dust particles
time = cdf_file.variables["time"]
X = cdf_file.variables["X"]
Y = cdf_file.variables["Y"]
#
#  Open a workstation and specify a different color map.
#
wks_type = "x11"
wks = Ngl.open_wks(wks_type,"ngl05p")


# #----------- Begin first plot -----------------------------------------
# resources = Ngl.Resources()
# ic = Ngl.new_color(wks,0.75,0.75,0.75)   # Add gray to the color map
# resources.mpProjection = "LambertConformal" # Change the map projection.
# resources.mpLambertMeridianF = 180 # Define center meridian
# resources.mpFillOn     = True           # Turn on map fill.
# resources.mpFillColors = ["white","transparent","gray","transparent"]

# resources.vpXF      = 0.1    # Change the size and location of the
# resources.vpYF      = 0.9    # plot on the viewport.
# resources.vpWidthF  = 0.7
# resources.vpHeightF = 0.7


# mnlvl = 0                        # Minimum contour level.
# mxlvl = 28                       # Maximum contour level.
# spcng = 2                        # Contour level spacing.
# ncn   = (mxlvl-mnlvl)//spcng + 1  # Number of contour levels.

# resources.cnLevelSelectionMode = "ManualLevels" # Define your own
# resources.cnMinLevelValF       = mnlvl          # contour levels.
# resources.cnMaxLevelValF       = mxlvl
# resources.cnLevelSpacingF      = spcng

# resources.cnLineThicknessF     = 2.0   # Double the line thickness.

# resources.cnFillOn           = True  # Turn on contour level fill.
# resources.cnMonoFillColor    = True  # Use one fill color.
# resources.cnMonoFillPattern  = False # Use multiple fill patterns.
# FillPatterns = numpy.zeros([ncn+1],'i')-1
# FillPatterns[ncn-1:ncn+1] =  17
# resources.cnFillPatterns     = FillPatterns
# resources.cnLineDrawOrder      = "Predraw" # Draw lines and filled
# resources.cnFillDrawOrder      = "Predraw" # areas before map gets drawn.

# resources.tiMainString = 'Test'

# resources.sfXCStartV = float(min(lon))   # Define where contour plot
# resources.sfXCEndV   = float(max(lon))   # should lie on the map plot.
# resources.sfYCStartV = float(min(lat))
# resources.sfYCEndV   = float(max(lat))

# resources.pmLabelBarDisplayMode = "Never"  # Turn off the label bar.

# map = Ngl.contour_map(wks,fcrs[0,:,:],resources) # Draw contours over a map.


# Test numero 2 (Kinda works, it kinda prints something)
resources = Ngl.Resources()
lon_length = len(lon)
ic = Ngl.new_color(wks,0.75,0.75,0.75)
resources.cnFillOn = True
resources.cnLinesOn = False
#resources.gsnSpreadColors = True
resources.lbLabelAutoStride = True # every other label
resources.cnLevelSelectionMode = "ManualLevels"
resources.cnMinLevelValF = 100
resources.cnMaxLevelValF = 3500
resources.cnLevelSpacingF = 100
resources.cnRasterModeOn = True
resources.tiMainString = "PLEASE WORK PLEASE WORK"
resources.mpProjection = "LambertConformal"
resources.mpLambertParallel1F = 20
resources.mpLambertParallel2F = 38.70000076293945
resources.mpLambertMeridianF = 20
resources.mpLimitMode = "Corners"
resources.mpLeftCornerLatF = lat[0:0]
resources.mpLeftCornerLonF = lon[0:0]
resources.mpRightCornerLatF = lat[0:0]
resources.mpRightCornerLonF = lon[0:0]
resources.mpRightCornerLatF = lat[lon_length-1,lon_length-1]
resources.mpRightCornerLonF = lon[lon_length-1,lon_length-1]
resources.tfDoNDCOverlay = True
resources.pmTickMarkDisplayMode = "Always"
resources.tmXTOn = False
resources.tmXBOn = False
resources.tmYROn = False
resources.tmYLOn = False
Ngl.contour_map(wks,fcrs[0,0,:],resources)
cdf_file.close()
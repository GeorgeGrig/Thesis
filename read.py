import time as currenttime
start_time = currenttime.time()
import Nio
import Ngl
import numpy,sys,os, math


#############Code refactoring

def plotter(targetVariable, outputType, outputName, time, layer, plotTitle, palette, levels, file_name, key, z_dim):
    #pyNgl setup
    wkres = Ngl.Resources()
    wkres.wkWidth = wkres.wkHeight = 1000
    path = f"./outputs/{file_name[6]}{file_name[7]}/{key}"
    os.makedirs(path, exist_ok=True) 
    wks = Ngl.open_wks(outputType, f'{path}/{outputName}',wkres)
    resources = Ngl.Resources()
    #Plot settings

    #maxVariable = int(math.ceil(numpy.amax(targetVariable[:,layer,:,:]) / 100.0)) * 100
    if palette:
        resources.cnFillPalette = palette 
    resources.cnFillOn = True
    resources.cnLinesOn = False
    resources.cnLineLabelsOn = False # Hide in-plot labels
    resources.cnLevelSelectionMode = "ExplicitLevels"
    resources.cnLevels = levels
    resources.cnGridBoundFillColor = "black"
    resources.cnRasterModeOn = True
    #resources.cnMinLevelValF = 100
    #resources.cnMaxLevelValF = maxVariable
    #resources.cnLevelSpacingF = int(maxVariable/7)
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
    if layer == 'SUM':
        i = 1
        targetVariable_ = targetVariable[time,0,:,:]
        while i < z_dim:
            targetVariable_ += targetVariable[time,i,:,:]
            i += 1
    elif type(layer) is int:
        targetVariable_ = targetVariable[time,layer,:,:]
    else:
        i = 1
        targetVariable_ = targetVariable[time,layer[0],:,:]
        while i < len(layer):
            targetVariable_ += targetVariable[time,layer[i],:,:]
            i += 1
    Ngl.contour_map(wks,targetVariable_,resources)
    Ngl.destroy(wks)

# SCRIPT SETTINGS ###########################################
file_names = ['20200514grd01.nc','20200515grd01.nc','20200516grd01.nc']
layers = [[0,1,4,5],0,'SUM']
starting_time = 0
max_time = 10
palette = 'test'
levels = [10,20,40,80,160,320,640,1280]
# SCRIPT SETTINGS ###########################################

for file_name in file_names:
    cdf_file = Nio.open_file(f"data/{file_name}","r")
    #print(cdf_file.dimensions)
    #print(cdf_file.attributes.keys())
    #print(cdf_file.rank)
    #print(cdf_file.variables)
    #print(cdf_file)
    #print(Ngl.pynglpath('rangs'))

    #Assign variables
    lat  = cdf_file.variables["latitude"]  # Latitude
    lon  = cdf_file.variables["longitude"]  # Longitude
    # Z    = cdf_file.variables["z"]    # Geopotential height
    z_dim = cdf_file.dimensions['LAY']
    fcrs = cdf_file.variables["FCRS"] # Fine dust particles
    ccrs = cdf_file.variables["CCRS"] # Coarse dust particles
    #time = cdf_file.variables["time"]
    X = cdf_file.variables["X"]
    Y = cdf_file.variables["Y"]
    particles = {   'fcrs':fcrs,
                    'ccrs':ccrs}
    keys = particles.keys()
    for key in keys:
        for layer in layers:
            time = starting_time
            while time < max_time:
                print(f'Now doing time {time}h - layer {layer} - particle {key} and filename {file_name}')
                name = f"time {time}h - layer {layer} - particle {key} - day {file_name[6]}{file_name[7]}"
                plotTitle = f"Layer: {layer} / Time: {time}h / {key}"
                
                plotter(particles[key], 'png', name, time, layer, plotTitle,palette, levels, file_name, key, z_dim)
                time +=1

    cdf_file.close()
    print(f"--- {float(currenttime.time() - start_time):.4f} seconds ---")
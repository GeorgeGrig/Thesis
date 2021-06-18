import time as currenttime
start_time = currenttime.time()
import Nio
import Ngl
import numpy,sys,os, math, glob, re
from PIL import Image
import imageio
maxVariable = 0
step = 0
def animator(path, layer):
    # Create the frames
    images = []
    #Get all images in specified order
    imgs = glob.glob(f"{path}/*.png")
    #Sort by date created
    imgs.sort(key=os.path.getmtime)
    for i in imgs:
        #Check if image matches specified layer
        check = i.split(' - layer ')[1]
        check = check.split(' -')[0]
        if check == str(layer):
            new_frame = Image.open(i)
            images.append(new_frame)
    # Save into a GIF file that loops forever
    print(f"Generating GIF for layer: {layer}")
    imageio.mimsave(f"{path}/{layer} animation.gif", images, duration=0.2)

def cropper(name):
    im = Image.open(name)
    # Setting the points for cropped image
    left = 0
    top = 230
    right = left + 1000
    bottom = top + 547
    im1 = im.crop((left, top, right, bottom))
    im1.save(name)

def plotter(targetVariable, outputType, outputName, time, layer, plotTitle, palette, alt_palette, levels, path, resolution, Z):
    global maxVariable, step
    #pyNgl setup
    wkres = Ngl.Resources()
    wkres.wkWidth = wkres.wkHeight = 1000
    #Make required folders if the don't exist
    os.makedirs(path, exist_ok=True) 
    full_path = f'{path}/{outputName}'
    wks = Ngl.open_wks(outputType,full_path ,wkres)
    resources = Ngl.Resources()
    #Global pyngl settings
    resources.cnFillPalette = palette 
    resources.cnFillOn = True
    resources.cnLinesOn = False
    resources.cnLineLabelsOn = False # Hide in-plot labels
    resources.cnLevelSelectionMode = "ExplicitLevels"
    resources.cnGridBoundFillColor = "black"
    resources.cnRasterModeOn = True
    resources.tiMainString = plotTitle
    #Smoothing
    resources.cnRasterSmoothingOn = True
    # resources.cnSmoothingOn = True
    # resources.cnSmoothingDistanceF = 1
    #Projection settings
    resources.mpProjection = "LambertConformal"
    resources.mpLambertParallel1F = cdf_file.attributes['P_ALP'] #45
    resources.mpLambertParallel2F = cdf_file.attributes['P_BET'] #22
    resources.mpLambertMeridianF = cdf_file.attributes['P_GAM'] #20
    resources.mpDataBaseVersion    = resolution
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
    # If combination plot is required
    if isinstance(targetVariable, list):
        print('Variable Combination...')
        i = 0
        targetVariable_ = targetVariable[0][:,:,:,:]
        while i < len(targetVariable):
            targetVariable_ += targetVariable[i][:,:,:,:]
            i += 1
        targetVariable = targetVariable_
    # If layer sum plot is required make neccesary changes (change palette, add layer concetrations, specify new levels)
    
    if layer == 'SUM':
        print(f"Generating sum of all available layers...")
        i = 1 
        resources.cnFillPalette = alt_palette
        #print(len(targetVariable[:,0,:,:]))
        targetVariable_ = targetVariable[time,0,:,:]*Z[time,0,:,:]
        #print(len(targetVariable_))
        while i < z_dim:
            targetVariable_ += targetVariable[time,i,:,:]*(Z[time,i,:,:] - Z[time,i-1,:,:])
            #print(Z[time,i,0,0] - Z[time,i-1,0,0])
            #Find max variable for max layer
            _maxVariable = int(math.ceil(numpy.amax(targetVariable_[:,:]) / 100.0)) * 100
            if _maxVariable > maxVariable and time == 0:
                maxVariable = _maxVariable
                step = int(maxVariable/(7*100))*100
                #print(maxVariable)
            # resources.cnLevelSelectionMode = "ManualLevels"
            # resources.cnLevelSpacingF = step
            # resources.cnMinLevelValF = 10000
            # resources.cnMaxLevelValF = maxVariable
            i += 1
            levels = list(range(10000,int(maxVariable),step))#maybe comment this out if layers appear off 
            #print(levels)
    # If layer is a simple integer
    elif type(layer) is int:
        targetVariable_ = targetVariable[time,layer,:,:]
    # If layer is a list of integers combine said layers
    else:
        print(f"Generating sum of selected layers...")
        i = 1
        targetVariable_ = targetVariable[time,layer[0],:,:]*Z[time,layer[0],:,:]
        while i < len(layer):
            targetVariable_ += targetVariable[time,layer[i],:,:]*(Z[time,layer[i],:,:] - Z[time,layer[i-1],:,:])
            i += 1
            _maxVariable = int(math.ceil(numpy.amax(targetVariable_[:,:]) / 100.0)) * 100
            if time == 0:
                maxVariable = 0
            if _maxVariable > maxVariable and time == 0:
                maxVariable = _maxVariable
        # resources.cnLevelSelectionMode = "ManualLevels"
        # resource.cnLevelSpacingF = 7
        levels = list(range(10000,int(maxVariable),int(maxVariable/(7*100))*100))#maybe comment this out if layers appear off 
    resources.cnLevels = levels
    Ngl.contour_map(wks,targetVariable_,resources)
    #cropper(f'{full_path}.{outputType}')
    Ngl.destroy(wks)

# SCRIPT SETTINGS ###########################################
file_names = ['20200514grd01.nc','20200515grd01.nc','20200516grd01.nc']#]#'20200515grd03.nc',
layers = ['SUM',[0,1,4,5],0] # Use integer/'SUM'/list_of_integers
starting_time = 0
max_time = 23
palette = 'test'
alt_palette = 'precip4_11lev'
levels = [20,40,80,160,320,640,1280,2560]
animate = True
resolution = "MediumRes" # "MediumRes" Don't use HighRes for Domain 1, no difference, more compute time
# SCRIPT SETTINGS ###########################################

# For each file (day) repeat
for file_name in file_names:
    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Now doing file: {file_name}")
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
    Z    = cdf_file.variables["z"]    # Geopotential height
    z_dim = cdf_file.dimensions['LAY']
    fcrs = cdf_file.variables["FCRS"] # Fine dust particles
    ccrs = cdf_file.variables["CCRS"] # Coarse dust particles
    #time = cdf_file.variables["time"]
    X = cdf_file.variables["X"] 
    Y = cdf_file.variables["Y"]
    particles = {   'fcrs':fcrs,
                    'ccrs':ccrs,
                    'comb':[fcrs,ccrs],
                    }
    keys = particles.keys()
    #print(Z[:,3,:,:])
    # Recursively make plots for choosen variables/layers/time
    for key in keys:
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Now doing variable: {key}")
        for layer in layers:
            time = starting_time
            path = f"./outputs/{file_name[6]}{file_name[7]}/{key}"
            while time <= max_time:
                print(f'Now doing time {time}h - layer {layer} - particle {key} and filename {file_name}')
                name = f"{time}h - layer {layer} - particle {key} - day {file_name[6]}{file_name[7]}"
                plotTitle = f"Layer: {layer} / Time: {time}h / {key}"
                plotter(particles[key], 'png', name, time, layer, plotTitle,palette,alt_palette, levels, path, resolution, Z)
                time +=1
            if animate:
                animator(path,layer)
    cdf_file.close()

print(f"--- Total run time : {float((currenttime.time() - start_time)/60):.4f} minutes ---")
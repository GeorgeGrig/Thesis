import time as currenttime
start_time = currenttime.time()
import Nio
import Ngl
import numpy,sys,os, math, glob, re
from PIL import Image
import imageio
maxVariable = 0
step = 0

#Grabs all available image files, sorts them and picks only the specified
def sorter(path, layer):
    #Get all images in specified order
    imgs = glob.glob(f"{path}/*.png")
    #Sort by date created
    imgs.sort(key=os.path.getmtime)
    images = []
    for image in imgs:
        if '~ layer' in image:
            check = image.split(' ~ layer ')[1]
            check = check.split(' ~')[0]
            if check == str(layer):
                images.append(image)
    return images

#Creates gif animation
def animator(path, layer):
    # Create the frames
    images = []
    imgs = sorter(path, layer)
    for i in imgs:
        new_frame = Image.open(i)
        images.append(new_frame)
    # Save into a GIF file that loops forever
    print(f"Generating GIF for layer: {layer}")
    os.makedirs(f"{path}/{layer}", exist_ok=True)
    imageio.mimsave(f"{path}/{layer}/{layer} animation.gif", images, duration=0.2)

#Crops the image
def cropper(name):
    im = Image.open(name)
    # Setting the points for cropped image
    left = 0
    top = 230
    right = left + 1000
    bottom = top + 547
    im1 = im.crop((left, top, right, bottom))
    im1.save(name)

#Creates collages for the images
def collager(path, layer, total, step):
    imgs = sorter(path, layer)
    k = 0
    t = -1
    m = 0
    #Split available hours in parts
    if step == 1:
        while m < len(imgs)/total:
            #Create new collage image
            collage = Image.new("RGBA", (1998,1650), color=(255,255,255,255))
            for i in range(0,1998,999):
                for j in range(0,1650,550):
                    #Paste each image to the correct location of the grid
                    image = Image.open(imgs[k]).convert("RGBA")
                    collage.paste(image, (i,j))
                    #Check if grid is filled
                    if k == (total+t):
                        os.makedirs(f"{path}/{layer}", exist_ok=True)
                        collage.save(f"{path}/{layer}/{layer} part {m+1} collage.png")
                        t = k
                        print(f"Saved collage part {m+1}")
                    k += 1
            m += 1
    elif isinstance(step, list):
        #Create new collage image
        collage = Image.new("RGBA", (1998,1650), color=(255,255,255,255))
        for i in range(0,1998,999):
            for j in range(0,1650,550):
                #Paste each image to the correct location of the grid
                image = Image.open(imgs[step[k]]).convert("RGBA")
                collage.paste(image, (i,j))
                #Check if grid is filled
                if step[k] == step[-1]:
                    os.makedirs(f"{path}/{layer}", exist_ok=True)
                    collage.save(f"{path}/{layer}/{layer} collage (short version).png")
                    t = k
                    print(f"Saved collage (short version)")
                k += 1   

def plotter(targetVariable, outputType, outputName, time, layer, plotTitle, palette, alt_palette, levels, path, resolution, Z, alt_levels):
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
    resources.pmTickMarkDisplayMode = 'Always' 
    #Smoothing
    resources.cnRasterSmoothingOn = True
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
    resources.tmXBOn = True
    resources.tmYROn = False
    resources.tmYLOn = True
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
        targetVariable_ = targetVariable[time,0,:,:]*Z[time,0,:,:]*0.001
        while i < z_dim:  
            targetVariable_ += targetVariable[time,i,:,:]*(Z[time,i,:,:] - Z[time,i-1,:,:])*0.001
            i += 1
        levels = alt_levels
    # If layer is a simple integer
    elif type(layer) is int:
        targetVariable_ = targetVariable[time,layer,:,:]
    # If layer is a list of integers combine said layers
    elif layer == 'Daily':
        print(f"Generating daily mean...")
        i = 1 
        targetVariable_ = targetVariable[0,0,:,:]
        while i < 24:
            targetVariable_ += targetVariable[i,0,:,:]/24
            i += 1 
    else:
        print(f"Generating sum of selected layers...")
        i = 1
        resources.cnFillPalette = alt_palette
        targetVariable_ = targetVariable[time,layer[0],:,:]*0.001*Z[time,layer[0],:,:]*0.001
        while i < len(layer):
            targetVariable_ += targetVariable[time,layer[i],:,:]*(Z[time,layer[i],:,:] - Z[time,layer[i-1],:,:])*0.001
            i += 1
        levels = alt_levels
    resources.cnLevels = levels
    Ngl.contour_map(wks,targetVariable_,resources)
    cropper(f'{full_path}.{outputType}')
    Ngl.destroy(wks)

# SCRIPT SETTINGS ###########################################
file_names = ['20200514grd01.nc','20200515grd01.nc','20200516grd01.nc']#]#'20200515grd03.nc',
layers = ['SUM',[0,1,2,3,4,5,6,7,8,9,10,11,12,13],[14,15,16,17],'Daily',0] # Use integer/'SUM'/list_of_integers
starting_time = 0
max_time = 23
palette = 'test'
alt_palette = 'MPL_YlOrBr'
levels = [20,40,80,160,320,640,1280,2560]
alt_levels_comb = [850,1700,2500,3300,4200,5100]
alt_levels_fine = [20,180,340,500,700,850,1100]
alt_levels_coarse = [10,300,600,900,1200,1500,1800,2200]
animate = True
collage = True
collage_short = True
resolution = "MediumRes" # "MediumRes" Don't use HighRes for Domain 1, no difference, more compute time and weird artifacts
# SCRIPT SETTINGS ###########################################

# For each file (day) repeat
for file_name in file_names:
    maxVariable = step = 0
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
                    'comb':[fcrs,ccrs]
                    }
    keys = particles.keys()
    # Recursively make plots for choosen variables/layers/time
    date = f'{file_name[6]}{file_name[7]} May {file_name[0]}{file_name[1]}{file_name[2]}{file_name[3]}'
    for key in keys:
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Now doing variable: {key}")
        for layer in layers:
            time = starting_time
            if layer == 'Daily':
                time = max_time
            path = f"./outputs/{file_name[6]}{file_name[7]}/{key}"
            while time <= max_time:
                layer_name = layer 
                if not isinstance(layer, int):
                    if len(layer) > 6: layer_name = f'[{layer[0]} - {layer[-1]}]' #Make title names sorter to avoid weird artifacts
                print(f'Now doing time {time}h - layer {layer_name} - particle {key} and filename {file_name}')
                name = f"{time}h ~ layer {layer} ~ particle {key} ~ day {file_name[6]}{file_name[7]}"
                if time <= 9:
                    time_name = '0' + str(time)
                else:
                    time_name = time
                if key == 'fcrs':
                    key_name = 'Fine Dust'
                    alt_levels = alt_levels_fine
                if key == 'ccrs':
                    key_name = 'Coarse Dust'
                    alt_levels = alt_levels_coarse
                if key == 'comb':
                    key_name = 'Dust'
                    alt_levels = alt_levels_comb
                if layer == 'SUM':
                    plotTitle = f"{time_name}h {date} - {key_name} Load (mg/m~S~2~N~)"
                elif layer == 0:
                    layer_name = 'Surface Level'
                    plotTitle = f"{layer_name} - {date} ~C~{key_name} (~F33~m~F~g/m~S~3~N~)"
                elif layer == 'Daily':
                    name = f"Surface Daily ~ particle {key} ~ day {file_name[6]}{file_name[7]}"
                    path += '/daily/'
                    plotTitle = f"Surface {date} ~C~{key_name} Daily Load (~F33~m~F~g/m~S~3~N~)"
                else:
                    plotTitle = f"Layers: {layer_name} - {time_name}h {date} ~C~{key_name} Partial Load (mg/m~S~2~N~)"
                plotter(particles[key], 'png', name, time, layer, plotTitle,palette,alt_palette, levels, path, resolution, Z, alt_levels)
                time +=1
            if animate and not layer == 'Daily':
                animator(path,layer)
            if collage and not layer == 'Daily':
                collager(path, layer, 6, 1)      
            if collage_short and not layer == 'Daily':
                collager(path, layer, 6, [0,4,9,13,18,23])                       
    cdf_file.close()

print(f"--- Total run time : {float((currenttime.time() - start_time)/60):.2f} minutes ---")
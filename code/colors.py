import numpy as np
import pandas as pd
import os, cv2, colorsys
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
from collections import Counter
from sklearn.cluster import KMeans
from skimage.color import rgb2lab, deltaE_cie76, rgb2hsv


#############################################
######### HELPER FUNCTIONS 
#############################################

def RGB2HEX(color):
    return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

    """
    Takes tuple and converts to hex value.
    """
    conversion = '#%02x%02x%02x' % color
    return conversion


def RGB2HSV(red=40, green=32, blue=28):
    #rgb normal: range (0-255, 0-255, 0-255)
    
    #get rgb percentage: range (0-1, 0-1, 0-1 )
    red_percentage= red / float(255)
    green_percentage= green/ float(255)
    blue_percentage=blue / float(255)

    #get hsv percentage: range (0-1, 0-1, 0-1)
    color_hsv_percentage=colorsys.rgb_to_hsv(red_percentage, green_percentage, blue_percentage) 
    print('color_hsv_percentage: ', color_hsv_percentage)

    #get normal hsv: range (0-360, 0-255, 0-255)
    color_h=round(360*color_hsv_percentage[0])
    color_s=round(255*color_hsv_percentage[1])
    color_v=round(255*color_hsv_percentage[2])
    color_hsv=(color_h, color_s, color_h)

    print('color_hsv: ', color_hsv)
    return color_hsv


def HEX2RGB(val):
    """
    Takes hex string and converts to rgb tuple.
    """
    hexNum = val.strip('#')
    hexLen = len(hexNum)
    conversion = tuple(int(hexNum[i:i+hexLen//3], 16) for i in range(0, hexLen, hexLen//3))
    return conversion


def get_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def get_colors(image, number_of_colors, show_chart):
    
    modified_image = cv2.resize(image, (600, 400), interpolation = cv2.INTER_AREA)
    modified_image = modified_image.reshape(modified_image.shape[0]*modified_image.shape[1], 3)
    
    clf = KMeans(n_clusters = number_of_colors)
    labels = clf.fit_predict(modified_image)
    
    counts = Counter(labels)
    # sort to ensure correct color percentage
    counts = dict(sorted(counts.items()))
    
    center_colors = clf.cluster_centers_
    # We get ordered colors by iterating through the keys
    ordered_colors = [center_colors[i] for i in counts.keys()]
    hex_colors = [RGB2HEX(ordered_colors[i]) for i in counts.keys()]
    rgb_colors = [ordered_colors[i] for i in counts.keys()]

    if (show_chart):
        plt.figure(figsize = (8, 6))
        plt.pie(counts.values(), labels = hex_colors, colors = hex_colors)
    
    print(rgb_colors, hex_colors)
    return rgb_colors, hex_colors


def recognize_color(csv, R=0, G=0, B=0):
    minimum = 10000
    for i in range(len(csv)):
        d = abs(R- int(csv.loc[i,"R"])) + abs(G- int(csv.loc[i,"G"]))+ abs(B- int(csv.loc[i,"B"]))
        if(d<=minimum):
            minimum = d
            cname = csv.loc[i,"color_name"]
    return cname


def checkBrightness(img, threshold=180):
    """
    checks the overall brightness of an image
    to make sure colors are interpreted correctly

    if brightness is lower than threshold,
    user is prompted to take another image
    """
    print(f"\nchecking image brightness ...")
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    values = img[:, :, 2]
    brightness = int(np.mean(values))
    print(f"average brightness of image = {brightness}")

    if brightness < threshold :
        print(f"brightness is too low !\nplease take another picture in better lighting")
    else:
        print(f"great photography skills !")
    
    plt.imshow(values, cmap="gray")


def complimentary(val):
    """
    Takes rgb tuple and produces complimentary color.
    """
    #value has to be 0 < x 1 in order to convert to hls
    r, g, b = map(lambda x: x/255.0, val)
    #hls provides color in radial scale
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    #get hue changes at 150 and 210 degrees
    deg_180_hue = h + (180.0 / 360.0)
    color_180_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_180_hue, l, s)))
    return color_180_rgb


def splitComplimentary(val):
    """
    Takes rgb tuple and produces list of split complimentary colors.
    """
    #value has to be 0 <span id="mce_SELREST_start" style="overflow:hidden;line-height:0;"></span>&lt; x 1 in order to convert to hls
    r, g, b = map(lambda x: x/255.0, val)
    #hls provides color in radial scale
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    #get hue changes at 150 and 210 degrees
    deg_150_hue = h + (150.0 / 360.0)
    deg_210_hue = h + (210.0 / 360.0)
    #convert to rgb
    color_150_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_150_hue, l, s)))
    color_210_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_210_hue, l, s)))
    return [color_150_rgb, color_210_rgb]


def analogous(val, d):
    """
    Takes rgb tuple and angle (out of 100) and produces list of analogous colors)
    """
    analogous_list = []
    #set color wheel angle
    d = d /360.0
    #value has to be 0 <span id="mce_SELREST_start" style="overflow:hidden;line-height:0;"></span>&lt; x 1 in order to convert to hls
    r, g, b = map(lambda x: x/255.0, val)
    #hls provides color in radial scale
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    #rotate hue by d
    h = [(h+d) % 1 for d in (-d, d)]
    for nh in h:
        new_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(nh, l, s)))
        analogous_list.append(new_rgb)
    return analogous_list


def triadic(val):
    """
    Takes rgb tuple and produces list of triadic colors.
    """
    #value has to be 0 < x 1 in order to convert to hls
    r, g, b = map(lambda x: x/255.0, val)
    #hls provides color in radial scale
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    #get hue changes at 120 and 240 degrees
    deg_120_hue = h + (120.0 / 360.0)
    deg_240_hue = h + (240.0 / 360.0)
    #convert to rgb
    color_120_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_120_hue, l, s)))
    color_240_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_240_hue, l, s)))
    return [color_120_rgb, color_240_rgb]


def tetradic(val):
    """
    Takes rgb tuple and produces list of tetradic colors.
    """
    #value has to be 0 <span id="mce_SELREST_start" style="overflow:hidden;line-height:0;"></span>&lt; x 1 in order to convert to hls
    r, g, b = map(lambda x: x/255.0, val)
    #hls provides color in radial scale
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    #get hue changes at 120 and 240 degrees
    deg_60_hue = h + (60.0 / 360.0)
    deg_180_hue = h + (180.0 / 360.0)
    deg_240_hue = h + (240.0 / 360.0)
    #convert to rgb
    color_60_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_60_hue, l, s)))
    color_180_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_180_hue, l, s)))
    color_240_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_240_hue, l, s)))
    return [color_60_rgb, color_180_rgb, color_240_rgb]


def createRange(clr, margin=10):
    r, g, b = clr
    rRange = set(range(r-margin, r+margin))
    gRange = set(range(g-margin, g+margin))
    bRange = set(range(b-margin, b+margin))
    print(f"r Range : {rRange}\ng Range : {gRange}\nb Range : {bRange}\n")
    return rRange, gRange, bRange


def checkClr(clr, rRange, gRange, bRange, match=False):
    if (clr[0] not in rRange) and (clr[1] not in gRange) and (clr[2] not in bRange):
        print("colors are out of range ! try another piece")
    else:
        print("colors are all safe !\ncolors are a good match !")
        match = True
    return match


#############################################
######### MAIN
#############################################

match = False
image = cv2.imread("./misc/tshirt.png")
print("The type of this input is {}".format(type(image)))
print("Shape: {}".format(image.shape))

# CHECK IMAGE BRIGHTNESS
checkBrightness(image)

# RESIZE IMAGE
height, width = 500, 500
image = cv2.resize(image, (height, width))
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
plt.imshow(image)

# CROP ROI
h, w, c = image.shape
margin = 100
window = image[h//2-margin:h//2+margin, w//2-margin:w//2+margin]
print(window.shape)
plt.imshow(window)

rgb, hex = get_colors(window, 1, True)
print(f"rgb : {rgb, type(rgb)}")
print(f"hex : {hex, type(hex)}")

rgb, hex = rgb[0], hex[0]
print(f"rgb : {rgb, type(rgb)}")
print(f"hex : {hex, type(hex)}")

R, G, B = rgb.astype(int)
print(f"colors : {R, G, B}, type {type(R)}")

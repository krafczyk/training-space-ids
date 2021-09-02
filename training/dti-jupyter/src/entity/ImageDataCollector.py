import io
import numpy as np
import urllib
import os

def get_image_from_url(input_url):
    ## start request the image ##
    with urllib.request.urlopen(input_url) as url:
        with open('temp_cluster.jpg', 'wb') as f:
            f.write(url.read)
    ## return the pil_im ##
    return os.getcwd() + 'temp_cluster.jpg'

## funcions ##

def download(this):

    return -1

def preprocess(this):

    return -1

def predict(this):

    return -1



def get_metadata_from_url(this, input_url):
    
    import io
    import numpy as np
    import urllib
    from PIL import Image

    pil_im = None
    ## start request the image ##
    with urllib.request.urlopen(input_url) as url:
        temp_img = url.read()
        pil_im = Image.open(io.BytesIO(temp_img), 'r')
    ## assign the image info into the C3 Type ##
    iw, ih = pil_im.size

    ## update the ImageDataCollector by creating and merging
    updates = c3.ImageDataCollector(
            **{
                "id": this.id,
                "image_width": iw,
                "image_height": ih
                })
    updates.merge()

    #print("hello world!")

    return [iw, ih]


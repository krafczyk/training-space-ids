## funcions ##

def download(this):

    import os, requests, json, uuid
    from requests.auth import HTTPBasicAuth
    import urllib.request
    from tqdm import tqdm
    from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__

    # authentication
    BASE_URL = 'https://api.planet.com/basemaps/v1/mosaics/'
    API_KEY = "8fb5d85cdcfc40f6b4b9d3f44227142b" # [from Yihong]
    auth = HTTPBasicAuth(API_KEY, '')

    # setup the planet auth
    mosaic_id = '56f00cc2-6be4-4315-9603-c75d6afab225' # should probablity convert to args
    url = f'https://api.planet.com/basemaps/v1/mosaics/{mosaic_id}/quads'
    bbox = '-91.51307900019566, 36.970297999852846, -87.49519900023363, 42.50848099959849' 

    # request the planet images
    res = requests.get(url=url, auth=auth, params={'bbox':bbox, '_page_size':99999})
    out = json.loads(res.text)

    # download all images into container
    connect_str = "DefaultEndpointsProtocol=https;AccountName=yifangidsimagedatatest;AccountKey=U94rgN17/BHzZuF6TNVItpqLj5NH7Y5/G/ZloFZi21aVMIsthULdPH1KuySuZZznGoZDOTApGXMw2nmnnFvlJQ==;EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client("images-planet")
    
    blob_images = container_client.list_blobs()
    current_images = []
    for b in blob_images:
        current_images.append(b.name)
        print(b.name)

    return current_images

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


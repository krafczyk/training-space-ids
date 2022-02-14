

from turtle import update


def download_raw_image(this):

    import os, requests, json, uuid
    from requests.auth import HTTPBasicAuth
    import urllib.request
    from tqdm import tqdm

    # if the file is already downloaded #
    if(this.status != 'created'):
        raise RuntimeError('The file is already downloaded the raw file')

    def downloadToExternal(srcUrl, fileName, extDir):
        tmp_path = "/tmp/" + fileName
        with requests.get(srcUrl, stream=True) as r:
            r.raise_for_status()
            with open(tmp_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        c3.Client.uploadLocalClientFiles(localPath=tmp_path, dstUrlOrEncodedPath=extDir, spec={"peekForMetadata": True})
        #c3.Logger.info("file {} downloaded to {}".format(fileName, extDir + fileName))
        os.remove(tmp_path)
        return extDir + '/' + fileName

    # create the url for the original source from #
    url = this.query_url

    # create a fresh instance to avoid weird errors #
    updated = c3.PlanetFile(**{'id':this.id})
    updated.status = 'downloading'

    # get the download path #
    defined_download_path = 'yifang_guan/planet_collection/raw/' + this.planet_collector.id + ''

    # create the download #
    try:
        extPath = downloadToExternal(url, this.name + '.tif', defined_download_path)
        updated.status = 'raw'
        updated.raw_image_file = c3.File(**{'url': extPath}).readMetadata()
        updated.external_raw_path = extPath
        updated.merge()
    except Exception as e:
        updated.status = 'error'
        updated.merge()
        raise e

    return updated.external_raw_path


def preprocess_raw_image(this):

    # import gdal and couple other libraries #
    import os
    from osgeo import gdal
    import osgeo

    ## changing the GDAL env path to find proj package ##
    root = '/'.join(osgeo.__path__[0].split('/')[0:-4])
    os.environ['PROJ_LIB'] = root + '/share/proj'
    os.environ['GDAL_DATA'] = root + '/share'

    ## a series checking for this C3 Class and see if it is ready for preprocessing #
    
    # test 1: status check #
    if(this.status != 'raw'):
        raise RuntimeError('The file is not ready to preprocess')

    def get_encoded_path(path):
        """
        Trim local fs url to absolute path
        e.g. from "file:///tmp/d.txt" to "/tmp/d.txt"
        """
        if path.startswith("file://"):
            return path[7:]
        return path

    def local_file(base_path):
        """
        Downloads file locally
        :param base_path: string to remote file system url
        :return: temp_path: string to local file system path
        """
        file = c3.LocalFileSystem.makeTmpFile().url
        c3.Client.copyFilesToLocalClient(srcUrlOrEncodedPath=base_path, localPath=file)
        temp_path = os.path.join(get_encoded_path(file), os.path.basename(base_path))
        return temp_path

    ## creating the tmp file in the space
    tmp_url = this.raw_image_file.url
    tmp_local = local_file(tmp_url)

    # test 2: raw image file path check #
    updated = c3.PlanetFile(**{'id':this.id})
    if(this.external_raw_path != None):
        try:
            ## print(updated.external_processed_path, updated.external_raw_path)
            updated.status = 'preprocessing'
            updated.external_processed_path = this.external_raw_path.replace('.tif', '-warp.tif')
            gdal_raw_fp = this.raw_image_file.contentLocation
            gdal_preprocessed_fp = gdal_raw_fp.replace('.tif', '-warp.tif')
            ## using the full path ##
            file_name = os.path.basename(updated.external_processed_path)
            folder_name = os.path.dirname(updated.external_processed_path)
            ## gdal.Warp(gdal_preprocessed_fp, gdal_raw_fp, dstSRS='EPSG:32616', xRes=3, yRes=3)
            ds = gdal.Open(tmp_local)
            options = gdal.WarpOptions(srcSRS='EPSG:3857', dstSRS = 'EPSG:32616', yRes=3, xRes=3)
            tmp_path = "/tmp/" + file_name
            gdal.Warp(srcDSOrSrcDSTab=ds, destNameOrDestDS=tmp_path, options=options)
            c3.Client.uploadLocalClientFiles(localPath=tmp_path, dstUrlOrEncodedPath=folder_name, spec={"peekForMetadata": True})
            updated.processed_image_file = c3.File(**{'url': updated.external_processed_path}).readMetadata()
            updated.status = 'preprocessed'
            updated.merge()
        except Exception as e:
            updated.status = 'error'
            updated.merge()
            raise e

    return updated.external_processed_path

def predict_image(this):
    # test 1: status check #
    if(this.status != 'preprocessed'):
        raise RuntimeError('Need to preprocess first')
    
    # tf imports
    from tensorflow.keras import Model
    from tensorflow.keras.layers import Conv2D, concatenate, Dropout, Input, BatchNormalization, MaxPooling2D, UpSampling2D, ReLU, Conv2DTranspose

    #====================================================def util functions
    def conv2d_block(input_tensor, n_filters, kernel_size = 3, batchnorm = True):
        """Function to add 2 convolutional layers with the parameters passed to it"""
        # first layer
        x = Conv2D(filters = n_filters, kernel_size = (kernel_size, kernel_size),\
                kernel_initializer = 'he_normal', padding = 'same')(input_tensor)
        if batchnorm:
            x = BatchNormalization()(x)
        x = ReLU()(x)

        # second layer
        x = Conv2D(filters = n_filters, kernel_size = (kernel_size, kernel_size),\
                kernel_initializer = 'he_normal', padding = 'same')(x)
        if batchnorm:
            x = BatchNormalization()(x)
        x = ReLU()(x)

        return x

    def get_unet(input_img, n_filters = 16, dropout = 0.1, batchnorm = True):
        """Function to define the UNET Model"""
        # Contracting Path
        c1 = conv2d_block(input_img, n_filters * 1, kernel_size = 3, batchnorm = batchnorm)
        p1 = MaxPooling2D((2, 2))(c1)
        p1 = Dropout(dropout)(p1)

        c2 = conv2d_block(p1, n_filters * 2, kernel_size = 3, batchnorm = batchnorm)
        p2 = MaxPooling2D((2, 2))(c2)
        p2 = Dropout(dropout)(p2)

        c3 = conv2d_block(p2, n_filters * 4, kernel_size = 3, batchnorm = batchnorm)
        p3 = MaxPooling2D((2, 2))(c3)
        p3 = Dropout(dropout)(p3)

        c4 = conv2d_block(p3, n_filters * 8, kernel_size = 3, batchnorm = batchnorm)
        p4 = MaxPooling2D((2, 2))(c4)
        p4 = Dropout(dropout)(p4)

        c5 = conv2d_block(p4, n_filters = n_filters * 16, kernel_size = 3, batchnorm = batchnorm)

        # Expansive Path
        u6 = Conv2DTranspose(n_filters * 8, (3, 3), strides = (2, 2), padding = 'same')(c5)
        u6 = concatenate([u6, c4])
        u6 = Dropout(dropout)(u6)
        c6 = conv2d_block(u6, n_filters * 8, kernel_size = 3, batchnorm = batchnorm)

        u7 = Conv2DTranspose(n_filters * 4, (3, 3), strides = (2, 2), padding = 'same')(c6)
        u7 = concatenate([u7, c3])
        u7 = Dropout(dropout)(u7)
        c7 = conv2d_block(u7, n_filters * 4, kernel_size = 3, batchnorm = batchnorm)

        u8 = Conv2DTranspose(n_filters * 2, (3, 3), strides = (2, 2), padding = 'same')(c7)
        u8 = concatenate([u8, c2])
        u8 = Dropout(dropout)(u8)
        c8 = conv2d_block(u8, n_filters * 2, kernel_size = 3, batchnorm = batchnorm)

        u9 = Conv2DTranspose(n_filters * 1, (3, 3), strides = (2, 2), padding = 'same')(c8)
        u9 = concatenate([u9, c1])
        u9 = Dropout(dropout)(u9)
        c9 = conv2d_block(u9, n_filters * 1, kernel_size = 3, batchnorm = batchnorm)

        outputs = Conv2D(1, (1, 1), activation='sigmoid')(c9)
        model = Model(input_img, outputs)
        #model.summary()
        return model

    def get_encoded_path(path):
        """
        Trim local fs url to absolute path
        e.g. from "file:///tmp/d.txt" to "/tmp/d.txt"
        """
        if path.startswith("file://"):
            return path[7:]
        return path

    def local_file(base_path):
        """
        Downloads file locally
        :param base_path: string to remote file system url
        :return: temp_path: string to local file system path
        """
        file = c3.LocalFileSystem.makeTmpFile().url
        c3.Client.copyFilesToLocalClient(srcUrlOrEncodedPath=base_path, localPath=file)
        temp_path = os.path.join(get_encoded_path(file), os.path.basename(base_path))
        return temp_path
    #=====================================================end def util functions

    # prediction params
    THRESHOLD = 0.5
    img_size = 224
    PAD = 64
    add_gcvi = True
    batch_size = 32
    
    # get UNet model
    input_img = Input((img_size, img_size, 5), name='img')
    model = get_unet(input_img, n_filters=32, dropout=0.15, batchnorm=True)

    # download weight and load it
    import requests
    import os
    for (name, url) in zip(['weight.tf.data-00000-of-00001', 'weight.tf.index'], 
        ['https://drive.google.com/uc?export=download&id=1u5tp5WoUiTPuVXltL1LCo_uR_YGu5Njm', 
        'https://drive.google.com/uc?export=download&id=1bhzwEFf9H7OGWw7jGr0TKnjrFnET0SWv']):
        tmp_path = "/tmp/" + name
        if os.path.isfile(tmp_path):
            print("skipping")
            continue
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(tmp_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    model.load_weights("/tmp/weight.tf")
    
    tmp_url = this.processed_image_file.url
    tmp_local = local_file(tmp_url)
    
    updated = c3.PlanetFile(**{'id':this.id})
    if(this.external_processed_path != None):
        try:
            updated.status = 'predicting'

            # read tif files add gcvi band
            import rasterio
            import numpy as np
            base_img = rasterio.open(tmp_local).read()
            base_img = np.transpose(base_img, (1, 2, 0))
            base_img = base_img[:, :, :4]
            if add_gcvi:
                gcvi = base_img[:, :, 3] / base_img[:, :, 1]
                gcvi = gcvi - 1
                gcvi[gcvi > 20] = 20
                gcvi[gcvi < 0] = 0
                gcvi = np.nan_to_num(gcvi, False, 0, 0, 0)
                gcvi = np.expand_dims(gcvi, -1)
                base_img = np.concatenate([base_img, gcvi], 2) 

            # cut image into 224*224 slice for prediction
            h, w, _ = base_img.shape
            center_size = (img_size - 2*PAD)
            h_count = int(h / center_size) + 1
            w_count = int(w / center_size) + 1
            h_padded = h_count * center_size
            w_padded = w_count * center_size
            base_img = np.pad(base_img, ((0, h_padded - h), (0, w_padded-w), (0, 0)), 'constant')
            base_img = np.pad(base_img, ((PAD, PAD), (PAD, PAD), (0, 0)), 'constant')
            input_img = []
            x = 0
            while x < h_padded - PAD:
                y = 0
                while y < w_padded - PAD:
                    input_img.append(base_img[x : x + img_size, y : y + img_size, :])
                    y += center_size
                x += center_size
            input_img = np.array(input_img)
            
            # predict
            out = model.predict(input_img, batch_size = batch_size, verbose = 1)
            
            # put prediction result back into big img
            combined = np.zeros((h_padded, w_padded))
            x = 0
            idx = 0
            while x < combined.shape[0]:
                y = 0
                while y < combined.shape[1]:
                    combined[x : x + center_size, y : y + center_size] = np.squeeze(out[idx][PAD:-PAD, PAD:-PAD, :], 2)
                    y += center_size
                    idx += 1
                x += center_size
            combined_cut = np.array(combined)
            combined_cut = combined_cut[:h, :w]
            
            # !TODO: this part is not tested
            # save npy file    
            file_name = os.path.basename(updated.external_processed_path)
            npy_path = "/tmp/" + file_name.replace('-warp.tif', 'npy')
            np.save(npy_path, combined_cut)
            
            # save tif files
            meta = rasterio.open(tmp_local).meta.copy()
            meta.update({
                'count':1,
                'dtype':np.uint8
            })
            combined_cut[combined_cut > 0.5] = 1
            combined_cut[combined_cut < 1] = 0
            combined_cut = combined_cut.astype(np.uint8)
            with rasterio.open(npy_path.replace('npy', '-pred.tif'), 'w', **meta) as dest:
                dest.write(np.expand_dims(combined_cut, 0))
            
            # upload result
            updated.external_npy_path = updated.external_processed_path.replace("-warp.tif", "npy")
            c3.Client.uploadLocalClientFiles(
                localPath=npy_path, 
                dstUrlOrEncodedPath=os.path.dirname(updated.external_npy_path), 
                spec={"peekForMetadata": True})
            updated.npy_result = c3.File(**{'url': updated.external_npy_path}).readMetadata()

            updated.external_pred_path = updated.external_processed_path.replace("warp", "pred")
            c3.Client.uploadLocalClientFiles(
                localPath=npy_path.replace('npy', '-pred.tif'), 
                dstUrlOrEncodedPath=os.path.dirname(updated.external_pred_path), 
                spec={"peekForMetadata": True})
            updated.tif_result = c3.File(**{'url': updated.external_pred_path}).readMetadata()
            
            updated.status = 'preprocessed'
            updated.merge()
        
        except Exception as e:
            updated.status = 'error'
            updated.merge()
            raise e

    return (updated.external_npy_path, updated.external_pred_path)
def generate_epoch(data_gen, input, target_output, batch_size, is_train, random_state):
    while input.hasNext():
        x = input.next().data
        y = target_output.next().data if target_output else None
        flow = data_gen.flow(x, y, batch_size, shuffle=is_train, seed=random_state)
        count = 0
        while count < x.shape[0]:
            yield flow.next()
            # if count + batch_size > x.shape[0]:
            #     yield flow.next()
            # else:
            #     yield flow.next()
            count += batch_size


def generator(this, input, targetOutput, isTrain, batchSize):
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    aug = this.imageAugmentationOptions or c3.ImageAugmentationOptions()
    pre = this.imagePreprocessingOptions or c3.ImagePreprocessingOptions()
    if isTrain:
        data_gen = ImageDataGenerator(
            samplewise_center=pre.samplewiseCenter or False, 
            samplewise_std_normalization=pre.samplewiseStdNormalization or False,
            rotation_range=aug.rotationRange, width_shift_range=aug.widthShiftRange,
            height_shift_range=aug.heightShiftRange, brightness_range=aug.brightnessRange, 
            shear_range=aug.shearRange, zoom_range=aug.zoomRange, channel_shift_range=aug.channelShiftRange,
            fill_mode=aug.fillMode, cval=aug.cval, horizontal_flip=aug.horizontalFlip or False,
            vertical_flip=aug.verticalFlip or False, rescale=pre.rescale, data_format=this.dataFormat
        )
        while True:
            yield from generate_epoch(data_gen, input, targetOutput, batchSize, isTrain, this.randomState)
            input.reset()
            if targetOutput: targetOutput.reset()
    else:
        data_gen = ImageDataGenerator(
            samplewise_center=pre.samplewiseCenter or False, 
            samplewise_std_normalization=pre.samplewiseStdNormalization or False,
            rescale=pre.rescale, data_format=this.dataFormat
        )
        yield from generate_epoch(data_gen, input, targetOutput, batchSize, isTrain, this.randomState)

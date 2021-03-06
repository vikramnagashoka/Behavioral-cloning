
# coding: utf-8

import csv
import cv2
import numpy as np
import matplotlib.image as mpimg

####
samples = []
with open("./new/driving_log.csv") as csvfile:
    reader = csv.reader(csvfile)
    for line in reader:
        samples.append(line)

from sklearn.model_selection import train_test_split
from keras.layers import Cropping2D
import numpy as np
import sklearn

train_samples, validation_samples = train_test_split(samples, test_size=0.2)

def generator(samples, batch_size=32):
    num_samples = len(samples)
    while 1: # Loop forever so the generator never terminates
        shuffle(samples)
        for offset in range(0, num_samples, batch_size):
            batch_samples = samples[offset:offset+batch_size]

            images = []
            angles = []
            for batch_sample in batch_samples:
                name = "./new/IMG/"+batch_sample[0].split('/')[-1]
                center_image = mpimg.imread(name)
                center_angle = float(batch_sample[3])
                images.append(center_image)
                angles.append(center_angle)
                #left and right
                #left
                image_path = batch_sample[1]
                filename_left = image_path.split('/')[-1]
                left_path = "./new/IMG/" + filename_left
                left_image = mpimg.imread(left_path)
                images.append(left_image)
                left_angle = float(batch_sample[3]) + 0.1
                angles.append(left_angle)
                #right
                image_path = batch_sample[2]
                filename_right = image_path.split('/')[-1]
                right_path = "./new/IMG/" + filename_right
                right_image = mpimg.imread(right_path)
                images.append(right_image)
                right_angle = float(batch_sample[3]) - 0.3 
                angles.append(right_angle)

            X_train = np.array(images)
            y_train = np.array(angles)
            yield sklearn.utils.shuffle(X_train, y_train)


from keras.models import Sequential
from keras.layers import Flatten,Dense,Lambda
from keras.layers.convolutional import Convolution2D
from keras.layers.pooling import MaxPooling2D
from sklearn.utils import shuffle
from keras.layers import Cropping2D, Dropout
from keras import regularizers
from keras import backend as K
from keras.regularizers import l2, activity_l2


train_generator = generator(train_samples, batch_size=32)
validation_generator = generator(validation_samples, batch_size=32)



model = Sequential()
# Preprocess incoming data, centered around zero with small standard deviation 
model.add(Lambda(lambda x: x/255.0 - 0.5,
        input_shape=(160, 320, 3)))

model.add(Cropping2D(cropping=((50,15), (0,0))))
model.add(Convolution2D(24,5,5,subsample=(2,2),activation='relu'))
model.add(Convolution2D(36,5,5,subsample=(2,2),activation='relu'))
model.add(Convolution2D(48,5,5,subsample=(2,2),activation='relu'))
model.add(Convolution2D(64,3,3,activation='relu'))
model.add(Convolution2D(128,3,3,activation='relu'))
model.add(Convolution2D(64,3,3,activation='relu'))
model.add(Flatten())
model.add(Dense(100))
model.add(Dense(64))
model.add(Dense(50))
model.add(Dense(10))
model.add(Dense(1))
model.compile(loss='mse',optimizer='adam')
model.fit_generator(train_generator, samples_per_epoch=len(train_samples), validation_data=validation_generator, nb_val_samples=len(validation_samples), nb_epoch=5)
model.save('model.h5')



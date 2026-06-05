import tensorflow as tf

batch_size= 32 
img_h=224
img_w=224

train_dir = "dataset/chest_xray/train"
test_dir = "dataset/chest_xray/test"
val_dir = "dataset/chest_xray/val"

train_ds = tf.keras.utils.image_dataset_from_directory(
    train_dir ,
    subset='training',
    seed=123,
    image_size=(img_h,img_w),
    batch_size=batch_size
)
val_ds = tf.keras.utils.image_dataset_from_directory(
    train_dir,
    subset='validation',
    seed=123,
    image_size=(img_h,img_w),
    batch_size=batch_size
)
test_ds = tf.keras.utils.image_dataset_from_directory(
    test_dir,
    image_size=(img_h,img_w),
    shuffle=False
)

# create sequential model

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,Conv2D,MaxPooling2D,Flatten,Dropout

model=Sequential()

model.add(Conv2D(
    32,
    kernel_size=(3,3),
    padding='same',
    strides=(1,1),
    activation='relu'
    ))

model.add(MaxPooling2D(
       pool_size=(2,2),
       strides=(2,2)
      ))

model.add(Conv2D(
    64,
    kernel_size=(3,3),
    padding='same',
    activation='relu'
    ))

model.add(MaxPooling2D(
       pool_size=(2,2)
      ))

model.add(Flatten())

model.add(Dense(4,activation='relu'))
model.add(Dense(4,activation='relu'))
model.add(Dense(4,activation='relu'))
model.add(Dense(4,activation='relu'))

model.add(Dropout(0.5))

model.add(Dense(1,activation='sigmoid'))

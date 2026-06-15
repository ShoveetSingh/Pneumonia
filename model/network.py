import tensorflow as tf

batch_size= 64 
img_h=224
img_w=224

train_dir = "dataset/chest_xray/train"
test_dir = "dataset/chest_xray/test"
val_dir = "dataset/chest_xray/val"

train_ds = tf.keras.utils.image_dataset_from_directory(
    train_dir ,
    # subset='training',
    seed=123,
    image_size=(img_h,img_w),
    batch_size=batch_size
)
val_ds = tf.keras.utils.image_dataset_from_directory(
    train_dir,
    # subset='validation',
    seed=123,
    image_size=(img_h,img_w),
    batch_size=batch_size
)
test_ds = tf.keras.utils.image_dataset_from_directory(
    test_dir,
    image_size=(img_h,img_w),
    shuffle=False
)
print(train_ds.class_names)
# create sequential model

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,Conv2D,MaxPooling2D,Flatten,Dropout

model=Sequential()
import os

# wi=total/(k*ni)

n_files = len(os.listdir('dataset/chest_xray/train/NORMAL'))
print(f'Normal fils are {n_files}')
p_files = len(os.listdir('dataset/chest_xray/train/PNEUMONIA'))
print(f'Pneumonia files are {p_files}')
total = n_files+p_files
print(f'Total files are {total}')
normal_wt = total/(2*n_files) # take 2 coz two classes to predict pneumonia or normal
pneumonia_wt = total/(2*p_files) # same here


class_wt = {
    0:normal_wt,
    1:pneumonia_wt
}
print(class_wt)


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

model.add(Dense(128,activation='relu'))
model.add(Dense(128,activation='relu'))


model.add(Dropout(0.5))

model.add(Dense(1,activation='sigmoid'))

model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

from tensorflow.keras.callbacks import EarlyStopping

early_stop = EarlyStopping(
    monitor='val_loss',
    restore_best_weights=True,
    patience=2
)

model.fit(x=train_ds,
          validation_data=val_ds,
          class_weight =class_wt,
          callbacks = [early_stop],
          epochs=12)

result=model.evaluate(test_ds,verbose=2)  

print(f'Model evaluation result is {result}')

model.save('pneumonia.keras')
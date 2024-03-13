# -*- coding: utf-8 -*-
"""Proyek_NLP (1).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17dBnt2F_oJa7RqAkfTSR3fGz-ooM-cmB

# Proyek NLP : Deteksi Ungkapan Kebencian

*   Nama                : Hauzan Tsaaqif Mushaddaq
*   Username            : hauzantsaaqif
*   Email               : hauzantsaaqif28@gmail.com
*   No. Telepon         : 6285864995278
"""

from google.colab import files
files.upload()

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/

!chmod 600 ~/.kaggle/kaggle.json

!kaggle datasets download -d waalbannyantudre/hate-speech-detection-curated-dataset

import zipfile

local_zip = '/content/hate-speech-detection-curated-dataset.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('/content')
zip_ref.close()

import pandas as pd
df = pd.read_csv('HateSpeechDataset.csv')
df.head()

print(len(df))

"""Dikarenakan data pada dataset memiliki jumlah yang sangat besar, sehingga mengakibatkan waktu dalam training data sangat lama, sehingga saya pun pada akhirnya mengambil hanya 2000 untuk masing2 label."""

df_subset_0 = df[df['Label'] == "0"].sample(n=5000, random_state=42)
df_subset_1 = df[df['Label'] == "1"].sample(n=5000, random_state=42)

df_reduced = pd.concat([df_subset_0, df_subset_1])

df_reduced = df_reduced.sample(frac=1, random_state=42).reset_index(drop=True)

print("Jumlah setiap label pada subset:")
print(df_reduced['Label'].value_counts())
print(len(df_reduced))

"""Disini saya menggunakan one hot encoding pada Label dikarenakan Label memiliki tipe data String, sehingga saya berfikir untuk diubah kedalam integer dengan one hot encoding."""

category = pd.get_dummies(df.Label)
df_baru = pd.concat([df, category], axis=1)
df_baru = df_baru.drop(columns='Label')
df_final = df_baru.drop(columns='Content_int')
df_final

df_label_1 = df_final[df_final['0'] == 1]
df_label_1.head()

df_label_1 = df_final[df_final['1'] == 1]
df_label_1.head()

from sklearn.model_selection import train_test_split

comment = df_final['Content'].values
label = df_final[["0", "1"]].values
comment_latih, comment_test, label_latih, label_test = train_test_split(comment, label, test_size=0.2)

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

tokenizer = Tokenizer(num_words=9000, oov_token='x')
tokenizer.fit_on_texts(comment_latih)
tokenizer.fit_on_texts(comment_test)

sekuens_latih = tokenizer.texts_to_sequences(comment_latih)
sekuens_test = tokenizer.texts_to_sequences(comment_test)

padded_latih = pad_sequences(sekuens_latih, maxlen=100)
padded_test = pad_sequences(sekuens_test, maxlen=100)

import json

# Mendapatkan word_index dari Tokenizer
word_index = tokenizer.word_index

# Menyimpan word_index ke dalam file JSON
with open('word_index.json', 'w') as f:
    json.dump(word_index, f)

import tensorflow as tf

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(9000, 16, input_length=100),
    tf.keras.layers.LSTM(256),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(2, activation='sigmoid')
])

model.summary()

"""Disini menggunakan callbacks 3 macam untuk memaksimalkan training."""

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard

import os, shutil

if os.path.exists("logs/fit/"):
    shutil.rmtree("logs/fit/")
    print("Log directory deleted successfully.")
else:
    print("Log directory doesn't exist.")

import datetime
import tensorflow as tf
log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

from keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

checkpoint = ModelCheckpoint("model.h5", monitor="val_accuracy", save_best_only=True)
early_stopping = EarlyStopping(monitor="accuracy", min_delta=0.001, patience=5, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor="val_loss", factor=0.001, patience=5, min_lr=1e-6)
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

callbacks = [checkpoint, early_stopping, reduce_lr, tensorboard_callback]

# Commented out IPython magic to ensure Python compatibility.
# %tensorboard --logdir logs/fit

model.compile(loss='binary_crossentropy', optimizer=tf.optimizers.RMSprop(), metrics=['accuracy'])

history = model.fit(padded_latih, label_latih, epochs=50, steps_per_epoch=500, validation_data=(padded_test, label_test), verbose=2, callbacks=callbacks)

model.save("model.h5")

!pip install tensorflowjs

!tensorflowjs_converter --input_format=keras model.h5 tfjs_model

"""# Test Model"""

from tensorflow.keras.models import load_model

model = load_model('/content/model.h5')

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

import json

with open('/content/word_index.json', 'r') as f:
    word_index = json.load(f)

tokenizer_baru = Tokenizer(num_words=9000, oov_token='x')
tokenizer_baru.word_index = word_index

import numpy as np

teks_baru = ["why is this creature even alive murderer"]
teks_baru_1 = ["yeah retard haha"]
teks_baru_2 = ["denial of normal the con be asked to comment on tragedies an emotional retard"]
teks_baru_3 = ["booklet updated on"]
teks_baru_4 = ["you are ugly"]
teks_baru_5 = ["you are beautiful"]
teks_baru_6 = ["I think you are just a loser"]

sequences_baru = tokenizer_baru.texts_to_sequences(teks_baru_5)
print(sequences_baru)
padded_baru = pad_sequences(sequences_baru, maxlen=100)
print(padded_baru)
hasil_prediksi = model.predict(padded_baru)
kelas_prediksi = hasil_prediksi[0][0] > hasil_prediksi[0][1]

print(hasil_prediksi)

if kelas_prediksi:
  print("Non Hate Speech")
else:
  print("Hate Speech")

"""# Simulasi Sosial Media
"Good User Account"
Pada simulasi ini, user dapat memberikan komentar pada input teks, kemudian input teks akan dideteksi kategori komentar yang diberikan user, dan user akan diberikan punisment sesuai dengan kategori komentar.
"""

from tensorflow.keras.models import load_model

loaded_model = load_model('/content/model.h5')
run = 1
status = 0

def hatred_detection(teks_baru):
  teks_input = [teks_baru]
  sequences_baru = tokenizer.texts_to_sequences(teks_input)
  padded_baru = pad_sequences(sequences_baru, maxlen=100)

  hasil_prediksi = loaded_model.predict(padded_baru)
  kelas_prediksi = hasil_prediksi[0][0] > hasil_prediksi[0][1]

  if kelas_prediksi:
    return 0
  else:
    return 1

print("User Login")
print("...")
print("Tweets :")
print("Hello everyone, today I am in Jakarta to try somersaulting around Monas.")
print("...")
print("Comment Section : (input 'cls' for logout)")
while run:
  comment = input("User : ")

  if comment == "cls":
    run = 0
    print("Log out ....")
  else:
    status = status + hatred_detection(comment)

    if status == 1:
      print("System: Violation warning, hate speech is not allowed")
    elif status == 2:
      run = 0
      print("System: your account was suspended because some hate speech you wrote violated our rules")
from traceback import print_tb

import cv2
import numpy as np
import os
import zipfile
import tensorflow as tf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from rn_keras import RnKeras

width = 128
height = 128
directory_path = './homer_bart_1'
files = [os.path.join(directory_path, f) for f in sorted(os.listdir(directory_path))]
images = []
classes = []

for image_path in files:
    image = cv2.imread(image_path)
    (H, W) = image.shape[:2]
    image = cv2.resize(image, (width, height))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('estudos', image)
    # cv2.waitKey(0)
    image = image.ravel()
    images.append(image)
    name_image = os.path.basename(os.path.normpath(image_path))
    classes.append(0 if name_image.startswith('b') else 1)

X = np.asarray(images)
Y = np.asarray(classes)

# sns.countplot(classes)
# plt.show()
# print(np.unique(Y, return_counts=True))
# print(X[0].max(), X[0].min())

scaler = MinMaxScaler()
X = scaler.fit_transform(X)

# print(X.max(), X.min())

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=1)

# print(X_train.shape)
# print(X_test.shape)
# print(Y_train.shape)
# print(Y_test.shape)

rnKeras = RnKeras()
# rnKeras.train(X_train, Y_train)
model, history = rnKeras.load_nr()
print(model.summary())
# print(model)
# print(history)
# plt.plot(history['loss'])
# plt.show()
# plt.plot(history['accuracy'])
# plt.show()

# 0 False Bart
# 1 True Homer
previsions = model.predict(X_test)
previsions = (previsions > 0.5)
# print(previsions)

score = accuracy_score(Y_test, previsions)
print(score)
cm = confusion_matrix(Y_test, previsions)
# Criar o heatmap usando seaborn
# plt.figure(figsize=(8, 6))
# sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
#             xticklabels=["Classe 0", "Classe 1"], yticklabels=["Classe 0", "Classe 1"])
# plt.title("Matriz de Confusão")
# plt.xlabel("Previsão")
# plt.ylabel("Valor Real")
# plt.show()

print(classification_report(Y_test, previsions))

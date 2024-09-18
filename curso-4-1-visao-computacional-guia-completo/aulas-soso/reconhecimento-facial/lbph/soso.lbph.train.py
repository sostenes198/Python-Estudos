from PIL import Image
import os
import cv2
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix
import seaborn


class SosoLbphTrain:
    def __init__(self):
        self.__pathsTrain = [os.path.join('./../sosofaces/train', f) for f in os.listdir('../sosofaces/train')]
        self.__pathsTest = [os.path.join('./../sosofaces/test', f) for f in os.listdir('../sosofaces/test')]

    def __get_image_data(self, paths):
        faces = []
        ids = []
        for path in paths:
            img = Image.open(path).convert('L')
            img_np = np.array(img, 'uint8')
            face_id = int(os.path.split(path)[1].split('.')[0].split('_')[0])
            ids.append(face_id)
            faces.append(img_np)

        return np.array(ids), faces

    def __train_classifier(self):
        ids, faces = self.__get_image_data(self.__pathsTrain)
        lbph_classifier = cv2.face.LBPHFaceRecognizer.create()
        lbph_classifier.train(faces, ids)
        lbph_classifier.write('lbph_soso_classifier.yml')

    def __read_lbph_classifier(self):
        lbph_classifier = cv2.face.LBPHFaceRecognizer.create()
        lbph_classifier.read('lbph_soso_classifier.yml')
        return lbph_classifier

    def __evaluate_classifier_performance(self):
        previsions = []
        expect_results = []
        lbph_classifier = self.__read_lbph_classifier()

        for path in self.__pathsTest:
            img = Image.open(path).convert('L')
            img_np = np.array(img, 'uint8')
            prevision, _ = lbph_classifier.predict(img_np)
            expect_result = int(os.path.split(path)[1].split('.')[0].split('_')[0])
            previsions.append(prevision)
            expect_results.append(expect_result)

        np_previsions = np.array(previsions)
        np_expect_results = np.array(expect_results)
        accuracy_score_result = accuracy_score(np_previsions, np_expect_results)
        cm = confusion_matrix(np_expect_results, np_previsions)
        sb = seaborn.heatmap(cm, annot=True)
        print(accuracy_score_result)
        print(cm)
        print(sb)

    def execute(self):
        self.__train_classifier()
        # self.__evaluate_classifier_performance()


if __name__ == '__main__':
    classifier = SosoLbphTrain()
    classifier.execute()

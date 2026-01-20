# Local Binary Patterns Histograms

from PIL import Image
import cv2
import numpy as np
import os
from sklearn.metrics import accuracy_score, confusion_matrix
import seaborn


class EstudosLBPH:

    @staticmethod
    def __get_image_data():
        paths = [os.path.join('./../yalefaces/train', f) for f in os.listdir('../yalefaces/train')]
        faces = []
        ids = []
        for path in paths:
            img = Image.open(path).convert('L')
            img_np = np.array(img, 'uint8')
            id = int(os.path.split(path)[1].split('.')[0].replace('subject', ''))
            ids.append(id)
            faces.append(img_np)

        return np.array(ids), faces

    def __train_classifier(self):
        ids, faces = self.__get_image_data()
        lbph_classifier = cv2.face.LBPHFaceRecognizer.create(radius=4, neighbors=14, grid_x=9, grid_y=9)
        lbph_classifier.train(faces, ids)
        lbph_classifier.write('lbph_classifier.yml')

    @staticmethod
    def __read_lbph_classifier():
        lbph_classifier = cv2.face.LBPHFaceRecognizer.create()
        lbph_classifier.read('lbph_classifier.yml')
        return lbph_classifier

    def __test_classifier(self):
        lbph_classifier = self.__read_lbph_classifier()
        img_test = './yalefaces/test/subject10.sad.gif'
        img = Image.open(img_test).convert('L')
        img_np = np.array(img, 'uint8')
        prevision = lbph_classifier.predict(img_np)
        expect_result = int(os.path.split(img_test)[1].split('.')[0].replace('subject', ''))

        cv2.putText(img_np, 'PRED:' + str(prevision[0]), (10, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0))
        cv2.putText(img_np, 'Exp:' + str(expect_result), (10, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0))
        cv2.imshow('Test', img_np)
        cv2.waitKey()

    def __evaluate_classifier_performance(self):
        paths = [os.path.join('./../yalefaces/test', f) for f in os.listdir('../yalefaces/test')]
        previsions = []
        expect_results = []
        lbph_classifier = self.__read_lbph_classifier()

        for path in paths:
            img = Image.open(path).convert('L')
            img_np = np.array(img, 'uint8')
            prevision, _ = lbph_classifier.predict(img_np)
            expect_result = int(os.path.split(path)[1].split('.')[0].replace('subject', ''))
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
        self.__evaluate_classifier_performance()


if __name__ == '__main__':
    es = EstudosLBPH()
    es.execute()

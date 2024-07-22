import dlib
import cv2
import os
import numpy as np
from sklearn.metrics import accuracy_score
from PIL import Image


class EstudosDeteccaoPontosFaciais:

    def __init__(self):
        self.__face_detector = dlib.get_frontal_face_detector()
        self.__points_detector = dlib.shape_predictor(
            os.path.abspath('./../') + '/shape_predictor_68_face_landmarks.dat')
        self.__facial_descriptor_extractor = dlib.face_recognition_model_v1(
            os.path.abspath('./../') + '/dlib_face_recognition_resnet_model_v1.dat')

    def __face_detector(self):
        img = cv2.imread('../people2.jpg')
        detections = self.__face_detector(img, 1)
        for face in detections:
            points = self.__points_detector(img, face)
            # print(points.parts())
            # print(len(points.parts()))

            for point in points.parts():
                cv2.circle(img, (point.x, point.y), 2, (0, 255, 0), 1)

            l, t, r, b = face.left(), face.top(), face.right(), face.bottom()
            cv2.rectangle(img, (l, t), (r, b), (0, 255, 0), 2)
        cv2.imshow('Estudos', img)
        cv2.waitKey()

    def __face_dector_with_descriptor(self):
        index = {}
        idx = 0
        facial_descriptors = None
        confiance = 0.5
        previsions = []
        expected_previsions = []

        paths = [os.path.join('./../yalefaces/train', f) for f in os.listdir('./../yalefaces/train')]
        for path in paths:
            img = Image.open(path).convert('RGB')
            img_np = np.array(img, 'uint8')
            detections = self.__face_detector(img_np, 1)
            for face in detections:
                l, t, r, b = face.left(), face.top(), face.right(), face.bottom()
                cv2.rectangle(img_np, (l, t), (r, b), (0, 0, 255), 2)
                points = self.__points_detector(img_np, face)
                for point in points.parts():
                    cv2.circle(img_np, (point.x, point.y), 2, (0, 255, 0), 1)

                facial_descriptor = self.__facial_descriptor_extractor.compute_face_descriptor(img_np, points)
                facial_descriptor = [f for f in facial_descriptor]
                facial_descriptor = np.asarray(facial_descriptor, dtype=np.float64)
                facial_descriptor = facial_descriptor[np.newaxis, :]
                if facial_descriptors is None:
                    facial_descriptors = facial_descriptor
                else:
                    facial_descriptors = np.concatenate((facial_descriptors, facial_descriptor), axis=0)
                # print(type(facial_descriptor))
                # print(facial_descriptor.shape)
                # print(facial_descriptor)
                index[idx] = path
                idx += 1

        paths = [os.path.join('./../yalefaces/test', f) for f in os.listdir('./../yalefaces/test')]
        for path in paths:
            img = Image.open(path).convert('RGB')
            img_np = np.array(img, 'uint8')
            detections = self.__face_detector(img_np, 1)
            for face in detections:
                points = self.__points_detector(img_np, face)

                facial_descriptor = self.__facial_descriptor_extractor.compute_face_descriptor(img_np, points)
                facial_descriptor = [f for f in facial_descriptor]
                facial_descriptor = np.asarray(facial_descriptor, dtype=np.float64)
                facial_descriptor = facial_descriptor[np.newaxis, :]

                distances = np.linalg.norm(facial_descriptor - facial_descriptors, axis=1)
                min_index = np.argmin(distances)
                min_distance = distances[min_index]
                if min_distance <= confiance:
                    prevision_name = int(os.path.split(index[min_index])[1].split('.')[0].replace('subject', ''))
                else:
                    prevision_name = 'Face não encontrada'

                real_name = int(os.path.split(path)[1].split('.')[0].replace('subject', ''))

                previsions.append(prevision_name)
                expected_previsions.append(real_name)

                # cv2.putText(img_np, 'Pred ' + str(prevision_name), (10, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)
                # cv2.putText(img_np, 'Exp ' + str(real_name), (10, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)
                #
                # cv2.imshow('Estudos', img_np)
                # cv2.waitKey()

        previsions = np.array(previsions)
        expected_previsions = np.array(expected_previsions)

        print(accuracy_score(expected_previsions, previsions))

    def execute(self):
        self.__face_dector_with_descriptor()


if __name__ == '__main__':
    estudos = EstudosDeteccaoPontosFaciais()
    estudos.execute()

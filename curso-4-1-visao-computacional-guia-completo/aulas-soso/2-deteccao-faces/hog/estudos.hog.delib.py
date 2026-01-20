import dlib
import cv2


class EstudosHogDelib:
    def __init__(self):
        self.__img = cv2.imread('people_2.jpg')

        self.__detector_face_hog = dlib.get_frontal_face_detector()
        self.__detections = self.__detector_face_hog(self.__img, 1)

    def execute(self):
        self.__draw_rectangle_faces_in_image()
        self.__show_image()

    def __show_image(self):
        cv2.imshow('Estudos de Hog', self.__img)
        cv2.waitKey(0)

    def __print_detections(self):
        for face in self.__detections:
            print(face)
            print(face.left(), face.top(), face.right(), face.bottom())


    def __draw_rectangle_faces_in_image(self):
        for face in self.__detections:
            l, t, r, b = face.left(), face.top(), face.right(), face.bottom()
            cv2.rectangle(self.__img, (l, t), (r, b), (0, 255, 0), 2)


if __name__ == '__main__':
    study = EstudosHogDelib()
    study.execute()

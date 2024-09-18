import cv2 as cv  # OpenCv


class EstudosHaarcascade1EyeDetections:

    def __init__(self):
        # self.__image = cv.resize(cv.imread('people_1.png'), (800, 600))
        self.__image = cv.imread('people_1.png')
        self.__grayImage = cv.cvtColor(self.__image, cv.COLOR_BGR2GRAY)
        self.__faceDetector = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.__faceDetections = self.__faceDetector.detectMultiScale(self.__grayImage, scaleFactor=1.3, minSize=(30,30), minNeighbors=5)
        self.__eyeDetector = cv.CascadeClassifier('haarcascade_eye.xml')
        self.__eyesDetections = self.__eyeDetector.detectMultiScale(self.__grayImage, scaleFactor=1.09, minNeighbors=10, maxSize=(70,70))

    def show_image(self):
        cv.imshow('image', self.__image)
        cv.waitKey()

    def show__gray_image(self):
        cv.imshow('image', self.__grayImage)
        cv.waitKey()

    @staticmethod
    def show_calculate_channels():
        print(f'Color Image: {600 * 800 * 3}')
        print(f'Gray Image: {600 * 800 * 1}')

    def show_shape(self):
        print(self.__image.shape)

    def execute_detections_face(self):
        for x, y, w, h in self.__faceDetections:
            # print(x,y,w,h)
            cv.rectangle(self.__image, (x + w, y + h), (x, y), (0, 255, 255), 2)

    def execute_detections_eyes(self):
        for x, y, w, h in self.__eyesDetections:
            # print(x,y,w,h)
            cv.rectangle(self.__image, (x + w, y + h), (x, y), (0, 255, 0), 2)

    def execute(self):
        self.show_calculate_channels()
        self.execute_detections_face()
        self.execute_detections_eyes()
        self.show_image()



if __name__ == '__main__':
    study = EstudosHaarcascade1EyeDetections()

    study.execute()

import cv2


class SosoWebCam:
    def __init__(self):
        self.__face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.__recognition_face = SosoWebCam.__read_lbph_classifier()
        self.__height = 220
        self.__width = 220
        self.__font = cv2.FONT_HERSHEY_COMPLEX_SMALL
        self.__camera = cv2.VideoCapture(0)

    @staticmethod
    def __read_lbph_classifier():
        lbph_classifier = cv2.face.LBPHFaceRecognizer.create()
        lbph_classifier.read('lbph_soso_classifier.yml')
        return lbph_classifier

    def execute(self):
        while True:
            ok, frame = self.__camera.read()
            gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detections = self.__face_detector.detectMultiScale(gray_img, scaleFactor=1.5, minSize=(30, 30))
            for (x, y, w, h) in detections:
                face_image = cv2.resize(gray_img[y:y + w, x:x + h], (self.__width, self.__height))
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                id, confidence = self.__recognition_face.predict(face_image)
                if id == 1 and confidence <= 85:
                    name = "Soso"
                else:
                    name = "IDK"
                cv2.putText(frame, name, (x, y + (w + 30)), self.__font, 2, (0, 0, 255))
                cv2.putText(frame, str(confidence), (x, y + (h + 50)), self.__font, 2, (0, 0, 255))

            cv2.imshow('WebCam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.__camera.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    webCam = SosoWebCam()
    webCam.execute()

import cv2


class WebCam:

    def __init__(self):
        self.__detectorFace = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.__videoCapture = cv2.VideoCapture(0)

    def start_capture_webcam(self):
        while True:
            ok, frame = self.__videoCapture.read()
            gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            detections = self.__detectorFace.detectMultiScale(gray_img, scaleFactor=1.2, minSize=(100, 100))
            self.__write_rectacgle_face_in_image(frame, detections)
            cv2.imshow('WebCam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.__videoCapture.release()
        cv2.destroyAllWindows()

    def __write_rectacgle_face_in_image(self, frame, detections):
        for (x, y, w, h) in detections:
            print(w,h)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)


if __name__ == '__main__':
    webcam = WebCam()
    webcam.start_capture_webcam()

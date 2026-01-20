import cv2

rastreador = cv2.TrackerCSRT().create()

video = cv2.VideoCapture('street.mp4')
ok, frame = video.read()

bbox = cv2.selectROI(frame)

ok = rastreador.init(frame, bbox)
while True:
    ok, frame = video.read()
    if not ok:
        break

    ok, bbox = rastreador.update(frame)

    (x,y,w,h) = [int(v) for v in bbox]
    cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

    cv2.imshow('Rastreamento', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

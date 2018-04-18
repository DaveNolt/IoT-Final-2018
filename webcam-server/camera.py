import datetime
import time
import imutils
import cv2
from events import Events
from threading import Thread


class Camera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def getFrame(self):
        _, frame = self.video.read()
        return frame


class Scanner(object):
    def __init__(self):
        self.thread = Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()
        self.frame = None
        self.sentinel = True
        self.events = Events(('onOccupied', 'onTimeout', 'onSetTimeoutLength'))
        self.timeoutTime = None
        self.timeoutLength = 180
        self.events.onTimeout += self.timeout
        self.events.onSetTimeoutLength += self.setTimeoutLength
        self.events.onOccupied += self.timeout
        self.events.onTimeout += lambda: print(
            'Caught Event: onTimeout; ' + str(datetime.datetime.now().time()))
        self.events.onSetTimeoutLength += lambda length: print('Caught Event: onSetTimeoutLength, length = ' + str(
            length) + '; ' + str(datetime.datetime.now().time()))

    def stop(self):
        self.sentinel = False
        self.thread.join()

    def setTimeoutLength(self, length):
        self.timeoutLength = length

    def timeout(self):
        self.timeoutTime = time.time()

    def run(self):
        camera = Camera()
        firstFrame = None
        timer = time.time()
        text = "Nobody present"
        frame = None
        min_area = 10

        while self.sentinel:
            frame = camera.getFrame()
            frame = imutils.resize(frame, width=500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if (firstFrame is None) or (time.time() - timer >= 5):
                text = "Nobody present"
                firstFrame = gray
                frame = camera.getFrame()
                timer = time.time()
                continue

            frameDelta = cv2.absdiff(firstFrame, gray)
            thresh = cv2.threshold(
                frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

            thresh = cv2.dilate(thresh, None, iterations=2)
            (_, cnts, _) = cv2.findContours(thresh.copy(),
                                            cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for c in cnts:
                if cv2.contourArea(c) < min_area:
                    text = "Nobody present"
                    continue

                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "Occupied"

                if (self.timeoutTime == None or time.time() - self.timeoutTime >= self.timeoutLength):
                    self.events.onOccupied()

            cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            self.frame = frame

    def getJpeg(self):
        _, jpeg = cv2.imencode('.jpeg', self.frame)
        return jpeg.tobytes()

    def getRaw(self):
        return self.frame


if __name__ == '__main__':
    scanner = Scanner()
    scanner.events.onOccupied += lambda: print('occupied')
    time.sleep(2)
    cv2.namedWindow('preview')
    scanner.events.onSetTimeoutLength(length=15)
    scanner.events.onTimeout()
    while True:
        cv2.imshow('preview', scanner.getRaw())
        key = cv2.waitKey(20)
        if key == 27:
            break

    cv2.destroyWindow('preview')
    scanner.stop()

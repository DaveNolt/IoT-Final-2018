from flask import Flask, render_template, Response
from camera import Scanner
import paho.mqtt.client as mqtt
import const
from datetime import datetime

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(const.sub_topic, 1)


def on_message(client, userdata, msg):
    global scanner
    message = msg.payload.decode('utf-8')
    if 'SetTimeoutLength' in message:
        scanner.events.onSetTimeoutLength(int(message.split('=')[1]))
    elif 'Timeout' in message:
        scanner.events.onTimeout()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect_async(const.host, 1883, 60)
client.loop_start()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


def gen(camera):
    while True:

        frame = camera.getJpeg()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    global scanner
    return Response(gen(scanner),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    scanner = Scanner()
    scanner.events.onOccupied += lambda: client.publish(
        const.pub_topic, 'Occupied ' + str(datetime.now().time()), 1)
    scanner.events.onOccupied += lambda: print('Sent Event: onOccupied; ' +
                                               str(datetime.now().time()))
    app.run(host='0.0.0.0', debug=False)

const child_process = require('child_process');
const mqtt = require('mqtt');
let client = mqtt.connect('mqtt://188.242.74.76');

client.on('connect', function () {
  client.subscribe('mck/alarm');
})

client.on('message', function (topic, message) {
  let proc = child_process.spawn('ffplay', ['-autoexit', '-nodisp', './res/alarm.mp3']);
  if (!proc) {
    console.err("Unable to spawn process");
  }
})
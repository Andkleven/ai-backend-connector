Run the following in the raspberry pi camera to send video stream to IP 192.168.10.56
```sh
gst-launch-1.0 rpicamsrc bitrate=1700000 sensor-mode=4 ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.10.56 port=5200
```

Or this
```sh
raspivid -w 1080 -h 1080 -b 25000000 -cd MJPEG -fps 40 -n -t 0 -o - | gst-launch-1.0 -v fdsrc ! "image/jpeg,width=1640,height=1232",framerate=40/1 ! jpegparse ! rtpjpegpay ! udpsink host=192.168.10.56 port=5200
```

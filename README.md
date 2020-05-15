
# Intallation
## Setup a virtual environment
This repo is tested with Python 3.6.9.

Create Python virtual environment if you want.
### Ubuntu
`virtualenv venv`
`source venv/bin/activate`
### Windows 10
`python -m venv venv`
`venv\Scripts\Activate`

## Link Gstreamer packages to virtual environment in Linux
If you are using virtual environment in Linux, link the gi Python package from system's Python to the virtual environment's Python 
[Gist](https://gist.github.com/jegger/10003813)
```
cd venv/lib/python3.6/site-packages
ln -s /usr/lib/python3/dist-packages/gi
cd ../../../..
```

## Install Python packages
`pip install --upgrade pip`
`pip install --upgrade setuptools`
`pip install -r requirements.txt`
**Note for Windows:** Download Shapely-package which has it's geos-dependency built in from link below. Choose the one which matches your system from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely). Install with `pip install Shapely‑1.7.0‑cp36‑cp36m‑win_amd64.whl` or what ever is your system's package name. After installing Shapely wheel comment out `shapely` from requirements.txt and run `pip install -r requirements.txt`.


# Test Robot backend with Unity Simulation

## Test screen streaming from Unity Simulator
Run the following command in the project's root folder
`python -m camera_source.unity_simulation_camera`
Now load the Unity Simulator's scene `PushBlockRobotBackendTest` and press Play

## Generate proto codes
### gRPC code for Unity Simulation communication
```sh
python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. ./proto/RobotBackendCommunication.proto
```


## Calibrate camera
```sh
python -m computer_vision.camera_calibration -m=calibration -i=computer_vision/unity_camera_calibration/
```

## Raspberry Pi camera
Run the following in the raspberry pi camera to send video stream to IP 192.168.10.56
```sh
gst-launch-1.0 rpicamsrc bitrate=1700000 sensor-mode=4 ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.10.56 port=5200
```

Or this
```sh
raspivid -w 1080 -h 1080 -b 25000000 -cd MJPEG -fps 40 -n -t 0 -o - | gst-launch-1.0 -v fdsrc ! "image/jpeg,width=1640,height=1232",framerate=40/1 ! jpegparse ! rtpjpegpay ! udpsink host=192.168.10.56 port=5200
```

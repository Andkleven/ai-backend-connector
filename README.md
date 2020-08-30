# AI Backend Connector

Read the summary of Micro Invaders from [here](https://github.com/robot-uprising-hq/ai-guide).

This is repository is based on Unity ML Agents Release 6 and the PushBlock example. This has been tested on Ubuntu 20.04, macOS Catalina 10.15.2, and Windows 10.

# Installation

## Prequisites
- python3 (3.6.1 or higher)
- Git

# Using this repo

## Driving AI Simulator
See document [here](docs/Drive-AISimulator.md)

## Driving AI Robot
See document [here](docs/Drive-AIRobot.md)

# Developing guide
## Changes to gRPC messages
In case you change a gRPC message check [this document](https://github.com/robot-uprising-hq/ai-guide/blob/master/docs/Generating-gRPC-code.md)

# Known issues

1. Running `python gui_robot_backend.py -m=simu` causes the following error messages to be printed to the console:
    ```
    ALSA lib pcm_dmix.c:1089:(snd_pcm_dmix_open) unable to open slave
    ```
    This has most likely something to do with gstreamer or opencv.
    Some versions of `opencv-python`-package cause the script to crash but `opencv-python==4.2.0.32` and `opencv-contrib-python==4.2.0.32` don't crash.

2. Qt: Session management error: None of the authentication protocols specified are supported
    Something sets the `SESSION_MANAGER` environmental variable which opencv tries to use. Set the `SESSION_MANAGER` variable to empty string in terminal to fix the issue.

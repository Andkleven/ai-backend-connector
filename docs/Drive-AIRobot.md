# Driving AI Robot in real world with AI Backend Connector
This document shows how to drive a physical robot with AI Robot software in it with the AI Backend Connector.

You should have a brain file before trying this.

## Install Gstreamer
Check the instruction from [here](Gstreamer-Install.md)

## Setup and test AI Video Streamer
Check the instruction from [here](https://github.com/robot-uprising-hq/ai-video-streamer)

Leave the AI Video Streamer streaming video to your AI Backend Connectoräs IP-address.

## Calibrate AI Video Streamer's video stream
Check the instruction from [here](Camera-Calibration.md)

## Setup AI Robot
You can use either ESP32 based AI Robot or Raspberry Pi based AI Robot.
The repos are below:

[ESP32 AI Robot](https://github.com/robot-uprising-hq/ai-robot)

[Raspberry Pi AI Robot](https://gitlab.com/jsalli/artificial-invaders-micro-robot-frontend)

Leave the AI Robot online waiting for commands.

## Start AI Remote Brain
1. Make sure AI Remote Brain has a brain file in the `Assets/BrainFileToUse`-folder. If not see [these instructions](https://github.com/robot-uprising-hq/ai-simulator/blob/master/docs/Driving-with-AIRemoteBrain.md)
1. Start the AI Remote Brain-project in Unity and load the AIRemoteBrain-scene.
1. Press 'Play'-button in AI Remote Brain Unity window.

## Setup AI Backend Connector
1. See that `params-prod.yaml`-file parameters look good.
1. Make sure:
    - AI Video Streamer is sending video feed.
    - AI Robot is online waiting for commands.
    - AI Remote Brain is online
1. Test the setup. AI Robot nor AI Remote Brain are not used nor connected to in test-mode.
    ```sh
    python gui_robot_backend.py -m=test
    ```
1. Drive the AI Robot 
    ```sh
    python gui_robot_backend.py -m=prod
    ```

## System architecture
![system-architecture](https://github.com/robot-uprising-hq/ai-guide/raw/master/system-architecture.png)

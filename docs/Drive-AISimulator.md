# Driving AI Simulator with AI Backend Connector
This document shows how to drive the AI Simulator with the AI Backend Connector and test that the AI Backend Connector works.

The AI Simulator should be able to run and you should be able to train your agents in the simulation before trying this.

---
## Install Gstreamer
Check the instruction from [here](Gstreamer-Install.md)


## Test screen streaming from AI Simulator
### AI Simulator
1. Load the scene `AIBackendConnectorTest`.
1. Press Unity's `Play`-button.
### AI Backend Connector
1. Run the following:
    ```sh
    source venv/bin/activate
    python -m ai_simulator.ai_simulator
    ```
1. A video stream from AI Simulator should appear where the robot moves randomly.

---

## Drive AI Simulator with AI Backend Connector and AI Remote Brain
The AI Backend Connector creates observations from the image requested from AI Simulator and sends the observations to the AI Remote Brain which predicts an action and sends it back to AI Backend Connector which send it back to AI Simulator.

### Calibrate AI Video Streamer's video stream
Check the instruction from [here](Camera-Calibration.md)

### AI Simulator
1. Train a brain file in the simulation.
1. Use the `move-brainfile-to-AIRemoteBrain.sh` to move a brain file to AI Remote Brain.
1. Load the scene `AIBackendConnectorTest`.
1. Press Unity's 'Play'-button.
### AI Remote Brain
1. Load the `AIRemoteBrain`-scene.
1. Press Unity's 'Play'-button.
### AI Backend Connector
1. Start AI Backend Connector's main Python script:
    ```sh
    source venv/bin/activate
    python gui_robot_backend.py -m=simu
    ```
1. A video stream window should appear with the robot moving in the simulation arena.

---

## System architecture
![system-architecture](images/system-architecture_AISimulation_AIBackendConnector_AIRemoteBrain.png)

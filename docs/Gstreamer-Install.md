# Gstreamer Installation
The repo has a script `install-gstreamer.sh` to help in installation of Gstreamer.
1. Give the script permission to be executed with `chmod +x install-gstreamer.sh`
2. Run `./install-gstreamer.sh` in the project root.

The script installs Gstreamer packages and then creates a symbolic link from system's Gstreamer Python package to this repo's Python virtual environment for the Gstreamer to be functional in this Python virtual environment.

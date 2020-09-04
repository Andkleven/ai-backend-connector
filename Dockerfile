FROM ubuntu:18.04

RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y python3-pip

# Install gstreamer
RUN apt-get install -y libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
                       gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav \
                       gstreamer1.0-doc gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa \
                       gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio

RUN apt-get install -y libfreetype6-dev

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

RUN echo 'pcm.!default {' >> /etc/asound.conf
RUN echo '    type plug' >> /etc/asound.conf
RUN echo '    slave.pcm "null"' >> /etc/asound.conf
RUN echo '}' >> /etc/asound.conf

WORKDIR /code
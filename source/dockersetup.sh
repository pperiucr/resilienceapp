#!/bin/bash
install & setup docker
sudo apt update
sudo apt install python3-pip
pip install zmq
sudo apt install docker.io -y
sudo systemctl enable docker
sudo systemctl start docker

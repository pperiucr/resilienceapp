#!/bin/bash
sudo docker build -t resilienceapp .
sudo docker run -d -p 5555:5550 --name python-server resilienceapp
sudo docker ps | grep resilienceapp

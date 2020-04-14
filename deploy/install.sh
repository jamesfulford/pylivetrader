#!/bin/bash

yum install git docker -y
systemctl enable docker
systemctl start docker

groupadd docker
usermod -aG docker $USER

cd && git clone https://github.com/jamesfulford/pylivetrader.git pylivetrader

#!/bin/bash -ex
sudo yum install -y docker vim
sudo chkconfig docker on
sudo service docker start
sudo usermod -aG docker ec2-user
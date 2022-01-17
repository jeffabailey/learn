#!/bin/bash

echo "Waiting for port $1 to open on $2"

while ! nc -z $1 $2; do   
  sleep 0.1 # wait for 1/10 of the second before check again
done

echo "Port $1 ready on $2"
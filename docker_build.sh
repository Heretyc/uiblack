#!/usr/bin/env bash
# Use this Bash script to build a local docker image for the project

# Run ./docker_build.sh for creating image project:latest or run ./docker_build.sh your_tag to specify image tag.
if [ $# -eq 0 ]
  then
    tag='latest'
  else
    tag=$1
fi

thisfolder="$(basename $PWD)"

docker build -t $thisfolder:$tag .
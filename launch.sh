#!/bin/bash
echo "Launching metabase in background."
echo "screen -r to reconnect"
screen -S metabase -d -m java -jar metabase.jar

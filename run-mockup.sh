#!/bin/bash
# 
# Launch the mockup
cd /mockup
MODELIP="redfish-mockup-server"
cmd="./redfishMockupServer.py -H $MODELIP -p $MODELPORT -D /mockup/model"
echo "Launching $cmd"
python3 $cmd

#!/bin/bash

USERNAME=$1
DATASERVER="172.16.59.3"
DATAFOLDER="/var/www/rawdata/data/1"

CMD="rsync -r $USERNAME@$DATASERVER:$DATAFOLDER /home/$USER"
echo $CMD
echo "Wait..."
eval $CMD
echo "Files were copied!"

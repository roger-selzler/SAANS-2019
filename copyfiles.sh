#!/bin/bash

USERNAME=$1
DATASERVER="172.16.59.3"
DATAFOLDER="/var/www/rawdata/data/1"

CMD="rsync $USERNAME@$DATASERVER:$DATAFOLDER"
echo $CMD
eval $CMD
echo $2

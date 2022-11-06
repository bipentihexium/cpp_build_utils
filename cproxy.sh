#!/bin/bash
scriptpath=$(readlink -f "$0")
mypath=$(dirname "$scriptpath")
python3 ${mypath}/cproxy.py $*

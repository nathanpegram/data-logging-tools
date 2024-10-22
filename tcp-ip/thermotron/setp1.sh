#!/bin/bash

{ /bin/echo  -n  "thermotron "; /bin/echo -n "SETP1="; /bin/echo "SETP1?" | /bin/nc 192.168.0.10 8888 -N; } | /bin/cat
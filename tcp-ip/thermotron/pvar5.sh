#!/bin/bash

{ /bin/echo  -n  "thermotron "; /bin/echo -n "PVAR5="; /bin/echo "PVAR5?" | /bin/nc 192.168.0.10 8888 -N; } | /bin/cat

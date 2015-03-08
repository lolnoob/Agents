#!/bin/bash -x

echo "Sarting script by nohup, you can safetly leave this terminal session."
echo "Thank you for your help :)"
nohup nice -n 19 python3 main.py 1 0.55 0.6 0.65 0.7 0.75 > out1.log & nohup nice -n 19  python3 main.py 3 0.25 0.3 0.35 0.4  > out2.log &
nohup nice -n 19  python3 main.py 1 0.55 0.6 0.65 0.7 0.75  > out3.log & nohup nice -n 19  python3 main.py 3 0.25 0.3 0.35 0.4  > out4.log &

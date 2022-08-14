import random
import time
from threading import Thread
import pygame
import sys
import csv
import os
#import pandas as pd
import numpy as np
import subprocess
times = int(sys.argv[1])
threads = list()
for i in range(times):
    threads.append(Thread(target=subprocess.run, args=(["python", "helper.py", str(i+1)],)))
for i in range(times):
    threads[i].start()
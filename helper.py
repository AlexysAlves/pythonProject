import random
import time
import threading
import pygame
import sys
import csv
import os
import pandas as pd
import numpy as np

def generate_chromosome():
    chromosome = []
    for i in range(8):
        chromosome.append(random.randint(30, 90))
    with open('chromosomes.csv', 'a', encoding='UTF8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(chromosome)

def crossover(P1, P2):
    children = []
    for i in range(8):
        gene = random.randint(1, 2)
        if gene == 1:
            children.append(P1[i])
        else:
            children.append(P2[i])
    print(children)

class Main:
    with open('chromosomes.csv', 'r', encoding='UTF8', newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
        crossover(rows[0], rows[1])

Main()

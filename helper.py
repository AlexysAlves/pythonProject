import random
import time
import threading
import pygame
import sys
import csv
import os
#import pandas as pd
import numpy as np
best = [0, 0, 0, 0, 0]
round_index = 1
sheet = f"chromosomes{sys.argv[1]}.csv"
def generate_chromosome(begin=20, end=50):
    chromosome = []
    for i in range(4):
        chromosome.append(random.randint(begin, end))
    chromosome.append(execute_simulation(chromosome))
    global best
    if chromosome[4] > best[4]:
        best = chromosome
    with open(sheet, 'a', encoding='UTF8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(chromosome)
    return chromosome

def crossover(P1, P2):
    global best
    children = [[],[]]
    for i in range(4):
        gene = random.randint(1, 2)
        if gene == 1:
            children[0].append(P1[i])
            children[1].append(P2[i])
        else:
            children[0].append(P2[i])
            children[1].append(P1[i])
    children[0].append(execute_simulation(children[0]))
    if children[0][4] > best[4]:
        best = children[0]
    children[1].append(execute_simulation(children[1]))
    if children[1][4] > best[4]:
        best = children[1]
    with open(sheet, 'a', encoding='UTF8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(children[0])
        writer.writerow(children[1])
    return children

def execute_simulation(C):
    os.system(f"python fast.py {C[0]},{C[1]},{C[2]},{C[3]} {sys.argv[1]}")
    time.sleep(1)
    vehic = f"vehicles{sys.argv[1]}.csv"
    with open(vehic, 'r', encoding='UTF8', newline="") as f:
        csv_reader = csv.reader(f)
        reader = list(csv_reader)
        simCount = int(reader[4][0])
    return simCount

def make_round(chromosomes):
    global round_index
    round_index += 1
    with open(sheet, 'a', encoding='UTF8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow("")
        tmp = f"Round {round_index}"
        writer.writerow(tmp)
    children = []
    # chromosomes.sort(reverse = True, key = lambda chromosomes: chromosomes[4])
    for i in range(0, len(chromosomes), 4):
        C1 = chromosomes[i] if chromosomes[i][4] >= chromosomes[i+1][4] else chromosomes[i+1]
        C2 = chromosomes[i+2] if chromosomes[i+2][4] >= chromosomes[i+3][4] else chromosomes[i+3]
        crossed = crossover(C1, C2)
        children.append(crossed[0])
        children.append(crossed[1])
    return children

def tournament(rounds):
    with open(sheet, 'a', encoding='UTF8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow("")
        tmp = f"Round{round_index}"
        writer.writerow(tmp)
    chromosomes = []
    for i in range(2**rounds):
        chromosomes.append(generate_chromosome())
    for i in range(rounds-1):
        chromosomes = make_round(chromosomes)
    print(f"Melhor solucao: {best}")

class Main:
    with open(sheet, 'w', encoding='UTF8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow("")
    tournament(7)

Main()

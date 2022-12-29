import random
import time
import threading
import sys
import csv
import os
#import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
best_adapt = 0
best_chromossome = None
round_index = 1
sheet = f"chromosomes{sys.argv[1]}.csv"
chr_counter=0
averages = []
generations = 10
pop_size = 16
mutation_rate = 20
with open(sheet, 'w', encoding='UTF8', newline="") as f:
    writer = csv.writer(f)
    starter = ['Starting...']
    writer.writerow(starter)
class chromosome:
    def __init__(self, index, genes):
        self.index = index
        self.genes = genes
        self.adapt = self.execute_simulation()
    def execute_simulation(self):
        os.system(f"python fast.py {self.genes[0]},{self.genes[1]},{self.genes[2]},{self.genes[3]} {sys.argv[1]}")
        time.sleep(1)
        vehic = f"vehicles{sys.argv[1]}.csv"
        with open(vehic, 'r', encoding='UTF8', newline="") as f:
            csv_reader = csv.reader(f)
            reader = list(csv_reader)
            simCount = int(reader[4][0])
        global best_adapt, best_chromossome
        if simCount > best_adapt:
            best_adapt = simCount
            best_chromossome = self
        with open(sheet, 'a', encoding='UTF8', newline="") as f:
            writer = csv.writer(f)
            self.to_print = self.genes.copy()
            self.to_print.append(simCount)
            writer.writerow(self.to_print)
        return simCount

    def __repr__(self):
        rep = 'Times(' + str(self.genes) + ') ' + 'Adapt(' + str(self.adapt) + ')'
        return rep
def crossover(P1, P2):
    children = [[],[]]
    for i in range(4):
        gene = random.randint(1, 2)
        if gene == 1:
            children[0].append(P1.genes[i])
            children[1].append(P2.genes[i])
        else:
            children[0].append(P2.genes[i])
            children[1].append(P1.genes[i])
        for j in range(2):
            mu = random.randint(1,100)
            if mu <= mutation_rate:
                update = random.randint(-10,10)
                if update >= 8:
                    children[j][-1] += update
                else:
                    children[j][-1] = 8
    return children

def run_generation(pop):
    global chr_counter, round_index
    round_index += 1
    with open(sheet, 'a', encoding='UTF8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow("")
        tmp = [f"Generation {round_index}"]
        writer.writerow(tmp)
    new_pop = []
    for i in range(round(len(pop) / 4)):
        P1 = pop[roulette_wheel_selection(pop)]
        P2 = pop[roulette_wheel_selection(pop)]
        children = crossover(P1, P2)
        new_pop.append(chromosome(chr_counter, children[0]))
        chr_counter += 1
        new_pop.append(chromosome(chr_counter, children[1]))
        chr_counter += 1
        P1.adapt = (P1.adapt + P1.execute_simulation()) / 2
        P2.adapt = (P2.adapt + P2.execute_simulation()) / 2
        new_pop.append(P1)
        new_pop.append(P2)
    avr = 0
    for chr in new_pop:
        avr += chr.adapt
    avr /= pop_size
    averages.append(avr)
    with open(sheet, 'a', encoding='UTF8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow([avr])
    return new_pop

def roulette_wheel_selection(p):
    adaps = []
    for chr in p:
        adaps.append(chr.adapt)
    c = np.cumsum(adaps)
    r = sum(adaps) * np.random.rand()
    ind = np.argwhere(r <= c)
    return ind[0][0]
class Main:
    with open(sheet, 'a', encoding='UTF8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow("")
        tmp = [f"Generation {round_index}"]
        writer.writerow(tmp)
    chromosomes = []
    for i in range(pop_size):
        genes = [random.randint(15, 40) for j in range(4)]
        chromosomes.append(chromosome(chr_counter, genes))
        chr_counter += 1
    avr = 0
    for chr in chromosomes:
        avr += chr.adapt
    avr /= pop_size
    averages.append(avr)
    with open(sheet, 'a', encoding='UTF8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow([avr])
    for i in range(generations-1):
        chromosomes = run_generation(chromosomes)
    x = np.arange(1, generations+1)
    y = np.array(averages)
    plt.title("Evoluçao do Fluxo Medio")
    plt.xlabel("Geraçoes")
    plt.ylabel("Veiculos")
    plt.plot(x, y, color="red")
    plt.show()
    print(f"Melhor solucao: {best_chromossome}")


Main()

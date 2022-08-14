import random
import time
import threading
import pygame
import sys
import csv
import os

# import pandas as pd
# from openpyxl import Workbook, load_workbook
with open('info.csv', 'w', encoding='UTF8', newline="") as f:
    writer = csv.writer(f)
    writer.writerow("")

# Selection of genes based on chromosome [G1, G2, G3, G4]
print(sys.argv[1])
chromosome = [int(c) for c in sys.argv[1].split(',')]

# Default values of signal timers
# defaultGreen = {0: 10, 1: 10, 2: 10, 3: 10}
defaultRed = 150
defaultGreen = {0: chromosome[0], 1: chromosome[1], 2: chromosome[2], 3: chromosome[3]}
# defaultRed = {0: chromosome[0], 1: chromosome[1], 2: chromosome[2], 3: chromosome[3]}
defaultYellow = 5
firstGreen = 1000
signals = []
noOfSignals = 4
currentGreen = 0  # Indicates which signal is green currently
nextGreen = (currentGreen + 1) % noOfSignals  # Indicates which signal will turn green next
currentYellow = 0  # Indicates whether yellow signal is on or off

speeds = {'car': 20.0, 'bus': 20.0, 'truck': 20.0, 'bike': 20.0}  # average speeds of vehicles

info = []
# Coordinates of vehicles' start
x = {'right': [0, 0, 0], 'down': [755, 727, 697], 'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [348, 370, 398], 'down': [0, 0, 0], 'left': [498, 466, 436], 'up': [800, 800, 800]}

vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'bike'}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Coordinates of signal image, timer, and vehicle count
signalCoods = [(530, 230), (810, 230), (810, 570), (530, 570)]
signalTimerCoods = [(530, 210), (810, 210), (810, 550), (530, 550)]

# Coordinates of stop lines
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

# Gap between vehicles
stoppingGap = 15  # stopping gap
movingGap = 15  # moving gap
speedGap = 30

# set allowed vehicle types here
allowedVehicleTypes = {'car': True, 'bus': True, 'truck': True, 'bike': True}
allowedVehicleTypesList = []
vehiclesWaiting = {'right': {1: [], 2: []}, 'down': {1: [], 2: []}, 'left': {1: [], 2: []}, 'up': {1: [], 2: []}}
vehiclesTurned = {'right': {1: [], 2: []}, 'down': {1: [], 2: []}, 'left': {1: [], 2: []}, 'up': {1: [], 2: []}}
vehiclesNotTurned = {'right': {1: [], 2: []}, 'down': {1: [], 2: []}, 'left': {1: [], 2: []}, 'up': {1: [], 2: []}}
rotationAngle = 3
mid = {'right': {'x': 705, 'y': 445}, 'down': {'x': 695, 'y': 450}, 'left': {'x': 695, 'y': 425},
       'up': {'x': 695, 'y': 400}}
# set random or default green signal time here
randomGreenSignalTimer = False
# set random green signal time range here
randomGreenSignalTimerRange = [10, 20]

# vehiclesTimes = [[] for i in range(4)]
timeElapsed = 0
simulationTime = 250
timeElapsedCoods = (1100, 50)
vehicleCountTexts = ["0", "0", "0", "0"]
vehicleCountCoods = [(480, 210), (880, 210), (880, 550), (480, 550)]

pygame.init()
simulation = pygame.sprite.Group()


class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn_r, will_turn_l):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.rgap = random.randint(30, 70)
        self.waiting = False
        self.waited = False
        self.accelerationDist = 100
        self.speed = round(random.uniform(speeds[vehicleClass] + 0.01, speeds[vehicleClass] - 0.01), 2)
        self.initialSpeed = self.speed
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn_r = will_turn_r
        self.willTurn_l = will_turn_l
        self.turned = 0
        self.rotateAngle = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        self.crossedIndex = 0
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.image = pygame.image.load(path)
        self.initialTime = timeElapsed
        self.update_delay = 750
        self.last_update = pygame.time.get_ticks()
        vehiclesWaiting[self.direction][self.lane].append(False)
        if (len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0):
            if (direction == 'right'):
                self.stop = vehicles[direction][lane][self.index - 1].stop
                - vehicles[direction][lane][self.index - 1].image.get_rect().width
                - stoppingGap
            elif (direction == 'left'):
                self.stop = vehicles[direction][lane][self.index - 1].stop
                + vehicles[direction][lane][self.index - 1].image.get_rect().width
                + stoppingGap
            elif (direction == 'down'):
                self.stop = vehicles[direction][lane][self.index - 1].stop
                - vehicles[direction][lane][self.index - 1].image.get_rect().height
                - stoppingGap
            elif (direction == 'up'):
                self.stop = vehicles[direction][lane][self.index - 1].stop
                + vehicles[direction][lane][self.index - 1].image.get_rect().height
                + stoppingGap
        else:
            self.stop = defaultStop[direction]

        # Set new starting and stopping coordinate
        if (direction == 'right'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] -= temp
        elif (direction == 'left'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif (direction == 'down'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif (direction == 'up'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        #def accelerate(gap):
         #   if gap >= self.accelerationTime * 0.8:
          #      self.speed = self.initialSpeed - 1
          #  elif gap >= self.accelerationTime * 0.6:
          #      self.speed = self.initialSpeed - 0.75
          #  elif gap >= self.accelerationTime * 0.4:
          #      self.speed = self.initialSpeed - 0.5
          #  elif gap >= self.accelerationTime * 0.2:
          #      self.speed = self.initialSpeed - 0.25
          #  else:
          #      self.speed = self.initialSpeed
          #      self.waited = False

        if (self.direction == 'right'):
            if (self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[self.direction]):
                self.crossed = 1
                self.crosstime = timeElapsed - self.initialTime
                infor = []
                infor.append(f"Right: {self.crosstime}")
                with open('right.csv', 'a', encoding='UTF8', newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(infor)

                vehicles[self.direction]['crossed'] += 1
                if (self.willTurn_r == 0 and self.willTurn_l == 0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if (self.willTurn_l == 1):
                if (self.lane == 1):
                    if (self.crossed == 0 or self.x + self.image.get_rect().width < stopLines[self.direction] + 40):
                        if ((self.x + self.image.get_rect().width <= self.stop or (
                                currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x + self.image.get_rect().width < (
                                vehicles[self.direction][self.lane][self.index - 1].x - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            if self.x + self.image.get_rect().width < (
                                    vehicles[self.direction][self.lane][self.index - 1].x - movingGap - 50) \
                                    or stopLines['right'] - self.x < 80:
                                vehiclesWaiting[self.direction][self.lane][self.index] = False
                            if self.waited:
                                self.speed = self.initialSpeed - (self.waitx - self.x)/100
                                if self.waitx <= self.x:
                                    self.waited = False
                                    self.speed = self.initialSpeed
                            if not vehiclesWaiting[self.direction][self.lane][self.index]:
                                self.x += self.speed
                        elif (not self.x + self.image.get_rect().width < (
                                vehicles[self.direction][self.lane][self.index - 1].x - movingGap)) and stopLines[
                            'right'] - self.x > 80:
                            vehiclesWaiting[self.direction][self.lane][self.index] = True
                            self.waited = True
                            self.waitx = self.x + self.accelerationDist

                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x += 2.4
                            self.y -= 28
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.y > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().height + movingGap))):
                                self.y -= self.speed
                elif (self.lane == 2):
                    if (self.crossed == 0 or self.x + self.image.get_rect().width < mid[self.direction]['x']):
                        if ((self.x + self.image.get_rect().width <= self.stop or (
                                currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x + self.image.get_rect().width < (
                                vehicles[self.direction][self.lane][self.index - 1].x - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            if self.x + self.image.get_rect().width < (
                                    vehicles[self.direction][self.lane][self.index - 1].x - movingGap - 50) or \
                                    stopLines['right'] - self.x < 80:
                                vehiclesWaiting[self.direction][self.lane][self.index] = False
                            if self.waited:
                                self.speed = self.initialSpeed - (self.waitx - self.x)/100
                                if self.waitx <= self.x:
                                    self.waited = False
                                    self.speed = self.initialSpeed
                            if not vehiclesWaiting[self.direction][self.lane][self.index]:
                                self.x += self.speed
                        elif (not self.x + self.image.get_rect().width < (
                                vehicles[self.direction][self.lane][self.index - 1].x - movingGap)) and stopLines[
                            'right'] - self.x > 80:
                            vehiclesWaiting[self.direction][self.lane][self.index] = True
                            self.waited = True
                            self.waitx = self.x + self.accelerationDist
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, - self.rotateAngle)
                            self.x += 2
                            self.y += 18
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or ((self.y + self.image.get_rect().height) < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y - movingGap))):
                                self.y += self.speed
            else:
                if (self.crossed == 0):
                    if (self.crossed == 0 or self.x + self.image.get_rect().width < stopLines[self.direction] + 40):
                        if ((self.x + self.image.get_rect().width <= self.stop or (
                                currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x + self.image.get_rect().width < (
                                vehicles[self.direction][self.lane][self.index - 1].x - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            if self.x + self.image.get_rect().width < (
                                    vehicles[self.direction][self.lane][self.index - 1].x - movingGap - 50) \
                                    or stopLines['right'] - self.x < 80:
                                vehiclesWaiting[self.direction][self.lane][self.index] = False
                            if self.waited:
                                self.speed = self.initialSpeed - (self.waitx - self.x)/100
                                if self.waitx <= self.x:
                                    self.waited = False
                                    self.speed = self.initialSpeed

                            if not vehiclesWaiting[self.direction][self.lane][self.index]:
                                self.x += self.speed
                        elif (not self.x + self.image.get_rect().width < (
                                vehicles[self.direction][self.lane][self.index - 1].x - movingGap)) and stopLines[
                            'right'] - self.x > 80:
                            vehiclesWaiting[self.direction][self.lane][self.index] = True
                            self.waited = True
                            self.waitx = self.x + self.accelerationDist
                else:
                    if ((self.crossedIndex == 0) or (self.x + self.image.get_rect().width < (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].x - movingGap))):
                        self.x += self.speed


        elif (self.direction == 'down'):
            if (self.crossed == 0 and self.y + self.image.get_rect().height > stopLines[self.direction]):
                self.crossed = 1
                self.crosstime = timeElapsed - self.initialTime
                infor = []
                infor.append(f"Down: {self.crosstime}")
                with open('down.csv', 'a', encoding='UTF8', newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(infor)
                vehicles[self.direction]['crossed'] += 1
                if (self.willTurn_r == 0 and self.willTurn_l == 0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if (self.willTurn_l == 1):
                if (self.lane == 1):
                    if (self.crossed == 0 or self.y + self.image.get_rect().height < stopLines[self.direction] + 50):
                        if ((self.y + self.image.get_rect().height <= self.stop or (
                                currentGreen == 1 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.y + self.image.get_rect().height < (
                                vehicles[self.direction][self.lane][self.index - 1].y - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            if self.y + self.image.get_rect().height < (
                                    vehicles[self.direction][self.lane][self.index - 1].y - movingGap - self.rgap) \
                                    or stopLines['down'] - self.y < 120:
                                vehiclesWaiting[self.direction][self.lane][self.index] = False
                            if self.waited:
                                self.speed = self.initialSpeed - (self.waitx - self.y)/100
                                if self.waitx <= self.y:
                                    self.waited = False
                                    self.speed = self.initialSpeed
                            if not vehiclesWaiting[self.direction][self.lane][self.index]:
                                self.y += self.speed
                        elif (not self.y + self.image.get_rect().height < (
                                vehicles[self.direction][self.lane][self.index - 1].y - movingGap)) and stopLines[
                            'down'] - self.y > 120:
                            vehiclesWaiting[self.direction][self.lane][self.index] = True
                            self.waited = True
                            self.waitx = self.y + self.accelerationDist
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x += 12
                            self.y += 1.8
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or ((self.x + self.image.get_rect().width) < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x - movingGap))):
                                self.x += self.speed
                elif (self.lane == 2):
                    if (self.crossed == 0 or self.y + self.image.get_rect().height < mid[self.direction]['y']):
                        if ((self.y + self.image.get_rect().height <= self.stop or (
                                currentGreen == 1 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.y + self.image.get_rect().height < (
                                vehicles[self.direction][self.lane][self.index - 1].y - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            if self.y + self.image.get_rect().height < (
                                    vehicles[self.direction][self.lane][self.index - 1].y - movingGap - self.rgap) \
                                    or stopLines['down'] - self.y < 120:
                                vehiclesWaiting[self.direction][self.lane][self.index] = False
                            if self.waited:
                                self.speed = self.initialSpeed - (self.waitx - self.y)/100
                                if self.waitx <= self.y:
                                    self.waited = False
                                    self.speed = self.initialSpeed
                            if not vehiclesWaiting[self.direction][self.lane][self.index]:
                                self.y += self.speed
                        elif (not self.y + self.image.get_rect().height < (
                                vehicles[self.direction][self.lane][self.index - 1].y - movingGap)) and stopLines[
                            'down'] - self.y > 120:
                            vehiclesWaiting[self.direction][self.lane][self.index] = True
                            self.waited = True
                            self.waitx = self.y + self.accelerationDist
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x -= 25
                            self.y += 2
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.x > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().width + movingGap))):
                                self.x -= self.speed
            else:
                if (self.crossed == 0):
                    if ((self.y + self.image.get_rect().height <= self.stop or (
                            currentGreen == 1 and currentYellow == 0)) and (
                            self.index == 0 or self.y + self.image.get_rect().height < (
                            vehicles[self.direction][self.lane][self.index - 1].y - movingGap))):
                        if self.y + self.image.get_rect().height < (
                                vehicles[self.direction][self.lane][self.index - 1].y - movingGap - self.rgap) \
                                or stopLines['down'] - self.y < 120:
                            vehiclesWaiting[self.direction][self.lane][self.index] = False
                        if self.waited:
                            self.speed = self.initialSpeed - (self.waitx - self.y) / 100
                            if self.waitx <= self.y:
                                self.waited = False
                                self.speed = self.initialSpeed
                        if not vehiclesWaiting[self.direction][self.lane][self.index]:
                            self.y += self.speed
                    elif (not self.y + self.image.get_rect().height < (
                            vehicles[self.direction][self.lane][self.index - 1].y - movingGap)) and stopLines[
                        'down'] - self.y > 120:
                        vehiclesWaiting[self.direction][self.lane][self.index] = True
                        self.waited = True
                        self.waitx = self.y + self.accelerationDist
                else:
                    if ((self.crossedIndex == 0) or (self.y + self.image.get_rect().height < (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].y - movingGap))):
                        self.y += self.speed
        elif (self.direction == 'left'):
            if (self.crossed == 0 and self.x < stopLines[self.direction]):
                self.crossed = 1
                self.crosstime = timeElapsed - self.initialTime
                infor = []
                infor.append(f"Left: {self.crosstime}")
                with open('left.csv', 'a', encoding='UTF8', newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(infor)
                vehicles[self.direction]['crossed'] += 1
                if (self.willTurn_r == 0 and self.willTurn_l == 0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if (self.willTurn_l == 1):
                if (self.lane == 1):
                    if (self.crossed == 0 or self.x > stopLines[self.direction] - 70):
                        if ((self.x >= self.stop or (
                                currentGreen == 2 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index - 1].x +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().width + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            if self.x - self.image.get_rect().width > (
                                    vehicles[self.direction][self.lane][self.index - 1].x + movingGap + self.rgap) \
                                    or self.x - stopLines['left'] < 60:
                                vehiclesWaiting[self.direction][self.lane][self.index] = False
                            if self.waited:
                                self.speed = self.initialSpeed - (self.x - self.waitx)/100
                                if self.waitx >= self.x:
                                    self.waited = False
                                    self.speed = self.initialSpeed
                            if not vehiclesWaiting[self.direction][self.lane][self.index]:
                                self.x -= self.speed
                        elif (not self.x - self.image.get_rect().width > (
                                vehicles[self.direction][self.lane][self.index - 1].x + movingGap)) and self.x - \
                                stopLines['left'] > 60:
                            vehiclesWaiting[self.direction][self.lane][self.index] = True
                            self.waited = True
                            self.waitx = self.x - self.accelerationDist
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x -= 1
                            self.y += 12
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or ((self.y + self.image.get_rect().height) < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y - movingGap))):
                                self.y += self.speed
                elif (self.lane == 2):
                    if (self.crossed == 0 or self.x > mid[self.direction]['x']):
                        if ((self.x >= self.stop or (
                                currentGreen == 2 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index - 1].x +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().width + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            if self.x - self.image.get_rect().width > (
                                    vehicles[self.direction][self.lane][self.index - 1].x + movingGap + self.rgap) \
                                    or self.x - stopLines['left'] < 60:
                                vehiclesWaiting[self.direction][self.lane][self.index] = False
                            if self.waited:
                                self.speed = self.initialSpeed - (self.x - self.waitx)/100
                                if self.waitx >= self.x:
                                    self.waited = False
                                    self.speed = self.initialSpeed
                            if not vehiclesWaiting[self.direction][self.lane][self.index]:
                                self.x -= self.speed
                        elif (not self.x - self.image.get_rect().width > (
                                vehicles[self.direction][self.lane][self.index - 1].x + movingGap)) and self.x - \
                                stopLines['left'] > 60:
                            vehiclesWaiting[self.direction][self.lane][self.index] = True
                            self.waited = True
                            self.waitx = self.x - self.accelerationDist
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x -= 1.8
                            self.y -= 25
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.y > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().height + movingGap))):
                                self.y -= self.speed
            else:
                if (self.crossed == 0):
                    if ((self.x >= self.stop or (currentGreen == 2 and currentYellow == 0)) and (
                            self.index == 0 or self.x > (
                            vehicles[self.direction][self.lane][self.index - 1].x + vehicles[self.direction][self.lane][
                        self.index - 1].image.get_rect().width + movingGap))):
                        if self.x - self.image.get_rect().width > (
                                vehicles[self.direction][self.lane][self.index - 1].x + movingGap + self.rgap) \
                                or self.x - stopLines['left'] < 60:
                            vehiclesWaiting[self.direction][self.lane][self.index] = False
                        if self.waited:
                            self.speed = self.initialSpeed - (self.x - self.waitx) / 100
                            if self.waitx >= self.x:
                                self.waited = False
                                self.speed = self.initialSpeed
                        if not vehiclesWaiting[self.direction][self.lane][self.index]:
                            self.x -= self.speed
                    elif (not self.x - self.image.get_rect().width > (
                            vehicles[self.direction][self.lane][self.index - 1].x + movingGap)) and self.x - stopLines[
                        'left'] > 60:
                        vehiclesWaiting[self.direction][self.lane][self.index] = True
                        self.waited = True
                        self.waitx = self.x - self.accelerationDist
                else:
                    if ((self.crossedIndex == 0) or (self.x > (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].x +
                            vehiclesNotTurned[self.direction][self.lane][
                                self.crossedIndex - 1].image.get_rect().width + movingGap))):
                        self.x -= self.speed
        elif (self.direction == 'up'):
            if (self.crossed == 0 and self.y < stopLines[self.direction]):
                self.crossed = 1
                self.crosstime = timeElapsed - self.initialTime
                infor = []
                infor.append(f"Up: {self.crosstime}")
                with open('up.csv', 'a', encoding='UTF8', newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(infor)
                vehicles[self.direction]['crossed'] += 1
                if (self.willTurn_r == 0 and self.willTurn_l == 0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if (self.willTurn_l == 1):
                if (self.lane == 1):
                    if (self.crossed == 0 or self.y > stopLines[self.direction] - 60):
                        if ((self.y >= self.stop or (
                                currentGreen == 3 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index - 1].y +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().height + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            if self.y - self.image.get_rect().height > (
                                    vehicles[self.direction][self.lane][self.index - 1].y + movingGap + self.rgap) \
                                    or self.y - stopLines['up'] < 50:
                                vehiclesWaiting[self.direction][self.lane][self.index] = False
                            if self.waited:
                                self.speed = self.initialSpeed - (self.y - self.waitx) / 100
                                if self.waitx >= self.y:
                                    self.waited = False
                                    self.speed = self.initialSpeed
                            if not vehiclesWaiting[self.direction][self.lane][self.index]:
                                self.y -= self.speed
                        elif (not self.y - self.image.get_rect().height > (
                                vehicles[self.direction][self.lane][self.index - 1].y + movingGap)) and self.y - \
                                stopLines[
                                    'up'] > 50:

                            vehiclesWaiting[self.direction][self.lane][self.index] = True
                            self.waited = True
                            self.waitx = self.y - self.accelerationDist
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x -= 20
                            self.y -= 1.2
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.x > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().width + movingGap))):
                                self.x -= self.speed
                elif (self.lane == 2):
                    if (self.crossed == 0 or self.y > mid[self.direction]['y']):
                        if ((self.y >= self.stop or (
                                currentGreen == 3 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index - 1].y +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().height + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            if self.y - self.image.get_rect().height > (
                                    vehicles[self.direction][self.lane][self.index - 1].y + movingGap + self.rgap) \
                                    or self.y - stopLines['up'] < 50:
                                vehiclesWaiting[self.direction][self.lane][self.index] = False
                            if self.waited:
                                self.speed = self.initialSpeed - (self.y - self.waitx) / 100
                                if self.waitx >= self.y:
                                    self.waited = False
                                    self.speed = self.initialSpeed
                            if not vehiclesWaiting[self.direction][self.lane][self.index]:
                                self.y -= self.speed
                        elif (not self.y - self.image.get_rect().height > (
                                vehicles[self.direction][self.lane][self.index - 1].y + movingGap)) and self.y - \
                                stopLines[
                                    'up'] > 50:

                            vehiclesWaiting[self.direction][self.lane][self.index] = True
                            self.waited = True
                            self.waitx = self.y - self.accelerationDist
                    else:
                        if (self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x += 10
                            self.y -= 1
                            if (self.rotateAngle == 90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.x < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x -
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().width - movingGap))):
                                self.x += self.speed
            else:
                if (self.crossed == 0):
                    if ((self.y >= self.stop or (currentGreen == 3 and currentYellow == 0)) and (
                            self.index == 0 or self.y > (
                            vehicles[self.direction][self.lane][self.index - 1].y + vehicles[self.direction][self.lane][
                        self.index - 1].image.get_rect().height + movingGap))):
                        if self.y - self.image.get_rect().height > (
                                vehicles[self.direction][self.lane][self.index - 1].y + movingGap + self.rgap) \
                                or self.y - stopLines['up'] < 50:
                            vehiclesWaiting[self.direction][self.lane][self.index] = False
                        if self.waited:
                            self.speed = self.initialSpeed - (self.y - self.waitx) / 100
                            if self.waitx >= self.y:
                                self.waited = False
                                self.speed = self.initialSpeed
                        if not vehiclesWaiting[self.direction][self.lane][self.index]:
                            self.y -= self.speed
                    elif (not self.y - self.image.get_rect().height > (
                            vehicles[self.direction][self.lane][self.index - 1].y + movingGap)) and self.y - stopLines[
                        'up'] > 50:

                        vehiclesWaiting[self.direction][self.lane][self.index] = True
                        self.waited = True
                        self.waitx = self.y - self.accelerationDist
                else:
                    if ((self.crossedIndex == 0) or (self.y > (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].y +
                            vehiclesNotTurned[self.direction][self.lane][
                                self.crossedIndex - 1].image.get_rect().height + movingGap))):
                        self.y -= self.speed

                    # Initialization of signals with default values


def initialize():
    minTime = randomGreenSignalTimerRange[0]
    maxTime = randomGreenSignalTimerRange[1]
    if (randomGreenSignalTimer):
        ts1 = TrafficSignal(0, defaultYellow, random.randint(minTime, maxTime))
        signals.append(ts1)
        ts2 = TrafficSignal(ts1.red + ts1.yellow + ts1.green, defaultYellow, random.randint(minTime, maxTime))
        signals.append(ts2)
        ts3 = TrafficSignal(defaultRed, defaultYellow, random.randint(minTime, maxTime))
        signals.append(ts3)
        ts4 = TrafficSignal(defaultRed, defaultYellow, random.randint(minTime, maxTime))
        signals.append(ts4)
    else:
        ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
        signals.append(ts1)
        ts2 = TrafficSignal(ts1.yellow + ts1.green, defaultYellow, defaultGreen[1])
        signals.append(ts2)
        ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[2])
        signals.append(ts3)
        ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[3])
        signals.append(ts4)
    repeat()

# Print the signal timers on cmd
def printStatus():
    status = []
    for i in range(0, 4):
        if (signals[i] != None):
            if (i == currentGreen):
                if (currentYellow == 0):
                    tmp = f"   VERDE SV {i + 1} -> vrm: {signals[i].red}  ama: {signals[i].yellow}  vrd: {signals[i].green}"
                    #print(tmp)
                    status.append(tmp)
                else:
                    tmp = f"   AMARELO SV {i + 1} -> vrm: {signals[i].red}  ama: {signals[i].yellow}  vrd: {signals[i].green}"
                    #print(tmp)
                    status.append(tmp)
            else:
                tmp = f"   VERMELHO SV {i + 1} -> vrm: {signals[i].red}  ama: {signals[i].yellow}  vrd: {signals[i].green}"
                #print(tmp)
                status.append(tmp)
    info.append(status)
    with open('info.csv', 'a', encoding='UTF8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(status)
    #print()


def repeat():
    global currentGreen, currentYellow, nextGreen
    while (signals[currentGreen].green > 0):  # while the timer of current green signal is not zero
        printStatus()
        updateValues()
        time.sleep(0.1)
    currentYellow = 1  # set yellow signal on
    # reset stop coordinates of lanes and vehicles
    for i in range(0, 3):
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    while (signals[currentGreen].yellow > 0):  # while the timer of current yellow signal is not zero
        printStatus()
        updateValues()
        time.sleep(0.1)
    currentYellow = 0  # set yellow signal off

    # reset all signal times of current signal to default/random times
    if (randomGreenSignalTimer):
        signals[currentGreen].green = random.randint(randomGreenSignalTimerRange[0], randomGreenSignalTimerRange[1])
    else:
        signals[currentGreen].green = defaultGreen[currentGreen]

    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed

    currentGreen = nextGreen  # set next signal as green signal
    nextGreen = (currentGreen + 1) % noOfSignals  # set next green signal
    signals[nextGreen].red = signals[currentGreen].yellow + signals[
        currentGreen].green  # set the red time of next to next signal as (yellow time + green time) of next signal
    repeat()


# Update values of the signal timers after every second


# Generating vehicles in the simulation
def updateValues():
    for i in range(0, noOfSignals):

        if (i == currentGreen):
            if (currentYellow == 0):
                signals[i].green -= 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1


def generateVehicles():
    while (True):
        vehicle_type = random.choice(allowedVehicleTypesList)
        lane_number = random.randint(1, 2)
        will_turn_r = 0
        will_turn_l = 0
        temp1 = random.randint(0, 60)
        temp2 = random.randint(39, 99)
        temp = random.randint(0, 99)
        if (lane_number == 1 and temp <= temp1):
            will_turn_l = 1
        elif (lane_number == 2 and temp >= temp2):
            will_turn_l = 1
        temp = random.randint(0, 99)
        direction_number = 0
        if len(sys.argv) > 3:
            dist = [int(k) for k in sys.argv[3].split(",")]
        else:
            dist = [25, 50, 75, 100]
        if (temp < dist[0]):
            direction_number = 0
        elif (temp < dist[1]):
            direction_number = 1
        elif (temp < dist[2]):
            direction_number = 2
        elif (temp < dist[3]):
            direction_number = 3
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number],
                will_turn_r, will_turn_l)
        time.sleep(0.1)


def showStats():
    totalVehicles = 0
    print('Informações finais')
    vehic = f"vehicles{sys.argv[2]}.csv"
    with open(vehic, 'w', encoding='UTF8', newline="") as f:
        writer = csv.writer(f)
        for i in range(0, 4):
            if (signals[i] != None):
                tmp = [f"Direção {i + 1} : {vehicles[directionNumbers[i]]['crossed']}"]
                print(tmp[0])
                writer.writerow(tmp)
                totalVehicles += vehicles[directionNumbers[i]]['crossed']
        tmp = [f"{totalVehicles}"]
        print(tmp[0])
        writer.writerow(tmp)
        tmp = [f"Tempo total: {timeElapsed}"]
        print(tmp[0])
        writer.writerow(tmp)

    '''writer = pd.ExcelWriter('test.xlsx', engine='xlsxwriter') 
    workbook = writer.book
    worksheet = workbook.add_worksheet('Sheet1')
    writer.sheets['Sheet1'] = worksheet
    values = pd.DataFrame({'valor1':[tmp[0]], 'valor2':[tmp[1]], 'valor3':[tmp[2]], 'valor4':[tmp[3]]})
    values.to_excel('./graficos.xlsx', sheet_name='Sheet1', header=False, startrow=5)'''


def simTime():
    global timeElapsed, simulationTime
    while (True):
        timeElapsed += 1
        time.sleep(0.1)
        if (timeElapsed == simulationTime):
            showStats()
            os._exit(1)


def keyboardInterruptHandler():
    print('My application is ending!')


class Main:
    global allowedVehicleTypesList
    i = 0
    for vehicleType in allowedVehicleTypes:
        if (allowedVehicleTypes[vehicleType]):
            allowedVehicleTypesList.append(i)
        i += 1
    thread1 = threading.Thread(name="initialization", target=initialize, args=())  # initialization
    thread1.daemon = True
    thread1.start()

    # Colours
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('images/intersection.png')

    #screen = pygame.display.set_mode(screenSize)
    #pygame.display.set_caption("SIMULATION")

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)
    thread2 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())  # Generating vehicles
    thread2.daemon = True
    thread2.start()

    thread3 = threading.Thread(name="simTime", target=simTime, args=())
    thread3.daemon = True
    thread3.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                showStats()
                sys.exit()

        #screen.blit(background, (0, 0))  # display background in simulation
        for i in range(0,
                       noOfSignals):  # display signal and set timer according to current status: green, yello, or red
            if (i == currentGreen):
                if (currentYellow == 1):
                    signals[i].signalText = signals[i].yellow
                    #screen.blit(yellowSignal, signalCoods[i])
                else:
                    signals[i].signalText = signals[i].green
                    #screen.blit(greenSignal, signalCoods[i])
            else:
                if (signals[i].red <= 10):
                    signals[i].signalText = signals[i].red
                else:
                    signals[i].signalText = "---"
                #screen.blit(redSignal, signalCoods[i])
        signalTexts = ["", "", "", ""]

        # display signal timer
        for i in range(0, noOfSignals):
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            #screen.blit(signalTexts[i], signalTimerCoods[i])

        # display vehicle count
        for i in range(0, noOfSignals):
            displayText = vehicles[directionNumbers[i]]['crossed']
            vehicleCountTexts[i] = font.render(str(displayText), True, black, white)
            #screen.blit(vehicleCountTexts[i], vehicleCountCoods[i])

        # display time elapsed
        timeElapsedText = font.render(("Tempo de simulação: " + str(timeElapsed)), True, black, white)
        #screen.blit(timeElapsedText, timeElapsedCoods)

        # display the vehicles
        for vehicle in simulation:
           # screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()
        #pygame.display.update()


Main()